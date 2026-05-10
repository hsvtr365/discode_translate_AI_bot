import os
import sys
import types
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

dotenv_stub = types.ModuleType("dotenv")
dotenv_stub.load_dotenv = lambda: None
sys.modules.setdefault("dotenv", dotenv_stub)

aiohttp_stub = types.ModuleType("aiohttp")
aiohttp_stub.ClientError = Exception
aiohttp_stub.ClientSession = object
aiohttp_stub.ClientTimeout = lambda *args, **kwargs: None
sys.modules.setdefault("aiohttp", aiohttp_stub)

from app import config
from app import history
from app.translator import build_contextual_prompt


class ContextHistoryTests(unittest.TestCase):
    def setUp(self):
        history.clear_history()
        config.USER_KO_ID = 100
        config.USER_EN_ID = 200
        config.USER_KO_IDS = {100}
        config.TRANSLATION_USER_IDS = {100, 200}

    def tearDown(self):
        history.clear_history()

    def test_history_keeps_recent_messages_per_channel(self):
        for index in range(10):
            history.add_message(channel_id=1, author_id=100, content=f"메시지 {index}")

        context = history.get_context(channel_id=1)

        self.assertEqual(len(context), 8)
        self.assertEqual(context[0].content, "메시지 2")
        self.assertEqual(context[-1].content, "메시지 9")

    def test_history_is_separated_by_channel(self):
        history.add_message(channel_id=1, author_id=100, content="제미나이 얘기")
        history.add_message(channel_id=2, author_id=100, content="릭 얘기")

        self.assertEqual(history.get_context(channel_id=1)[0].content, "제미나이 얘기")
        self.assertEqual(history.get_context(channel_id=2)[0].content, "릭 얘기")

    def test_contextual_prompt_marks_context_and_current_message(self):
        history.add_message(channel_id=1, author_id=100, content="제미나이가 말이 청산유수예요")
        context = history.get_context(channel_id=1)

        prompt = build_contextual_prompt("말을 너무 잘하잖아요", context)

        self.assertIn("Conversation context:", prompt)
        self.assertIn("Korean speaker: 제미나이가 말이 청산유수예요", prompt)
        self.assertIn("Current Korean message:\n말을 너무 잘하잖아요", prompt)

    def test_contextual_prompt_without_context_is_original_text(self):
        self.assertEqual(build_contextual_prompt("안녕하세요", []), "안녕하세요")
        self.assertEqual(build_contextual_prompt("안녕하세요", None), "안녕하세요")

    def test_any_human_author_is_valid_in_allowed_channel(self):
        config.ALLOWED_CHANNEL_IDS = [1]

        from app import router

        self.assertTrue(
            router.is_valid_message(
                content="문맥 테스트 진행!",
                is_bot=False,
                channel_id=1,
                author_id=999999,
                has_attachments=False,
            )
        )

    def test_language_detection_uses_korean_text(self):
        from app import router

        self.assertTrue(router.contains_korean("문맥 테스트 진행!"))
        self.assertFalse(router.contains_korean("Context test!"))


if __name__ == "__main__":
    unittest.main()
