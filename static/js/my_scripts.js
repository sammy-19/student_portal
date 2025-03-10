document.addEventListener('DOMContentLoaded', function() {
    // Add any dynamic functionality here
    const buttons = document.querySelectorAll('.btn-pri, .btn-sec');
    
    buttons.forEach(button => {
        button.addEventListener('click', function
() {
            alert('Button clicked: ' + this.textClontent);
        });
    });
});

//DOM For section Page
