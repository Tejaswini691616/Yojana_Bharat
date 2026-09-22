// PATH: GovScheme/static/js/chatbot.js
(function () {
  const fab = document.getElementById("sgChatFab");
  const panel = document.getElementById("sgChatPanel");
  const closeBtn = document.getElementById("sgChatClose");
  const clearBtn = document.getElementById("sgChatClear");
  const messagesEl = document.getElementById("sgChatMessages");
  const inputEl = document.getElementById("sgChatInput");
  const sendBtn = document.getElementById("sgChatSend");
  const micBtn = document.getElementById("sgChatMic");
  const langSelect = document.getElementById("sgChatLanguage");
  const statusEl = document.getElementById("sgChatStatus");

  if (!fab) return; // widget not on this page

  let mediaRecorder = null;
  let audioChunks = [];

  fab.addEventListener("click", () => panel.classList.toggle("open"));
  closeBtn.addEventListener("click", () => panel.classList.remove("open"));
  clearBtn.addEventListener("click", () => { messagesEl.innerHTML = ""; });

  function addBubble(text, sender) {
    const div = document.createElement("div");
    div.className = "sg-chat-bubble " + sender;
    div.textContent = text;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  async function sendMessage(text) {
    if (!text.trim()) return;
    addBubble(text, "user");
    inputEl.value = "";
    statusEl.textContent = "Thinking...";
    try {
      const resp = await fetch("/api/chat/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, language: langSelect.value }),
      });
      const data = await resp.json();
      statusEl.textContent = "";
      if (data.reply) {
        addBubble(data.reply, "bot");
        playTts(data.reply);
      } else {
        addBubble("Something went wrong. Please try again.", "bot");
      }
    } catch (err) {
      statusEl.textContent = "";
      addBubble("Network error. Please try again.", "bot");
    }
  }

  sendBtn.addEventListener("click", () => sendMessage(inputEl.value));
  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage(inputEl.value);
  });

  async function playTts(text) {
    try {
      const resp = await fetch("/api/chat/voice-output", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, language: langSelect.value }),
      });
      if (resp.status !== 200) return; // voice not configured -> silently keep text-only
      const blob = await resp.blob();
      const audio = new Audio(URL.createObjectURL(blob));
      audio.play();
    } catch (err) {
      // text response already shown; audio is optional
    }
  }

  micBtn.addEventListener("click", async () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
      return;
    }
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      statusEl.textContent = "Microphone not supported in this browser.";
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunks = [];
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
      mediaRecorder.onstart = () => { statusEl.textContent = "Recording... click mic to stop."; micBtn.classList.add("text-danger"); };
      mediaRecorder.onstop = async () => {
        micBtn.classList.remove("text-danger");
        statusEl.textContent = "Processing audio...";
        const blob = new Blob(audioChunks, { type: "audio/webm" });
        const form = new FormData();
        form.append("audio", blob, "voice.webm");
        form.append("language", langSelect.value);
        try {
          const resp = await fetch("/api/chat/voice-input", { method: "POST", body: form });
          const data = await resp.json();
          if (resp.status === 200 && data.text) {
            statusEl.textContent = "";
            sendMessage(data.text);
          } else {
            statusEl.textContent = "";
            addBubble(data.message || "Microphone permission is required for voice input. You can continue using text chat.", "bot");
          }
        } catch (err) {
          statusEl.textContent = "";
          addBubble("Sorry, I couldn't understand the audio. Please try again or type your question.", "bot");
        }
      };
      mediaRecorder.start();
    } catch (err) {
      statusEl.textContent = "Microphone permission is required for voice input. You can continue using text chat.";
    }
  });
})();
