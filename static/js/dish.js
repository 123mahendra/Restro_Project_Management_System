async function loadDishes() {
    try {
        const response = await fetch("/api/dishes");
        const dishes = await response.json();

        const container = document.getElementById("dishes-container");
        container.innerHTML = "";

        dishes.forEach(dish => {
            container.innerHTML += `
                <div class="box">
                    <a href="#" class="fas fa-heart"></a>
                    <a href="#" class="fas fa-eye"></a>

                    <img src="/static/assets/dishes/${dish.image}" alt="${dish.name}">
                    <h3>${dish.name}</h3>

                    <div class="stars">
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                        <i class="fas fa-star"></i>
                    </div>

                    <span>£${dish.price}</span>
                    <button class="btn btn-primary add-to-cart" data-id="${dish._id}">
                        Add to Cart
                    </button>
                </div>
            `;
        });

    } catch (error) {
        console.error("Error loading dishes:", error);
    }
}

// Load dishes when page loads
document.addEventListener("DOMContentLoaded", loadDishes);
