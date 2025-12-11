document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector(".order form");

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const name = document.querySelector('input[placeholder="enter your name"]').value;
        const number = document.querySelector('input[placeholder="enter your number"]').value;
        const order = document.querySelector('input[placeholder="enter food name"]').value;
        const extra = document.querySelector('input[placeholder="extra with food"]').value;
        const quantity = document.querySelector('input[placeholder="how many orders"]').value;
        const datetime = document.querySelector('input[type="datetime-local"]').value;
        const address = document.querySelectorAll('textarea')[0].value;
        const message = document.querySelectorAll('textarea')[1].value;

        const orderData = {
            name,
            number,
            order,
            extra,
            quantity,
            datetime,
            address,
            message
        };

        try {
            const res = await fetch("http://localhost:5000/api/order", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(orderData)
            });

            const data = await res.json();

            if (res.ok) {
                alert("Order placed successfully!");
                form.reset();
            } else {
                alert("Error: " + data.msg);
            }
        } catch (err) {
            alert("Failed to connect to server.");
            console.error(err);
        }
    });
});
