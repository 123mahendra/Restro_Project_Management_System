let cart = [];

async function loadCart() {
    const res = await fetch('/api/cart');
    cart = await res.json();
    renderCart();
}

function renderCart() {
    const container = document.getElementById('cart-items');
    container.innerHTML = '';
    let total = 0;
    cart.forEach(item => {
        const div = document.createElement('div');
        div.innerHTML = `${item.name} x${item.qty} - $${item.price * item.qty}`;
        container.appendChild(div);
        total += item.price * item.qty;
    });
    document.getElementById('cart-total').innerText = '$' + total.toFixed(2);
}

async function addToCart(itemId) {
    await fetch('/api/cart/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: itemId, qty: 1 })
    });
    await loadCart();
}

async function checkoutCart() {
    const phone = document.getElementById('checkout-phone').value;
    const pickup = document.getElementById('checkout-pickup').value;
    const res = await fetch('/api/cart/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, pickup_time: pickup })
    });
    if (res.ok) {
        alert('Order placed!');
        cart = [];
        renderCart();
    }
}

document.addEventListener('DOMContentLoaded', loadCart);

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
