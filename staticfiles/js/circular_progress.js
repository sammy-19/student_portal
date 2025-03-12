circular_progress.js: function setCircularProgress(progressPercent) {
    const circularProgress = document.querySelector('.circular-progress');
    const progressValue = document.getElementById('number');
    const progressBar = document.querySelector('.circular-progress circle');

    if (!circularProgress || !progressValue || !progressBar) {
        console.error('Circular progress elements not found');
        return;
    }

    progressValue.textContent = `${progressPercent}%`;
    const progress = 440 - (440 * progressPercent) / 100;
    progressBar.style.strokeDashoffset = progress;
    circularProgress.style.background = `conic-gradient(darkgreen ${progressPercent * 3.6}deg, #ededed 0deg)`;
}