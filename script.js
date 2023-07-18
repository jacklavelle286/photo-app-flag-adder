document.querySelector('#upload-form').addEventListener('submit', uploadImage);

async function uploadImage(event) {
    event.preventDefault();

    const files = document.querySelector('#imageUpload').files;
    const flag = document.querySelector('#flagSelect').value;

    if (files.length > 0) {
        const file = files[0];

        // Start progress bar
        const progressBar = document.querySelector('#progress-bar');
        progressBar.style.width = '0%';

        // Set an interval to incrementally increase the progress bar value
        const interval = setInterval(() => {
            const currentWidth = parseInt(progressBar.style.width);
            if (currentWidth < 90) { // Slowly increment up to 90% initially
                progressBar.style.width = (currentWidth + 1) + '%';
            }
        }, 100); // The progress bar increases by 1% every 100ms

        // Convert image to base64
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = async function () {
            const base64Image = reader.result.split(',')[1];

            // Send JSON data in request
            const requestData = JSON.stringify({
                image: base64Image,
                flag: flag
            });

            // Change the URL to your API Gateway endpoint
            const response = await fetch('https://zx0yg2470a.execute-api.us-east-1.amazonaws.com/upload', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: requestData
            });

            clearInterval(interval); // Stop the interval

            // Handling the response from Lambda
            if (response.ok) {
                const data = await response.json();
                const imageUrl = data.image_url;

                // Complete progress bar
                progressBar.style.width = '100%';

                // Show download button with the link to the processed image
                const downloadButton = document.querySelector('#download-btn');
                downloadButton.style.display = 'block';
                downloadButton.onclick = function () {
                    window.location.href = imageUrl;
                };
            } else {
                console.error('Upload failed');
                progressBar.style.width = '0%';
            }
        };
    }
}
