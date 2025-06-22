let recorder;        // Recorder.js Recorder instance
let audioContext;   // Web Audio API context
let gumStream;      // stream from getUserMedia

const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const statusP = document.getElementById('status');

startBtn.onclick = startRecording;
stopBtn.onclick = stopRecording;

async function startRecording() {
  statusP.innerText = 'Requesting microphone...';
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    gumStream = stream;
    const input = audioContext.createMediaStreamSource(stream);
    recorder = new Recorder(input, { numChannels: 1 });
    recorder.record();
    statusP.innerText = 'Recording...';
    startBtn.disabled = true;
    stopBtn.disabled = false;
  } catch (err) {
    console.error("getUserMedia error:", err);
    statusP.innerText = 'Microphone access denied or error.';
  }
}

function stopRecording() {
  if (!recorder) return;
  statusP.innerText = 'Stopping...';
  stopBtn.disabled = true;
  recorder.stop();

  // Stop the microphone stream
  gumStream.getTracks().forEach(track => track.stop());

  // Export WAV blob
  recorder.exportWAV(async function(blob) {
    // Optionally play back to verify:
    // let url = URL.createObjectURL(blob);
    // new Audio(url).play();

    // Prepare upload
    const formData = new FormData();
    formData.append('audio', blob, 'recorded.wav');

    statusP.innerText = 'Uploading...';
    try {
      const response = await fetch('/upload', {
        method: 'POST',
        body: formData
      });
      if (!response.ok) {
        const errData = await response.json().catch(()=>({}));
        throw new Error(errData.details || response.statusText);
      }
      const result = await response.json();
      // Display results
      document.getElementById('transcript').innerText = "Transcript: " + (result.transcript||'');
      document.getElementById('claim').innerText = "Claim: " + (result.claim||'');
      document.getElementById('validity').innerText = "Validity: " + (result.validity||'');
      document.getElementById('question').innerText = "Question: " + (result.question||'');
      let sourcesText = "";
      if (result.sources && result.sources.length >= 2) {
        sourcesText = `Source: ${result.sources[0]}\nReason: ${result.sources[1]}`;
      } else if (result.sources) {
        sourcesText = result.sources.join("\n");
      }
      document.getElementById('sources').innerText = sourcesText;
      statusP.innerText = 'Finished.';
    } catch (err) {
      console.error("Upload error:", err);
      statusP.innerText = 'Upload error: ' + err.message;
    }
    // Clean up recorder for next time
    recorder.clear();
    recorder = null;
    startBtn.disabled = false;
  });
}
