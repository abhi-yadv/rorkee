const video = document.querySelector('#camera');
const startButton = document.querySelector('#start-camera');
const captureButton = document.querySelector('#capture');
const stopButton = document.querySelector('#stop-camera');
const status = document.querySelector('#camera-status');
const historyList = document.querySelector('#history');
const historyKey = 'expression-demo-history';
let stream;
let history;
try { history = JSON.parse(sessionStorage.getItem(historyKey) || '[]'); }
catch { history = []; }
if (!Array.isArray(history)) history = [];

function renderHistory(labels = []) {
  if (labels.length) {
    history.unshift({ time: new Date().toLocaleTimeString(), labels: labels.join(', ') });
    history = history.slice(0, 10);
    try { sessionStorage.setItem(historyKey, JSON.stringify(history)); } catch { /* storage optional */ }
  }
  historyList.replaceChildren();
  for (const item of history) {
    const row = document.createElement('li');
    row.textContent = `${item.time}: ${item.labels}`;
    historyList.append(row);
  }
}
renderHistory(JSON.parse(document.querySelector('#initial-predictions').textContent));

function stopCamera() {
  stream?.getTracks().forEach(track => track.stop());
  stream = undefined;
  video.srcObject = null;
  video.hidden = true;
  startButton.disabled = false;
  stopButton.disabled = true;
  captureButton.disabled = true;
}
startButton.addEventListener('click', async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    video.srcObject = stream;
    video.hidden = false;
    startButton.disabled = true;
    stopButton.disabled = false;
    await video.play();
    captureButton.disabled = false;
    status.textContent = 'Camera ready. Capture a frame when you are ready.';
  } catch {
    stopCamera();
    status.textContent = 'Camera unavailable. Allow camera access on localhost or HTTPS, or upload an image.';
  }
});
stopButton.addEventListener('click', () => { stopCamera(); status.textContent = 'Camera stopped.'; });
window.addEventListener('pagehide', stopCamera);
captureButton.addEventListener('click', async () => {
  captureButton.disabled = true;
  status.textContent = 'Analyzing captured frame...';
  try {
    if (!video.videoWidth) throw new Error('Wait for the camera preview before capturing.');
    const canvas = document.createElement('canvas');
    const scale = Math.min(1, 1280 / video.videoWidth);
    canvas.width = Math.round(video.videoWidth * scale);
    canvas.height = Math.round(video.videoHeight * scale);
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.85));
    if (!blob) throw new Error('The camera frame could not be captured.');
    const form = new FormData();
    form.append('image', blob, 'capture.jpg');
    const response = await fetch('/analyze?format=json', { method: 'POST', body: form });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Analysis failed. Try another image.');
    const result = document.querySelector('#camera-result');
    result.src = data.image_url;
    result.hidden = false;
    status.textContent = data.no_face ? 'No face detected.' : data.predictions.map(p => `${p.emotion}: ${Math.round(p.confidence * 100)}%`).join(' | ');
    renderHistory(data.predictions.map(p => `${p.emotion} (${Math.round(p.confidence * 100)}%)`));
  } catch (error) { status.textContent = error.message; }
  finally { captureButton.disabled = !stream; }
});
