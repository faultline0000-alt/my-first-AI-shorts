"""python -m unittest discover -s tests -v"""
import io
import unittest
from unittest.mock import patch
from PIL import Image
import app as web
from make_video import caption_image, find_font


class WebTests(unittest.TestCase):
    def setUp(self):
        self.client = web.app.test_client()

    def payload(self):
        data = {'highlights': 'AI, 미래'}
        for i in range(3):
            image = io.BytesIO()
            Image.new('RGB', (80, 100), 'blue').save(image, format='PNG')
            image.seek(0)
            data[f'photo{i}'] = (image, f'{i}.png')
            data[f'caption{i}'] = f'AI와 미래 {i}'
        return data

    def test_home_and_assets(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('장면 3', response.text)
        with self.client.get('/static/app.js') as asset:
            self.assertEqual(asset.status_code, 200)

    def test_missing_photo(self):
        self.assertEqual(self.client.post('/api/render', data={}).status_code, 400)

    def test_bad_image_releases_lock(self):
        data = self.payload()
        data['photo1'] = (io.BytesIO(b'not an image'), 'bad.jpg')
        response = self.client.post('/api/render', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(web.render_lock.locked())

    def test_busy(self):
        web.render_lock.acquire()
        try:
            self.assertEqual(self.client.post('/api/render', data=self.payload()).status_code, 409)
        finally:
            web.render_lock.release()

    def test_custom_inputs_and_download(self):
        def render(paths, captions, output, **kwargs):
            self.assertEqual(len(paths), 3)
            self.assertEqual(captions[2], 'AI와 미래 2')
            self.assertEqual(kwargs['highlight_words'], ('AI', '미래'))
            output.write_bytes(b'video-test')
            return output
        with patch.object(web, 'render_video', side_effect=render):
            response = self.client.post('/api/render', data=self.payload())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'video-test')
        self.assertEqual(response.mimetype, 'video/mp4')
        self.assertIn('ai_shorts.mp4', response.headers['Content-Disposition'])
        self.assertFalse(web.render_lock.locked())

    def test_highlight_survives_line_wrap(self):
        import numpy as np
        image = caption_image('사진으로 나만의 숏츠 만들기', find_font(), ('숏츠',))
        self.assertTrue(np.any(np.all(image[:, :, :3] == (255, 220, 40), axis=2)))

    def test_unbroken_caption_fits(self):
        image = caption_image('가나다라마바사아자차카타파하가나다라마바사아자차카타파하', find_font())
        self.assertEqual(image.shape, (420, 1080, 4))
        self.assertFalse(image[:, :35, 3].any())
        self.assertFalse(image[:, 1046:, 3].any())


if __name__ == '__main__':
    unittest.main()
