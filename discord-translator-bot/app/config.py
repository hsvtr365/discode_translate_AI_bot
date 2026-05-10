import os
import sys
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:2b")
DISCORD_CONNECTIVITY_CHECK_URL = os.getenv(
    "DISCORD_CONNECTIVITY_CHECK_URL",
    "https://discord.com/api/v10/gateway",
)


def _get_float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        parsed = float(value)
    except ValueError as e:
        print(f"{name} 파싱 오류. 숫자로 입력하세요: {e}", file=sys.stderr)
        sys.exit(1)
    if parsed <= 0:
        print(f"{name} 파싱 오류. 0보다 큰 숫자로 입력하세요.", file=sys.stderr)
        sys.exit(1)
    return parsed


def _parse_int_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


DISCORD_RECONNECT_BASE_DELAY_SECONDS = _get_float_env(
    "DISCORD_RECONNECT_BASE_DELAY_SECONDS",
    5,
)
DISCORD_RECONNECT_MAX_DELAY_SECONDS = _get_float_env(
    "DISCORD_RECONNECT_MAX_DELAY_SECONDS",
    300,
)
DISCORD_CONNECTIVITY_TIMEOUT_SECONDS = _get_float_env(
    "DISCORD_CONNECTIVITY_TIMEOUT_SECONDS",
    5,
)

try:
    _channels = os.getenv("ALLOWED_CHANNEL_IDS", "")
    ALLOWED_CHANNEL_IDS = [int(cid.strip()) for cid in _channels.split(",") if cid.strip()]
except ValueError as e:
    print(f"채널 ID 파싱 오류. ALLOWED_CHANNEL_IDS를 확인하세요: {e}", file=sys.stderr)
    sys.exit(1)

try:
    USER_EN_ID = int(os.getenv("USER_EN_ID", "0"))
    USER_KO_ID = int(os.getenv("USER_KO_ID", "0"))
    USER_AUTO_ID = int(os.getenv("USER_AUTO_ID", "0"))
    USER_AUTO_IDS = _parse_int_list(os.getenv("USER_AUTO_IDS", ""))
except ValueError as e:
    print(
        "사용자 ID 파싱 오류. USER_EN_ID, USER_KO_ID, USER_AUTO_ID, "
        f"또는 USER_AUTO_IDS를 확인하세요: {e}",
        file=sys.stderr,
    )
    sys.exit(1)

USER_KO_IDS = {
    user_id
    for user_id in [USER_KO_ID, USER_AUTO_ID, *USER_AUTO_IDS]
    if user_id
}
TRANSLATION_USER_IDS = {
    user_id
    for user_id in [USER_EN_ID, *USER_KO_IDS]
    if user_id
}
