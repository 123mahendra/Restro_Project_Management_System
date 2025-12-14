async function loadDishes() {
    try {
        const response = await fetch("/api/dishes");
        const dishes = await response.json();

        const container = document.getElementById("dishes-container");
        container.innerHTML = "";

        dishes.forEach(dish => {
            container.innerHTML += `
                <div class="box">
                    <img src="/static/assets/dishes/${dish.image}" alt="${dish.name}">
                    <h3>${dish.name}</h3>
                    <span>€${dish.price}</span>

                    <button class="btn add-to-cart" data-id="${dish._id}">
                        Add to Cart
                    </button>
                </div>
            `;
        });

        attachCartEvents(); 

    } catch (error) {
        console.error("Error loading dishes:", error);
    }
}

// Attach click events to buttons
function attachCartEvents() {
    document.querySelectorAll(".add-to-cart").forEach(btn => {
        btn.addEventListener("click", async () => {
            const id = btn.getAttribute("data-id");

            const res = await fetch("/api/cart/add", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    dishId: id,
                    quantity: 1
                })
            });

            const data = await res.json();

            if (data.success) {
                updateCartCount();
                showToast("Added to cart!");
            } else {
                showToast("Failed to add item");
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

document.addEventListener("DOMContentLoaded", loadDishes);
