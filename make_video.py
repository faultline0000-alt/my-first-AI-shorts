"""외부 이미지나 음악 없이 만드는 30초 AI 숏츠 (MoviePy 2.x)."""
import argparse
import os
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import CompositeVideoClip, ImageClip, vfx

WIDTH, HEIGHT, FPS = 1080, 1920, 30
SCENE_SECONDS, TRANSITION_SECONDS = 6, 0.4
CAPTIONS = ["AI 혁명은 이미 시작됐다", "반도체가 미래를 움직인다", "다음 혁신은 로봇이다",
            "AI가 우리의 일상을 바꾼다", "인간과 AI가 미래를 만든다"]
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


def background(scene):
    # 모든 도형을 직접 그리므로 외부 이미지가 필요하지 않습니다.
    y, x = np.mgrid[0:HEIGHT, 0:WIDTH]
    glow = np.exp(-((x - 540) ** 2 / 260000 + (y - 800) ** 2 / 650000))
    colors = [(15, 100, 165), (35, 150, 100), (100, 65, 170), (20, 130, 155), (155, 95, 45)]
    rgb = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    for channel, value in enumerate(colors[scene]):
        rgb[:, :, channel] = (8 + glow * value).astype(np.uint8)
    img = Image.fromarray(rgb)
    d = ImageDraw.Draw(img)
    accent = [(70, 220, 255), (80, 255, 160), (195, 150, 255), (70, 235, 225), (255, 195, 100)][scene]
    for xx in range(0, WIDTH, 90):
        d.line((xx, 0, xx, HEIGHT), fill=(22, 40, 60), width=2)
    for yy in range(0, HEIGHT, 90):
        d.line((0, yy, WIDTH, yy), fill=(22, 40, 60), width=2)
    if scene == 0:
        nodes = [(240, 560), (540, 420), (840, 560), (180, 850),
                 (540, 740), (900, 850), (300, 1180), (780, 1180), (540, 1390)]
        for i, a in enumerate(nodes):
            for b in nodes[i + 1:]:
                if abs(a[0] - b[0]) < 650:
                    d.line((*a, *b), fill=(30, 105, 150), width=4)
        for xx, yy in nodes:
            d.ellipse((xx-22, yy-22, xx+22, yy+22), fill=accent)
        for radius in (180, 240, 300):
            d.ellipse((540-radius, 870-radius, 540+radius, 870+radius), outline=accent, width=5)
    elif scene == 1:
        for offset in range(330, 800, 55):
            d.line((offset, 500, offset, 640), fill=accent, width=12)
            d.line((offset, 1220, offset, 1400), fill=accent, width=12)
        for yy in range(680, 1220, 60):
            d.line((140, yy, 290, yy), fill=accent, width=12)
            d.line((790, yy, 940, yy), fill=accent, width=12)
        d.rounded_rectangle((290, 620, 790, 1260), radius=35, fill=(12, 42, 38), outline=accent, width=12)
        for inset in (40, 80, 120):
            d.rectangle((290+inset, 620+inset, 790-inset, 1260-inset), outline=(35, 130, 95), width=5)
    elif scene == 2:
        d.rounded_rectangle((310, 420, 770, 850), radius=100, fill=(70, 65, 105), outline=accent, width=10)
        d.rounded_rectangle((365, 540, 715, 690), radius=45, fill=(10, 18, 35), outline=accent, width=5)
        for xx in (435, 645):
            d.ellipse((xx-30, 580, xx+30, 640), fill=(100, 235, 255))
        d.rectangle((475, 850, 605, 930), fill=accent)
        d.rounded_rectangle((270, 930, 810, 1430), radius=90, fill=(50, 48, 85), outline=accent, width=10)
        for left in (140, 830):
            d.rounded_rectangle((left, 970, left+110, 1430), radius=45, fill=(60, 55, 90), outline=accent, width=7)
        d.ellipse((470, 1100, 610, 1240), outline=accent, width=10)
    elif scene == 3:
        # 회로로 연결된 스마트 도시: AI가 일상에 스며드는 모습
        buildings = [(150, 690, 330, 1390), (380, 480, 600, 1390),
                     (650, 760, 900, 1390)]
        for left, top, right, bottom in buildings:
            d.rounded_rectangle((left, top, right, bottom), radius=20,
                                fill=(15, 45, 60), outline=accent, width=7)
            for xx in range(left + 30, right - 20, 50):
                for yy in range(top + 45, bottom - 30, 85):
                    d.rectangle((xx, yy, xx + 20, yy + 30), fill=accent)
        for radius in (85, 150, 215):
            d.arc((540-radius, 420-radius, 540+radius, 420+radius),
                  205, 335, fill=accent, width=8)
        d.line((120, 1460, 960, 1460), fill=accent, width=6)
    else:
        # 인간과 AI를 연결하는 빛: 기존의 도형·격자 스타일을 유지
        d.ellipse((190, 520, 410, 740), fill=(65, 55, 45), outline=accent, width=9)
        d.rounded_rectangle((160, 800, 440, 1350), radius=90,
                            fill=(55, 43, 35), outline=accent, width=9)
        d.rounded_rectangle((670, 520, 890, 740), radius=45,
                            fill=(55, 43, 35), outline=accent, width=9)
        for xx in (730, 830):
            d.ellipse((xx-16, 600, xx+16, 632), fill=accent)
        d.rounded_rectangle((640, 800, 920, 1350), radius=45,
                            fill=(55, 43, 35), outline=accent, width=9)
        d.line((420, 1140, 540, 1210, 660, 1140), fill=accent, width=18)
        for radius in (65, 100, 140):
            d.ellipse((540-radius, 410-radius, 540+radius, 410+radius),
                      outline=accent, width=5)
    return np.array(img)


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
    """아래 화면 밖에서 출발해 중앙으로 올라오며 부드럽게 감속합니다."""
    progress = min(max(t / CAPTION_ENTRY_SECONDS, 0), 1)
    resting_y = (HEIGHT - CAPTION_HEIGHT) / 2
    y = resting_y + (HEIGHT - resting_y) * (1 - progress) ** 3
    return (0, y)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", help="한글 TTF/OTF/TTC 폰트 경로")
    args = parser.parse_args()
    font_path = find_font(args.font)
    print(f"사용하는 한글 폰트: {font_path}")
    layers = []
    for i, text in enumerate(CAPTIONS):
        duration = SCENE_SECONDS + (TRANSITION_SECONDS if i < len(CAPTIONS) - 1 else 0)
        bg = (ImageClip(background(i)).with_duration(duration)
              .resized(lambda t: 1 + 0.012 * t).with_position("center"))
        scene = CompositeVideoClip([bg], size=(WIDTH, HEIGHT)).with_duration(duration)
        if i:
            scene = scene.with_effects([vfx.CrossFadeIn(TRANSITION_SECONDS)])
        layers.append(scene.with_start(i * SCENE_SECONDS))
    # 자막은 배경 전환과 별도로 정확히 0/6/12/18/24초에 바뀝니다.
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
