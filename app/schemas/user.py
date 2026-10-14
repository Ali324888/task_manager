from pydantic import BaseModel, Field, field_validator

class UserCreate(BaseModel):
    username : str = Field(min_length=3, max_length=30)
    email : str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Username cannot be empty")

        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()

        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("invalid email format")

        return value


class UserPublic(BaseModel):
    id: int
    username: str
    email: str
    created_at: str

