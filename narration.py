"""한국어 합성 음성을 만들고 장면별로 배치합니다."""
import asyncio
import os
import json
import subprocess
import sys
from pathlib import Path

import edge_tts
from moviepy import AudioFileClip, CompositeAudioClip

VOICES = {
    'male': 'ko-KR-InJoonNeural',
    'female': 'ko-KR-SunHiNeural',
}


WINDOWS_SPEECH_SCRIPT = r"""
$ErrorActionPreference = 'Stop'
$data = [Console]::In.ReadToEnd() | ConvertFrom-Json
Add-Type -AssemblyName System.Speech
$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $voice = $speaker.GetInstalledVoices() | Where-Object {
        $_.Enabled -and $_.VoiceInfo.Culture.TwoLetterISOLanguageName -eq 'ko'
    } | Select-Object -First 1
    if ($null -eq $voice) { throw 'KOREAN_VOICE_NOT_INSTALLED' }
    $speaker.SelectVoice($voice.VoiceInfo.Name)
    $speaker.Rate = -1
    $speaker.Volume = 100
    $speaker.SetOutputToWaveFile([string]$data.output)
    $speaker.Speak([string]$data.text)
    $speaker.SetOutputToNull()
} finally {
    $speaker.Dispose()
}
"""


def synthesize_windows(text, output):
    """외부 서비스 없이 설치된 한국어 Windows 목소리를 사용합니다."""
    if sys.platform != 'win32':
        raise ValueError('Windows 기본 음성은 Windows PC에서만 사용할 수 있습니다.')
    try:
        result = subprocess.run(
            ['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', WINDOWS_SPEECH_SCRIPT],
            input=json.dumps({'text': text.replace('AI', '에이아이'),
                              'output': str(Path(output).resolve())}, ensure_ascii=True),
            capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=45)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ValueError('Windows 음성 실행에 실패했습니다. PowerShell 실행 가능 여부를 확인해 주세요.') from error
    if result.returncode != 0 or not Path(output).is_file():
        raise ValueError('Windows 한국어 음성을 사용할 수 없습니다. Windows 설정 → 시간 및 언어 → '
                         '언어 및 지역 → 한국어의 언어 옵션에서 음성 기능을 설치해 주세요. '
                         '설치 후에도 실패하면 실행 창의 오류를 확인해 주세요.')


async def synthesize(text, voice, output):
    if voice == 'windows':
        await asyncio.to_thread(synthesize_windows, text, output)
        return
    try:
        communication = edge_tts.Communicate(
            text.replace('AI', '에이아이'), VOICES[voice], rate='-5%',
            pitch='-2Hz' if voice == 'male' else '+0Hz',
            proxy=os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy'),
            connect_timeout=15, receive_timeout=30)
        await communication.save(str(output))
    except Exception as error:
        status = getattr(error, 'status', None)
        detail = f'HTTP {status}, ' if status is not None else ''
        raise ValueError('온라인 음성 서비스가 연결을 받아들이지 못했습니다. '
                         '목소리를 "Windows 기본 한국어 (오프라인)"로 바꾸면 외부 서비스 없이 제작할 수 있습니다. '
                         f'({detail}{type(error).__name__})') from error


def create_narration(captions, voice, folder):
    """각 문장을 0.3초 뒤에 읽고, 문장 끝을 잘라내지 않고 5초 안에 맞춥니다."""
    if voice not in (*VOICES, 'windows'):
        raise ValueError('지원하지 않는 목소리입니다.')
    folder = Path(folder)
    clips = []
    sources = []
    try:
        for i, text in enumerate(captions):
            extension = 'wav' if voice == 'windows' else 'mp3'
            path = folder / f'narration{i}.{extension}'
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
