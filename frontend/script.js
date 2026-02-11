const API_BASE = "http://127.0.0.1:5000"; // same-origin

// DOM
const titleInput = document.getElementById("titleInput");
const contentInput = document.getElementById("contentInput");
const createForm = document.getElementById("createForm");
const entriesList = document.getElementById("entriesList");
const refreshBtn = document.getElementById("refreshBtn");
const summarizeBtn = document.getElementById("summarizeBtn");
const summaryBox = document.getElementById("summaryBox");
const summaryText = document.getElementById("summaryText");
const loadingText = document.getElementById("loadingText");
const periodSelect = document.getElementById("periodSelect");

let taskId = null;

// ---------- Entries ----------
async function fetchEntries(){
  const res = await fetch(`${API_BASE}/entries`);
  const data = await res.json();
  renderEntries(data);
}

async function createEntry(title, content){
  await fetch(`${API_BASE}/entries`,{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({title,content})
  });
  fetchEntries();
}

// ---------- AI Summary ----------
summarizeBtn.onclick = async () => {
  const period = periodSelect.value;

  summaryBox.classList.remove('hidden');
  loadingText.classList.remove('hidden');
  summaryText.innerHTML = '';

  const res = await fetch(`${API_BASE}/entries/summarize/${period}`,{method:'POST'});
  const data = await res.json();

  taskId = data.task_id;
  pollTask();
};

async function pollTask(){
  if(!taskId) return;

  const interval = setInterval(async ()=>{
    const res = await fetch(`${API_BASE}/tasks/${taskId}`);
    const data = await res.json();

    if(data.state === 'SUCCESS'){
      loadingText.classList.add('hidden');
      // Markdown render
      summaryText.innerHTML = marked.parse(data.summary);
      clearInterval(interval);
    }

    if(data.state === 'FAILURE'){
      loadingText.innerText = 'Error generating summary';
      clearInterval(interval);
    }
  },2000);
}

// ---------- UI ----------
function renderEntries(entries){
  entriesList.innerHTML='';
  entries.forEach(e=>{
    const div=document.createElement('div');
    // Updated with hover animation classes
    div.className='entry-item bg-gray-950/50 border border-gray-800 rounded-xl p-4 cursor-pointer fade-in';
    div.innerHTML=`
      <div class="flex justify-between items-start mb-2">
        <h3 class="font-semibold text-base">${e.title}</h3>
        <span class="text-xs text-gray-500">${new Date(e.created_at || Date.now()).toLocaleDateString()}</span>
      </div>
      <p class="text-gray-400 text-sm line-clamp-2">${e.content}</p>
    `;
    entriesList.appendChild(div);
  });
}

createForm.onsubmit = (e)=>{
  e.preventDefault();
  createEntry(titleInput.value, contentInput.value);
  titleInput.value='';
  contentInput.value='';
};

refreshBtn.onclick = fetchEntries;
fetchEntries();

// ================= CHATBOT (RAG) =================
const chatToggle = document.getElementById("chatToggle");
const chatPopup = document.getElementById("chatPopup");
const closeChat = document.getElementById("closeChat");
const chatInput = document.getElementById("chatInput");
const sendChat = document.getElementById("sendChat");
const chatMessages = document.getElementById("chatMessages");

// Updated with animation class
chatToggle.onclick = () => {
  chatPopup.classList.toggle("hidden");
  if (!chatPopup.classList.contains("hidden")) {
    chatPopup.classList.add("flex", "show");
  } else {
    chatPopup.classList.remove("flex", "show");
  }
};

closeChat.onclick = () => {
  chatPopup.classList.add("hidden");
  chatPopup.classList.remove("flex", "show");
};

function addMessage(text, type="user") {
  const div = document.createElement("div");
  // Updated with better chat bubble styling
  div.className = `flex ${type === "user" ? "justify-end" : "justify-start"} fade-in`;
  
  const bubble = document.createElement("div");
  bubble.className = type === "user"
    ? "bg-indigo-600 rounded-lg px-3 py-2 max-w-[80%]"
    : "bg-gray-800 rounded-lg px-3 py-2 max-w-[80%]";
  bubble.innerHTML = `<p class="text-sm">${text}</p>`;
  
  div.appendChild(bubble);
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

sendChat.onclick = sendMessage;
chatInput.addEventListener("keydown", e => {
  if (e.key === "Enter") sendMessage();
});

async function sendMessage() {
  const msg = chatInput.value.trim();
  if (!msg) return;

  addMessage(msg, "user");
  chatInput.value = "";

  try {
    const res = await fetch("http://127.0.0.1:5000/rag/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: msg,
        top_k: 5
      })
    });

    const data = await res.json();
    addMessage(data.answer || "No answer", "bot");

  } catch (err) {
    addMessage("Error connecting to AI service", "bot");
  }
}

// Add line-clamp utility for truncating text
const style = document.createElement('style');
style.textContent = `
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
`;
document.head.appendChild(style);