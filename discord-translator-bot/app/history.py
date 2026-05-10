from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Deque

MAX_HISTORY_PER_CHANNEL = 8


@dataclass(frozen=True)
class ConversationMessage:
    speaker_label: str
    content: str


_channel_history: dict[int, Deque[ConversationMessage]] = defaultdict(
    lambda: deque(maxlen=MAX_HISTORY_PER_CHANNEL)
)


def contains_korean(text: str) -> bool:
    return any("가" <= char <= "힣" for char in text)


def speaker_label_for(content: str) -> str:
    if contains_korean(content):
        return "Korean speaker"
    return "English speaker"


def add_message(channel_id: int, author_id: int, content: str) -> None:
    text = content.strip()
    if not text:
        return

    _channel_history[channel_id].append(
        ConversationMessage(
            speaker_label=speaker_label_for(text),
            content=text,
        )
    )


def get_context(channel_id: int) -> list[ConversationMessage]:
    return list(_channel_history[channel_id])


def clear_history() -> None:
    _channel_history.clear()
