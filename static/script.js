const chatBox = document.getElementById("chatBox");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");

// মেসেজ স্ক্রিনে যোগ করার ফাংশন
function addMessage(text, sender, extra = "") {
  const div = document.createElement("div");
  div.className = "msg " + sender;
  div.textContent = text;
  if (extra) {
    const small = document.createElement("small");
    small.textContent = extra;
    div.appendChild(small);
  }
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
  return div;
}

// সার্ভারে মেসেজ পাঠানো
async function sendMessage(text) {
  text = text.trim();
  if (!text) return;

  addMessage(text, "user");
  userInput.value = "";
  const typing = addMessage("Typing...", "bot");

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    });
    const data = await response.json();
    typing.remove();
    const extra = data.matched ? `Matched: "${data.matched}" (${data.score})` : "";
    addMessage(data.answer, "bot", extra);
  } catch (error) {
    typing.remove();
    addMessage("Server error. Is app.py running?", "bot");
  }
}

sendBtn.addEventListener("click", () => sendMessage(userInput.value));
userInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage(userInput.value);
});
document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => sendMessage(chip.textContent));
});

// শুরুর স্বাগত বার্তা
addMessage("Hi! 👋 I am Riya assistant. Ask me anything about orders, delivery, payment or returns.", "bot");