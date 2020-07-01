from typing import List, Callable, Optional

from pydantic import BaseModel
from typing import Protocol


class Credentials(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    username: str
    full_name: Optional[str] = None
    organization: str = "Public"
    access_level: int = 0


class UserInfoWithoutOrg(BaseModel):
    username: str
    access_level: int = 0


class FullUser(Credentials, UserInfo):
    pass


class NewUser(Credentials):
    full_name: str
    invitation_code: str

class InviteCode(BaseModel):
    issuer_id: str
    code: str
    docs: List[str] = []

class TokenTester(Protocol):
    def __call__(
        self,
        greater_or_equal: Optional[int] = None,
        one_of: Optional[List[int]] = None,
    ) -> Callable[[str], UserInfo]:
        ...


class OrganisationInfo(BaseModel):
    title: Optional[str] = None
    org_id: str


class FullOrganisationInfo(OrganisationInfo):
    users: List[UserInfoWithoutOrg]
