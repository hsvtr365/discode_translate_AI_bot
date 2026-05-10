import asyncio
import os
import sys
import types
import unittest
from unittest.mock import patch

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

dotenv_stub = types.ModuleType("dotenv")
dotenv_stub.load_dotenv = lambda: None
sys.modules.setdefault("dotenv", dotenv_stub)

aiohttp_stub = types.ModuleType("aiohttp")
aiohttp_stub.ClientError = Exception
aiohttp_stub.ClientTimeout = lambda *args, **kwargs: None
aiohttp_stub.ClientSession = object
sys.modules.setdefault("aiohttp", aiohttp_stub)

discord_stub = types.ModuleType("discord")


class DiscordException(Exception):
    pass


class LoginFailure(DiscordException):
    pass


class PrivilegedIntentsRequired(DiscordException):
    pass


class Intents:
    @classmethod
    def default(cls):
        return cls()


class Client:
    def __init__(self, *args, **kwargs):
        self._closed = False

    def is_closed(self):
        return self._closed

    async def close(self):
        self._closed = True


discord_stub.Client = Client
discord_stub.DiscordException = DiscordException
discord_stub.Intents = Intents
discord_stub.Message = object
discord_stub.errors = types.SimpleNamespace(
    LoginFailure=LoginFailure,
    PrivilegedIntentsRequired=PrivilegedIntentsRequired,
)
sys.modules.setdefault("discord", discord_stub)

from app import bot
from app import config
from app import connectivity


class AsyncResponse:
    def __init__(self, status):
        self.status = status

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class AsyncSession:
    def __init__(self, status=200, error=None, **kwargs):
        self.status = status
        self.error = error

    async def __aenter__(self):
        if self.error:
            raise self.error
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    def get(self, url):
        return AsyncResponse(self.status)


class ReconnectTests(unittest.TestCase):
    def test_reconnect_delay_is_capped(self):
        delay = bot.calculate_reconnect_delay(
            failure_count=10,
            base_delay=5,
            max_delay=30,
            jitter_ratio=0,
        )

        self.assertEqual(delay, 30)

    def test_connectivity_returns_true_for_successful_response(self):
        result = asyncio.run(
            connectivity.is_online(
                url="https://discord.example/gateway",
                timeout_seconds=1,
                session_factory=lambda **kwargs: AsyncSession(status=200),
            )
        )

        self.assertTrue(result)

    def test_connectivity_returns_false_for_connection_error(self):
        result = asyncio.run(
            connectivity.is_online(
                url="https://discord.example/gateway",
                timeout_seconds=1,
                session_factory=lambda **kwargs: AsyncSession(error=OSError("offline")),
            )
        )

        self.assertFalse(result)

    def test_supervisor_retries_after_recoverable_error(self):
        starts = []

        class FakeClient:
            def __init__(self):
                self.closed = False

            async def start(self, token, reconnect=True):
                starts.append((token, reconnect))
                if len(starts) == 1:
                    raise OSError("network down")

            def is_closed(self):
                return self.closed

            async def close(self):
                self.closed = True

        async def wait_for_connectivity():
            return None

        async def sleep(delay):
            return None

        with patch.object(config, "DISCORD_TOKEN", "token"), patch.object(
            bot,
            "TranslatorBot",
            side_effect=[FakeClient(), FakeClient()],
        ), patch.object(bot, "wait_for_connectivity", wait_for_connectivity), patch.object(
            bot.asyncio,
            "sleep",
            sleep,
        ), patch.object(
            bot,
            "calculate_reconnect_delay",
            return_value=0,
        ):
            asyncio.run(bot.run_with_reconnect())

        self.assertEqual(starts, [("token", True), ("token", True)])


if __name__ == "__main__":
    unittest.main()
