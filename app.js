const products = {
  p1: { id: 'p1', name: 'Everyday Canvas Tote', price: 799 },
  p2: { id: 'p2', name: 'Wireless Desk Mouse', price: 1499 },
};

const cart = new Map();
let placingOrder = false;

const currency = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
});

const els = {
  cartRows: document.querySelector('[data-testid="cart-rows"]'),
  cartTable: document.querySelector('[data-testid="cart-table"]'),
  emptyCart: document.querySelector('[data-testid="empty-cart"]'),
  orderTotal: document.querySelector('[data-testid="order-total"]'),
  validation: document.querySelector('[data-testid="validation-message"]'),
  name: document.querySelector('[data-testid="customer-name"]'),
  form: document.querySelector('#checkout-form'),
  placeOrder: document.querySelector('[data-testid="place-order"]'),
  confirmation: document.querySelector('[data-testid="confirmation"]'),
  confirmationMessage: document.querySelector('[data-testid="confirmation-message"]'),
  orderReference: document.querySelector('[data-testid="order-reference"]'),
};

function formatMoney(value) {
  return currency.format(value);
}

function cartEntries() {
  return [...cart.entries()]
    .map(([id, quantity]) => ({ product: products[id], quantity }))
    .filter(({ product, quantity }) => product && quantity > 0);
}

function cartTotal() {
  return cartEntries().reduce((sum, { product, quantity }) => sum + product.price * quantity, 0);
}

function setValidation(message, focusTarget) {
  els.validation.textContent = message;
  els.validation.hidden = false;
  if (focusTarget) focusTarget.focus();
}

function clearValidation() {
  els.validation.textContent = '';
  els.validation.hidden = true;
}

function renderCart() {
  const entries = cartEntries();
  els.cartRows.innerHTML = '';

  entries.forEach(({ product, quantity }) => {
    const row = document.createElement('tr');
    row.dataset.testid = `cart-row-${product.id}`;
    row.dataset.productId = product.id;
    row.innerHTML = `
      <td>${product.name}</td>
      <td>${formatMoney(product.price)}</td>
      <td>
        <input
          class="quantity-input"
          type="number"
          min="1"
          max="99"
          step="1"
          value="${quantity}"
          data-testid="qty-${product.id}"
          aria-label="Quantity for ${product.name}"
        />
      </td>
      <td data-testid="line-total-${product.id}">${formatMoney(product.price * quantity)}</td>
      <td><button type="button" class="remove-button" data-testid="remove-${product.id}">Remove</button></td>
    `;
    els.cartRows.append(row);
  });

  const hasItems = entries.length > 0;
  els.cartTable.hidden = !hasItems;
  els.emptyCart.hidden = hasItems;
  els.orderTotal.textContent = formatMoney(cartTotal());

  els.cartRows.querySelectorAll('.quantity-input').forEach((input) => {
    input.addEventListener('input', handleQuantityChange);
  });
  els.cartRows.querySelectorAll('.remove-button').forEach((button) => {
    button.addEventListener('click', handleRemove);
  });
}

function addToCart(id) {
  const nextQuantity = (cart.get(id) || 0) + 1;
  cart.set(id, Math.min(nextQuantity, 99));
  clearValidation();
  renderCart();
}

function handleAdd(event) {
  const button = event.target.closest('[data-add]');
  if (!button) return;
  addToCart(button.dataset.add);
}

function handleQuantityChange(event) {
  const input = event.target;
  const row = input.closest('tr');
  if (!row) return;

  const id = row.dataset.productId;
  const parsed = Number.parseInt(input.value, 10);
  const nextQuantity = Number.isFinite(parsed) ? Math.min(Math.max(parsed, 1), 99) : 1;

  cart.set(id, nextQuantity);
  input.value = String(nextQuantity);
  clearValidation();
  renderCart();
}

function handleRemove(event) {
  const button = event.target.closest('.remove-button');
  if (!button) return;

  const row = button.closest('tr');
  if (!row) return;

  cart.set(row.dataset.productId, 0);
  clearValidation();
  renderCart();
}

function makeOrderReference() {
  const suffix = Math.random().toString(36).slice(2, 10).toUpperCase();
  return `FYND-${suffix}`;
}

function handleCheckout(event) {
  event.preventDefault();
  if (placingOrder) return;

  if (cartEntries().length === 0) {
    setValidation('Your cart is empty. Add at least one item before checkout.');
    return;
  }

  const enteredName = els.name.value;
  if (enteredName.trim().length === 0) {
    setValidation('Please enter your name to place the order.', els.name);
    return;
  }

  placingOrder = true;
  els.placeOrder.disabled = true;

  const reference = makeOrderReference();
  els.confirmationMessage.textContent = `Thank you, ${enteredName.trim()}. Your order was placed successfully.`;
  els.orderReference.textContent = reference;
  els.confirmation.hidden = false;
  clearValidation();

  cart.clear();
  renderCart();
  els.name.value = '';
}

document.querySelector('.products').addEventListener('click', handleAdd);
els.name.addEventListener('input', clearValidation);
els.form.addEventListener('submit', handleCheckout);
renderCart();
