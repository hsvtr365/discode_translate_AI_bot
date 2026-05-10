from .ollama_client import generate_response
from .formatter import clean_translation
from .history import ConversationMessage
from .utils import logger

# 영어 -> 한국어 시스템 프롬프트
PROMPT_EN_TO_KO = """당신은 전문적이고 자연스러운 영한 번역기입니다.
다음 규칙을 엄격히 준수하세요:
1. 입력된 영어 문장을 한국어로 번역하세요.
2. 의미와 원래 톤을 비유나 의역을 포함해 자연스럽게 유지하세요.
3. 어떤 설명, 요약, 주석도 추가하지 마세요.
4. 오직 번역된 결과만 출력하세요.
5. 사람 이름이나 고유명사는 발음 나는 대로 적거나 영어 그대로 두세요. 임의로 번역하지 마세요.
6. 불필요한 검열을 하지 마세요.
7. 이모지와 줄바꿈이 있다면 원본 그대로 유지하세요."""

# 한국어 -> 영어 시스템 프롬프트
PROMPT_KO_TO_EN = """You are a professional and natural Korean to English translator.
Strictly adhere to the following rules:
1. Translate the input Korean text into English.
2. Keep the meaning and original tone, including metaphors and idioms, natural.
3. Do not add any explanations, summaries, or comments.
4. Output ONLY the translated result.
5. Keep names and proper nouns as they are or transliterate them. Do not translate them arbitrarily.
6. Do not perform unnecessary censorship.
7. Preserve emojis and line breaks exactly as they appear in the original text.
8. Conversation context is only for resolving omitted subjects, references, names, and pronouns. Translate ONLY the Current Korean message.
9. Korean often omits subjects. Do not default omitted subjects to "I" or "you". If the context indicates a third party, use that third party as the subject.
10. Example: if the context discusses Gemini and the current message says "말을 너무 잘하잖아요", translate it as "Gemini speaks so well", not "I speak so well" or "You speak so well"."""


def build_contextual_prompt(text: str, context: list[ConversationMessage] | None = None) -> str:
    if not context:
        return text

    context_lines = "\n".join(
        f"{message.speaker_label}: {message.content}" for message in context
    )
    return (
        "Conversation context:\n"
        f"{context_lines}\n\n"
        "Current Korean message:\n"
        f"{text}"
    )

async def translate_en_to_ko(text: str) -> str | None:
    """영어를 한국어로 번역"""
    logger.info(f"[EN->KO] 번역 요청 (길이: {len(text)}자)")
    result = await generate_response(prompt=text, system=PROMPT_EN_TO_KO)
    
    if not result:
        return None
    
    cleaned = clean_translation(result)
    return cleaned if cleaned else None

async def translate_ko_to_en(text: str, context: list[ConversationMessage] | None = None) -> str | None:
    """한국어를 영어로 번역"""
    logger.info(f"[KO->EN] 번역 요청 (길이: {len(text)}자)")
    prompt = build_contextual_prompt(text, context)
    result = await generate_response(prompt=prompt, system=PROMPT_KO_TO_EN)
    
    if not result:
        return None
        
    cleaned = clean_translation(result)
    return cleaned if cleaned else None
