// --------------------------- API Helpers ---------------------------
async function apiGET(path) {
    const response = await fetch(path);
    return response.ok ? response.json() : Promise.reject(await response.text());
}

async function apiPOST(path, body) {
    const response = await fetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    return response.ok ? response.json() : Promise.reject(await response.text());
}

async function apiDELETE(path) {
    const response = await fetch(path, { method: 'DELETE' });
    return response.ok ? response.json() : Promise.reject(await response.text());
}

// --------------------------- DOM Elements ---------------------------
const sidebar = document.getElementById("sidebar");
const toggleBtn = document.getElementById("menu-toggle");
const closeBtn = document.getElementById("close-sidebar");
const links = document.querySelectorAll(".sidebar a");
const pages = document.querySelectorAll(".section-page");
const userMenu = document.querySelector('.user-menu');
const sectionTitle = document.getElementById("section-title");

// --------------------------- Sidebar Toggle ---------------------------
toggleBtn.addEventListener("click", () => {
    if (window.innerWidth <= 768) {
        sidebar.classList.toggle("mobile-active");
    } else {
        sidebar.classList.toggle("collapsed");
    }
});

closeBtn.addEventListener("click", () => {
    sidebar.classList.remove("mobile-active");
});

// --------------------------- User Dropdown ---------------------------
userMenu.addEventListener('click', () => {
    const dropdown = userMenu.querySelector('.user-dropdown');
    dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
});

document.addEventListener('click', (e) => {
    const dropdown = document.querySelector('.user-dropdown');
    if (!userMenu.contains(e.target)) dropdown.style.display = 'none';
});

// --------------------------- Section Activation ---------------------------
function activateSection(section) {
    // Show correct page
    pages.forEach(p => p.classList.remove("active"));
    const activePage = document.getElementById(section);
    if (activePage) activePage.classList.add("active");

    // Update topbar title
    if (sectionTitle)
        sectionTitle.innerText = section.charAt(0).toUpperCase() + section.slice(1);

    // Update sidebar active link
    links.forEach(link => link.classList.remove("active"));
    const activeLink = document.querySelector(`.sidebar a[data-section="${section}"]`);
    if (activeLink) activeLink.classList.add("active");

    // Load Users section dynamically
    if (section === "users") loadUsers();

    // Update URL without reload
    history.pushState({}, "", `/admin/${section}`);
}

// --------------------------- Page Load ---------------------------
document.addEventListener("DOMContentLoaded", () => {
    const initialSection = document.body.dataset.section || "dashboard";
    activateSection(initialSection);
});

// --------------------------- Sidebar Click ---------------------------
links.forEach(link => {
    link.addEventListener("click", (e) => {
        e.preventDefault(); // prevent default anchor behavior
        const section = link.dataset.section;
        activateSection(section);
    });
});

// --------------------------- Browser Back/Forward ---------------------------
window.addEventListener('popstate', () => {
    const sectionFromURL = window.location.pathname.split("/").pop() || "dashboard";
    activateSection(sectionFromURL);
});

// --------------------------- Users Section ---------------------------
async function loadUsers() {
    try {
        const res = await apiGET("/api/users");
        const tbody = document.getElementById("users-table");
        tbody.innerHTML = "";

        res.forEach((user, index) => {
            tbody.innerHTML += `
                <tr>
                    <td>${index + 1}</td>
                    <td>${user.first_name || ""} ${user.last_name || ""}</td>
                    <td>${user.email || ""}</td>
                    <td>${user.contact_number || ""}</td>
                    <td>${user.role || "User"}</td>
                    <td>
                        <button class="delete-btn" data-id="${user._id}">Delete</button>
                    </td>
                </tr>
            `;
        });

        // Attach delete button listeners
        document.querySelectorAll(".delete-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const id = btn.getAttribute("data-id");
                deleteUser(id);
            });
        });

    } catch (err) {
        console.error("Error loading users:", err);
        const tbody = document.getElementById("users-table");
        if (tbody) tbody.innerHTML = "<tr><td colspan='5'>Failed to load users.</td></tr>";
    }
}

// --------------------------- Delete User ---------------------------
async function deleteUser(id) {
    if (!confirm("Are you sure you want to delete this user?")) return;

    try {
        const res = await apiDELETE(`/api/users/${id}`);
        if (res.success) {
            alert("User deleted successfully.");
            loadUsers(); 
        } else {
            alert(res.message || "Failed to delete user.");
        }
    } catch (err) {
        console.error("Error deleting user:", err);
        alert("Error deleting user.");
    }
}
