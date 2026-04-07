import os
import sys
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:2b")

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
except ValueError as e:
    print(
        f"사용자 ID 파싱 오류. USER_EN_ID, USER_KO_ID 또는 USER_AUTO_ID를 확인하세요: {e}",
        file=sys.stderr,
    )
    sys.exit(1)

try:
    _auto_ids = os.getenv("USER_AUTO_IDS", "")
    USER_AUTO_IDS = [int(uid.strip()) for uid in _auto_ids.split(",") if uid.strip()]
except ValueError as e:
    print(f"사용자 ID 파싱 오류. USER_AUTO_IDS를 확인하세요: {e}", file=sys.stderr)
    sys.exit(1)

TRANSLATION_MODE_EN_TO_KO = "EN_TO_KO"
TRANSLATION_MODE_KO_TO_EN = "KO_TO_EN"
TRANSLATION_MODE_AUTO_REVERSE = "AUTO_REVERSE"

USER_TRANSLATION_MODES: dict[int, str] = {}

if USER_EN_ID > 0:
    USER_TRANSLATION_MODES[USER_EN_ID] = TRANSLATION_MODE_EN_TO_KO

if USER_KO_ID > 0:
    USER_TRANSLATION_MODES[USER_KO_ID] = TRANSLATION_MODE_KO_TO_EN

for auto_user_id in USER_AUTO_IDS:
    if auto_user_id > 0:
        USER_TRANSLATION_MODES[auto_user_id] = TRANSLATION_MODE_AUTO_REVERSE

if USER_AUTO_ID > 0:
    USER_TRANSLATION_MODES[USER_AUTO_ID] = TRANSLATION_MODE_AUTO_REVERSE
