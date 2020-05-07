from typing import Optional

from pydantic import BaseModel


class Credentials(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    username: str
    full_name: Optional[str] = None
    organization: str = "Public"
    access_level: int = 0


class FullUser(Credentials, UserInfo):
    pass


class NewUser(FullUser):
    invitation_code: str
