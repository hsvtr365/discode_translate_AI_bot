# Discord Translate AI Bot

로컬 Ollama를 사용해 Discord 특정 채널에서 한국어와 영어를 양방향 번역하는 봇 프로젝트입니다.

현재 실제 애플리케이션 코드는 [`discord-translator-bot`](./discord-translator-bot) 디렉토리에 들어 있습니다.

## 주요 기능

- 특정 채널에서만 번역 동작
- 지정한 영어 사용자와 한국어 사용자 간 양방향 번역
- 로컬 Ollama 모델 사용
- `!ping`, `!status`, `!on`, `!off` 명령 지원

## 프로젝트 위치

- 앱 코드: [`discord-translator-bot/app`](./discord-translator-bot/app)
- 상세 실행 가이드: [`discord-translator-bot/README.md`](./discord-translator-bot/README.md)
- 환경 변수 예시: [`discord-translator-bot/.env.example`](./discord-translator-bot/.env.example)

## 빠른 시작

```bash
cd discord-translator-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 -m app.bot
```

## 필수 설정

- Discord Developer Portal에서 `Message Content Intent` 활성화
- `.env`에 Discord 봇 토큰, 허용 채널 ID, 사용자 ID 입력
- 로컬 Ollama 실행
- 사용 모델 예시: `gemma4:26b`

## 참고

이 저장소 루트 README는 GitHub 소개용입니다. 실제 설정과 테스트 절차는 [`discord-translator-bot/README.md`](./discord-translator-bot/README.md)에서 확인할 수 있습니다.
