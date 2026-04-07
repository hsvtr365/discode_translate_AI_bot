import aiohttp
from . import config
from .utils import logger

async def generate_response(prompt: str, system: str) -> str | None:
    url = f"{config.OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": config.OLLAMA_MODEL,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }
    
    try:
        # timeout 처리 포함 (30초 설정)
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("response", "")
                else:
                    text = await response.text()
                    logger.error(f"Ollama API 에러 [Status: {response.status}]: {text}")
                    return None
    except aiohttp.ClientConnectorError:
        logger.error(f"Ollama 서버에 연결할 수 없습니다. URL을 확인하세요: {url}")
        return None
    except Exception as e:
        logger.error(f"Ollama API 호출 중 예측하지 못한 오류 발생: {e}")
        return None
