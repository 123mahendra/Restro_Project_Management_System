// Load menu for a given day
async function loadMenu(day) {
    try {
        const response = await fetch(`/api/menu/${day}`);
        const menuItems = await response.json();

        const container = document.getElementById("menu-container");
        container.innerHTML = "";

        menuItems.forEach(item => {
            container.innerHTML += `
                <div class="box">
                    <div class="image">
                        <img src="/static/assets/dishes/${item.image}" alt="${item.dish_name}">
                        <a href="#" class="fas fa-heart"></a>
                    </div>
                    <div class="content">
                        <div class="stars">
                            <i class="fas fa-star"></i>
                            <i class="fas fa-star"></i>
                            <i class="fas fa-star"></i>
                            <i class="fas fa-star"></i>
                            <i class="fas fa-star-half-alt"></i>
                        </div>
                        <h3>${item.dish_name}</h3>
                        <p>${item.description ?? "Delicious and tasty."}</p>
                        <a href="#" class="btn add-to-cart" data-id="${item.dish_id}">add to cart</a>
                        <span class="price">£${item.price}</span>
                    </div>
                </div>
            `;
        });

        // Attach event listeners AFTER HTML is inserted
        attachAddToCartEvents();

    } catch (err) {
        console.error("Failed to load menu:", err);
    }
}

// Add to cart functionality
function attachAddToCartEvents() {
    document.querySelectorAll(".add-to-cart").forEach(btn => {
        btn.addEventListener("click", async (e) => {
            e.preventDefault();

            const dishId = btn.getAttribute("data-id");

            const res = await fetch("/api/cart/add", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ dishId, quantity: 1 })
            });

            const data = await res.json();

            if (data.success) {
                updateCartCount();
                showToast("Added to cart!");
            } else {
                showToast("Failed: " + data.message);
            }
        });
    });
}

// Update cart count
async function updateCartCount() {
    const res = await fetch("/api/cart/count");
    const data = await res.json();

    document.getElementById("cart-count").innerText = data.count;
}

// Simple toast popup
function showToast(message) {
    alert(message);
}

// Load today's menu on page load
document.addEventListener("DOMContentLoaded", () => {
    const days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"];
    const today = days[new Date().getDay()];

    const daySelect = document.getElementById("menu-day");
    if (daySelect) {
        daySelect.value = today;
        daySelect.addEventListener("change", (event) => {
            loadMenu(event.target.value);
        });
    }

    loadMenu(today);
});
