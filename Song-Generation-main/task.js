
let intervalStart = 0; // Fixed starting interval at 30 seconds
let intervalEnd = 30; // Allow interval to start from 30 seconds onward
let isPlaying = false;
let isDragging = null;
const fileInput = document.getElementById("fileInput");
const playButton = document.getElementById("playButton");
const addFileButton = document.getElementById("addFileButton");
const audioPlayer = document.getElementById("audioPlayer");
const playerContainer = document.getElementById("playerContainer");
const seekBarContainer = document.getElementById("seekBarContainer");
const progressBar = document.getElementById("progressBar");
const startMarker = document.getElementById("startMarker");
const endMarker = document.getElementById("endMarker");
const playPauseButton = document.getElementById("playPauseButton");
const timeDisplay = document.getElementById("timeDisplay");
const intervalDisplay = document.getElementById("intervalDisplay");
const message = document.getElementById("message");
const fileList = document.getElementById("fileList");

playButton.addEventListener("click", () => loadFile());
addFileButton.addEventListener("click", () => fileInput.click());

function loadFile() {
  const file = fileInput.files[0];
  if (!file) {
    message.textContent = "Please select a music file.";
    return;
  }

  if (!file.type.startsWith("audio/")) {
    message.textContent = "Invalid file type. Please upload an audio file.";
    return;
  }

  message.textContent = "";
  audioPlayer.src = URL.createObjectURL(file);
  playerContainer.style.display = "block";

  // Ensure there's only one extract clip button
  const existingClipButton = fileList.querySelector(`button[data-file="${file.name}"]`);
  if (existingClipButton) {
    return; // Do not add a new button if it already exists
  }

  const fileItem = document.createElement("div");
  fileItem.className = "fileItem";
  fileItem.innerHTML = `
                  <span>${file.name}</span>
                  <button class="clipButton" data-file="${file.name}" onclick="extractClip('${file.name}')">Extract Clip</button>
              `;
  fileList.appendChild(fileItem);

  audioPlayer.addEventListener("loadedmetadata", () => {
    intervalEnd = Math.min(intervalStart + 30, audioPlayer.duration); // Ensure intervalStart is respected
    updateMarkers();
  });
}

playPauseButton.addEventListener("click", () => {
  if (isPlaying) {
    audioPlayer.pause();
    playPauseButton.textContent = "Play";
  } else {
    audioPlayer.currentTime = intervalStart;
    audioPlayer.play();
    playPauseButton.textContent = "Pause";
  }
  isPlaying = !isPlaying;
});

audioPlayer.addEventListener("timeupdate", () => {
  const currentTime = audioPlayer.currentTime;

  if (currentTime >= intervalEnd) {
    audioPlayer.pause();
    playPauseButton.textContent = "Play";
    isPlaying = false;
  }

  updateProgressBar();
  timeDisplay.textContent = `${formatTime(currentTime)} / ${formatTime(audioPlayer.duration)}`;
  intervalDisplay.textContent = `Interval: ${formatTime(intervalStart)} - ${formatTime(intervalEnd)}`;
});

function updateProgressBar() {
  const duration = audioPlayer.duration || 1;
  const currentPercent = (audioPlayer.currentTime / duration) * 100;
  progressBar.style.width = `${currentPercent}%`;
}

function updateMarkers() {
  const duration = audioPlayer.duration || 1;
  const startPercent = (intervalStart / duration) * 100;
  const endPercent = (intervalEnd / duration) * 100;

  startMarker.style.left = `${startPercent}%`;
  endMarker.style.left = `${endPercent}%`;
}

function extractClip(fileName) {
  const formData = new FormData();
  formData.append("audioFile", fileName);
  formData.append("start", intervalStart);
  formData.append("end", intervalEnd);
  console.log(fileName, intervalStart, intervalEnd);

  const url = `http://127.0.0.1:5000/process?start=${intervalStart}&end=${intervalEnd}&fileName=${fileName}`;
  fetch(url)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      if (data.error) {
        document.getElementById("finalmessage").textContent = data.error;
      } else {
        document.getElementById("finalmessage").textContent = data.message;
        document.getElementById("finaloutput").textContent = data.output;
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      document.getElementById("finalmessage").textContent = "An error occurred. Please try again.";
    });
}

document.addEventListener("mousedown", (event) => {
  if (event.target === startMarker) {
    isDragging = "start";
  } else if (event.target === endMarker) {
    isDragging = "end";
  }
});

document.addEventListener("mousemove", (event) => {
  if (!isDragging) return;

  const rect = seekBarContainer.getBoundingClientRect();
  const position = Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width));
  const newTime = position * audioPlayer.duration;

  if (isDragging === "start") {
    intervalStart = Math.max(30, Math.min(newTime, intervalEnd - 30)); // Ensure minimum 30 seconds interval
  } else if (isDragging === "end") {
    intervalEnd = Math.max(intervalStart + 30, Math.min(newTime, audioPlayer.duration)); // Ensure minimum 30 seconds interval
  }

  updateMarkers();
  updateProgressBar();
});

document.addEventListener("mouseup", () => {
  isDragging = null;
});

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}





