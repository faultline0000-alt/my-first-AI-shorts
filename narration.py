"""한국어 합성 음성을 만들고 장면별로 배치합니다."""
import asyncio
import os
from pathlib import Path

import edge_tts
from moviepy import AudioFileClip, CompositeAudioClip

VOICES = {
    'male': 'ko-KR-InJoonNeural',
    'female': 'ko-KR-SunHiNeural',
}


async def synthesize(text, voice, output):
    try:
        communication = edge_tts.Communicate(
            text.replace('AI', '에이아이'), VOICES[voice], rate='-5%',
            pitch='-2Hz' if voice == 'male' else '+0Hz',
            proxy=os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy'),
            connect_timeout=15, receive_timeout=30)
        await communication.save(str(output))
    except Exception as error:
        raise ValueError('음성 서비스에 연결하지 못했습니다. 인터넷 연결을 확인하고 다시 시도해 주세요. '
                         '계속 실패하면 목소리를 "음성 없음"으로 선택할 수 있습니다. '
                         f'(오류 종류: {type(error).__name__})') from error


def create_narration(captions, voice, folder):
    """각 문장을 0.3초 뒤에 읽고, 문장 끝을 잘라내지 않고 5초 안에 맞춥니다."""
    if voice not in VOICES:
        raise ValueError('지원하지 않는 목소리입니다.')
    folder = Path(folder)
    clips = []
    sources = []
    try:
        for i, text in enumerate(captions):
            path = folder / f'narration{i}.mp3'
            asyncio.run(synthesize(text, voice, path))
            source = AudioFileClip(str(path))
            sources.append(source)
            # 지나치게 빨라지면 신뢰감과 이해도가 떨어지므로 문장을 줄이도록 안내합니다.
            factor = max(1, source.duration / 4.4)
            if factor > 1.35:
                raise ValueError(f'{i + 1}번 자막을 읽으면 5초를 넘습니다. 자연스럽게 들리도록 문장을 줄여 주세요.')
            clip = source.with_speed_scaled(factor=factor) if factor > 1 else source
            clips.append(clip.with_start(i * 5 + 0.3))
        return CompositeAudioClip(clips).with_duration(15), sources
    except BaseException:
        for source in sources:
            source.close()
        raise
