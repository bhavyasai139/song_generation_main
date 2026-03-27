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

let intervalStart = 0;
let intervalEnd = 30;
let isPlaying = false;
let isDragging = null;
let file;

playButton.addEventListener("click", () => loadFile());
addFileButton.addEventListener("click", () => fileInput.click());

function loadFile() {
    file = fileInput.files[0];
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
  
    // Avoid duplicate entries
    const existingItems = fileList.querySelectorAll(".fileItem span");
    for (const item of existingItems) {
      if (item.textContent === file.name) {
        // message.textContent = "File is already loaded.";
        return;
      }
    }
  
    const fileItem = document.createElement("div");
    fileItem.className = "fileItem";
    fileItem.innerHTML = `
        <span>${file.name}</span>
        <button class="clipButton" onclick="extractClip('${file.name}')">Next</button>
    `;
    fileList.appendChild(fileItem);
  
    audioPlayer.addEventListener("loadedmetadata", () => {
      intervalEnd = Math.min(30, audioPlayer.duration);
      updateMarkers();
    });
  }
  
playPauseButton.addEventListener("click", () => {
  if (isPlaying) {
    audioPlayer.pause();
    playPauseButton.textContent = "Play";
  } else {
    if (intervalStart === intervalEnd)
      intervalEnd = Math.min(30, audioPlayer.duration);
    audioPlayer.currentTime = intervalStart;
    audioPlayer.play();
    playPauseButton.textContent = "Pause";
  }
  isPlaying = !isPlaying;
});

startMarker.addEventListener("mousedown", () => (isDragging = "start"));
endMarker.addEventListener("mousedown", () => (isDragging = "end"));

document.addEventListener("mousemove", (event) => {
  if (!isDragging) return;

  const rect = seekBarContainer.getBoundingClientRect();
  const position = Math.max(
    0,
    Math.min(1, (event.clientX - rect.left) / rect.width)
  );
  const time = position * audioPlayer.duration;

  if (isDragging === "start") {
    intervalStart = Math.min(time, intervalEnd - 30);
  } else if (isDragging === "end") {
    intervalEnd = Math.max(time, intervalStart + 30);
  }

  updateMarkers();
});

document.addEventListener("mouseup", () => (isDragging = null));

function updateMarkers() {
  const duration = audioPlayer.duration;
  const startPercent = (intervalStart / duration) * 100;
  const endPercent = (intervalEnd / duration) * 100;

  startMarker.style.left = `${startPercent}%`;
  endMarker.style.left = `${endPercent}%`;
  updateProgressBar();
}

audioPlayer.addEventListener("timeupdate", () => {
  const currentTime = audioPlayer.currentTime;

  if (currentTime >= intervalEnd) {
    audioPlayer.pause();
    playPauseButton.textContent = "Play";
  }

  updateProgressBar();
  timeDisplay.textContent = `${formatTime(currentTime)} / ${formatTime(
    audioPlayer.duration
  )}`;
  intervalDisplay.textContent = `Interval: ${formatTime(
    intervalStart
  )} - ${formatTime(intervalEnd)}`;
});

function updateProgressBar() {
  const duration = audioPlayer.duration;
  const startPercent = (intervalStart / duration) * 100;
  const endPercent = (intervalEnd / duration) * 100;

  progressBar.style.left = `${startPercent}%`;
  progressBar.style.width = `${endPercent - startPercent}%`;
}


function extractClip(fileName) {
  ctrfunction3();
  const reader = new FileReader();

  reader.onload = async () => {
    const base64Audio = reader.result.split(",")[1]; // Extract Base64 content

    const payload = {
      filename: file.name,
      content_type: file.type,
      audio_data: base64Audio,
      start: intervalStart,
      end: intervalEnd,
    };

    const url = `http://127.0.0.1:5000/process`;
    try {
      const response = await fetch(url, {
        method: "POST",
        body: JSON.stringify(payload),
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }

      const data = await response.json();

      if (data.error) {
        document.getElementById("message").textContent = `Error: ${data.error}`;
      } else {
        // Update the UI with the response message and output
        text[3]="Yayy!! It's a "+data.output+" song";
        // document.getElementById("message").textContent = `Yayy!! ${data.message}`;
        // document.getElementById("finaloutput").textContent = `Genre:::::::: ${data.output}`;
        ctrfunction4();
      }
    } catch (error) {
      console.error("Error during fetch:", error);
      document.getElementById("message").textContent = "An error occurred while processing your request.";
    }
  };

  reader.readAsDataURL(file); // Trigger file reading and Base64 conversion
}

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}
