let currentVideoIndex = 0;
let videoData = [];

function initVideoPlayer(videos) {
    videoData = videos;
    loadVideo(currentVideoIndex);
    updateButtons();
    updateProgress();
}

function loadVideo(index) {
    if (index < 0 || index >= videoData.length) return;

    const video = videoData[index];
    const container = document.getElementById('video-container');
    let videoHTML = '';

    if (video.isVideoFile) {
        videoHTML = `
            <div class="video-item">
                <h3>${video.title}</h3>
                <video controls>
                    <source src="${video.url}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
                <p>${video.description}</p>
                ${video.completed ? '<div class="completed">COMPLETE</div>' : ''}
            </div>
        `;
    } else if (video.url) {  // Check for a valid URL (YouTube embed)
        videoHTML = `
            <div class="video-item">
                <h3>${video.title}</h3>
                <iframe width="560" height="315" src="${video.url}" title="${video.title}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
                <p>${video.description}</p>
                ${video.completed ? '<div class="completed">COMPLETE</div>' : ''}
            </div>
        `;
    } else {
        videoHTML = `<div class="video-item"><p>No video available.</p></div>`;
    }


    container.innerHTML = videoHTML;
}

function updateButtons() {
    const prevButton = document.getElementById('prev-button');
    const nextButton = document.getElementById('next-button');

    prevButton.disabled = currentVideoIndex === 0;
    nextButton.disabled = currentVideoIndex === videoData.length - 1;

    prevButton.onclick = () => {
        currentVideoIndex--;
        loadVideo(currentVideoIndex);
        updateButtons();
        updateProgress();
    };

    nextButton.onclick = () => {
        currentVideoIndex++;
        loadVideo(currentVideoIndex);
        updateButtons();
        updateProgress();
    };
}
function updateProgress() {
    const countSpan = document.getElementById('video-count');
    const percentageSpan = document.getElementById('progress-percentage');
    const progressCircle = document.getElementById('progress-circle');

    const currentVideoNum = currentVideoIndex + 1;
    const totalVideos = videoData.length;
    const percentage = (currentVideoNum / totalVideos) * 100;

    countSpan.textContent = `${currentVideoNum} of ${totalVideos} videos`;
    percentageSpan.textContent = `${percentage.toFixed(0)}%`; // Display percentage

     // Update the conic-gradient for the progress circle
    progressCircle.style.background = `conic-gradient(#007bff 0% ${percentage}%, #ddd ${percentage}% 100%)`;

}