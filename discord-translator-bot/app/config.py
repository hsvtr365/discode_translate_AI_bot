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
except ValueError as e:
    print(f"사용자 ID 파싱 오류. USER_EN_ID 또는 USER_KO_ID를 확인하세요: {e}", file=sys.stderr)
    sys.exit(1)
