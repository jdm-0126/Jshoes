function addToCart(productId) {
    fetch(`/add_to_cart/${productId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Added to Cart!',
                    text: 'Product added to cart successfully',
                    showCancelButton: true,
                    confirmButtonText: 'View Cart',
                    cancelButtonText: 'Continue Shopping',
                    timer: 5000,
                    timerProgressBar: true,
                    width: '90%',
                    heightAuto: false
                }).then((result) => {
                    if (result.isConfirmed) {
                        window.location.href = '/cart';
                    }
                });
                updateCartCount(data.cart_count);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error!',
                text: 'Error adding product to cart',
                timer: 5000,
                width: '90%',
                heightAuto: false
            });
        });
}

function updateCartCount(count) {
    const cartLink = document.getElementById('cart-link');
    if (cartLink) {
        cartLink.innerHTML = count > 0 ? `Cart (${count})` : 'Cart';
    }
}

function removeFromCart(itemId) {
    Swal.fire({
        title: 'Remove Item?',
        text: 'Are you sure you want to remove this item from cart?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, remove it!',
        cancelButtonText: 'Cancel'
    }).then((result) => {
        if (!result.isConfirmed) return;
    fetch(`/cart/remove/${itemId}`, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                if (typeof data.cart_count !== 'undefined') {
                    updateCartCount(data.cart_count);
                }
                location.reload();
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error!',
                    text: 'Error removing item: ' + (data.error || 'unknown'),
                    timer: 5000,
                    width: '90%',
                    heightAuto: false
                });
            }
        }).catch(err => { 
            Swal.fire({
                icon: 'error',
                title: 'Request Failed!',
                text: 'Failed to remove item from cart',
                timer: 5000,
                width: '90%',
                heightAuto: false
            });
            console.error(err); 
        });
    });
}

function clearCart() {
    Swal.fire({
        title: 'Clear Cart?',
        text: 'Are you sure you want to clear your entire cart?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, clear it!',
        cancelButtonText: 'Cancel'
    }).then((result) => {
        if (!result.isConfirmed) return;
    fetch('/cart/clear', { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                updateCartCount(0);
                location.reload();
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error!',
                    text: 'Error clearing cart: ' + (data.error || 'unknown'),
                    timer: 5000,
                    width: '90%',
                    heightAuto: false
                });
            }
        }).catch(err => { 
            Swal.fire({
                icon: 'error',
                title: 'Request Failed!',
                text: 'Failed to clear cart',
                timer: 5000,
                width: '90%',
                heightAuto: false
            });
            console.error(err); 
        });
    });
}

function updateQuantity(itemId, quantity) {
    if (quantity < 1) quantity = 1;
    
    const formData = new FormData();
    formData.append('quantity', quantity);
    
    fetch(`/cart/update/${itemId}`, {
        method: 'POST',
        body: formData
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            updateCartCount(data.cart_count);
            if (typeof data.total !== 'undefined') {
                document.getElementById('cart-total').textContent = '₱' + Number(data.total).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2});
            }
            location.reload();
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Error!',
                text: 'Error updating quantity: ' + (data.error || 'unknown'),
                timer: 5000,
                width: '90%',
                heightAuto: false
            });
        }
    })
    .catch(err => {
        Swal.fire({
            icon: 'error',
            title: 'Request Failed!',
            text: 'Failed to update quantity',
            timer: 5000,
            width: '90%',
            heightAuto: false
        });
        console.error(err);
    });
}

// Initialize cart count on page load
document.addEventListener('DOMContentLoaded', function() {
    // Get cart count from session or server
    fetch('/cart/count')
        .then(response => response.json())
        .then(data => {
            if (data.cart_count !== undefined) {
                updateCartCount(data.cart_count);
            }
        })
        .catch(error => console.log('Cart count fetch failed:', error));
});