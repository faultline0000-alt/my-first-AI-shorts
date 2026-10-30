# AI가 바꾸는 미래 — Python 숏츠 만들기

**`shorts_사진` 폴더의 사진 3장**을 순서대로 사용해 **15초짜리 세로 영상**을 만듭니다.
처음 실행할 때 라이브러리를 내려받을 인터넷 연결이 필요합니다. 생성 자체에는 API 키가 필요하지 않습니다.

## 1. 준비하기

Python **3.10 이상**을 설치하세요. Windows에서는 설치 화면에서 `Add Python to PATH`를 체크하세요.
이 프로젝트 폴더를 열고 터미널을 실행하세요. 아래 명령어는 한 줄씩 입력하고 Enter를 누르면 됩니다.

## 사진 넣기

프로젝트 폴더에 `shorts_사진` 폴더를 만들고 사진 3장을 넣으세요.
원하는 순서대로 `01.jpg`, `02.jpg`, `03.jpg`처럼 이름을 붙이면 됩니다.
사진은 파일명에 있는 숫자를 고려해 정렬합니다(1, 2, 10 순서).
JPG, JPEG, PNG, WebP, BMP, TIFF를 지원하며 사진은 정확히 3장이어야 합니다.
사진이 없으면 안내 메시지와 함께 종료하고 기존 출력 영상은 건드리지 않습니다.
휴대폰 사진의 회전을 자동 보정합니다. 사진 전체를 흐린 배경 위에 올려
가로 사진 속 인물이 잘리지 않도록 합니다. 줌인에 필요한 여백도 확보합니다.
직접 촬영했거나 사용 권한이 있는 사진을 사용하세요.

다른 폴더를 쓰려면 실행 명령 뒤에 `--photos "사진 폴더 경로"`를 붙이세요.
예: `.venv/bin/python make_video.py --photos "/경로/shorts_사진"`

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

| 시간 | 코드로 그린 배경 | 사진 아래의 강조 자막 |
| --- | --- | --- |
| 0~5초 | 첫 번째 사진 | AI 혁명은 이미 시작됐다 |
| 5~10초 | 두 번째 사진 | 반도체가 미래를 움직인다 |
| 10~15초 | 세 번째 사진 | 다음 혁신은 로봇이다 |

- MP4 / H.264, 1080×1920, 세로 9:16, 30fps, 총 15초입니다.
- 사진마다 5초 동안 천천히 약 6% 확대합니다. 전환 부근에는 0.2초 페이드 효과가 적용됩니다.

- 자막은 112px의 큰 글씨로, 긴 문장은 두 줄로 표시합니다. 검정 반투명 띠·외곽선·그림자를 사용합니다.
- AI, 혁명, 반도체, 미래, 로봇, 일상, 인간 등 핵심 단어는 노란색으로 강조합니다.
- 각 장면 시작 때 자막이 화면 아래에서 사진 아래쪽으로 0.6초 동안 올라오며 부드럽게 감속합니다.
- 영상은 **무음**이며 사용자가 준비한 사진만 사용합니다.

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
`load_photo()`는 Pillow로 사진 크기·회전·흐린 배경을 처리하고, `main()`은 MoviePy 2.x로 확대·전환·저장을 담당합니다.
`requirements.txt`에는 설치할 라이브러리 버전이 들어 있습니다.

## 사진 순서

- `shorts_사진/01.png`: 남성 단독 사진, 0~5초
- `shorts_사진/02.png`: 여성 단독 사진, 5~10초
- `shorts_사진/03.png`: 세 사람이 함께 나온 사진, 10~15초

기존 AI 주제의 자막과 노란색 강조·아래에서 올라오는 효과는 유지합니다.
인물을 가리지 않도록 자막은 사진 아래쪽에 표시합니다.

## 검증 상태

업로드된 사진 3장으로 실제 영상을 생성했습니다. FFprobe로 15.000초,
1080×1920, 30fps, 450프레임, H.264를 확인했고 전체 디코딩도 오류 없이 통과했습니다.
각 장면의 실제 출력 프레임에서 사진 순서와 인물이 잘리지 않는 배치를 확인했습니다.
