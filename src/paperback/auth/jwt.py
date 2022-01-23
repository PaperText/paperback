import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable, TypedDict
from functools import lru_cache

from fastapi import HTTPException, status, Depends
from authlib.jose import jwt
import ecdsa

from paperback.auth.logging import logger
from paperback.auth.crud import get_user_by_token_uuid
from paperback.auth.settings import AuthSettings, get_auth_settings
from paperback.auth import schemas
from paperback.auth.crud import get_token
from paperback.auth.database import get_session


claim_option: dict[str, dict[str, bool | list[str]]] = {
    "iss": {
        "essential": True,
        "values": ["paperback"],
    },
    "sub": {
        "essential": True,
    },
    "exp": {
        "essential": True,
    },
    "jti": {
        "essential": True,
    },
}


def generate_keys(curve: str) -> tuple[bytes, bytes]:
    match curve:
        case "secp521r1":
            logger.debug("creating secp521r1 keys")
            sk: ecdsa.SigningKey = ecdsa.SigningKey.generate(curve=ecdsa.NIST521p)
            vk: ecdsa.VerifyingKey = sk.verifying_key
            sk_bytes: bytes = bytes(sk.to_pem())
            vk_bytes: bytes = bytes(vk.to_pem())
            return sk_bytes, vk_bytes
        case _:
            logger.error("can't find specified curve")
            raise KeyError("can't find specified curve")


def read_keys(
    curve: str, private_key_file: Path, public_key_file: Path
) -> tuple[bytes, bytes]:
    match curve:
        case "secp521r1":
            logger.debug("reading secp521r1 keys")
            sk: ecdsa.SigningKey = ecdsa.SigningKey.from_pem(
                private_key_file.read_text()
            )
            vk: ecdsa.VerifyingKey = sk.verifying_key
            sk_bytes: bytes = bytes(sk.to_pem())
            vk_bytes: bytes = bytes(vk.to_pem())
            return sk_bytes, vk_bytes
        case _:
            logger.error("can't read specified curve")
            raise KeyError("can't read specified curve")


class JWTKeys(TypedDict):
    private_key_file: Path
    public_key_file: Path
    private_key: bytes
    public_key: bytes


keys: JWTKeys | None = None


def get_jwt_keys(settings: AuthSettings = Depends(get_auth_settings)) -> JWTKeys:
    logger.debug("getting jwt keys")
    global keys

    if keys is None:
        logger.debug("processing jwt keys")
        private_key_file, public_key_file = (
            settings.storage_path / "private.pem",
            settings.storage_path / "public.pem",
        )
        private_key: bytes
        public_key: bytes

        if settings.recreate_keys:
            logger.debug("option for recreating keys is enabled")
            if public_key_file.exists():
                logger.warning("public key exist, saving it")
                bak_public_key_file = Path(str(private_key_file) + ".bak")
                private_key_file.rename(bak_public_key_file)
                public_key_file.touch()
            if private_key_file.exists():
                logger.warning("private key exist, saving it")
                bak_private_key_file = Path(str(private_key_file) + ".bak")
                private_key_file.rename(bak_private_key_file)
                private_key_file.touch()
            if not (public_key_file.exists() and private_key_file.exists()):
                logger.debug("no keys found")
                public_key_file.touch()
                private_key_file.touch()
            logger.debug("generating new keys")
            private_key, public_key = generate_keys(settings.curve)
            logger.debug("saving new keys")
            private_key_file.write_bytes(private_key)
            public_key_file.write_bytes(public_key)
        else:
            if public_key_file.exists() and private_key_file.exists():
                logger.debug("both keys are present")
            else:
                logger.error("one of the keys if missing")
                # TODO: better exception
                raise Exception("one of the keys if missing")
            private_key, public_key = read_keys(
                settings.curve, private_key_file, public_key_file
            )
        keys = JWTKeys(
            private_key_file=private_key_file,
            public_key_file=public_key_file,
            private_key=private_key,
            public_key=public_key,
        )
    else:
        logger.debug("using cached jwt keys")
    return keys


def get_decode_token(
    session=Depends(get_session), jwt_keys: JWTKeys = Depends(get_jwt_keys)
) -> Callable[[str], schemas.Token]:
    def decode_token(token: str) -> schemas.Token:
        try:
            claims = jwt.decode(
                token, jwt_keys["public_key"], claims_options=claim_option
            )
            claims.validate()
        except Exception as exception:
            logger.error("can't verify token %s", token)
            logger.error(exception)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="can't verify token",
            )

        token_uuid = uuid.UUID(claims["jti"])
        token = get_token(session, token_uuid)
        return token

    return decode_token
