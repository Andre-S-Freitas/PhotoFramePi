// Photo count
const photoCount = document.getElementById("photo-count");

// Upload button
const uploadButton = document.getElementById("upload-button");
uploadButton.addEventListener("click", openFileUpload);

// File input
const fileInput = document.getElementById("file-input");
fileInput.addEventListener("change", handleFileUpload);

// Config form
const configForm = document.getElementById("config-form");
const submitConfig = document.getElementById("submit-config");
submitConfig.addEventListener("click", handleConfigSubmit);

// Upload progress
const uploadingProgress = document.getElementById("upload-progress");
const progressBar = document.getElementById("progress-bar");
const progressBarError = document.getElementById("progress-bar-error");
const dismissProgress = document.getElementById("dismiss-progress");
const alertTitle = document.getElementById("alert-title");
const alertMessage = document.getElementById("alert-message");

// Photo list
const photoList = document.getElementById("photo-list");

function setProgressBar(progress, error, step) {
    const e = Math.round(error * step);
    progressBarError.children[0].textContent = e + "%";
    progressBarError.style.width = e + "%";

    const p = Math.round(progress * step);
    progressBar.children[0].textContent = p + "%";
    progressBar.style.width = p + "%";
}

function startProgressBar() {
    uploadingProgress.classList.remove("d-none");
    progressBar.children[0].classList.add("progress-bar-striped", "progress-bar-animated");
    alertMessage.textContent = `Do not close this window until the upload is finished.`
}

function stopProgressBar(success, error) {
    progressBar.children[0].classList.remove("progress-bar-striped", "progress-bar-animated");
    dismissProgress.classList.remove("d-none");
    alertTitle.textContent = "Upload complete";
    if (error > 0) {
        if (success > 0) {
            alertMessage.textContent = `${success} files have been uploaded successfully but ${error} files failed to be uploaded`;
        } else {
            alertMessage.textContent = `${error} files failed to be uploaded`;
        }
    } else {
        alertMessage.textContent = `${success} files have been uploaded successfully`;
    }
}

async function handleConfigSubmit(event) {
    event.preventDefault();

    const data = Object.fromEntries(new FormData(configForm).entries());

    if (!data.interval || data.interval <= 0) {
        console.error("Interval must greater than 0");
        return;
    }

    const response = await fetch('/config', {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });

    if (response.status !== 200) {
        console.error("Failed to update config", response);
    }
}

async function handleFileUpload(event) {
    const files = event.target.files;
    let success = 0;
    let error = 0;
    const step = 100 / files.length;

    startProgressBar();
    setProgressBar(success, error, step);

    for (const file of files) {
        const response = await postFile(file);
        if (response.status !== 200) {
            console.error("Failed to upload file", response);
            error++;
        } else {
            success++;
        }
        setProgressBar(success, error, step);
    }

    stopProgressBar(success, error);

    photoCount.textContent = parseInt(photoCount.textContent) + success;
    await refreshPhotoList();
}

async function refreshPhotoList() {
    const response = await fetch("/photo-list");
    photoList.innerHTML = await response.text();
}

async function postFile(file) {
    const formData = new FormData();
    formData.append("file", file);
    return fetch("/upload", {
        method: "POST",
        body: formData
    })
}

function openFileUpload() {
    fileInput.click();
}

async function requestPhotoRemove(photoId) {
    const body = { id: photoId };
    return fetch("/remove", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
    })
}

async function setPhoto(photoId) {
    const response = await fetch('/set', {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ id: photoId })
    })

    if (response.status !== 200) {
        console.error("Failed to set photo", response);
        return;
    }

    const activeCard = document.getElementsByClassName("card-outline border-light")[0];
    activeCard.classList.remove("border-light");
    const button = activeCard.getElementsByClassName('activate-button')[0];
    button.attributes.removeNamedItem("disabled");
    button.classList.remove("btn-outline-secondary");
    button.classList.add("btn-outline-primary");

    const newActiveCard = document.getElementById("photo-" + photoId);
    newActiveCard.children[0].classList.add("border-light");
    const newActiveButton = newActiveCard.getElementsByClassName('activate-button')[0];
    newActiveButton.attributes.setNamedItem(document.createAttribute("disabled"));
    newActiveButton.classList.remove("btn-outline-primary");
    newActiveButton.classList.add("btn-outline-secondary");
}

async function removePhoto(photoId) {
    const response = await requestPhotoRemove(photoId);

    if (response.status !== 200) {
        console.error("Failed to remove photo", response);
        return;
    }

    const photoContainer = document.getElementById("photo-" + photoId);
    photoContainer.remove();

    photoCount.textContent = parseInt(photoCount.textContent) - 1;
}
