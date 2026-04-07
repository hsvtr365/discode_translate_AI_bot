from . import config
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

def is_valid_message(content: str, is_bot: bool, channel_id: int, author_id: int, has_attachments: bool) -> bool:
    """메시지가 번역을 처리해야 하는 조건에 맞는지 검증합니다."""
    if not _is_translation_enabled:
        return False
        
    if is_bot:
        return False
        
    if channel_id not in config.ALLOWED_CHANNEL_IDS:
        return False
        
    if author_id not in (config.USER_EN_ID, config.USER_KO_ID):
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

async def route_and_translate(content: str, author_id: int) -> str | None:
    """사용자에 따라 번역기를 호출하고 접두어를 포함해 반환합니다."""
    if author_id == config.USER_EN_ID:
        translated = await translate_en_to_ko(content)
        if translated:
            return f"🇰🇷 {translated}"
            
    elif author_id == config.USER_KO_ID:
        translated = await translate_ko_to_en(content)
        if translated:
            return f"🇺🇸 {translated}"
            
    return None
