from . import config
from .translator import translate_en_to_ko, translate_ko_to_en
from .utils import logger
import re

# 동작 상태 저장 변수 (메모리 유지)
_is_translation_enabled = True

LANGUAGE_ENGLISH = "english"
LANGUAGE_KOREAN = "korean"

_KOREAN_CHAR_PATTERN = re.compile(r"[가-힣]")
_ENGLISH_CHAR_PATTERN = re.compile(r"[A-Za-z]")

def toggle_translation() -> bool:
    """번역 활성화/비활성화 상태를 토글합니다."""
    global _is_translation_enabled
    _is_translation_enabled = not _is_translation_enabled
    return _is_translation_enabled

def is_enabled() -> bool:
    return _is_translation_enabled

def get_user_translation_mode(author_id: int) -> str | None:
    return config.USER_TRANSLATION_MODES.get(author_id)

def detect_primary_language(content: str) -> str | None:
    """메시지에서 우세한 언어를 단순 판별합니다."""
    korean_count = len(_KOREAN_CHAR_PATTERN.findall(content))
    english_count = len(_ENGLISH_CHAR_PATTERN.findall(content))

    logger.info(
        "언어 판별: korean_count=%s english_count=%s content=%r",
        korean_count,
        english_count,
        content,
    )

    if korean_count == 0 and english_count == 0:
        return None

    if korean_count == english_count:
        if korean_count == 0:
            return None
        return LANGUAGE_KOREAN

    if korean_count >= english_count:
        return LANGUAGE_KOREAN

    return LANGUAGE_ENGLISH

def is_valid_message(content: str, is_bot: bool, channel_id: int, author_id: int, has_attachments: bool) -> bool:
    """메시지가 번역을 처리해야 하는 조건에 맞는지 검증합니다."""
    if not _is_translation_enabled:
        return False
        
    if is_bot:
        return False
        
    if channel_id not in config.ALLOWED_CHANNEL_IDS:
        return False

    if get_user_translation_mode(author_id) is None:
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
    mode = get_user_translation_mode(author_id)

    if mode == config.TRANSLATION_MODE_EN_TO_KO:
        translated = await translate_en_to_ko(content)
        if translated:
            return f"🇰🇷 {translated}"

    elif mode == config.TRANSLATION_MODE_KO_TO_EN:
        translated = await translate_ko_to_en(content)
        if translated:
            return f"🇺🇸 {translated}"

    elif mode == config.TRANSLATION_MODE_AUTO_REVERSE:
        detected_language = detect_primary_language(content)

        if detected_language == LANGUAGE_ENGLISH:
            translated = await translate_en_to_ko(content)
            if translated:
                return f"🇰🇷 {translated}"
            logger.info("AUTO_REVERSE 영어 메시지 번역에 실패했습니다.")

        elif detected_language == LANGUAGE_KOREAN:
            translated = await translate_ko_to_en(content)
            if translated:
                return f"🇺🇸 {translated}"
            logger.info("AUTO_REVERSE 한국어 메시지 번역에 실패했습니다.")

        else:
            logger.info("AUTO_REVERSE 계정 메시지의 언어를 판별하지 못해 번역을 건너뜁니다.")

    return None
