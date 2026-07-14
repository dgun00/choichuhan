from __future__ import annotations

import math
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Body, Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from .database import (
    Base,
    apply_sqlite_compatibility_migrations,
    engine,
    get_db,
)
from .models import Post
from .public_data import (
    get_summary,
    preview_file,
    search_public_data,
)
from .schemas import (
    ChatRequest,
    ChatResponse,
    PasswordRequest,
    PostCreate,
    PostResponse,
    PostUpdate,
)

load_dotenv()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    apply_sqlite_compatibility_migrations()
    yield


app = FastAPI(
    title="LocalHub API",
    version="2.0.0",
    lifespan=lifespan,
)

origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://127.0.0.1:5500,http://localhost:5500,"
        "http://127.0.0.1:5173,http://localhost:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"message": "LocalHub API is running"}


@app.get("/api/health")
def api_health():
    return {"status": "ok"}


@app.get("/api/posts", response_model=list[PostResponse])
def get_posts(
    category: str | None = Query(default=None),
    keyword: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
):
    filters = []

    if category:
        filters.append(Post.category == category)

    if keyword and keyword.strip():
        search_word = f"%{keyword.strip()}%"
        filters.append(
            or_(
                Post.title.ilike(search_word),
                Post.content.ilike(search_word),
            )
        )

    statement = select(Post)
    if filters:
        statement = statement.where(*filters)

    return list(
        db.scalars(
            statement.order_by(Post.id.desc())
        ).all()
    )


@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    post.views += 1
    db.commit()
    db.refresh(post)
    return post


@app.post("/api/posts", response_model=PostResponse, status_code=201)
def create_post(payload: PostCreate, db: Session = Depends(get_db)):
    post = Post(
        category=payload.category,
        title=payload.title,
        content=payload.content,
        password=payload.password,
        views=0,
        likes=0,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@app.post("/api/posts/{post_id}/verify-password")
def verify_password(
    post_id: int,
    payload: PasswordRequest,
    db: Session = Depends(get_db),
):
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    if post.password != payload.password:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")

    return {"verified": True}


@app.put("/api/posts/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    payload: PostUpdate,
    db: Session = Depends(get_db),
):
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    if post.password != payload.password:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")

    post.category = payload.category
    post.title = payload.title
    post.content = payload.content

    db.commit()
    db.refresh(post)
    return post


@app.delete("/api/posts/{post_id}", status_code=204)
def delete_post(
    post_id: int,
    payload: PasswordRequest = Body(...),
    db: Session = Depends(get_db),
):
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    if post.password != payload.password:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")

    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/api/posts/{post_id}/like", response_model=PostResponse)
def like_post(post_id: int, db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    post.likes += 1
    db.commit()
    db.refresh(post)
    return post


@app.get("/api/public-data/summary")
def public_data_summary():
    return get_summary()


@app.get("/api/public-data/search")
def public_data_search(
    keyword: str = Query(min_length=1, max_length=100),
    limit: int = Query(default=20, ge=1, le=100),
):
    return {
        "keyword": keyword,
        "items": search_public_data(keyword, limit),
    }


@app.get("/api/public-data/files/{relative_path:path}")
def public_data_file_preview(
    relative_path: str,
    limit: int = Query(default=30, ge=1, le=100),
):
    try:
        return preview_file(relative_path, limit)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="데이터 파일을 찾을 수 없습니다.")
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    keyword = payload.message.strip()

    public_results = search_public_data(keyword, limit=5)

    community_posts = list(
        db.scalars(
            select(Post)
            .where(
                or_(
                    Post.title.ilike(f"%{keyword}%"),
                    Post.content.ilike(f"%{keyword}%"),
                    Post.category.ilike(f"%{keyword}%"),
                )
            )
            .order_by(Post.likes.desc(), Post.views.desc())
            .limit(3)
        ).all()
    )

    community_results = [
        {
            "id": post.id,
            "category": post.category,
            "title": post.title,
        }
        for post in community_posts
    ]

    sections = []

    if public_results:
        public_lines = "\n".join(
            f"- [{item['category']}] {item['title']}: {item['summary']}"
            for item in public_results[:3]
        )
        sections.append(f"부산 공공데이터 검색 결과\n{public_lines}")

    if community_results:
        community_lines = "\n".join(
            f"- [{item['category']}] {item['title']}"
            for item in community_results
        )
        sections.append(f"커뮤니티 게시글 검색 결과\n{community_lines}")

    if sections:
        answer = "\n\n".join(sections)
    else:
        answer = (
            f'"{keyword}"와 관련된 부산 공공데이터 또는 게시글을 찾지 못했습니다. '
            "데이터에 실제로 포함된 장소명·지역명·축제명으로 다시 질문해 보세요."
        )

    return ChatResponse(
        answer=answer,
        public_data_results=public_results,
        community_results=community_results,
    )
