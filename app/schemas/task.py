from pydantic import BaseModel, Field, field_validator, ConfigDict


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("task title cannot be empty")

        return value


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:

        if value is None:
            return value

        value = value.strip()
    
        if not value:
            raise ValueError("task title cannot be empty")
    
        return value


class TaskPublic(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    completed: bool
    created_at: str

    model_config = ConfigDict(from_attributes=True)

    