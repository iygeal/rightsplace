// ======================================================================
// report_create.js — FINAL FIXED VERSION
// ======================================================================

// DOM Elements
const dropArea = document.getElementById('drop-area');
const pickBtn = document.getElementById('pick-files-btn');
const fileInput = document.querySelector("input[name='evidence_files']");
const fileList = document.getElementById('file-list');
const form = document.getElementById('reportForm');
const progressContainer = document.getElementById('upload-progress-container');
const progressBar = document.getElementById('upload-progress');

// Internal store
let filesBucket = [];

// Refresh UI
function refreshFileList() {
  fileList.innerHTML = '';
  filesBucket.forEach((file, index) => {
    const item = document.createElement('div');
    item.className = 'file-item';
    item.innerHTML = `
            <span>${file.name} (${Math.round(file.size / 1024)} KB)</span>
            <button type="button" class="file-remove-btn" data-index="${index}">&times;</button>
        `;
    fileList.appendChild(item);
  });
}

// Sync bucket → input
function syncToInput() {
  const dt = new DataTransfer();
  filesBucket.forEach((f) => dt.items.add(f));
  fileInput.files = dt.files;
}

// Add files
function addFiles(newFiles) {
  for (const file of newFiles) {
    if (filesBucket.length >= 20) {
      alert('Maximum of 20 files allowed.');
      break;
    }
    if (file.size > 100 * 1024 * 1024) {
      alert(file.name + ' exceeds 100MB and was skipped.');
      continue;
    }
    filesBucket.push(file);
  }
  refreshFileList();
  syncToInput();
}

// Drag/drop handlers
dropArea.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropArea.classList.add('dragover');
});
dropArea.addEventListener('dragleave', () =>
  dropArea.classList.remove('dragover')
);
dropArea.addEventListener('drop', (e) => {
  e.preventDefault();
  dropArea.classList.remove('dragover');
  addFiles(e.dataTransfer.files);
});

// Click "pick files"
pickBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', () => addFiles(fileInput.files));

// Remove file
fileList.addEventListener('click', (e) => {
  if (e.target.classList.contains('file-remove-btn')) {
    const index = parseInt(e.target.dataset.index);
    filesBucket.splice(index, 1);
    refreshFileList();
    syncToInput();
  }
});

// ======================================================================
// FIXED FORM SUBMISSION LOGIC
// Handles Django 302 redirects correctly
// ======================================================================

form.addEventListener('submit', function (event) {
  event.preventDefault();

  const url = form.action || window.location.href;

  const formData = new FormData(form);

  // Django-multiupload requires multiple "evidence_files"
  formData.delete('evidence_files');
  filesBucket.forEach((f) => formData.append('evidence_files', f));

  // Show progress
  progressContainer.classList.remove('d-none');
  progressBar.style.width = '0%';
  progressBar.textContent = '0%';

  const xhr = new XMLHttpRequest();
  xhr.open('POST', url);

  // CSRF
  const csrftoken = document.querySelector(
    "input[name='csrfmiddlewaretoken']"
  ).value;
  xhr.setRequestHeader('X-CSRFToken', csrftoken);

  // Progress
  xhr.upload.addEventListener('progress', (e) => {
    if (e.lengthComputable) {
      const percent = Math.round((e.loaded / e.total) * 100);
      progressBar.style.width = percent + '%';
      progressBar.textContent = percent + '%';
    }
  });

  // SUCCESS HANDLER
  xhr.onload = () => {
    // Case 1: Django success with redirect (most common)
    if (xhr.status === 302) {
      const redirectURL = xhr.getResponseHeader('Location');
      if (redirectURL) window.location.href = redirectURL;
      return;
    }

    // Case 2: Normal 200/201 JSON or HTML response
    if (xhr.status >= 200 && xhr.status < 300) {
      window.location.href = window.location.href; // Reload page cleanly
      return;
    }

    // Otherwise: error
    alert('Upload failed. Please try again.');
  };

  xhr.onerror = () => alert('An error occurred during upload.');

  xhr.send(formData);
});
