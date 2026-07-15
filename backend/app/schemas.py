from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

ALLOWED_CATEGORIES = {
    "관광지", "맛집", "축제·행사", "레포츠", "문화시설",
    "쇼핑", "숙박", "여행코스", "자유",
}


class PostFields(BaseModel):
    category: str
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1, max_length=5000)

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        value = value.strip()
        if value not in ALLOWED_CATEGORIES:
            raise ValueError("허용되지 않은 카테고리입니다.")
        return value

    @field_validator("title", "content")
    @classmethod
    def trim_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("공백만 입력할 수 없습니다.")
        return value


class PostCreate(PostFields):
    password: str = Field(min_length=1, max_length=30)


class PostUpdate(PostFields):
    password: str = Field(min_length=1, max_length=30)


class PasswordRequest(BaseModel):
    password: str = Field(min_length=1, max_length=30)


class PostResponse(PostFields):
    model_config = ConfigDict(from_attributes=True)

    id: int
    views: int
    likes: int
    created_at: datetime
    updated_at: datetime


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)
    password: str = Field(min_length=1, max_length=30)

    @field_validator("content")
    @classmethod
    def trim_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("공백만 입력할 수 없습니다.")
        return value


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int
    content: str
    created_at: datetime


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)


class ChatResponse(BaseModel):
    answer: str
    public_data_results: list[dict] = []
    community_results: list[dict] = []
