"""네트워크 대신 시험 신호로 오디오 배치와 길이 처리를 검사합니다."""
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch
import numpy as np
from narration import create_narration
import app as web


def fake_speech(seconds):
    async def synthesize(text, voice, output):
        rate = 24000
        samples = (np.sin(np.arange(int(rate * seconds)) * 2 * np.pi * 440 / rate)
                   * 5000).astype('<i2')
        with wave.open(str(output), 'wb') as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(rate)
            audio.writeframes(samples.tobytes())
    return synthesize


class NarrationTests(unittest.TestCase):
    def test_audio_is_placed_in_each_scene(self):
        with tempfile.TemporaryDirectory() as folder, patch('narration.synthesize', fake_speech(1)):
            audio, sources = create_narration(['하나', '둘', '셋'], 'male', folder)
            try:
                self.assertEqual(audio.duration, 15)
                for t in (0.1, 5.1, 10.1, 14.9):
                    self.assertTrue(np.allclose(audio.get_frame(t), 0))
                for t in (.3007, 5.3007, 10.3007):
                    self.assertTrue(np.any(abs(audio.get_frame(t)) > .01))
            finally:
                audio.close()
                for source in sources:
                    source.close()

    def test_slow_audio_is_sped_up_without_cutting(self):
        with tempfile.TemporaryDirectory() as folder, patch('narration.synthesize', fake_speech(5)):
            audio, sources = create_narration(['하나', '둘', '셋'], 'female', folder)
            try:
                self.assertAlmostEqual(audio.clips[-1].end, 14.7, places=1)
            finally:
                audio.close()
                for source in sources:
                    source.close()

    def test_overlong_narration_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder, patch('narration.synthesize', fake_speech(8)):
            with self.assertRaisesRegex(ValueError, '1번 자막'):
                create_narration(['긴 문장'] * 3, 'male', folder)

    def test_windows_voice_uses_stdin_for_user_text(self):
        import json
        import narration
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'voice.wav'
            output.write_bytes(b'test')
            with patch.object(narration.sys, 'platform', 'win32'), patch.object(narration.subprocess, 'run') as run:
                run.return_value.returncode = 0
                narration.synthesize_windows('한글 $변수; AI', output)
                self.assertEqual(json.loads(run.call_args.kwargs['input'])['text'], '한글 $변수; 에이아이')
                self.assertNotIn('한글', run.call_args.args[0][-1])

    def test_windows_missing_voice_has_installation_help(self):
        import narration
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(narration.sys, 'platform', 'win32'), patch.object(narration.subprocess, 'run') as run:
                run.return_value.returncode = 1
                with self.assertRaisesRegex(ValueError, '언어 옵션'):
                    narration.synthesize_windows('한국어', Path(folder) / 'voice.wav')

    def test_invalid_voice_is_rejected(self):
        from test_web import WebTests
        with web.app.test_client() as client:
            data = WebTests().payload()
            data['voice'] = 'unknown'
            self.assertEqual(client.post('/api/render', data=data).status_code, 400)


if __name__ == '__main__':
    unittest.main()
