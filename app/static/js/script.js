const processButton = document.getElementById("processButton");

function displayResults(results, resultContainer) {
    resultContainer.innerHTML = results.replace(/\n/g, "<br>");
}

processButton.addEventListener("click", function () {
    const form = document.getElementById("uploadForm");
    const resultContainer = document.getElementById("resultContainer");

    // Check if a file has been selected
    const fileInput = form.querySelector('input[type="file"]');
    if (fileInput.files.length === 0) {
        alert("Please select a file to upload.");
        return;
    }

    const formData = new FormData(form);

    // Send the FormData object with the file
    sendFormDataToBackend(formData, resultContainer);
});

function sendFormDataToBackend(formData, resultContainer) {
    fetch("/classify-fasta", {
        method: "POST",
        body: formData,
    })
    .then(response => {
        if (response.ok) {
            return response.text();
        } else {
            throw new Error("Server responded with an error: " + response.status);
        }
    })
    .then(data => {
        displayResults(data, resultContainer);
    })
    .catch(error => {
        console.error("Error sending data to backend:", error);
    });
}
