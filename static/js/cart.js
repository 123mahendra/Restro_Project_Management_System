async function loadCart() {
    let res = await fetch("/api/cart");

    if (res.status === 401) {
        document.getElementById("cart-container").innerHTML = "Login required!";
        return;
    }

    let cart = await res.json();

    let container = document.getElementById("cart-container");
    let total = 0;

    container.innerHTML = "";

    cart.items.forEach((item, index) => {
        total += item.price * item.quantity;

        container.innerHTML += `
            <div class="cart-item">
                <h3>${item.name}</h3>
                <p>$${item.price}</p>
                <input type="number" min="1" value="${item.quantity}"
                       onchange="updateQuantity('${item.product_id}', this.value)">
                <button onclick="removeItem('${item.product_id}')">Remove</button>
            </div>
        `;
    });

    document.getElementById("total-price").innerText = "Total: $" + total;
}

async function updateQuantity(pid, qty) {
    await fetch("/api/cart/update", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({product_id: pid, quantity: parseInt(qty)})
    });

    loadCart();
}

async function removeItem(pid) {
    await fetch("/api/cart/remove", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({product_id: pid})
    });

    loadCart();
}

async function checkout() {
    let res = await fetch("/create-checkout-session", {
        method: "POST"
    });

    let data = await res.json();
    location.href = data.url;
}

loadCart();
