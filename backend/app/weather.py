from __future__ import annotations

import json
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request

KST_TIMEZONE = "Asia/Seoul"

REGION_COORDS: tuple[dict[str, Any], ...] = (
    {"id": "haeundae", "name": "해운대·광안리", "label": "해운대·광안리", "lat": 35.1587, "lon": 129.1604},
    {"id": "jungnampo", "name": "중구·남포동", "label": "중구·남포동", "lat": 35.1033, "lon": 129.0403},
    {"id": "yeongdo", "name": "영도", "label": "영도", "lat": 35.0730, "lon": 129.0650},
    {"id": "dongnae", "name": "동래·온천장", "label": "동래·온천장", "lat": 35.2050, "lon": 129.0771},
    {"id": "seomyeon", "name": "서면", "label": "서면", "lat": 35.1578, "lon": 129.0595},
    {"id": "gijang", "name": "기장", "label": "기장", "lat": 35.2445, "lon": 129.2136},
    {"id": "saha", "name": "사하·감천", "label": "사하·감천", "lat": 35.0964, "lon": 128.9709},
)

WEATHER_CODE_LABELS = {
    0: "맑음",
    1: "대체로 맑음",
    2: "부분적으로 흐림",
    3: "흐림",
    45: "안개",
    48: "진한 안개",
    51: "가벼운 비",
    53: "보통 비",
    55: "강한 비",
    61: "가벼운 비",
    63: "보통 비",
    65: "강한 비",
    71: "가벼운 눈",
    73: "보통 눈",
    75: "강한 눈",
    80: "소나기",
    81: "강한 소나기",
    82: "심한 소나기",
    95: "천둥번개",
    96: "천둥번개와 우박",
    99: "천둥번개와 우박",
}


def _weather_label(code: int | None) -> str:
    if code is None:
        return "정보 없음"
    return WEATHER_CODE_LABELS.get(code, f"코드 {code}")


def compute_travel_suitability(weather_data: dict[str, Any]) -> dict[str, Any]:
    temperature = float(weather_data.get("temperature", 0) or 0)
    precipitation = float(weather_data.get("precipitation", 0) or 0)
    windspeed = float(weather_data.get("windspeed", 0) or 0)
    weather_code = int(weather_data.get("weathercode", 0) or 0)

    score = 100
    reasons: list[str] = []

    if precipitation > 2:
        score -= 16 + min(precipitation * 4, 16)
        reasons.append("강수 확률이 높아요")
    elif precipitation > 0.5:
        score -= 6
        reasons.append("가벼운 비가 예상돼요")

    if windspeed > 12:
        score -= 10
        reasons.append("바람이 강하게 불어요")
    elif windspeed > 8:
        score -= 5

    if temperature > 31:
        score -= 8
        reasons.append("더위가 강해요")
    elif temperature < 12:
        score -= 6
        reasons.append("날씨가 쌀쌀해요")

    if weather_code in {45, 48, 95, 96, 99}:
        score -= 16
        reasons.append("기상 상태가 불안정해요")
    elif weather_code in {61, 63, 65, 80, 81, 82}:
        score -= 8
        reasons.append("비나 소나기가 이어질 수 있어요")

    score = max(0, min(100, round(score)))

    if score >= 80:
        level = "좋음"
        summary = "야외 이동이 편한 날씨예요"
    elif score >= 65:
        level = "보통"
        summary = "외출은 괜찮지만 소지품 체크가 필요해요"
    elif score >= 35:
        level = "주의"
        summary = "우산과 바람 대비를 챙기면 좋아요"
    else:
        level = "나쁨"
        summary = "실내 위주 일정이 더 안전해요"

    return {
        "score": score,
        "level": level,
        "summary": summary,
        "reasons": reasons,
    }


def _fetch_current_weather(lat: float, lon: float) -> dict[str, Any]:
    endpoint = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,precipitation,windspeed_10m,weather_code"
        f"&timezone={KST_TIMEZONE}"
    )

    request = urllib_request.Request(endpoint, headers={"User-Agent": "LocalHub/1.0"})
    try:
        with urllib_request.urlopen(request, timeout=12) as response:
            payload = json.load(response)
    except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return {}

    current = payload.get("current") or {}
    weather_code = current.get("weather_code")
    temperature = current.get("temperature_2m")
    precipitation = current.get("precipitation")
    windspeed = current.get("windspeed_10m")
    humidity = current.get("relative_humidity_2m")

    return {
        "temperature": temperature,
        "humidity": humidity,
        "precipitation": precipitation,
        "windspeed": windspeed,
        "weathercode": weather_code,
        "weatherlabel": _weather_label(weather_code),
    }


def get_weather_regions() -> list[dict[str, Any]]:
    regions: list[dict[str, Any]] = []
    for region in REGION_COORDS:
        weather_data = _fetch_current_weather(region["lat"], region["lon"])
        if not weather_data:
            weather_data = {
                "temperature": 24,
                "humidity": 55,
                "precipitation": 0,
                "windspeed": 4,
                "weathercode": 1,
                "weatherlabel": "맑음",
            }

        suitability = compute_travel_suitability(weather_data)
        regions.append(
            {
                "id": region["id"],
                "name": region["name"],
                "lat": region["lat"],
                "lon": region["lon"],
                "current_weather": {
                    **weather_data,
                    "temperature": round(float(weather_data.get("temperature", 0) or 0), 1),
                    "humidity": round(float(weather_data.get("humidity", 0) or 0), 1),
                    "precipitation": round(float(weather_data.get("precipitation", 0) or 0), 1),
                    "windspeed": round(float(weather_data.get("windspeed", 0) or 0), 1),
                },
                "travel_suitability": suitability,
            }
        )

    return regions
