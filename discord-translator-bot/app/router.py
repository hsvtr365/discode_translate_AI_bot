from . import config
from .history import ConversationMessage
from .translator import translate_en_to_ko, translate_ko_to_en
from .utils import logger
import re

# 동작 상태 저장 변수 (메모리 유지)
_is_translation_enabled = True

def toggle_translation() -> bool:
    """번역 활성화/비활성화 상태를 토글합니다."""
    global _is_translation_enabled
    _is_translation_enabled = not _is_translation_enabled
    return _is_translation_enabled

def is_enabled() -> bool:
    return _is_translation_enabled

def contains_korean(text: str) -> bool:
    return re.search(r"[가-힣]", text) is not None

def is_valid_message(content: str, is_bot: bool, channel_id: int, author_id: int, has_attachments: bool) -> bool:
    """메시지가 번역을 처리해야 하는 조건에 맞는지 검증합니다."""
    if not _is_translation_enabled:
        return False
        
    if is_bot:
        return False
        
    if channel_id not in config.ALLOWED_CHANNEL_IDS:
        return False
        
    text = content.strip()
    if not text:
        # 빈 메시지(첨부파일만 있는 경우 등) 무시
        return False
        
    if text.startswith("!raw "):
        return False
        
    # URL만 있는 메시지 무시
    url_pattern = re.compile(r'^(?:http|ftp)s?://[^\s]+$', re.IGNORECASE)
    if url_pattern.match(text):
        return False

    return True

async def route_and_translate(
    content: str,
    author_id: int,
    context: list[ConversationMessage] | None = None,
) -> str | None:
    """메시지 언어를 감지해 번역기를 호출하고 접두어를 포함해 반환합니다."""
    if contains_korean(content):
        translated = await translate_ko_to_en(content, context=context)
        if translated:
            return f"🇺🇸 {translated}"

    else:
        translated = await translate_en_to_ko(content)
        if translated:
            return f"🇰🇷 {translated}"
            
    return None
