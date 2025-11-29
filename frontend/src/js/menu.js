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
