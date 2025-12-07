document.addEventListener('DOMContentLoaded', () => {
  const realInput = document.getElementById('djangoFileInput');
  const dropZone = document.getElementById('dropZone');
  const fileList = document.getElementById('fileList');
  const fileErrors = document.getElementById('fileErrors');

  if (!realInput) return;

  // Highlight drop area
  ['dragenter', 'dragover'].forEach((ev) => {
    dropZone.addEventListener(ev, (e) => {
      e.preventDefault();
      dropZone.classList.add('bg-light');
    });
  });

  ['dragleave', 'drop'].forEach((ev) => {
    dropZone.addEventListener(ev, (e) => {
      e.preventDefault();
      dropZone.classList.remove('bg-light');
    });
  });

  // Handle click to open picker
  dropZone.addEventListener('click', () => realInput.click());

  // Drop handler
  dropZone.addEventListener('drop', (e) => {
    const dtFiles = e.dataTransfer.files;
    appendFiles(dtFiles);
  });

  // Normal picker change
  realInput.addEventListener('change', () => {
    appendFiles(realInput.files);
  });

  function appendFiles(fileListObject) {
    const newFiles = Array.from(fileListObject);
    const existingFiles = Array.from(realInput.files);

    const combined = [...existingFiles, ...newFiles];

    const dataTransfer = new DataTransfer();
    combined.forEach((f) => dataTransfer.items.add(f));
    realInput.files = dataTransfer.files;

    renderFileList();
  }

  function renderFileList() {
    fileList.innerHTML = '';
    fileErrors.style.display = 'none';

    if (realInput.files.length === 0) return;

    for (let f of realInput.files) {
      const li = document.createElement('li');
      li.className = 'list-group-item small';
      li.textContent = `${f.name} (${Math.round(f.size / 1024)} KB)`;
      fileList.appendChild(li);
    }
  }
});
