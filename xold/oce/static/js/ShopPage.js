// Array of product objects
const products = [
    { id: 1, name: "Product A", price: "$20", image: "oce/static/images/smileyface.webp", description: "This is Product A" },
    { id: 2, name: "Product B", price: "$35", image: "oce/static/images/smileyface.webp", description: "This is Product B" },
    { id: 3, name: "Product C", price: "$50", image: "oce/static/images/smileyface.webp", description: "This is Product C" },
    { id: 4, name: "Product D", price: "$25", image: "oce/static/images/smileyface.webp", description: "This is Product D" }
];
  
// Function to display products
function displayProducts() {
    const productContainer = document.getElementById("product-container");
  
    products.forEach(product => {
      const productCard = document.createElement("div");
      productCard.classList.add("product-card");
  
      productCard.innerHTML = `
        <img src="${product.image}" alt="${product.name}">
        <h3>${product.name}</h3>
        <p>${product.description}</p>f
        <p class="price">${product.price}</p>
        <button>Add to Cart</button>
      `;
  
      productContainer.appendChild(productCard);
    });
}
  
// Call the function to display products on page load
document.addEventListener("DOMContentLoaded", displayProducts);