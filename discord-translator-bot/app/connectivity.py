import aiohttp

from .utils import logger

_last_failure_signature: str | None = None
_repeated_failure_count = 0


def _summarize_failure(error: Exception) -> None:
    global _last_failure_signature, _repeated_failure_count

    signature = f"{type(error).__name__}: {error}"
    if signature == _last_failure_signature:
        _repeated_failure_count += 1
    else:
        _last_failure_signature = signature
        _repeated_failure_count = 1

    if _repeated_failure_count == 1:
        logger.warning("Discord 연결 확인 실패: %s", signature)
    elif _repeated_failure_count % 5 == 0:
        logger.warning(
            "Discord 연결 확인 실패가 반복 중입니다. count=%s last_error=%s",
            _repeated_failure_count,
            signature,
        )


async def is_online(
    url: str,
    timeout_seconds: float,
    session_factory=aiohttp.ClientSession,
) -> bool:
    timeout = aiohttp.ClientTimeout(total=timeout_seconds)

    try:
        async with session_factory(timeout=timeout) as session:
            async with session.get(url) as response:
                if 200 <= response.status < 500:
                    return True

                logger.warning(
                    "Discord 연결 확인 응답이 비정상입니다. status=%s url=%s",
                    response.status,
                    url,
                )
                return False
    except Exception as e:
        _summarize_failure(e)
        return False
