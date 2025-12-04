async function loadCart() {
    let res = await fetch("/api/cart");
    let items = await res.json();

    const container = document.getElementById("cart-items");
    container.innerHTML = "";

    let subtotal = 0;

    items.forEach((item, index) => {
        let total = item.price * item.qty;
        subtotal += total;

        container.innerHTML += `
            <div class="cart-item">
                <div class="item-info">
                    <h4>${item.name}</h4>
                    <p class="item-price">$${item.price}</p>
                </div>

                <div class="qty-box">
                    <button onclick="updateQty(${index}, -1)">−</button>
                    <span>${item.qty}</span>
                    <button onclick="updateQty(${index}, 1)">+</button>
                </div>

                <button class="remove-btn" onclick="removeItem(${index})">Remove</button>
            </div>
        `;
    });

    let tax = subtotal * 0.10;
    let total = subtotal + tax;

    document.getElementById("subtotal").innerText = `$${subtotal.toFixed(2)}`;
    document.getElementById("tax").innerText = `$${tax.toFixed(2)}`;
    document.getElementById("total").innerText = `$${total.toFixed(2)}`;
}

async function updateQty(index, change) {
    await fetch(`/api/cart/update/${index}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ change })
    });

    loadCart();
}

async function removeItem(index) {
    await fetch(`/api/cart/remove/${index}`, { method: "DELETE" });
    loadCart();
}
