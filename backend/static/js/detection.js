const video = document.getElementById('video');
const letterEl = document.getElementById('letter');
const confEl = document.getElementById('confidence');

// Access webcam
navigator.mediaDevices.getUserMedia({ video: true })
.then(stream => {
    video.srcObject = stream;
    detectLoop();
})
.catch(err => console.error("Camera error:", err));

// Mock detection loop
function detectLoop() {
    setInterval(async () => {
        const response = await fetch('/api/detect', { method: 'POST' });
        const data = await response.json();
        letterEl.textContent = data.letter;
        confEl.textContent = data.confidence;
    }, 1000); // every 1 second
}

// Logout
function logout() {
    window.location.href = '/logout';
}
