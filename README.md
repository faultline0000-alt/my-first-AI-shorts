# AI가 바꾸는 미래 — Python 숏츠 만들기

외부 이미지 없이 Python으로 배경을 그려 **30초짜리 세로 영상**을 만듭니다.
처음 실행할 때 라이브러리를 내려받을 인터넷 연결이 필요합니다. 생성 자체에는 API 키가 필요하지 않습니다.

## 1. 준비하기

Python **3.10 이상**을 설치하세요. Windows에서는 설치 화면에서 `Add Python to PATH`를 체크하세요.
이 프로젝트 폴더를 열고 터미널을 실행하세요. 아래 명령어는 한 줄씩 입력하고 Enter를 누르면 됩니다.

## 2. 필요한 라이브러리 설치하기

Windows:

```powershell
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

macOS 또는 Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

가상환경(`.venv`)은 이 프로젝트에서 쓸 라이브러리를 따로 보관하는 폴더입니다.
별도로 활성화하지 않아도 위 명령어대로 실행하면 됩니다.

## 3. 영상 만들기

Windows:

```powershell
.venv\Scripts\python make_video.py
```

macOS 또는 Linux:

```bash
.venv/bin/python make_video.py
```

진행 표시가 끝날 때까지 기다리세요. 컴퓨터 성능에 따라 몇 분 걸릴 수 있습니다.
완성된 파일은 프로젝트의 **`output/ai_shorts.mp4`**입니다. 파일을 더블클릭해서 재생하세요.
다시 실행하면 기존 결과 파일을 덮어씁니다. 중요한 결과는 먼저 다른 이름으로 보관하세요.

## 영상 구성

| 시간 | 코드로 그린 배경 | 중앙의 강조 자막 |
| --- | --- | --- |
| 0~6초 | AI 신경망과 빛나는 원 | AI 혁명은 이미 시작됐다 |
| 6~12초 | 반도체 칩과 회로 | 반도체가 미래를 움직인다 |
| 12~18초 | 휴머노이드 로봇 | 다음 혁신은 로봇이다 |
| 18~24초 | 연결된 스마트 도시 | AI가 우리의 일상을 바꾼다 |
| 24~30초 | 인간과 AI의 협력 | 인간과 AI가 미래를 만든다 |

- MP4 / H.264, 1080×1920, 세로 9:16, 30fps, 총 30초입니다.
- 각 배경은 천천히 확대됩니다. 6초, 12초, 18초, 24초부터 0.4초 동안 배경이 부드럽게 겹쳐 전환됩니다.
- 자막은 112px의 큰 글씨로, 긴 문장은 두 줄로 표시합니다. 검정 반투명 띠·외곽선·그림자를 사용합니다.
- AI, 혁명, 반도체, 미래, 로봇, 일상, 인간 등 핵심 단어는 노란색으로 강조합니다.
- 각 장면 시작 때 자막이 화면 아래에서 중앙으로 0.6초 동안 올라오며 부드럽게 감속합니다.
- 영상은 **무음**입니다. 외부 이미지나 음악을 사용하지 않습니다.

## 한글이 나오지 않거나 폰트 오류가 날 때

프로그램은 Windows의 맑은 고딕, macOS의 Apple SD Gothic Neo,
Linux의 Noto CJK 또는 나눔고딕 폰트 파일이 있는지 확인합니다.
폰트가 없으면 설명을 출력하고 종료합니다. 임의 폰트를 지정할 때는 한글을 지원하는 폰트인지 확인하세요.

Ubuntu/Debian에서는 다음 명령으로 설치할 수 있습니다(관리자 권한 필요).

```bash
sudo apt-get update
sudo apt-get install -y fonts-noto-cjk
```

다른 운영체제에서는 Google Fonts의 **Noto Sans KR**을 내려받아 압축을 풀고,
실제 `.ttf` 파일을 프로젝트의 `fonts` 폴더에 `NotoSansKR-Regular.ttf`라는 이름으로 넣으세요.
Noto 폰트는 SIL Open Font License로 배포됩니다. 폰트를 재배포할 때 라이선스 파일도 함께 보관하세요.
또는 설치된 한글 폰트의 경로를 직접 지정할 수 있습니다.

```bash
.venv/bin/python make_video.py --font "/폰트가/있는/경로/NotoSansKR-Regular.ttf"
```

Windows에서는 위 명령의 `.venv/bin/python` 대신 `.venv\Scripts\python`을 사용하세요.
`KOREAN_FONT` 환경 변수로 경로를 지정하는 방법도 지원합니다.

## 자주 만나는 문제

- `No module named moviepy`: 2단계에서 사용한 가상환경 Python으로 3단계를 실행했는지 확인하세요.
- FFmpeg 오류: 인터넷이 연결된 상태에서 라이브러리 설치를 다시 확인하세요. 기본적으로 imageio-ffmpeg가 제공하는 실행 파일을 사용합니다. 별도 FFmpeg를 쓴다면 실행 전에 `IMAGEIO_FFMPEG_EXE`에 실행 파일 경로를 설정하세요.
- 출력 파일이 안 보임: 터미널에 표시되는 `완료:` 뒤의 절대 경로를 확인하세요.

## 코드 살펴보기

`make_video.py`의 `CAPTIONS`를 바꾸면 자막을 수정할 수 있습니다.
노란색 강조 단어는 `HIGHLIGHT_WORDS`, 등장 속도는 `CAPTION_ENTRY_SECONDS`에서 바꿀 수 있습니다.
`background()`는 Pillow로 장면을 그리고, `main()`은 MoviePy 2.x로 확대·전환·저장을 담당합니다.
`requirements.txt`에는 설치할 라이브러리 버전이 들어 있습니다.

## 이 클라우드 환경에서 확인한 결과

Python 3.12에서 직접 실행하여 영상 생성을 완료했습니다.
FFprobe로 **30.000초, 1080×1920, 30fps, 총 900프레임, H.264**를 확인했고,
FFmpeg로 전체 영상을 디코딩했을 때 오류가 없었습니다.
이 환경에서는 다음 명령으로 바로 다시 생성할 수 있습니다.

```bash
cd /workspace/my-first-AI-shorts
/workspace/shorts-venv/bin/python make_video.py
```

개인 컴퓨터에서는 앞서 설명한 `.venv` 설치·실행 방법을 사용하세요.
