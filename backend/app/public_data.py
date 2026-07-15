from __future__ import annotations

import json
import os
import re
import unicodedata
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

BACKEND_ROOT = Path(__file__).resolve().parent.parent
configured_path = os.getenv("BUSAN_DATA_DIR", "../docs")
BUSAN_DATA_DIR = (
    Path(configured_path)
    if Path(configured_path).is_absolute()
    else (BACKEND_ROOT / configured_path).resolve()
)

TITLE_KEYS = (
    "title", "name", "facilityName", "placeName",
    "제목", "명칭", "이름", "관광지명", "축제명", "행사명",
    "업소명", "시설명", "상호명", "콘텐츠명", "코스명",
)
SUMMARY_KEYS = (
    "overview", "description", "content", "summary",
    "개요", "설명", "내용", "소개", "상세내용", "특징",
)
ADDRESS_KEYS = (
    "address", "addr1", "addr", "roadAddress",
    "주소", "소재지", "도로명주소", "지번주소",
)

SEARCH_STOPWORDS = {
    "그리고", "그러면", "그럼", "그거", "그것", "그곳", "그쪽", "근처",
    "부산", "부산에", "부산에서", "부산의", "이번", "이번달", "이번달에",
    "이번주", "이번주에", "이번주말", "이번주말에", "이번에", "오늘", "내일",
    "어떤", "어떤거", "어떤거해", "어디", "어디야", "어디서", "뭐", "뭐야",
    "뭐해", "뭐가", "있나", "있어", "있는", "알려줘", "알려줘요", "추천",
    "추천해", "추천해줘", "추천해줘요", "알려", "해줘", "해주세요", "주세요",
    "찾아줘", "찾아", "가볼", "갈만한", "좀", "좀요", "정보", "후기", "싶어",
}

KST = timezone(timedelta(hours=9))


def today_kst() -> date:
    return datetime.now(KST).date()


BUSAN_DISTRICTS: tuple[str, ...] = (
    "강서구", "금정구", "기장군", "남구", "동구", "동래구", "부산진구",
    "북구", "사상구", "사하구", "서구", "수영구", "연제구", "영도구",
    "중구", "해운대구",
)

QUERY_CATEGORY_HINTS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("축제", "행사", "공연", "페스티벌"), "축제·행사"),
    (("관광", "여행", "명소", "가볼", "가볼만한", "갈만한", "추천", "둘러", "산책", "구경"), "관광지"),
    (("맛집", "음식", "식당", "밥집", "먹", "카페", "디저트"), "맛집"),
    (("숙박", "호텔", "모텔", "펜션", "게스트하우스"), "숙박"),
    (("쇼핑", "아울렛", "몰", "백화점", "시장"), "쇼핑"),
    (("레포츠", "운동", "체험", "액티비티", "서핑", "요트"), "레포츠"),
    (("문화", "전시", "미술관", "박물관", "도서관"), "문화시설"),
    (("코스", "일정", "동선", "여행코스"), "여행코스"),
)


def _read_json(path: Path) -> Any:
    last_error: Exception | None = None

    for encoding in ("utf-8-sig", "utf-8", "cp949"):
        try:
            with path.open("r", encoding=encoding) as file:
                return json.load(file)
        except UnicodeDecodeError as error:
            last_error = error
        except json.JSONDecodeError:
            raise

    if last_error:
        raise last_error
    raise ValueError(f"파일을 읽을 수 없습니다: {path.name}")


def _find_record_lists(value: Any) -> list[list[dict[str, Any]]]:
    candidates: list[list[dict[str, Any]]] = []

    if isinstance(value, list):
        dict_items = [item for item in value if isinstance(item, dict)]
        if dict_items:
            candidates.append(dict_items)

        for item in value:
            candidates.extend(_find_record_lists(item))

    elif isinstance(value, dict):
        for child in value.values():
            candidates.extend(_find_record_lists(child))

    return candidates


def extract_records(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list) and all(isinstance(item, dict) for item in value):
        return value

    candidates = _find_record_lists(value)
    if candidates:
        return max(candidates, key=len)

    if isinstance(value, dict):
        return [value]

    return []


def _flatten_scalars(
    value: Any,
    prefix: str = "",
    output: dict[str, str] | None = None,
) -> dict[str, str]:
    if output is None:
        output = {}

    if isinstance(value, dict):
        for key, child in value.items():
            child_key = f"{prefix}.{key}" if prefix else str(key)
            _flatten_scalars(child, child_key, output)
    elif isinstance(value, list):
        for index, child in enumerate(value[:10]):
            child_key = f"{prefix}[{index}]"
            _flatten_scalars(child, child_key, output)
    elif value is not None:
        output[prefix] = str(value)

    return output


def _pick_value(record: dict[str, Any], keys: tuple[str, ...]) -> str:
    flattened = _flatten_scalars(record)

    # 정확한 키를 우선합니다.
    for wanted in keys:
        for key, value in flattened.items():
            leaf = key.split(".")[-1]
            if leaf == wanted and value.strip():
                return value.strip()

    # 부분 일치도 허용합니다.
    for wanted in keys:
        wanted_lower = wanted.lower()
        for key, value in flattened.items():
            leaf = key.split(".")[-1].lower()
            if wanted_lower in leaf and value.strip():
                return value.strip()

    return ""


def _normalize_text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).lower().split())


def _extract_query_terms(keyword: str) -> list[str]:
    normalized_keyword = _normalize_text(keyword)
    raw_terms = re.findall(r"[0-9A-Za-z가-힣]+", normalized_keyword)
    terms = []

    for term in raw_terms:
        if len(term) < 2:
            continue
        if term in SEARCH_STOPWORDS:
            continue
        terms.append(term)

    return terms


def _infer_query_category(keyword: str) -> str | None:
    normalized_keyword = _normalize_text(keyword)
    for keywords, category in QUERY_CATEGORY_HINTS:
        if any(token in normalized_keyword for token in keywords):
            return category
    return None


def _extract_query_districts(keyword: str) -> list[str]:
    normalized_keyword = _normalize_text(keyword)
    return [district for district in BUSAN_DISTRICTS if district in normalized_keyword]


_WEEKDAY_KEYWORDS: tuple[tuple[str, int], ...] = (
    ("월요일", 0), ("화요일", 1), ("수요일", 2), ("목요일", 3),
    ("금요일", 4), ("토요일", 5), ("일요일", 6),
)

_SEASON_RANGES: tuple[tuple[str, int, int], ...] = (
    ("봄", 3, 5),
    ("여름", 6, 8),
    ("가을", 9, 11),
    ("겨울", 12, 2),
)

_MONTH_DAY_RE = re.compile(r"(\d{1,2})\s*월\s*(\d{1,2})\s*일")
_MONTH_ONLY_RE = re.compile(r"(\d{1,2})\s*월(?!요일)")


def _month_range(year: int, month: int) -> tuple[date, date]:
    start = date(year, month, 1)
    end = (
        date(year + 1, 1, 1) - timedelta(days=1)
        if month == 12
        else date(year, month + 1, 1) - timedelta(days=1)
    )
    return (start, end)


def _extract_query_date_range(keyword: str) -> tuple[date, date] | None:
    normalized = _normalize_text(keyword)
    compact = normalized.replace(" ", "")
    today = today_kst()

    # 1) "8월 1일"처럼 구체적인 날짜
    day_match = _MONTH_DAY_RE.search(normalized)
    if day_match:
        month, day = int(day_match.group(1)), int(day_match.group(2))
        if 1 <= month <= 12 and 1 <= day <= 31:
            try:
                target = date(today.year, month, day)
            except ValueError:
                target = None
            if target:
                return (target, target)

    # 2) 특정 요일 ("이번주 토요일", "다음주 금요일", 그냥 "토요일" 등)
    for name, idx in _WEEKDAY_KEYWORDS:
        if name not in compact:
            continue
        if "다음주" in compact:
            base_monday = today - timedelta(days=today.weekday()) + timedelta(days=7)
            target = base_monday + timedelta(days=idx)
        else:
            days_ahead = (idx - today.weekday()) % 7
            target = today + timedelta(days=days_ahead)
        return (target, target)

    # 3) 오늘 기준 하루 단위 상대 표현
    if "글피" in compact:
        target = today + timedelta(days=3)
        return (target, target)
    if "모레" in compact:
        target = today + timedelta(days=2)
        return (target, target)
    if "어제" in compact:
        target = today - timedelta(days=1)
        return (target, target)
    if "내일" in compact:
        target = today + timedelta(days=1)
        return (target, target)
    if "오늘" in compact:
        return (today, today)

    # 4) 주/주말 단위
    if "다음주말" in compact:
        saturday = today + timedelta(days=(5 - today.weekday()) % 7 + 7)
        return (saturday, saturday + timedelta(days=1))
    if "주말" in compact:
        saturday = today + timedelta(days=(5 - today.weekday()) % 7)
        return (saturday, saturday + timedelta(days=1))
    if "다음주" in compact:
        this_monday = today - timedelta(days=today.weekday())
        next_monday = this_monday + timedelta(days=7)
        return (next_monday, next_monday + timedelta(days=6))
    if "저번주" in compact or "지난주" in compact:
        this_monday = today - timedelta(days=today.weekday())
        last_monday = this_monday - timedelta(days=7)
        return (last_monday, last_monday + timedelta(days=6))
    if "이번주" in compact:
        monday = today - timedelta(days=today.weekday())
        return (monday, monday + timedelta(days=6))

    # 5) "8월"처럼 특정 달만 지정 (요일·일자 표현은 위에서 먼저 처리됨)
    month_match = _MONTH_ONLY_RE.search(normalized)
    if month_match:
        month = int(month_match.group(1))
        if 1 <= month <= 12:
            return _month_range(today.year, month)

    # 6) 이번달/다음달/저번달
    if "다음달" in compact:
        next_month = (
            today.replace(year=today.year + 1, month=1, day=1)
            if today.month == 12
            else today.replace(month=today.month + 1, day=1)
        )
        return _month_range(next_month.year, next_month.month)
    if "저번달" in compact or "지난달" in compact:
        prev_month = (
            today.replace(year=today.year - 1, month=12, day=1)
            if today.month == 1
            else today.replace(month=today.month - 1, day=1)
        )
        return _month_range(prev_month.year, prev_month.month)
    if "이번달" in compact:
        return _month_range(today.year, today.month)

    # 7) 계절
    for season, start_month, end_month in _SEASON_RANGES:
        if season not in compact:
            continue
        start = date(today.year, start_month, 1)
        if start_month <= end_month:
            _, end = _month_range(today.year, end_month)
        else:
            _, end = _month_range(today.year + 1, end_month)
        return (start, end)

    # 8) 연 단위
    if "내년" in compact:
        return (date(today.year + 1, 1, 1), date(today.year + 1, 12, 31))
    if "작년" in compact or "지난해" in compact:
        return (date(today.year - 1, 1, 1), date(today.year - 1, 12, 31))
    if "올해" in compact or "금년" in compact:
        return (date(today.year, 1, 1), date(today.year, 12, 31))

    return None


def _parse_event_date(value: Any) -> date | None:
    if not isinstance(value, str) or len(value) != 8 or not value.isdigit():
        return None
    try:
        return date(int(value[:4]), int(value[4:6]), int(value[6:8]))
    except ValueError:
        return None


def _format_event_period(record: dict[str, Any]) -> str:
    start = _parse_event_date(record.get("eventstartdate"))
    end = _parse_event_date(record.get("eventenddate")) or start

    if not start:
        return ""
    if end and end != start:
        return f"기간 {start.strftime('%Y.%m.%d')}~{end.strftime('%Y.%m.%d')}"
    return f"기간 {start.strftime('%Y.%m.%d')}"


def _record_searchable_text(record: dict[str, Any]) -> str:
    flattened_values = [
        value.strip()
        for value in _flatten_scalars(record).values()
        if value.strip()
    ]
    return _normalize_text(" ".join(flattened_values))


def _record_score(
    record: dict[str, Any],
    path: Path,
    query_terms: list[str],
    query_category: str | None,
    query_districts: list[str] | None = None,
    query_date_range: tuple[date, date] | None = None,
) -> float:
    searchable = _record_searchable_text(record)
    title = _normalize_text(_pick_value(record, TITLE_KEYS))
    summary = _normalize_text(_compact_summary(record))
    address = _normalize_text(_pick_value(record, ADDRESS_KEYS))
    file_category = infer_category(path.name)

    score = 0.0

    if query_category and file_category == query_category:
        score += 6.0

    if query_category and query_category in searchable:
        score += 3.0

    if query_districts:
        if any(district in address for district in query_districts):
            score += 5.0
        elif any(district in searchable for district in query_districts):
            score += 3.0

    if query_date_range:
        event_start = _parse_event_date(record.get("eventstartdate"))
        event_end = _parse_event_date(record.get("eventenddate")) or event_start
        if event_start and event_end:
            query_start, query_end = query_date_range
            if event_start <= query_end and event_end >= query_start:
                score += 8.0

    for term in query_terms:
        if term in title:
            score += 4.0
        if term in summary:
            score += 2.5
        if term in searchable:
            score += 1.5

    if query_terms:
        exact_query = _normalize_text(" ".join(query_terms))
        if exact_query and exact_query in searchable:
            score += 3.0

    return score


def _compact_summary(record: dict[str, Any], max_length: int = 220) -> str:
    summary = _pick_value(record, SUMMARY_KEYS)
    address = _pick_value(record, ADDRESS_KEYS)

    if summary and address:
        text = f"{summary} · {address}"
    elif summary:
        text = summary
    elif address:
        text = address
    else:
        values = [
            value.strip()
            for value in _flatten_scalars(record).values()
            if value.strip()
        ]
        text = " · ".join(values[:5])

    # 축제공연행사(contentTypeId=15) 전용 일정 필드가 있으면 기간·장소·요금을 요약 앞에 붙입니다.
    event_bits = []
    period = _format_event_period(record)
    if period:
        event_bits.append(period)

    event_place = str(record.get("eventplace") or "").strip()
    if event_place:
        event_bits.append(f"장소 {event_place}")

    fee = str(record.get("usetimefestival") or "").strip()
    if fee:
        event_bits.append(f"요금 {fee}")

    if event_bits:
        text = " · ".join(event_bits) + " · " + text

    text = " ".join(text.split())
    return text[:max_length] + ("…" if len(text) > max_length else "")


def infer_category(filename: str) -> str:
    stem = unicodedata.normalize("NFC", Path(filename).stem)

    mappings = (
        ("축제", "축제·행사"),
        ("행사", "축제·행사"),
        ("공연", "축제·행사"),
        ("음식", "맛집"),
        ("맛집", "맛집"),
        ("모범", "맛집"),
        ("관광", "관광지"),
        ("명소", "관광지"),
        ("문화", "문화시설"),
        ("숙박", "숙박"),
        ("쇼핑", "쇼핑"),
        ("레포츠", "레포츠"),
        ("코스", "여행코스"),
    )

    for keyword, category in mappings:
        if keyword in stem:
            return category

    return stem


@lru_cache(maxsize=128)
def _load_cached(path_text: str, modified_time: float) -> Any:
    del modified_time
    return _read_json(Path(path_text))


def load_file(path: Path) -> Any:
    stat = path.stat()
    return _load_cached(str(path.resolve()), stat.st_mtime)


def list_json_files() -> list[Path]:
    if not BUSAN_DATA_DIR.exists():
        return []

    return sorted(
        path
        for path in BUSAN_DATA_DIR.rglob("*.json")
        if path.is_file()
    )


def get_summary() -> dict[str, Any]:
    files = []
    errors = []
    total_records = 0

    for path in list_json_files():
        try:
            records = extract_records(load_file(path))
            count = len(records)
            total_records += count
            files.append(
                {
                    "filename": path.name,
                    "relative_path": str(path.relative_to(BUSAN_DATA_DIR)),
                    "category": infer_category(path.name),
                    "record_count": count,
                }
            )
        except Exception as error:
            errors.append(
                {
                    "filename": path.name,
                    "error": str(error),
                }
            )

    return {
        "region": "부산",
        "directory": str(BUSAN_DATA_DIR),
        "file_count": len(files),
        "total_records": total_records,
        "files": files,
        "errors": errors,
    }


def search_public_data(keyword: str, limit: int = 20) -> list[dict[str, Any]]:
    normalized_keyword = _normalize_text(keyword)
    if not normalized_keyword:
        return []

    query_terms = _extract_query_terms(keyword)
    query_category = _infer_query_category(keyword)
    query_districts = _extract_query_districts(keyword)
    query_date_range = _extract_query_date_range(keyword)

    scored_results: list[tuple[float, dict[str, Any]]] = []

    for path in list_json_files():
        try:
            records = extract_records(load_file(path))
        except Exception:
            continue

        for record in records:
            score = _record_score(
                record, path, query_terms, query_category, query_districts, query_date_range
            )

            if score <= 0 and query_category is None:
                continue

            if score <= 0 and query_category is not None:
                continue

            if score <= 0:
                continue

            title = _pick_value(record, TITLE_KEYS)
            if not title:
                title = f"{infer_category(path.name)} 정보"
            title = " ".join(title.split())

            scored_results.append(
                (
                    score,
                    {
                        "source_file": path.name,
                        "category": infer_category(path.name),
                        "title": title[:120],
                        "summary": _compact_summary(record),
                    },
                )
            )

    scored_results.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in scored_results[:limit]]


def preview_file(relative_path: str, limit: int = 30) -> dict[str, Any]:
    safe_relative = Path(relative_path)
    full_path = (BUSAN_DATA_DIR / safe_relative).resolve()

    if BUSAN_DATA_DIR not in full_path.parents:
        raise ValueError("허용되지 않은 파일 경로입니다.")

    if full_path.suffix.lower() != ".json" or not full_path.exists():
        raise FileNotFoundError(relative_path)

    records = extract_records(load_file(full_path))
    return {
        "filename": full_path.name,
        "category": infer_category(full_path.name),
        "total": len(records),
        "items": records[:limit],
    }


_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html_tags(value: str) -> str:
    return _HTML_TAG_RE.sub("", value).strip()


def get_festival_events() -> list[dict[str, Any]]:
    """FullCalendar에 바로 넣을 수 있는 형태로 축제·행사 일정을 반환합니다."""
    events: list[dict[str, Any]] = []

    for path in list_json_files():
        if infer_category(path.name) != "축제·행사":
            continue

        try:
            records = extract_records(load_file(path))
        except Exception:
            continue

        for record in records:
            start = _parse_event_date(record.get("eventstartdate"))
            if not start:
                continue

            end = _parse_event_date(record.get("eventenddate")) or start

            def _field(key: str) -> str:
                return str(record.get(key) or "").strip()

            title = _pick_value(record, TITLE_KEYS) or "축제·행사"
            title = " ".join(title.split())[:120]
            address = _pick_value(record, ADDRESS_KEYS)
            place = _field("eventplace") or address

            events.append(
                {
                    "id": str(record.get("contentid") or f"{path.stem}-{len(events)}"),
                    "title": title,
                    # FullCalendar의 종일 이벤트 end는 배타적(exclusive)이라 하루를 더해줍니다.
                    "start": start.isoformat(),
                    "end": (end + timedelta(days=1)).isoformat(),
                    # 상세 모달 표시용 (exclusive 보정 없는 실제 날짜)
                    "date_start": start.isoformat(),
                    "date_end": end.isoformat(),
                    "place": place,
                    "address": address,
                    "fee": _field("usetimefestival"),
                    "playtime": _field("playtime"),
                    "image": _field("firstimage"),
                    "tel": _field("tel"),
                    "program": _field("program"),
                    "subevent": _field("subevent"),
                    "sponsor1": _field("sponsor1"),
                    "sponsor1tel": _field("sponsor1tel"),
                    "sponsor2": _field("sponsor2"),
                    "sponsor2tel": _field("sponsor2tel"),
                    "eventhomepage": _strip_html_tags(_field("eventhomepage")),
                    "bookingplace": _field("bookingplace"),
                    "agelimit": _field("agelimit"),
                    "festivalgrade": _field("festivalgrade"),
                    "placeinfo": _field("placeinfo"),
                    "spendtimefestival": _field("spendtimefestival"),
                    "discountinfofestival": _field("discountinfofestival"),
                }
            )

    events.sort(key=lambda event: event["start"])
    return events
