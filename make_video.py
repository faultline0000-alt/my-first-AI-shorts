"""shorts_사진의 사진 3장으로 만드는 15초 숏츠 (MoviePy 2.x)."""
import argparse
import os
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from moviepy import CompositeVideoClip, ImageClip, vfx

WIDTH, HEIGHT, FPS = 1080, 1920, 30
SCENE_SECONDS, TRANSITION_SECONDS = 5, 0.2
CAPTIONS = ["AI 혁명은 이미 시작됐다", "반도체가 미래를 움직인다", "다음 혁신은 로봇이다"]
TOTAL_SECONDS = SCENE_SECONDS * len(CAPTIONS)
CAPTION_HEIGHT = 420
CAPTION_ENTRY_SECONDS = 0.6
HIGHLIGHT_WORDS = ("AI", "혁명", "반도체", "미래", "로봇", "일상", "인간")
ROOT = Path(__file__).resolve().parent


def find_font(explicit=None):
    candidates = [explicit, os.environ.get("KOREAN_FONT"),
                  ROOT / "fonts/NotoSansKR-Regular.ttf",
                  "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
                  "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
                  "C:/Windows/Fonts/malgun.ttf",
                  "/System/Library/Fonts/AppleSDGothicNeo.ttc"]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            try:
                ImageFont.truetype(str(candidate), 64)
                return str(candidate)
            except OSError:
                pass
    raise SystemExit("한글 폰트를 찾지 못했습니다. README의 폰트 설치 방법을 따라 주세요.\n"
                     "설치 후 python make_video.py --font 폰트파일경로 로 실행하세요.")


def photo_paths(folder):
    """01, 02, 03 또는 1, 2, 10처럼 숫자를 고려한 파일명 순서입니다."""
    if not folder.is_dir():
        raise SystemExit(f"사진 폴더가 없습니다: {folder}\n"
                         "shorts_사진 폴더에 사진 3장을 넣거나 --photos 경로를 지정하세요.")
    supported = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
    paths = [p for p in folder.iterdir()
             if p.is_file() and not p.name.startswith(".") and p.suffix.lower() in supported]
    def sort_key(path):
        return [(0, int(part)) if part.isdigit() else (1, part.casefold())
                for part in re.split(r"(\d+)", path.name)]
    paths.sort(key=lambda p: (sort_key(p), p.name))
    if len(paths) != 3:
        raise SystemExit(f"사진은 정확히 3장이어야 합니다. 현재 {len(paths)}장: {folder}")
    return paths


def load_photo(path):
    """회전을 보정하고, 인물이 잘리지 않도록 흐린 배경 위에 사진을 올립니다."""
    try:
        with Image.open(path) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
            backdrop = ImageOps.fit(image, (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS)
            backdrop = backdrop.filter(ImageFilter.GaussianBlur(35))
            # 6% 줌인 후에도 원본 사진 가장자리가 화면 안에 남도록 여유를 둡니다.
            photo = ImageOps.contain(image, (int(WIDTH / 1.07), int(HEIGHT / 1.07)),
                                    method=Image.Resampling.LANCZOS)
            backdrop.paste(photo, ((WIDTH - photo.width) // 2, (HEIGHT - photo.height) // 2))
            return np.array(backdrop)
    except (OSError, ValueError) as error:
        raise SystemExit(f"사진을 읽을 수 없습니다: {path}\n{error}") from error


def caption_image(text, font_path):
    """큰 두 줄 자막을 그리고 핵심 단어만 노란색으로 강조합니다."""
    img = Image.new("RGBA", (WIDTH, CAPTION_HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, 112)
    # 글자를 작게 줄이는 대신 단어 사이에서 줄을 바꿉니다.
    lines = []
    line = ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if line and d.textlength(candidate, font=font) > WIDTH - 160:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    line_height = 145
    block_height = line_height * len(lines)
    if block_height > CAPTION_HEIGHT - 40:
        raise ValueError("자막이 너무 깁니다. CAPTIONS의 문장을 짧게 줄여 주세요.")
    top = (CAPTION_HEIGHT - block_height) // 2
    d.rounded_rectangle((35, top - 15, WIDTH - 35, top + block_height + 15),
                        radius=32, fill=(0, 0, 0, 175))
    pattern = "(" + "|".join(re.escape(word) for word in HIGHLIGHT_WORDS) + ")"
    for index, line in enumerate(lines):
        x = (WIDTH - d.textlength(line, font=font)) / 2
        y = top + index * line_height + line_height / 2
        for part in re.split(pattern, line):
            if not part:
                continue
            color = (255, 220, 40) if part in HIGHLIGHT_WORDS else "white"
            d.text((x + 3, y + 7), part, font=font, anchor="lm",
                   fill=(0, 0, 0, 230), stroke_width=7, stroke_fill=(0, 0, 0, 230))
            d.text((x, y), part, font=font, anchor="lm", fill=color,
                   stroke_width=5, stroke_fill=(0, 0, 0, 255))
            x += d.textlength(part, font=font)
    return np.array(img)


def caption_position(t):
    """아래 화면 밖에서 출발해 사진 아래쪽으로 올라오며 부드럽게 감속합니다."""
    progress = min(max(t / CAPTION_ENTRY_SECONDS, 0), 1)
    resting_y = HEIGHT - CAPTION_HEIGHT - 160
    y = resting_y + (HEIGHT - resting_y) * (1 - progress) ** 3
    return (0, y)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", help="한글 TTF/OTF/TTC 폰트 경로")
    parser.add_argument("--photos", type=Path, default=ROOT / "shorts_사진",
                        help="사진 3장이 있는 폴더 (기본: 프로젝트의 shorts_사진)")
    args = parser.parse_args()
    paths = photo_paths(args.photos)
    photos = [load_photo(path) for path in paths]
    for i, path in enumerate(paths):
        print(f"{i * SCENE_SECONDS}~{(i + 1) * SCENE_SECONDS}초: {path.name}")
    font_path = find_font(args.font)
    print(f"사용하는 한글 폰트: {font_path}")
    layers = []
    for i, photo in enumerate(photos):
        duration = SCENE_SECONDS
        bg = (ImageClip(photo).with_duration(duration)
              .resized(lambda t: 1 + 0.012 * t).with_position("center"))
        scene = CompositeVideoClip([bg], size=(WIDTH, HEIGHT)).with_duration(duration)
        # 겹침 없이 정확히 5초씩 유지하면서 짧은 페이드로 연결합니다.
        effects = []
        if i:
            effects.append(vfx.FadeIn(TRANSITION_SECONDS))
        if i < len(photos) - 1:
            effects.append(vfx.FadeOut(TRANSITION_SECONDS))
        scene = scene.with_effects(effects)
        layers.append(scene.with_start(i * SCENE_SECONDS))
    # 자막은 배경 전환과 별도로 정확히 0/5/10초에 바뀝니다.
    for i, text in enumerate(CAPTIONS):
        layers.append(ImageClip(caption_image(text, font_path))
                      .with_duration(SCENE_SECONDS).with_position(caption_position)
                      .with_start(i * SCENE_SECONDS))
    video = CompositeVideoClip(layers, size=(WIDTH, HEIGHT)).with_duration(TOTAL_SECONDS)
    output = ROOT / "output/ai_shorts.mp4"
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        video.write_videofile(str(output), fps=FPS, codec="libx264", audio=False,
                              preset="fast", threads=2,
                              ffmpeg_params=["-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart"])
    finally:
        video.close()
        for layer in layers:
            layer.close()
    print(f"완료: {output}")


if __name__ == "__main__":
    main()
