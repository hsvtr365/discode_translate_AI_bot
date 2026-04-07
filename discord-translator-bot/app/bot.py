import discord
from . import config
from . import router
from .utils import logger

class TranslatorBot(discord.Client):
    def __init__(self):
        # 디스코드 메시지 내용 읽기를 위한 인텐트 활성화
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

    async def on_ready(self):
        logger.info(f"봇이 시작되었습니다! 유저 식별자: {self.user}")
        guild_names = ", ".join(f"{guild.name}({guild.id})" for guild in self.guilds) or "없음"
        logger.info(f"접속된 서버: {guild_names}")

    async def on_message(self, message: discord.Message):
        # 자기가 보낸 메시지 무시
        if message.author == self.user:
            return

        logger.info(
            "메시지 수신: guild=%s channel=%s author=%s content=%r",
            getattr(message.guild, "id", None),
            message.channel.id,
            message.author.id,
            message.content,
        )

        content = message.content.strip()

        # 명령어 처리 (심플 구현)
        if content == "!ping":
            logger.info("!ping 명령 감지, pong 응답 시도")
            await message.channel.send("pong")
            return
            
        if content == "!status":
            state_str = "ON 🟢" if router.is_enabled() else "OFF 🔴"
            allowed_channels = ", ".join(str(cid) for cid in config.ALLOWED_CHANNEL_IDS) or "없음"
            target_users = ", ".join(
                f"{user_id}:{mode}" for user_id, mode in config.USER_TRANSLATION_MODES.items()
            ) or "없음"
            msg = (
                "**[통역 봇 상태]**\n"
                f"- 번역 모드: {state_str}\n"
                f"- 허용된 채널 수: {len(config.ALLOWED_CHANNEL_IDS)}개\n"
                f"- 허용 채널 IDs: `{allowed_channels}`\n"
                f"- 사용 언어 모델: `{config.OLLAMA_MODEL}`\n"
                f"- 대상 사용자 모드: `{target_users}`"
            )
            logger.info("!status 명령 감지, 상태 응답 시도")
            await message.channel.send(msg)
            return
            
        if content == "!on":
            if router.is_enabled():
                await message.channel.send("번역 기능이 이미 켜져 있습니다.")
            else:
                router.toggle_translation()
                await message.channel.send("번역 기능이 켜졌습니다.")
            return

        if content == "!off":
            if not router.is_enabled():
                await message.channel.send("번역 기능이 이미 꺼져 있습니다.")
            else:
                router.toggle_translation()
                await message.channel.send("번역 기능이 꺼졌습니다.")
            return

        # 원문 통과는 번역 로직 이전 예외처리
        if content.startswith("!raw "):
            return

        # 유효성 검사 (채널, 작성자, 봇 여부 등)
        has_attachments = len(message.attachments) > 0
        if not router.is_valid_message(content, message.author.bot, message.channel.id, message.author.id, has_attachments):
            return

        # 너무 긴 메시지는 무시하거나 제한
        if len(content) > 1500:
            logger.warning(f"메시지가 너무 깁니다. 번역을 건너뜁니다. ({len(content)}자)")
            return

        # 번역 처리
        try:
            translated_message = await router.route_and_translate(content, message.author.id)
            if translated_message:
                await message.channel.send(translated_message)
            else:
                logger.info("번역 결과가 없어 응답을 생략합니다. author=%s", message.author.id)
        except Exception as e:
            logger.error(f"메시지 번역/처리 과정에서 에러 발생: {e}")
            await message.channel.send("번역 실패")

    async def on_error(self, event_method: str, *args, **kwargs):
        logger.exception("Discord 이벤트 처리 중 오류 발생: %s", event_method)

def run():
    if not config.DISCORD_TOKEN:
        logger.error("환경 변수에 DISCORD_TOKEN이 설정되지 않았습니다.")
        return
        
    client = TranslatorBot()
    try:
        client.run(config.DISCORD_TOKEN)
    except discord.errors.PrivilegedIntentsRequired:
        logger.error(
            "Discord Developer Portal 설정이 필요합니다. "
            "'Bot > Privileged Gateway Intents > Message Content Intent'를 켠 뒤 다시 실행하세요."
        )
    except discord.errors.LoginFailure:
        logger.error(
            "디스코드 로그인에 실패했습니다. DISCORD_TOKEN이 현재 앱의 봇 토큰인지 확인하세요."
        )

if __name__ == "__main__":
    run()
