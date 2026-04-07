# Discord 양방향 통역 봇 (로컬 Ollama 사용)

특정 채널과 특정 두 사용자 간의 대화를 실시간으로 양방향 통역(한국어 <-> 영어)해주는 디스코드 봇입니다. 

## 기능 및 특징
- **양방향 통역**: `USER_EN_ID`의 메시지는 영어 원문으로 간주하여 한국어로 번역하고, `USER_KO_ID`의 메시지는 한국어로 간주하여 영어로 번역합니다.
- **로컬 LLM 연동**: Ollama의 `gemma4:26b` 모델 API를 활용하여 번역을 수행합니다.
- **간단한 명령어**:
  - `!ping`: `pong` 응답.
  - `!status`: 현재 봇의 번역 상태, 허용 채널, 사용 모델 등을 출력.
  - `!on` / `!off`: 봇의 번역 기능을 즉각적으로 활성화/비활성화.
- **원본 유입 무시**: URL만 있는 메시지, 빈 메시지, `!raw `로 시작하는 메시지는 번역하지 않고 무시합니다.
- **결과 포맷팅**: 
  - 영어 -> 한국어 번역: `🇰🇷 결과`
  - 한국어 -> 영어 번역: `🇺🇸 결과`

## 설치 및 준비

### 1. Python 환경 세팅
Python 3.11 이상 환경을 준비하고 패키지를 설치합니다.
```bash
python3 -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. .env 환경 변수 설정
`.env.example`을 복사하여 `.env`를 만듭니다.
```bash
cp .env.example .env
```
그 다음 파일 안에 봇 토큰과 올바른 ID 정보를 기입하세요:
- `DISCORD_TOKEN`: Discord Developer Portal에서 받은 봇 토큰
- `ALLOWED_CHANNEL_IDS`: 봇이 동작할 텍스트 채널 ID 목록 (쉼표 구분)
- `USER_EN_ID`: 영어를 쓰는 사용자의 디스코드 숫자 ID
- `USER_KO_ID`: 한국어를 쓰는 사용자의 디스코드 숫자 ID

### 3. Discord Developer Portal 인텐트 설정
봇이 메시지를 읽으려면 **Message Content Intent**가 활성화되어 있어야 합니다.
1. [Discord Developer Portal](https://discord.com/developers/applications)의 봇 페이지로 이동.
2. 왼쪽 메뉴에서 `Bot` 클릭.
3. 스크롤을 내려 **Privileged Gateway Intents** 섹션을 찾음.
4. **Message Content Intent** 스위치를 `켜기(ON)`로 설정 후 `Save Changes`.

### 4. 로컬 Ollama 구동
동작하는 기기(또는 원격 서버)에 Ollama가 실행 중이어야 합니다. 현재 설정 기준 모델은 `gemma4:26b` 입니다.

```bash
# 로컬에서 모델 실행 (HTTP 서버 자동 구동 됨)
ollama run gemma4:26b
```

## 실행 방법

아래 커맨드를 통해 봇을 실행하세요.
```bash
python3 -m app.bot
```

## 테스트 시나리오

1. **테스트 시나리오 1: 영->한 번역 확인**
   - 대상: `USER_EN_ID`
   - 디스코드 동작: 허용된 채널에 `USER_EN_ID` 계정으로 `I think we should redesign the architecture tomorrow.` 메시지 전송.
   - 예상 결과: 봇이 `🇰🇷 내일 아키텍처를 다시 디자인해야 할 것 같아요.`라고 메시지 전송.

2. **테스트 시나리오 2: 한->영 번역 확인**
   - 대상: `USER_KO_ID`
   - 디스코드 동작: 해당 채널에 `USER_KO_ID` 계정으로 `그럼 내일 회의 전에 명세를 먼저 정리해서 공유해 드릴게요.` 메시지 전송.
   - 예상 결과: 봇이 `🇺🇸 Then I'll summarize the specifications and share them with you before the meeting tomorrow.`라고 메시지 전송.

3. **테스트 시나리오 3: 기능 비활성화 및 무시 규칙 확인**
   - 디스코드 동작 1: 아무나 제 3의 계정으로 `Hello?` 입력. -> 응답 없음 (무시)
   - 디스코드 동작 2: `USER_KO_ID`가 `!off` 입력 후 `테스트입니다.` 전송. -> 봇이 번역 기능을 비활성화 했다는 안내 후 이후 메시지 무시.
   - 디스코드 동작 3: `!on` 입력 후 다시 기능을 켠 상태에서 `!raw 이 메시지는 번역하지 마세요` 전송. -> 접두어 조건에 의해 응답 없음 (무시).
