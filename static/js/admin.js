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
    if (section === "dishes") loadDishes();
    if (section === "menu") ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"].forEach(day => loadDayMenu(day));

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


// ---------------------------- Dish Modal ----------------------------
document.getElementById("add-dish-btn").addEventListener("click", () => {
    document.getElementById("dish-modal").style.display = "flex";
});

// Close modal
document.getElementById("close-modal").addEventListener("click", () => {
    document.getElementById("dish-modal").style.display = "none";
});

// Submit dish
document.getElementById("dish-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);

    let res = await fetch("/api/dishes", {
        method: "POST",
        body: formData
    });

    let data = await res.json();

    if (data.success) {
        alert("Dish Added Successfully");
        document.getElementById("dish-modal").style.display = "none";
        e.target.reset();
        loadDishes();
    } else {
        alert("Failed to add dish");
    }
});

// ---------------------------- Load Dishes --------------------------
async function loadDishes() {
    try {
        const res = await apiGET("/api/dishes");
        const tbody = document.getElementById("dishes-table");
        tbody.innerHTML = "";

        res.forEach((dish, index) => {
            tbody.innerHTML += `
                <tr>
                    <td>${index + 1}</td>
                    <td>${dish.name || ""}</td>
                    <td>${dish.price || ""}</td>
                    <td>${dish.description || ""}</td>
                    <td>
                    ${dish.image
                    ? `<img src="/static/assets/dishes/${dish.image}" class="dish-image">`
                    : "No Image"}
                    </td>
                    <td>
                        <button class="edit-btn" data-id="${dish._id}">Edit</button>
                        <button class="delete-btn" data-id="${dish._id}">Delete</button>
                    </td>
                </tr>
            `;
        });

        document.querySelectorAll(".delete-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            deleteDish(btn.getAttribute("data-id"));
        });
    });

    document.querySelectorAll(".edit-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            openEditDishModal(btn.getAttribute("data-id"));
        });
    });

    } catch (err) {
        console.error("Error loading dishes:", err);
        const tbody = document.getElementById("dishes-table");
        if (tbody) tbody.innerHTML = "<tr><td colspan='6'>Failed to load dishes.</td></tr>";
    }
}

// ------------------- DELETE DISH -------------------
async function deleteDish(id) {
    if (!confirm("Are you sure you want to delete this dish?")) return;

    const res = await apiDELETE(`/api/dishes/${id}`);
    if (res.success) {
        alert("Dish deleted!");
        loadDishes();
    }
}

async function openEditDishModal(id) {
    let res = await fetch(`/api/dishes/${id}`);
    let dish = await res.json();

    document.getElementById("editDishId").value = dish._id;
    document.getElementById("editDishName").value = dish.name;
    document.getElementById("editDishPrice").value = dish.price;
    document.getElementById("editDishDescription").value = dish.description;

    document.getElementById("editDishModal").style.display = "flex";
}

document.getElementById("editDishForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    let id = document.getElementById("editDishId").value;

    let formData = new FormData();
    formData.append("name", document.getElementById("editDishName").value);
    formData.append("price", document.getElementById("editDishPrice").value);
    formData.append("description", document.getElementById("editDishDescription").value);

    let image = document.getElementById("editDishImage").files[0];
    if (image) formData.append("image", image);

    let res = await fetch(`/api/dishes/${id}`, {
        method: "PUT",
        body: formData
    });

    let data = await res.json();

    if (data.success) {
        alert("Dish updated!");
        document.getElementById("editDishModal").style.display = "none";
        loadDishes();
    } else {
        alert("Update failed");
    }
});

document.getElementById("closeEditDish").addEventListener("click", () => {
    document.getElementById("editDishModal").style.display = "none";
});

// ---------------------------- Menu Section ----------------------------

// Open Add Dish to Day Modal
document.querySelectorAll(".add-btn[data-day]").forEach(btn => {
    btn.addEventListener("click", async () => {
        const day = btn.getAttribute("data-day");
        openMenuModal(day);
    });
});

function openMenuModal(day) {
    // Create or use a single modal for all days
    let modal = document.getElementById("menuModal");
    if (!modal) {
        modal = document.createElement("div");
        modal.id = "menuModal";
        modal.className = "modal";
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close" id="closeMenuModal">&times;</span>
                <h3>Add Dish to <span id="modalDayName">${day}</span></h3>
                <label>Day</label>
                <input type="text" id="modalDay" readonly value="${day}">
                <label>Select Dish</label>
                <select id="modalDishSelect">
                    <option value="">Loading dishes...</option>
                </select>
                <div class="modal-buttons">
                    <button id="saveMenuDish" class="save-btn">Save</button>
                    <button id="closeMenuModalBtn" class="close-btn">Close</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        // Close handlers
        document.getElementById("closeMenuModal").onclick = () => modal.style.display = "none";
        document.getElementById("closeMenuModalBtn").onclick = () => modal.style.display = "none";
    } else {
        document.getElementById("modalDayName").innerText = day;
        document.getElementById("modalDay").value = day;
    }

    // Save button
    document.getElementById("saveMenuDish").onclick = async () => {
        const selectedDishId = document.getElementById("modalDishSelect").value;
        if (!selectedDishId) return alert("Please select a dish");

        try {
            const res = await apiPOST("/api/menu", {
                day: day,
                dishId: selectedDishId
            });
            if (res.success) {
                alert(`Dish added to ${day}`);
                modal.style.display = "none";
                loadDayMenu(day);
            }
        } catch (err) {
            console.error(err);
            alert("Failed to add dish to menu");
        }
    };

    modal.style.display = "flex";
}

// Load dishes for a specific day
async function loadDayMenu(day) {
    try {
        const res = await apiGET(`/api/menu/${day}`);
        // print(res)
        const tbody = document.getElementById(`${day.toLowerCase()}-table`);
        tbody.innerHTML = "";

        if (res.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;">No dishes added!</td></tr>`;
            return;
        }

        res.forEach((item, index) => {
            tbody.innerHTML += `
                <tr>
                    <td>${index + 1}</td>
                    <td>${item.dish_name}</td>
                    <td>£${item.price}</td>
                    <td>
                        <button class="delete-btn" data-id="${item._id}" data-day="${day}">Delete</button>
                    </td>
                </tr>
            `;
        });

        // Attach delete handlers
        document.querySelectorAll(".delete-btn").forEach(btn => {
            btn.onclick = async () => {
                if (!confirm("Delete this dish from the day?")) return;
                try {
                    await apiDELETE(`/api/menu/${btn.dataset.id}`);
                    loadDayMenu(btn.dataset.day);
                } catch (err) {
                    console.error(err);
                    alert("Failed to delete dish from menu");
                }
            };
        });

    } catch (err) {
        console.error(err);
        const tbody = document.getElementById(`${day.toLowerCase()}-table`);
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;">Failed to load dishes</td></tr>`;
    }
}

// Load all days on page load
["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"].forEach(day => loadDayMenu(day));

// All add buttons in menu section
document.querySelectorAll(".add-btn[data-day]").forEach(btn => {
    btn.addEventListener("click", async () => {
        const day = btn.dataset.day;
        document.getElementById("modalDay").innerText = day;
        document.getElementById("menuModal").style.display = "flex";

        // Load dishes into select
        const dishSelect = document.getElementById("modalDishSelect");
        dishSelect.innerHTML = ""; 

        const defaultOption = document.createElement("option");
        defaultOption.value = ""; 
        defaultOption.textContent = "-- Select a dish --"; 
        dishSelect.appendChild(defaultOption);

        const dishes = await apiGET("/api/dishes");
        dishes.forEach(d => {
            const option = document.createElement("option");
            option.value = d._id;
            option.textContent = d.name;
            dishSelect.appendChild(option);
        });

        // Save the day in form dataset
        document.getElementById("menuForm").dataset.day = day;
    });
});

// Close modal
document.getElementById("closeMenuModal").addEventListener("click", () => {
    document.getElementById("menuModal").style.display = "none";
});

// Submit modal form
document.getElementById("menuForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const day = e.target.dataset.day;
    const dishId = document.getElementById("modalDishSelect").value;

    const res = await apiPOST("/api/menu", { day, dishId });
    if (res.success) {
        alert("Dish added to " + day);
        document.getElementById("menuModal").style.display = "none";
        loadDayMenu(day);
    } else {
        alert("Failed to add dish");
    }
});


// Load announcements
function loadAnnouncements() {
    fetch("/api/announcements")
    .then(res => res.json())
    .then(data => {
        const table = document.getElementById("announcementsTable");
        table.innerHTML = "";

        data.forEach(a => {
            table.innerHTML += `
                <tr>
                    <td>${a.title}</td>
                    <td>${a.message}</td>
                    <td>${a.type}</td>
                    <td>${a.active ? "Yes" : "No"}</td>
                    <td>
                        <button class="edit-btn" onclick="editAnnouncement('${a.id}')">Edit</button>
                        <button class="delete-btn" onclick="deleteAnnouncement('${a.id}')">Delete</button>
                    </td>
                </tr>
            `;
        });
    });
}

window.editAnnouncement = function(id){
    alert("Open modal to edit announcement " + id);
};

window.deleteAnnouncement = function(id){
    fetch(`/api/announcements/${id}`, {
        method: "DELETE"
    }).then(() => loadAnnouncements());
};

const annModal = document.getElementById("announcementModal");
const addAnnBtn = document.getElementById("addAnnBtn");
const closeAnnModal = document.getElementById("closeAnnModal");

addAnnBtn.onclick = () => {
    // reset fields
    document.getElementById("annTitle").value = "";
    document.getElementById("annMessage").value = "";
    document.getElementById("annType").value = "info";
    document.getElementById("annActive").checked = true;

    annModal.style.display = "block";
};

closeAnnModal.onclick = () => {
    annModal.style.display = "none";
};

// close modal when clicking outside
window.onclick = (e) => {
    if(e.target === annModal) {
        annModal.style.display = "none";
    }
};

document.getElementById("saveAnnouncementBtn").onclick = () => {
    const newAnnouncement = {
        title: document.getElementById("annTitle").value,
        message: document.getElementById("annMessage").value,
        type: document.getElementById("annType").value,
        active: document.getElementById("annActive").checked
    };

    fetch("/api/announcements", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newAnnouncement)
    })
    .then(res => res.json())
    .then(() => {
        annModal.style.display = "none";
        loadAnnouncements();  // reload table
    });
};


// Load on section change
document.body.addEventListener("click", e => {
    if (e.target.dataset.section === "announcements") loadAnnouncements();
});

document.addEventListener("change", function (e) {
    if (e.target.classList.contains("order-status")) {
        const orderId = e.target.getAttribute("data-id");
        const newStatus = e.target.value;

        fetch("/admin/update-order-status", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ order_id: orderId, status: newStatus })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                console.log("Status updated successfully");
            }
        });
    }
});
