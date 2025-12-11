let menu = docuument.querySelector('#menu-icon');
let navlist = docuument.querySelector('.navlist');

menu.onclick = () => {
    menu.classList.toggle('bx-x');
    navlist.classList.toggle('open');
};

window.onscroll = () => {
    menu.classList.remove('bx-x');
    navlist.classList.remove('open');
};
let cart = [];
//product page
// Function to render products dynamically
const renderProducts = () => {
    const productList = document.getElementById("product-list");
    products.forEach(product => {
        const productRow = document.createElement("div");
        productRow.classList.add("row");

        productRow.innerHTML = `
            <div class="row-img">
                <img src="${product.image}" alt="${product.name}">
            </div>
            <h5>${product.name}</h5>
            <h6>$${product.price.toFixed(2)}</h6>
            <div class="s-btn">
                <a href="#" data-id="${product.id}" class="add-to-cart">
                    Add to Cart
                    <i class="ri-shopping-cart-line"></i>
                </a>
            </div>
        `;
        productList.appendChild(productRow);
    });
};

// Function to handle Add to Cart
const handleAddToCart = (e) => {
    if (e.target.classList.contains("add-to-cart")) {
        e.preventDefault();
        const productId = parseInt(e.target.dataset.id);
        const product = products.find(p => p.id === productId);

        if (product) {
            cart.push(product);
            alert(`${product.name} added to cart!`);
        }
    }
};

// Render products when the page loads
renderProducts();

// Add event listener for Add to Cart buttons
document.getElementById("product-list").addEventListener("click", handleAddToCart);


//page blog
const blogContainer = document.getElementById("blog-content");

blogData.forEach(blog => {
    const blogBox = document.createElement("div");
    blogBox.classList.add("blog-box");

    blogBox.innerHTML = `
        <div class="blog-img">
            <img src="${blog.image}" alt="${blog.title}" />
        </div>
        <div class="blog-in">
            <div class="blog-left">
                <h3>${blog.date}</h3>
            </div>
            <div class="bbb-in">
                <h6>${blog.month}</h6>
            </div>
        </div>
        <div class="blog-right">
            <h4>${blog.title}</h4>
            <p>${blog.postDetails}</p>
        </div>
    `;

    blogContainer.appendChild(blogBox);
});