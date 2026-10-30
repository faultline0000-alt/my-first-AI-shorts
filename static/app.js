const form = document.querySelector('#shorts-form');
const statusText = document.querySelector('#status');
const button = document.querySelector('#make-button');
let videoUrl;
for (const input of document.querySelectorAll('input[type=file]')) {
  let previewUrl;
  input.addEventListener('change', () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    const label = document.querySelector(`label[for="${input.id}"]`);
    const image = label.querySelector('img');
    const file = input.files[0];
    image.hidden = !file;
    label.querySelector('.upload-label').hidden = !!file;
    if (file) {
      previewUrl = URL.createObjectURL(file);
      image.src = previewUrl;
    }
  });
}
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const files = [...form.querySelectorAll('input[type=file]')].map(input => input.files[0]);
  if (files.reduce((sum, file) => sum + (file?.size || 0), 0) > 31 * 1024 * 1024) {
    statusText.textContent = '사진 전체 용량을 31MB 이하로 줄여 주세요.';
    return;
  }
  button.disabled = true;
  button.textContent = '영상 제작 중…';
  statusText.textContent = '사진을 업로드하고 영상을 만드는 중입니다. 컴퓨터 성능에 따라 몇 분 걸릴 수 있습니다.';
  const result = document.querySelector('#result');
  result.hidden = true;
  try {
    const response = await fetch('/api/render', { method: 'POST', body: new FormData(form) });
    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.error || '서버 연결 또는 업로드에 실패했습니다. 잠시 후 다시 시도해 주세요.');
    }
    const blob = await response.blob();
    if (videoUrl) URL.revokeObjectURL(videoUrl);
    videoUrl = URL.createObjectURL(blob);
    document.querySelector('#result-video').src = videoUrl;
    document.querySelector('#download').href = videoUrl;
    result.hidden = false;
    statusText.textContent = '완료! 아래에서 영상을 확인하고 다운로드하세요.';
    result.scrollIntoView({ behavior: 'smooth', block: 'start' });
  } catch (error) {
    statusText.textContent = error.message;
  } finally {
    button.disabled = false;
    button.textContent = '15초 영상 만들기 →';
  }
});
