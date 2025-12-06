// Sidebar toggle for mobile
const closeBtn = document.getElementById("close-sidebar");
closeBtn.addEventListener("click", () => {
    sidebar.classList.remove("mobile-active");
});


// Sidebar toggle for mobile
const sidebar = document.getElementById("sidebar");
const toggleBtn = document.getElementById("menu-toggle");
toggleBtn.addEventListener("click", () => {
    if (window.innerWidth <= 768) {
        sidebar.classList.toggle("mobile-active");
    } else {
        // DESKTOP VIEW — collapse/expand sidebar
        sidebar.classList.toggle("collapsed");
    }
});


// Page switching
const links = document.querySelectorAll(".sidebar a");
const pages = document.querySelectorAll(".section-page");


// Open sidebar when clicking dashboard icon on mobile
const dashboardIcon = document.querySelector("[data-section='dashboard'] .material-icons");
dashboardIcon.addEventListener("click", (e) => {
    if (window.innerWidth <= 768) {
        e.stopPropagation();
        sidebar.classList.add("mobile-active");
    }
});


links.forEach(link => {
    link.addEventListener("click", () => {
        links.forEach(l => l.classList.remove("active"));
        link.classList.add("active");


        const section = link.dataset.section;
        document.getElementById("section-title").innerText = section.charAt(0).toUpperCase() + section.slice(1);


        pages.forEach(page => page.classList.remove("active"));
        document.getElementById(section).classList.add("active");
    });
});