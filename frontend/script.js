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
    div.className='bg-gray-950 border border-gray-800 rounded-xl p-3';
    div.innerHTML=`<h3 class="font-semibold">${e.title}</h3><p class="text-gray-400 text-sm">${e.content}</p>`;
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