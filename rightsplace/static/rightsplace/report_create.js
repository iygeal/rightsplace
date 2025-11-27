document.addEventListener("DOMContentLoaded", function () {
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("fileInput");
    const fileList = document.getElementById("fileList");

    // Allowed MIME type groups
    const allowedTypes = [
        "image/",      // jpg, png, gif, etc.
        "video/",      // mp4, avi, mov
        "audio/",      // mp3, wav
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain"
    ];

    // Validate file type
    function isValidFile(file) {
        return allowedTypes.some(type => file.type.startsWith(type) || file.type === type);
    }

    // Add files to preview list
    function displayFiles(files) {
        fileList.innerHTML = ""; // Clear existing list

        Array.from(files).forEach(file => {
            const li = document.createElement("li");
            li.textContent = `${file.name} (${Math.round(file.size / 1024)} KB)`;
            fileList.appendChild(li);
        });
    }

    // Highlight dropzone
    dropzone.addEventListener("dragover", function (e) {
        e.preventDefault();
        dropzone.classList.add("dragover");
    });

    dropzone.addEventListener("dragleave", function () {
        dropzone.classList.remove("dragover");
    });

    // Handle dropped files
    dropzone.addEventListener("drop", function (e) {
        e.preventDefault();
        dropzone.classList.remove("dragover");

        const droppedFiles = e.dataTransfer.files;

        // Validate
        for (let file of droppedFiles) {
            if (!isValidFile(file)) {
                alert("One or more files have an unsupported format.");
                return;
            }
        }

        // Pass files to hidden input
        fileInput.files = droppedFiles;

        // Display preview
        displayFiles(droppedFiles);
    });

    // Click to open file picker
    dropzone.addEventListener("click", () => {
        fileInput.click();
    });

    // When selecting with click
    fileInput.addEventListener("change", function () {
        const selected = fileInput.files;

        // Validate
        for (let file of selected) {
            if (!isValidFile(file)) {
                alert("One or more selected files have an unsupported format.");
                fileInput.value = ""; // reset
                return;
            }
        }

        displayFiles(selected);
    });
});
