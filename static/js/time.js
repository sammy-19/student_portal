function updateDateTime() {
    const now = new Date();
    const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
    };
    const dateTimeString = now.toLocaleString('en-UK', options);

    document.getElementById('datetime').innerText = dateTimeString;
}

// Update the date and time every second
setInterval(updateDateTime, 1000);

// Initial call to display date and time immediately
updateDateTime();
