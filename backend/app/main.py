from __future__ import annotations

import json
import math
import os
from contextlib import asynccontextmanager
from urllib import error as urllib_error
from urllib import request as urllib_request

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
    SessionLocal,
)
from .models import Comment, Post
from .public_data import (
    get_summary,
    preview_file,
    search_public_data,
    today_kst,
)
from .schemas import (
    ChatRequest,
    ChatResponse,
    CommentCreate,
    CommentResponse,
    PasswordRequest,
    PostCreate,
    PostResponse,
    PostUpdate,
)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
OPENAI_API_URL = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions").strip()


DEFAULT_POSTS = [
    {
        "category": "맛집",
        "title": "부산 광안리 국밥 찐맛집 추천합니다",
        "content": "공공데이터에 등록된 ㅇㅇ국밥 가봤는데 국물이 진짜 진하고 고기 양이 엄청나네요. 주차장도 넓어서 광안리 드라이브 가실 때 강추합니다!",
        "password": "1234",
        "views": 42,
        "likes": 15,
    },
    {
        "category": "축제·행사",
        "title": "이번 주말 광안리 어방축제 일정 공유",
        "content": "공공데이터 축제 캘린더 보니까 이번 주 토요일 저녁에 드론쇼랑 불꽃놀이 같이 한다고 합니다. 꿀팁 자리 공유해요!",
        "password": "1234",
        "views": 88,
        "likes": 32,
    },
    {
        "category": "관광지",
        "title": "해운대 블루라인파크 캡슐 열차 예약 팁",
        "content": "현장 예매는 주말에 절대 불가입니다. 최소 2주 전에 공식 홈페이지 열릴 때 바로 잡으셔야 노을 지는 시간대 탑승 가능해요.",
        "password": "1111",
        "views": 65,
        "likes": 19,
    },
    {
        "category": "자유",
        "title": "영도 카페거리 주차하기 편한 곳 어디인가요?",
        "content": "초보 운전인데 영도 오르막길이 좀 무서워서요. 평지 쪽에 주차장 넓은 대형 카페 추천 부탁드립니다~",
        "password": "0000",
        "views": 24,
        "likes": 4,
    },
    {
        "category": "맛집",
        "title": "남포동 이재모피자 웨이팅 실시간 상황",
        "content": "화요일 오후 2시 기준 웨이팅 40팀 있습니다. 포장 주문은 키오스크로 바로 가능하니 참고하세요!",
        "password": "1234",
        "views": 112,
        "likes": 28,
    },
    {
        "category": "관광지",
        "title": "송도 해상케이블카 바닥 투명한 크리스탈 후기",
        "content": "바닥이 아예 유리로 뚫려 있어서 바다 내려다보는 맛이 있습니다. 고소공포증 있으시면 일반 캐빈 타세요ㅎㅎ",
        "password": "1234",
        "views": 53,
        "likes": 11,
    },
    {
        "category": "자유",
        "title": "LocalHub 부산 커뮤니티 오픈 축하합니다 🥳",
        "content": "로그인 없이 바로 글 쓸 수 있어서 너무 편하네요! 앞으로 좋은 지역 정보 많이 나누었으면 좋겠습니다.",
        "password": "1234",
        "views": 95,
        "likes": 45,
    },
]


def seed_default_posts() -> None:
    with SessionLocal() as db:
        post_count = db.scalar(select(func.count()).select_from(Post)) or 0
        if post_count > 0:
            return

        for post_data in DEFAULT_POSTS:
            db.add(Post(**post_data))

        db.commit()


def _format_public_context(items: list[dict[str, object]]) -> str:
    if not items:
        return ""

    lines = []
    for index, item in enumerate(items, start=1):
        lines.append(
            f"[{index}] {item.get('category', '')} | {item.get('title', '')} | {item.get('summary', '')}"
        )
    return "\n\n".join(lines)


_WEEKDAY_KO = ("월", "화", "수", "목", "금", "토", "일")


def _today_str() -> str:
    today = today_kst()
    return f"{today.year}년 {today.month}월 {today.day}일 ({_WEEKDAY_KO[today.weekday()]}요일)"


def _build_retrieval_prompt(keyword: str, public_results: list[dict[str, object]]) -> list[dict[str, str]]:
    context = _format_public_context(public_results)
    today_str = _today_str()
    return [
        {
            "role": "system",
            "content": (
                "너는 LocalHub의 부산 권역 정보 챗봇이다. "
                "아래 제공된 부산 공공데이터 문맥을 우선 근거로 삼아 한국어로 친절하고 자연스럽게 답한다. "
                "말투는 친절하고 간결하게 유지하고, 실제 상담하듯 한두 문장으로 먼저 핵심을 말한다. "
                "문맥에 있는 장소·시설 이름, 주소 같은 정보는 적극적으로 활용해서 최대한 도움이 되게 답한다. "
                "사용자 메시지에는 오늘 날짜가 함께 주어진다. "
                "축제·행사 항목의 문맥에 '기간 YYYY.MM.DD~YYYY.MM.DD' 또는 '기간 YYYY.MM.DD'처럼 날짜가 나와 있으면, "
                "그 날짜를 오늘 날짜와 직접 비교해서 질문에 나온 시점(이번 주말·이번달·오늘·내일 등)에 실제로 해당하는지 정확하게 판단해서 답한다. "
                "해당하지 않으면 '그 기간은 아니고, ~에 열린다'처럼 사실대로 알려준다. "
                "축제·행사인데도 기간 정보가 안 나와 있거나, 관광지·숙박처럼 애초에 날짜 개념이 없는 카테고리의 경우에만 "
                "'이 항목은 날짜 정보가 없어서 확인해 드릴 수 없어요'라고 그 부분만 솔직히 밝히고, "
                "답변 전체를 거부하지 말고 아는 선에서는 계속 답한다. "
                "문맥에 요금처럼 구체적인 세부사항이 없으면 그 부분만 모른다고 솔직히 밝힌다. "
                "문맥에 질문과 관련된 내용이 정말 하나도 없을 때만 '관련 정보를 찾지 못했습니다'라고 말하고, "
                "대신 어떤 종류의 질문(관광지·맛집·축제 등)이면 도움을 줄 수 있는지 짧게 안내한다. "
                "문맥에 없는 사실을 지어내거나 과장하지는 않는다. "
                "목록을 나열해야 할 때만 짧은 불릿을 사용하고, 그 외에는 대화하듯 답한다."
            ),
        },
        {
            "role": "user",
            "content": (
                f"오늘 날짜: {today_str}\n\n"
                f"사용자 질문: {keyword}\n\n"
                f"참고할 문맥:\n{context}\n\n"
                "위 문맥을 우선 활용해서, 사용자가 바로 이해할 수 있게 답변해 주세요. "
                "가능하면 장소의 특징, 위치, 분위기, 방문 팁처럼 실제 도움이 되는 표현으로 자연스럽게 설명하세요."
            ),
        },
    ]


def _call_openai_chat(messages: list[dict[str, str]]) -> str:
    if not OPENAI_API_KEY:
        return ""

    payload = json.dumps(
        {
            "model": OPENAI_MODEL,
            "messages": messages,
        }
    ).encode("utf-8")

    request = urllib_request.Request(
        OPENAI_API_URL,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib_request.urlopen(request, timeout=20) as response:
            response_data = json.load(response)
    except urllib_error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        print(f"[OpenAI API error] status={error.code} body={body[:500]}")
        return ""
    except (urllib_error.URLError, TimeoutError, ValueError) as error:
        print(f"[OpenAI API error] {type(error).__name__}: {error}")
        return ""

    choices = response_data.get("choices") or []
    if not choices:
        return ""

    message = choices[0].get("message") or {}
    content = message.get("content") or ""
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if text:
                    parts.append(str(text))
        return "\n".join(parts).strip()

    return str(content).strip()


def _prefix_chat_answer(answer: str, is_ai_answer: bool) -> str:
    prefix = "[AI응답]" if is_ai_answer else "[더미응답]"
    return f"{prefix} {answer}" if answer else prefix


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    apply_sqlite_compatibility_migrations()
    seed_default_posts()
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
        "http://127.0.0.1:5173,http://localhost:5173,null",
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


@app.get("/api/posts/{post_id}/comments", response_model=list[CommentResponse])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    return list(
        db.scalars(
            select(Comment).where(Comment.post_id == post_id).order_by(Comment.id.asc())
        ).all()
    )


@app.post("/api/posts/{post_id}/comments", response_model=CommentResponse, status_code=201)
def create_comment(post_id: int, payload: CommentCreate, db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    comment = Comment(post_id=post_id, content=payload.content, password=payload.password)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@app.delete("/api/posts/{post_id}/comments/{comment_id}", status_code=204)
def delete_comment(
    post_id: int,
    comment_id: int,
    payload: PasswordRequest = Body(...),
    db: Session = Depends(get_db),
):
    comment = db.get(Comment, comment_id)
    if comment is None or comment.post_id != post_id:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")

    if comment.password != payload.password:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")

    db.delete(comment)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
    if not public_results:
        answer = _prefix_chat_answer(
            f'"{keyword}"와 관련된 부산 공공데이터를 찾지 못했습니다. '
            "데이터에 실제로 포함된 장소명·지역명·축제명으로 다시 질문해 보세요.",
            False,
        )
    else:
        messages = _build_retrieval_prompt(keyword, public_results[:5])
        llm_answer = _call_openai_chat(messages)

        if llm_answer:
            answer = _prefix_chat_answer(llm_answer, True)
        else:
            public_lines = "\n".join(
                f"- [{item['category']}] {item['title']}: {item['summary']}"
                for item in public_results[:3]
            )
            answer = _prefix_chat_answer(f"부산 공공데이터 검색 결과\n{public_lines}", False)

    return ChatResponse(
        answer=answer,
        public_data_results=public_results,
        community_results=[],
    )
