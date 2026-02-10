# -*- coding: utf-8 -*-
'''new Env('DNF房间PENDING通知');'''

import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
except Exception as e:
    print(str(e) + "\n缺少requests模块, 请执行命令：pip3 install requests\n")
    sys.exit(1)

os.environ["no_proxy"] = "*"
requests.packages.urllib3.disable_warnings()

try:
    from notify import send
except Exception:
    def send(title: str, content: str) -> None:
        print(title)
        print(content)


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


API_URL = "https://dnfm.chelvguanjia.cn/game/room/roomCenterList"

ENV_ENABLE = "DNFM_7713_ENABLE"
ENV_COOKIE = "DNFM_7713_COOKIE"
ENV_OPEN_ID = "DNFM_7713_OPEN_ID"
ENV_UNION_ID = "DNFM_7713_UNION_ID"
ENV_APP_ID = "DNFM_7713_APP_ID"

ENV_USER_ID = "DNFM_7713_USER_ID"
ENV_TUANBEN_ID = "DNFM_7713_TUANBEN_ID"
ENV_ROOM_TYPE = "DNFM_7713_ROOM_TYPE"
ENV_PLATFORM_TYPE = "DNFM_7713_PLATFORM_TYPE"
ENV_IS_ZIQIANG = "DNFM_7713_IS_ZIQIANG"


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
    "MicroMessenger/8.0.67(0x18004330) NetType/WIFI Language/zh_CN"
)
DEFAULT_REFERER = "https://servicewechat.com/wx15d3cf8a858e0bca/192/page-frame.html"


def _truncate_text(text: str, limit: int) -> str:
    if limit <= 0:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit] + f"...(truncated, total={len(text)})"



def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except Exception:
        logger.info(f"环境变量{name}不是整数，使用默认值: {default}")
        return default


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    if raw in {"1", "true", "t", "yes", "y", "on", "enable", "enabled"}:
        return True
    if raw in {"0", "false", "f", "no", "n", "off", "disable", "disabled"}:
        return False
    logger.info(f"环境变量{name}不是布尔值，使用默认值: {default}")
    return default


def _build_headers(cookie: str) -> Dict[str, str]:
    open_id = os.environ.get(ENV_OPEN_ID, "").strip()
    union_id = os.environ.get(ENV_UNION_ID, "").strip()
    app_id = os.environ.get(ENV_APP_ID, "").strip()

    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "User-Agent": DEFAULT_USER_AGENT,
        "Referer": DEFAULT_REFERER,
        "Cookie": cookie,
        "Connection": "keep-alive",
        "openId": open_id,
        "unionId": union_id,
        "appId": app_id,
    }

    return headers


def _build_payload() -> Dict[str, Any]:
    user_id = _env_int(ENV_USER_ID, 210955)
    tuanben_id = _env_int(ENV_TUANBEN_ID, 9)
    is_ziqiang = _env_int(ENV_IS_ZIQIANG, 1)
    room_type = os.environ.get(ENV_ROOM_TYPE, "TAILA").strip() or "TAILA"
    platform_type = os.environ.get(ENV_PLATFORM_TYPE, "QQ").strip() or "QQ"

    return {
        "pageNum": 1,
        "pageSize": 10,
        "tuanbenId": tuanben_id,
        "isZiQiang": is_ziqiang,
        "roomType": room_type,
        "platformType": platform_type,
        "userId": user_id,
    }


def _post_json(url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> Tuple[int, str]:
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    logger.info(f"请求URL: {url}")
    logger.info(f"请求头: {json.dumps(headers, ensure_ascii=False)}")
    logger.info(f"请求体: {body}")
    resp = requests.post(url, headers=headers, data=body, timeout=20, verify=False)
    logger.info(f"响应HTTP: {resp.status_code}")
    return resp.status_code, resp.text


def _parse_room_center_list(text: str) -> Tuple[Optional[List[Dict[str, Any]]], Optional[int], Optional[str]]:
    try:
        data = json.loads(text)
    except Exception as e:
        return None, None, f"响应不是合法JSON: {e}"

    code = data.get("code")
    message = data.get("message")
    if code != "000000":
        return None, None, f"接口返回异常: code={code}, message={message}"

    result = data.get("result") or {}
    pages = result.get("pages")
    records = result.get("records") or []
    if not isinstance(records, list):
        return None, None, "接口返回records类型异常"

    return records, pages if isinstance(pages, int) else None, None


def _format_room(room: Dict[str, Any]) -> str:
    room_id = room.get("id")
    status = room.get("status")
    room_status_desc = room.get("roomStatusDesc")
    match_desc = room.get("matchTypeDesc") or room.get("matchType")
    platform_desc = room.get("platformTypeDesc") or room.get("platformType")
    participant = room.get("participantCount")
    current_participant = room.get("currentPassengerCount")
    last_refresh = room.get("lastRefreshTime")
    return (
        f"id={room_id} status={status}({room_status_desc}) "
        f"{match_desc}/{platform_desc} 乘客={current_participant}/{participant} "
        f"refresh={last_refresh}"
    )


def fetch_all_rooms(cookie: str) -> List[Dict[str, Any]]:
    headers = _build_headers(cookie)
    payload = _build_payload()
    status_code, text = _post_json(API_URL, headers, payload)
    if status_code != 200:
        raise RuntimeError(f"HTTP状态码异常: {status_code}, body={text[:500]}")

    records, _, err = _parse_room_center_list(text)
    if err:
        raise RuntimeError(err)
    return records or []


def main() -> None:
    if not _env_bool(ENV_ENABLE, False):
        logger.info(f"{ENV_ENABLE}=false，脚本已跳过执行")
        return

    cookie = os.environ.get(ENV_COOKIE, "").strip()
    if not cookie:
        logger.info(f"未设置环境变量 {ENV_COOKIE}，请在青龙面板添加后再运行")
        sys.exit(1)

    try:
        rooms = fetch_all_rooms(cookie)
    except Exception as e:
        msg = f"请求房间列表失败: {e}"
        logger.info(msg)
        sys.exit(1)

    def _as_int(value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except Exception:
            return default

    pending_rooms = [
        r for r in rooms
        if str(r.get("status", "")).upper() == "PENDING"
        and _as_int(r.get("currentZiqiangCount")) < 9
        and _as_int(r.get("currentHscCount")) < 2
    ]
    if not pending_rooms:
        logger.info(f"未发现PENDING房间，共扫描{len(rooms)}条")
        return

    lines: List[str] = [f"发现pending房间，共{len(pending_rooms)}"]
    show_limit = 20
    for idx, room in enumerate(pending_rooms[:show_limit], start=1):
        hsc_count = _as_int(room.get("currentHscCount"))
        ziqiang_count = _as_int(room.get("currentZiqiangCount"))
        taila_rate = room.get("tailaRate")
        taila_quantity = room.get("tailaQuantity")
        lines.append(
            f"{idx}，打手{hsc_count}人，老板{ziqiang_count}人，比例{taila_rate}，出售泰拉{taila_quantity}万"
        )
    if len(pending_rooms) > show_limit:
        lines.append(f"... 其余 {len(pending_rooms) - show_limit} 个未展示")

    content = "\n".join(lines)
    logger.info(content)
    send("7713泰拉车房间", content)


if __name__ == "__main__":
    main()
