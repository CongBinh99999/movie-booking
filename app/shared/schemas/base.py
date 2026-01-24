from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True
    )


class BaseRequest(BaseSchema):
    model_config = ConfigDict(
        **BaseSchema.model_config.__dict__,
        extra="forbid"
    )


class BaseResponse(BaseSchema):
    pass


class TimeStampMixin(BaseModel):
    created_at: datetime
    updated_at: datetime


class IdentifiableMixin(BaseModel):
    id: UUID
