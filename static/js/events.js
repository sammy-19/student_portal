document.addEventListener("DOMContentLoaded", function() {
    // Get all the navigation links and the content sections
    const navLinks = document.querySelectorAll(".sidebar ul li a");
    const sections = document.querySelectorAll("section");

    // Hide all sections except the first one (page1) on page load
    sections.forEach((section, index) => {
        if (index !== 0) {
            section.style.display = "none";
        }
    });

    // Add click event listeners to the nav links
    navLinks.forEach((link, index) => {
        link.addEventListener("click", function(event) {
            event.preventDefault(); // Prevent default link behavior

            // Remove 'active' class from all links
            navLinks.forEach(link => link.classList.remove("active"));
            // Add 'active' class to the clicked link
            this.classList.add("active");

            // Hide all sections
            sections.forEach(section => section.style.display = "none");
            // Show the corresponding section
            sections[index].style.display = "block";
        });
    });
});