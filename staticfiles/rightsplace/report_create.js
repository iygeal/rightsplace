// DOM Elements
const dropArea = document.getElementById('drop-area');
const pickBtn = document.getElementById('pick-files-btn');
const fileInput = document.querySelector("input[name='evidence_files']");
const fileList = document.getElementById('file-list');
const form = document.getElementById('reportForm');
const progressContainer = document.getElementById('upload-progress-container');
const progressBar = document.getElementById('upload-progress');
const successBox = document.getElementById('success-box');
const formCard = document.getElementById('form-card');
const submitBtn = form.querySelector("button[type='submit']");

// Internal store
let filesBucket = [];

// ----------------------------------------------------------------------
// UI helpers
// ----------------------------------------------------------------------

/**
 * Refreshes the file list in the UI based on the filesBucket array.
 * This function is called whenever the filesBucket array is modified.
 * It iterates over the filesBucket array and appends a new file item to the
 * fileList element for each file in the array.
 */
function refreshFileList() {
  fileList.innerHTML = '';
  filesBucket.forEach((file, index) => {
    const item = document.createElement('div');
    item.className = 'file-item';
    item.innerHTML = `
      <span>${file.name} (${Math.round(file.size / 1024)} KB)</span>
      <button type="button" class="file-remove-btn" data-index="${index}">
        &times;
      </button>
    `;
    fileList.appendChild(item);
  });
}

/**
 * Synchronizes the filesBucket array with the fileInput element.
 * This function is called whenever the filesBucket array is modified.
 * It creates a new DataTransfer object and adds each file in the filesBucket
 * array to the DataTransfer object. It then assigns the DataTransfer object's
 * files property to the fileInput element, effectively synchronizing the
 * filesBucket array with the fileInput element.
 */
function syncToInput() {
  const dt = new DataTransfer();
  filesBucket.forEach((file) => dt.items.add(file));
  fileInput.files = dt.files;
}

/**
 * Adds new files to the filesBucket array and refreshes the file list in the UI.
 * If the filesBucket array already contains 20 files, it will display an alert
 * and stop adding new files. If a file exceeds 100MB, it will display an alert
 * and skip adding that file.
 * @param {FileList} newFiles - The new files to be added to the filesBucket array.
 */
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
fileInput.addEventListener('change', () => addFiles(fileInput.files));

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
// Form submission
// ----------------------------------------------------------------------

form.addEventListener('submit', function (event) {
  event.preventDefault();

  submitBtn.disabled = true;
  submitBtn.textContent = 'Submitting...';

  const url = form.action;
  const formData = new FormData(form);

  // Multi-upload support
  formData.delete('evidence_files');
  filesBucket.forEach((file) => formData.append('evidence_files', file));

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

  // Response handler
  xhr.onload = () => {
    let response;

    try {
      response = JSON.parse(xhr.responseText);
    } catch {
      alert('Unexpected server response.');
      submitBtn.disabled = false;
      submitBtn.textContent = 'Submit Report';
      return;
    }

    // SUCCESS
    if (xhr.status === 200 && response.success) {
      // SHOW success UI — NO redirect
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
    } else {
      alert('Upload failed. Please try again.');
    }

    submitBtn.disabled = false;
    submitBtn.textContent = 'Submit Report';
  };

  xhr.onerror = () => {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Submit Report';
    alert('A network error occurred during upload.');
  };

  xhr.send(formData);
});
