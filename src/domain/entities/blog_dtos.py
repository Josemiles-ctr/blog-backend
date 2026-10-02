from datetime import datetime
from typing import Any

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

MAX_TITLE = 255
MAX_TOPIC_NAME = 100
MAX_REFERENCE_TITLE = 255
MAX_REFERENCE_LINK = 2048
MAX_RELATIONS = 50


def _not_blank(value: str | None) -> str | None:
    if value is None:
        return None
    if not value.strip():
        raise ValueError("must not be blank")
    return value.strip()


class TopicCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=MAX_TOPIC_NAME)
    description: str | None = Field(default=None)

    _strip_name = field_validator("name")(_not_blank)
    _strip_description = field_validator("description")(_not_blank)


class TopicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class ReferenceCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=MAX_REFERENCE_TITLE)
    link: AnyHttpUrl | None = None

    _strip_title = field_validator("title")(_not_blank)


class ReferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    link: str | None
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def domain(self) -> str | None:
        if not self.link:
            return None
        return AnyHttpUrl(self.link).host


def _check_duplicates(
    value: list[Any] | None, field_name: str
) -> list[Any] | None:
    if value is None:
        return None
    keys = [
        (item.name,) if isinstance(item, TopicCreate) else (item.title, item.link)
        for item in value
    ]
    if len(set(keys)) != len(keys):
        raise ValueError(f"{field_name} must not contain duplicates")
    return value


class BlogCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=MAX_TITLE)
    content: str = Field(min_length=1)
    topics: list[TopicCreate] = Field(default_factory=list, max_length=MAX_RELATIONS)
    references: list[ReferenceCreate] = Field(default_factory=list, max_length=MAX_RELATIONS)

    _strip_title = field_validator("title")(_not_blank)

    @field_validator("topics")
    @classmethod
    def _unique_topics(cls, value: list[TopicCreate]) -> list[TopicCreate]:
        return _check_duplicates(value, "topics")  # type: ignore[return-value]

    @field_validator("references")
    @classmethod
    def _unique_references(
        cls, value: list[ReferenceCreate]
    ) -> list[ReferenceCreate]:
        return _check_duplicates(value, "references")  # type: ignore[return-value]


class BlogUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=MAX_TITLE)
    content: str | None = Field(default=None, min_length=1)
    topics: list[TopicCreate] | None = Field(
        default=None, max_length=MAX_RELATIONS
    )
    references: list[ReferenceCreate] | None = Field(
        default=None, max_length=MAX_RELATIONS
    )

    _strip_title = field_validator("title")(_not_blank)

    @model_validator(mode="after")
    def _at_least_one_field(self) -> "BlogUpdate":
        if not self.model_fields_set:
            raise ValueError("at least one field must be provided")
        return self

    @field_validator("topics")
    @classmethod
    def _unique_topics(cls, value: list[TopicCreate] | None) -> list[TopicCreate] | None:
        return _check_duplicates(value, "topics")  # type: ignore[return-value]

    @field_validator("references")
    @classmethod
    def _unique_references(
        cls, value: list[ReferenceCreate] | None
    ) -> list[ReferenceCreate] | None:
        return _check_duplicates(value, "references")  # type: ignore[return-value]


class BlogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    topics: list[TopicRead] = Field(default_factory=list)
    references: list[ReferenceRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime