"""로컬 웹 화면: python app.py"""
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Lock

from flask import Flask, jsonify, render_template, request, send_file
from PIL import Image, UnidentifiedImageError

from make_video import CAPTIONS, HIGHLIGHT_WORDS, render_video

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
render_lock = Lock()


@app.get('/')
def index():
    return render_template('index.html', captions=CAPTIONS,
                           highlights=', '.join(HIGHLIGHT_WORDS))


@app.errorhandler(413)
def too_large(_error):
    return jsonify(error='전체 업로드는 32MB 이하로 줄여 주세요.'), 413


@app.post('/api/render')
def create_video():
    photos = [request.files.get(f'photo{i}') for i in range(3)]
    captions = [request.form.get(f'caption{i}', '').strip() for i in range(3)]
    if any(photo is None or not photo.filename for photo in photos):
        return jsonify(error='사진을 각 장면에 한 장씩, 총 3장 선택해 주세요.'), 400
    if any(not text or len(text) > 60 for text in captions):
        return jsonify(error='각 자막은 1~60자로 입력해 주세요.'), 400
    voice = request.form.get('voice', 'male')
    if voice not in ('none', 'male', 'female'):
        return jsonify(error='목소리를 다시 선택해 주세요.'), 400
    highlights = tuple(word.strip() for word in request.form.get('highlights', '').split(',')
                       if word.strip())
    if len(highlights) > 20 or any(len(word) > 30 for word in highlights):
        return jsonify(error='강조 단어는 30자 이하로 최대 20개까지 입력해 주세요.'), 400
    if not render_lock.acquire(blocking=False):
        return jsonify(error='다른 영상이 제작 중입니다. 잠시 후 다시 시도해 주세요.'), 409
    try:
        with TemporaryDirectory(prefix='shorts-web-') as temporary:
            folder = Path(temporary)
            paths = []
            for i, upload in enumerate(photos):
                path = folder / f'photo{i}'
                upload.save(path)
                try:
                    with Image.open(path) as image:
                        if image.width * image.height > 25_000_000:
                            raise ValueError('사진 해상도를 2,500만 화소 이하로 줄여 주세요.')
                        image.verify()
                except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as error:
                    raise ValueError(f'{i + 1}번 사진을 읽을 수 없습니다. JPG 또는 PNG 파일을 확인해 주세요.') from error
                paths.append(path)
            output = render_video(paths, captions, folder / 'ai_shorts.mp4',
                                  highlight_words=highlights, logger=None, voice=voice)
            # 임시 사진·파일을 지워도 브라우저는 완성된 영상 데이터를 받을 수 있습니다.
            result = BytesIO(output.read_bytes())
        return send_file(result, mimetype='video/mp4', as_attachment=True,
                         download_name='ai_shorts.mp4', max_age=0)
    except ValueError as error:
        return jsonify(error=str(error)), 400
    except Exception:
        app.logger.exception('영상 제작 실패')
        return jsonify(error='영상 제작에 실패했습니다. 서버 터미널의 오류와 README의 폰트·FFmpeg 안내를 확인해 주세요.'), 500
    finally:
        render_lock.release()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=False)
