from typing import List, Callable, Optional

from pydantic import BaseModel
from typing_extensions import Protocol


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
    organization: str = "Public"
    access_level: int = 0


class FullUser(Credentials, UserInfo):
    pass


class NewUser(FullUser):
    invitation_code: str


class TokenTester(Protocol):
    def __call__(
        self,
        greater_or_equal: Optional[int] = None,
        one_of: Optional[List[int]] = None,
    ) -> Callable[[str], UserInfo]:
        ...


class OrganisationInfo(BaseModel):
    title: str
    name: str


class FullOrganisationInfo(OrganisationInfo):
    users: List[UserInfoWithoutOrg]
