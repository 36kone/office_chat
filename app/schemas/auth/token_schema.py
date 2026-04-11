from pydantic import BaseModel

from ..user.user_schema import SimpleUserResponse


class CreateToken(BaseModel):
    id: str
    token_role: str
    username: str | None = None
    session_id: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str
    token_role: str
    user: SimpleUserResponse
