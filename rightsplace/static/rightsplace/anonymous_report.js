// ======================================================================
// anonymous_report.js — FINAL VERSION
// ======================================================================

// DOM Elements
const dropArea = document.getElementById('drop-area');
const pickBtn = document.getElementById('pick-files-btn');
const fileInput = document.querySelector("input[name='evidence_files']");
const fileList = document.getElementById('file-list');
const form = document.getElementById('anonymousReportForm');
const progressContainer = document.getElementById('upload-progress-container');
const progressBar = document.getElementById('upload-progress');
const successBox = document.getElementById('success-box');
const formCard = document.getElementById('form-card');

// Internal store
let filesBucket = [];

// ----------------------------------------------------------------------
// UI helpers
// ----------------------------------------------------------------------

function refreshFileList() {
  fileList.innerHTML = '';

  filesBucket.forEach((file, index) => {
    const item = document.createElement('div');
    item.className = 'file-item';
    item.innerHTML = `
      <span>${file.name} (${Math.round(file.size / 1024)} KB)</span>
      <button type="button"
              class="file-remove-btn"
              data-index="${index}">
        &times;
      </button>
    `;
    fileList.appendChild(item);
  });
}

function syncToInput() {
  const dt = new DataTransfer();
  filesBucket.forEach((f) => dt.items.add(f));
  fileInput.files = dt.files;
}

function addFiles(newFiles) {
  for (const file of newFiles) {
    if (filesBucket.length >= 20) {
      alert('Maximum of 20 files allowed.');
      break;
    }

    if (file.size > 100 * 1024 * 1024) {
      alert(`${file.name} exceeds 100MB and was skipped.`);
      continue;
    }

    filesBucket.push(file);
  }

  refreshFileList();
  syncToInput();
}

// ----------------------------------------------------------------------
// Drag & drop
// ----------------------------------------------------------------------

dropArea.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropArea.classList.add('dragover');
});

dropArea.addEventListener('dragleave', () => {
  dropArea.classList.remove('dragover');
});

dropArea.addEventListener('drop', (e) => {
  e.preventDefault();
  dropArea.classList.remove('dragover');
  addFiles(e.dataTransfer.files);
});

// ----------------------------------------------------------------------
// File picking
// ----------------------------------------------------------------------

pickBtn.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', () => {
  addFiles(fileInput.files);
});

// ----------------------------------------------------------------------
// Remove file
// ----------------------------------------------------------------------

fileList.addEventListener('click', (e) => {
  if (e.target.classList.contains('file-remove-btn')) {
    const index = parseInt(e.target.dataset.index, 10);
    filesBucket.splice(index, 1);
    refreshFileList();
    syncToInput();
  }
});

// ----------------------------------------------------------------------
// Form submission (AJAX, no redirect)
// ----------------------------------------------------------------------

form.addEventListener('submit', function (event) {
  event.preventDefault();

  const url = form.action || window.location.href;
  const formData = new FormData(form);

  // Ensure multiple evidence_files entries
  formData.delete('evidence_files');
  filesBucket.forEach((f) => formData.append('evidence_files', f));

  // Reset progress
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

  // Upload progress
  xhr.upload.addEventListener('progress', (e) => {
    if (e.lengthComputable) {
      const percent = Math.round((e.loaded / e.total) * 100);
      progressBar.style.width = percent + '%';
      progressBar.textContent = percent + '%';
    }
  });

  // Response handler
  xhr.onload = () => {
    let response;

    try {
      response = JSON.parse(xhr.responseText);
    } catch (err) {
      alert('Unexpected server response.');
      return;
    }

    // SUCCESS
    if (xhr.status === 200 && response.success) {
      formCard.classList.add('d-none');
      successBox.classList.remove('d-none');
      return;
    }

    // VALIDATION ERRORS
    if (xhr.status === 400 && response.errors) {
      let msg = 'Please correct the following:\n\n';

      for (const [field, errs] of Object.entries(response.errors)) {
        msg += `${field}: ${errs.join(', ')}\n`;
      }

      alert(msg);
      return;
    }

    alert('Submission failed. Please try again.');
  };

  xhr.onerror = () => {
    alert('Network error. Please check your connection.');
  };

  xhr.send(formData);
});
