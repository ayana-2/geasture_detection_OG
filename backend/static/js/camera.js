const video = document.getElementById('video');
const output = document.getElementById('letterOutput');

// Access webcam
navigator.mediaDevices.getUserMedia({ video: true })
.then(stream => {
    video.srcObject = stream;
})
.catch(err => {
    alert("Could not access camera: " + err);
});

// Capture frame and send to backend every 500ms
setInterval(() => {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataURL = canvas.toDataURL('image/jpeg');

    fetch('/api/detect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: dataURL })
    })
    .then(res => res.json())
    .then(data => {
        if(data.success){
            output.innerText = `Detected Letter: ${data.letter} (${data.confidence*100}%)`;
        }
    })
    .catch(err => console.error(err));

}, 500);
