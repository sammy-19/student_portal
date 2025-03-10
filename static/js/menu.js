function dropDown() {
    var dropdownMenu = document.getElementById('dpdown');
    if (dropdownMenu.classList.contains('show')) {
        dropdownMenu.classList.remove('show');
        setTimeout(function() {
            dropdownMenu.style.display = 'none';
        }, 500); // Match the transition duration
    } else {
        dropdownMenu.style.display = 'block';
        setTimeout(function() {
            dropdownMenu.classList.add('show');
        }, 10); // Small delay to trigger transition
    }
}