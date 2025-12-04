document.addEventListener('DOMContentLoaded', () => {
  const fakeBtn = document.getElementById('openFilePicker');
  const realInput = document.getElementById('djangoFileInput');
  const fileList = document.getElementById('fileList');

  if (!fakeBtn || !realInput) return;

  fakeBtn.addEventListener('click', () => {
    realInput.click();
  });

  realInput.addEventListener('change', () => {
    fileList.innerHTML = '';

    if (realInput.files.length === 0) {
      fileList.textContent = 'No files selected.';
      return;
    }

    const ul = document.createElement('ul');
    for (let f of realInput.files) {
      const li = document.createElement('li');
      li.textContent = `${f.name} (${Math.round(f.size / 1024)} KB)`;
      ul.appendChild(li);
    }

    fileList.appendChild(ul);
  });
});
