"""Windows 실행.bat에서 사용하는 브라우저 자동 실행 도우미."""
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener

URL = 'http://127.0.0.1:8000'
ROOT = Path(__file__).resolve().parent


def server_ready():
    # 로컬 서버 확인에는 외부 프록시를 사용하지 않습니다.
    try:
        with build_opener(ProxyHandler({})).open(URL, timeout=1) as response:
            return '사진으로 만드는 15초 숏츠' in response.read(65536).decode('utf-8')
    except (OSError, URLError, UnicodeError):
        return False


def main():
    if server_ready():
        print('이미 실행 중인 프로그램을 브라우저에서 엽니다.')
        webbrowser.open(URL)
        return 0
    process = subprocess.Popen([sys.executable, str(ROOT / 'app.py')], cwd=ROOT)
    try:
        print('프로그램을 시작합니다. 이 창은 사용 중에 닫지 마세요.', flush=True)
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if process.poll() is not None:
                print('실행하지 못했습니다. 위 오류를 확인해 주세요.')
                print('라이브러리 설치: .venv\\Scripts\\python -m pip install -r requirements.txt')
                return 1
            if server_ready():
                if not webbrowser.open(URL):
                    print(f'브라우저 주소창에 {URL} 을 입력하세요.')
                print('브라우저를 열었습니다. 종료하려면 이 창에서 Ctrl+C를 누르세요.', flush=True)
                return process.wait()
            time.sleep(0.3)
        print('서버 시작을 30초 동안 확인하지 못했습니다. 위 오류를 확인해 주세요.')
        return 1
    except KeyboardInterrupt:
        print('\n프로그램을 종료합니다.')
        return 0
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


if __name__ == '__main__':
    raise SystemExit(main())
