const cart = JSON.parse(localStorage.getItem("cart")) || [];

document.querySelectorAll(".add-to-cart").forEach(btn => {
    btn.addEventListener("click", () => {
        const item = {
            name: btn.dataset.name,
            price: btn.dataset.price
        };

        cart.push(item);
        localStorage.setItem("cart", JSON.stringify(cart));

        alert(`${item.name} added to cart!`);
    });
});

async function loadMenu(day) {
    try {

        // const today = new Date();
        // const day = today.toLocaleDateString('en-US', { weekday: 'long' });
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
                        <a href="#" class="btn">add to cart</a>
                        <span class="price">£${item.price}</span>
                    </div>
                </div>
            `;
        });

    } catch (err) {
        console.error("Failed to load menu:", err);
    }
}

// Load today's menu on page load
document.addEventListener("DOMContentLoaded", () => {
    const days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"];
    const today = days[new Date().getDay()];

    document.getElementById("menu-day").value = today;
    loadMenu(today);
});

// Change menu when dropdown changes
document.getElementById("menu-day").addEventListener("change", (event) => {
    loadMenu(event.target.value);
});

document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll(".add-to-cart").forEach(btn => {
        btn.addEventListener("click", async () => {
            const dishId = btn.dataset.id;

            const res = await fetch("/api/cart/add", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ dishId, quantity: 1 })
            });

            const data = await res.json();

            alert(data.message);

            if (data.success) {
                updateCartCount();
            }
        });
    });

    function updateCartCount() {
        fetch("/api/cart/count")
            .then(res => res.json())
            .then(data => {
                const badge = document.getElementById("cart-count");
                badge.textContent = data.count;
            });
    }

    updateCartCount();
});
