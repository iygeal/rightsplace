document.addEventListener('DOMContentLoaded', function () {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');
  const fileList = document.getElementById('fileList');

  // Store ALL selected files here
  let storedFiles = [];

  // Allowed file types
  const allowedTypes = [
    'image/',
    'video/',
    'audio/',
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/plain',
  ];

  function isValidFile(file) {
    return allowedTypes.some(
      (type) => file.type.startsWith(type) || file.type === type
    );
  }

  // Rebuild file input using DataTransfer
  function syncInputFiles() {
    const dt = new DataTransfer();
    storedFiles.forEach((f) => dt.items.add(f));
    fileInput.files = dt.files;
  }

  // Update file preview list
  function refreshPreview() {
    fileList.innerHTML = '';
    storedFiles.forEach((file) => {
      const li = document.createElement('li');
      li.textContent = `${file.name} (${Math.round(file.size / 1024)} KB)`;
      fileList.appendChild(li);
    });
  }

  // Add one or more files to the stored list
  function addFiles(files) {
    for (let file of files) {
      if (!isValidFile(file)) {
        alert(`Unsupported file format: ${file.name}`);
        return;
      }
      storedFiles.push(file);
    }

    syncInputFiles();
    refreshPreview();
  }

  // Highlight dropzone
  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
  });

  // Handle dropped files
  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    addFiles(e.dataTransfer.files);
  });

  // Click to trigger file picker
  dropzone.addEventListener('click', () => {
    fileInput.click();
  });

  // When selecting through file picker
  fileInput.addEventListener('change', function () {
    addFiles(fileInput.files);
  });
});
