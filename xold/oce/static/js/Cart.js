

function updateCartCount() {
    const cart = JSON.parse(localStorage.getItem("cart")) || [];
    const count = cart.length;
    const badge = document.getElementById("cart_count");
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? "inline-block" : "none";
    }
    document.getElementById("cart_count").textContent = count;
    
}

function addToCart(product) {
  let cart = JSON.parse(localStorage.getItem("cart")) || [];

  // Only store ID and quantity
  const existingItem = cart.find(item => item.id === product.id);
  if (existingItem) {
    existingItem.quantity += 1;
  } else {
    cart.push({ id: product.id, quantity: 1 });
  }

  localStorage.setItem("cart", JSON.stringify(cart));
  updateCartCount();
  alert(`${product.name} has been added to your cart!`);
}

document.getElementById("clear-cart").addEventListener("click", () => {
    localStorage.removeItem("cart"); // Clear the cart from localStorage

    updateCartCount();
    // alert("Cart has been cleared.");
    loadCart(); // Refresh the cart display
    location.reload();
    
});

  // Run on page load
  document.addEventListener("DOMContentLoaded", updateCartCount);

document.getElementById("checkout-form").addEventListener("submit", function(e) {
  const cart = JSON.parse(localStorage.getItem("cart")) || [];

  const formattedCart = cart.map(item => ({
    id: item.id,
    quantity: item.quantity || 1
  }));

  document.getElementById("cart-data").value = JSON.stringify(formattedCart);
});
