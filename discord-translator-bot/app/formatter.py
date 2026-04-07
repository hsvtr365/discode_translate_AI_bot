import re

def clean_translation(text: str) -> str:
    if not text:
        return ""
    
    # 앞뒤 공백 제거
    text = text.strip()
    
    # 번역 접두어 제거 (대소문자 무시)
    prefixes_to_remove = [
        r"^Translati(?:on)?:\s*",
        r"^번역:\s*",
        r"^Korean:\s*",
        r"^English:\s*",
        r"^\*\*번역:\*\*\s*",
        r"^\*\*Translation:\*\*\s*"
    ]
    
    for prefix in prefixes_to_remove:
        text = re.sub(prefix, "", text, flags=re.IGNORECASE)
        
    text = text.strip()
    
    # 전체를 감싸는 따옴표 제거 (따옴표로 시작하고 끝나는 경우)
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        if len(text) > 1:
            text = text[1:-1]
        
    return text.strip()
