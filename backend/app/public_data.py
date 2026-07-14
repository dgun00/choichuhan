from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

BACKEND_ROOT = Path(__file__).resolve().parent.parent
configured_path = os.getenv("BUSAN_DATA_DIR", "./data/busan")
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


def _compact_summary(record: dict[str, Any], max_length: int = 180) -> str:
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

    return text[:max_length] + ("…" if len(text) > max_length else "")


def infer_category(filename: str) -> str:
    stem = Path(filename).stem

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
    normalized_keyword = keyword.strip().lower()
    if not normalized_keyword:
        return []

    results: list[dict[str, Any]] = []

    for path in list_json_files():
        try:
            records = extract_records(load_file(path))
        except Exception:
            continue

        for record in records:
            searchable = " ".join(_flatten_scalars(record).values()).lower()
            if normalized_keyword not in searchable:
                continue

            title = _pick_value(record, TITLE_KEYS)
            if not title:
                title = f"{infer_category(path.name)} 정보"

            results.append(
                {
                    "source_file": path.name,
                    "category": infer_category(path.name),
                    "title": title[:120],
                    "summary": _compact_summary(record),
                }
            )

            if len(results) >= limit:
                return results

    return results


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
