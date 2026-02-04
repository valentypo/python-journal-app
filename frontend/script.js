// CHANGE THIS if your backend runs somewhere else
const API_BASE = "http://127.0.0.1:5000";

// DOM elements
const createForm = document.getElementById("createForm");
const titleInput = document.getElementById("titleInput");
const contentInput = document.getElementById("contentInput");
const entriesList = document.getElementById("entriesList");
const refreshBtn = document.getElementById("refreshBtn");
const statusText = document.getElementById("statusText");

// -----------------------------
// Helpers
// -----------------------------
function setStatus(msg) {
  statusText.textContent = msg;
}

function escapeHtml(str) {
  return str.replace(/[&<>"']/g, (m) => {
    const map = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;",
    };
    return map[m];
  });
}

// -----------------------------
// API Calls
// -----------------------------
async function fetchEntries() {
  setStatus("Loading entries...");

  const res = await fetch(`${API_BASE}/entries`);
  const data = await res.json();

  renderEntries(data);
  setStatus(`Loaded ${data.length} entries.`);
}

async function createEntry(title, content) {
  const res = await fetch(`${API_BASE}/entries`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, content }),
  });

  if (!res.ok) {
    const err = await res.json();
    alert("Create failed: " + JSON.stringify(err));
    return;
  }

  await fetchEntries();
}

async function updateEntry(id, title, content) {
  const res = await fetch(`${API_BASE}/entries/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, content }),
  });

  if (!res.ok) {
    const err = await res.json();
    alert("Update failed: " + JSON.stringify(err));
    return;
  }

  await fetchEntries();
}

async function deleteEntry(id) {
  const ok = confirm("Delete this entry?");
  if (!ok) return;

  const res = await fetch(`${API_BASE}/entries/${id}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    const err = await res.json();
    alert("Delete failed: " + JSON.stringify(err));
    return;
  }

  await fetchEntries();
}

// -----------------------------
// UI Rendering
// -----------------------------
function renderEntries(entries) {
  entriesList.innerHTML = "";

  if (!entries || entries.length === 0) {
    entriesList.innerHTML = `
      <div class="text-gray-400 text-sm">
        No entries yet. Create one above ✨
      </div>
    `;
    return;
  }

  for (const entry of entries) {
    const id = entry.id; // Mongo ObjectId string (or UUID if you chose that)
    const title = escapeHtml(entry.title ?? "");
    const content = escapeHtml(entry.content ?? "");
    const createdAt = entry.created_at ? new Date(entry.created_at).toLocaleString() : "";
    const updatedAt = entry.updated_at ? new Date(entry.updated_at).toLocaleString() : "";

    const card = document.createElement("div");
    card.className =
      "bg-gray-950 border border-gray-800 rounded-xl p-4 space-y-3";

    card.innerHTML = `
      <div class="flex items-start justify-between gap-3">
        <div class="min-w-0">
          <h3 class="font-semibold text-lg break-words">${title}</h3>
          <p class="text-xs text-gray-500 mt-1">
            Created: ${createdAt || "—"} • Updated: ${updatedAt || "—"}
          </p>
        </div>

        <div class="flex gap-2 shrink-0">
          <button
            class="editBtn text-sm px-3 py-1 rounded-lg border border-gray-700 hover:bg-gray-800 transition"
          >
            Edit
          </button>

          <button
            class="deleteBtn text-sm px-3 py-1 rounded-lg border border-red-900 text-red-300 hover:bg-red-950 transition"
          >
            Delete
          </button>
        </div>
      </div>

      <p class="text-gray-200 whitespace-pre-wrap break-words">${content}</p>

      <!-- Hidden edit form -->
      <div class="editBox hidden border-t border-gray-800 pt-3 space-y-2">
        <div>
          <label class="block text-sm text-gray-300 mb-1">Edit Title</label>
          <input
            class="editTitle w-full rounded-lg bg-gray-950 border border-gray-800 px-3 py-2 outline-none focus:ring focus:ring-gray-700"
            value="${title}"
          />
        </div>

        <div>
          <label class="block text-sm text-gray-300 mb-1">Edit Content</label>
          <textarea
            class="editContent w-full rounded-lg bg-gray-950 border border-gray-800 px-3 py-2 outline-none focus:ring focus:ring-gray-700"
            rows="4"
          >${content}</textarea>
        </div>

        <div class="flex gap-2">
          <button
            class="saveBtn bg-white text-gray-950 font-semibold px-4 py-2 rounded-lg hover:bg-gray-200 transition"
          >
            Save
          </button>

          <button
            class="cancelBtn text-sm px-4 py-2 rounded-lg border border-gray-700 hover:bg-gray-800 transition"
          >
            Cancel
          </button>
        </div>
      </div>
    `;

    // Wire up buttons
    const editBtn = card.querySelector(".editBtn");
    const deleteBtn = card.querySelector(".deleteBtn");
    const editBox = card.querySelector(".editBox");
    const saveBtn = card.querySelector(".saveBtn");
    const cancelBtn = card.querySelector(".cancelBtn");

    const editTitle = card.querySelector(".editTitle");
    const editContent = card.querySelector(".editContent");

    editBtn.addEventListener("click", () => {
      editBox.classList.toggle("hidden");
    });

    cancelBtn.addEventListener("click", () => {
      editBox.classList.add("hidden");
      editTitle.value = entry.title ?? "";
      editContent.value = entry.content ?? "";
    });

    saveBtn.addEventListener("click", async () => {
      const newTitle = editTitle.value.trim();
      const newContent = editContent.value.trim();

      if (!newTitle || !newContent) {
        alert("Title and content cannot be empty.");
        return;
      }

      await updateEntry(id, newTitle, newContent);
    });

    deleteBtn.addEventListener("click", async () => {
      await deleteEntry(id);
    });

    entriesList.appendChild(card);
  }
}

// -----------------------------
// Events
// -----------------------------
createForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const title = titleInput.value.trim();
  const content = contentInput.value.trim();

  if (!title || !content) {
    alert("Please enter title + content.");
    return;
  }

  await createEntry(title, content);

  titleInput.value = "";
  contentInput.value = "";
});

refreshBtn.addEventListener("click", fetchEntries);

// Load entries on page start
fetchEntries();
