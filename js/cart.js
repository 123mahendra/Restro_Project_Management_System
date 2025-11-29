async function addToCart(name, price) {
    let res = await fetch("/api/cart/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, price })
    });

    let data = await res.json();
    alert(data.message);
}

async function loadCart() {
    let res = await fetch("/api/cart");
    let items = await res.json();

    let cartList = document.querySelector("#cart-items");
    cartList.innerHTML = "";

    items.forEach(item => {
        cartList.innerHTML += `
            <div class="cart-item">
                ${item.name} - $${item.price}
            </div>
        `;
    });
}
