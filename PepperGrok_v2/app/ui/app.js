const conversation = document.getElementById("conversation");
const promptForm = document.getElementById("prompt-form");
const promptField = document.getElementById("prompt");
const modeSelect = document.getElementById("mode");
const rememberForm = document.getElementById("remember-form");
const memoryText = document.getElementById("memory-text");
const memoryCategory = document.getElementById("memory-category");
const memoriesContainer = document.getElementById("memories");
const statusLabel = document.getElementById("online-status");

async function fetchStatus() {
  try {
    const res = await fetch("/status");
    if (!res.ok) throw new Error("status failed");
    const data = await res.json();
    statusLabel.textContent = data.grok_online ? "Online" : "Offline";
  } catch (error) {
    statusLabel.textContent = "Status unavailable";
  }
}

async function loadMemories() {
  const res = await fetch("/memories?limit=15");
  if (!res.ok) return;
  const data = await res.json();
  memoriesContainer.innerHTML = "";
  data.memories.forEach((memory) => {
    const el = document.createElement("div");
    el.className = "memory-item";
    el.textContent = `(${memory.category}) ${memory.text}`;
    memoriesContainer.appendChild(el);
  });
  const bias = document.createElement("div");
  bias.className = "memory-item";
  bias.textContent = `Emotional bias: ${data.emotional_bias.toFixed(2)}`;
  memoriesContainer.appendChild(bias);
}

function addMessage(role, text) {
  const wrapper = document.createElement("div");
  wrapper.className = "message";
  wrapper.innerHTML = `<strong>${role}:</strong> ${text}`;
  conversation.appendChild(wrapper);
  conversation.scrollTop = conversation.scrollHeight;
}

promptForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const prompt = promptField.value.trim();
  if (!prompt) return;
  addMessage("You", prompt);
  promptField.value = "";

  const body = {
    prompt,
    mode: modeSelect.value,
  };

  const res = await fetch("/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    addMessage("Pepper", "I hit a snag reaching my mind.");
    return;
  }
  const data = await res.json();
  addMessage("Pepper", data.response);
});

rememberForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = memoryText.value.trim();
  if (!text) return;
  const body = { text, category: memoryCategory.value };

  const res = await fetch("/remember", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (res.ok) {
    memoryText.value = "";
    await loadMemories();
  }
});

fetchStatus();
loadMemories();
