document.addEventListener('DOMContentLoaded', async function () {
    const orderId = new URLSearchParams(window.location.search).get('order');
    const checkoutItemsElement = document.getElementById('checkout-items');
    const checkoutSubtotalElement = document.getElementById('checkout-subtotal');
    const checkoutTaxElement = document.getElementById('checkout-tax');
    const checkoutTotalElement = document.getElementById('checkout-total');
    const placeOrderButton = document.getElementById('place-order-btn');

    async function loadCheckoutData() {
        try {
            console.log('Loading checkout data for order:', orderId);
            const response = await fetch(`https://w2k19-web.lph.local/checkout_handler.php?order_id=${orderId}`);
            const data = await response.json();
            console.log('Received cart data:', data);

            if (data.status === 'success' && data.cart_items) {
                checkoutItemsElement.innerHTML = '';

                data.cart_items.forEach(item => {
                    console.log('Processing item:', item);
                    let itemHtml = `
                        <div class="item-details">
                            <span class="item-name">${item.product_name}</span>
                            <span class="item-quantity">Quantity: ${item.quantity}</span>
                            <span class="item-price">$${(item.quantity * item.unit_price).toFixed(2)}</span>
                    `;

                    if (item.addons && item.addons.length > 0) {
                        itemHtml += '<div class="addon-details">';
                        item.addons.forEach(addon => {
                            itemHtml += `
                                <div class="addon-item">
                                    + ${addon.addon_name}: $${(addon.price * item.quantity).toFixed(2)}
                                </div>
                            `;
                        });
                        itemHtml += '</div>';
                    }

                    itemHtml += `<div class="item-total">Total: $${item.item_total.toFixed(2)}</div>`;
                    itemHtml += '</div>';
                    checkoutItemsElement.innerHTML += itemHtml;
                });

                // Update totals
                checkoutSubtotalElement.textContent = data.subtotal.toFixed(2);
                checkoutTaxElement.textContent = data.tax.toFixed(2);
                checkoutTotalElement.textContent = data.total.toFixed(2);
            } else {
                throw new Error(data.message || 'Invalid cart data received');
            }
        } catch (error) {
            console.error('Error loading checkout data:', error);
            alert('Error loading checkout data. Please try again.');
        }
    }

    placeOrderButton.addEventListener('click', async function() {
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const address = document.getElementById('address').value;

        if (!name || !email || !address) {
            alert('Please fill in all customer information fields.');
            return;
        }

        try {
            const response = await fetch('https://w2k19-web.lph.local/checkout_handler.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action: 'place_order',
                    order_id: orderId,
                    customer_info: {
                        name: name,
                        email: email,
                        address: address
                    },
                    totals: {
                        subtotal: parseFloat(checkoutSubtotalElement.textContent),
                        tax: parseFloat(checkoutTaxElement.textContent),
                        total: parseFloat(checkoutTotalElement.textContent)
                    }
                })
            });

            const data = await response.json();

            if (data.status === 'success') {
                alert('Order placed successfully!');
                localStorage.removeItem('currentOrderId');
                window.location.href = 'polloshermanoswebsite.html';
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Error placing order:', error);
            alert('Error placing order. Please try again.');
        }
    });

    // Load checkout data when page loads
    if (orderId) {
        loadCheckoutData();
    } else {
        alert('No order found. Please add items to your cart first.');
        window.location.href = 'PollosHermanosShoppingCart.html';
    }
});