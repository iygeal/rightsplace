document.addEventListener('DOMContentLoaded', function () {
  const fileInput = document.getElementById('fileInput');
  const djangoInput = document.querySelector("input[name='evidence_files']");
  const dropZone = document.getElementById('dropZone');
  const fileList = document.getElementById('fileList');

  let storedFiles = [];

  function refreshFileList() {
    fileList.innerHTML = '';

    storedFiles.forEach((file, index) => {
      const li = document.createElement('li');
      li.classList.add(
        'list-group-item',
        'd-flex',
        'justify-content-between',
        'align-items-center'
      );

      li.innerHTML = `
                <span>${file.name}</span>
                <button type="button" class="btn btn-sm btn-danger" data-index="${index}">Remove</button>
            `;

      fileList.appendChild(li);
    });

    syncToDjangoField();
  }

  function syncToDjangoField() {
    const dataTransfer = new DataTransfer();
    storedFiles.forEach((file) => dataTransfer.items.add(file));
    djangoInput.files = dataTransfer.files;
  }

  // Clicking dropzone opens file dialog
  dropZone.addEventListener('click', () => fileInput.click());

  // Dragging over dropzone
  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('bg-light');
  });

  dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('bg-light');
  });

  // Dropping files
  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('bg-light');

    const newFiles = Array.from(e.dataTransfer.files);
    storedFiles.push(...newFiles);
    refreshFileList();
  });

  // Selecting files using file dialog
  fileInput.addEventListener('change', (e) => {
    const newFiles = Array.from(e.target.files);
    storedFiles.push(...newFiles);
    refreshFileList();
  });

  // Removing files
  fileList.addEventListener('click', (e) => {
    if (e.target.tagName === 'BUTTON') {
      const index = e.target.dataset.index;
      storedFiles.splice(index, 1);
      refreshFileList();
    }
  });
});
