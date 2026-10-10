// =====================================================================
// TASTY HEAVEN — FRONTEND <-> FLASK BACKEND BRIDGE
// =====================================================================
// This file preserves the original cart UX (Local Storage based) but now:
//   - Menu items are loaded from the Flask + SQLite backend (GET /api/menu)
//   - Login / Signup / Logout use Flask sessions (POST /api/login etc.)
//   - Reservation & Contact forms are saved to SQLite
//   - Checkout sends the cart to the backend, which recalculates the total
//     from the DATABASE prices (the frontend total is for display only)
// =====================================================================

const DELIVERY_FEE = 40;

// ---------------------------------------------------------------------
// Small fetch() helper — always sends/receives JSON and cookies (session)
// ---------------------------------------------------------------------
async function apiRequest(url, method = "GET", body = null) {
    const options = {
        method,
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin",
    };
    if (body !== null) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);
    let data = {};
    try {
        data = await response.json();
    } catch (e) {
        data = { success: false, message: "Unexpected server response." };
    }
    data._status = response.status;
    return data;
}

function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function showFormMessage(text, isError = false) {
    const box = document.getElementById("formMessage");
    if (!box) {
        // Fall back to alert if the page has no message container
        alert(text);
        return;
    }
    box.textContent = text;
    box.className = "form-message " + (isError ? "form-error" : "form-success");
    box.style.display = "block";
}

// ================================
// Cart (Local Storage) — same behaviour as before, now item-aware of DB id
// ================================

let cart = JSON.parse(localStorage.getItem("cart")) || [];

function saveCart() {
    localStorage.setItem("cart", JSON.stringify(cart));
}
function updateCartBadge() {
    const badge = document.querySelector(".cart-badge");
    if (!badge) return;

    const count = cart.reduce((total, item) => total + item.quantity, 0);

    badge.textContent = count;
    badge.style.display = count > 0 ? "flex" : "none";
}
// Called from the dynamically rendered "Add to Cart" buttons on menu.html
// id = menu item's database id (REQUIRED for checkout to work)
function addToCart(id, name, price, image) {
    let item = cart.find(food => food.id === id);

    if (item) {
        item.quantity++;
    } else {
        cart.push({ id: id, name: name, price: price, image: image, quantity: 1 });
    }

    saveCart();
    updateCartBadge();
    alert(name + " added to cart!");
}

// ================================
// Display Cart (cart.html)
// ================================

function displayCart() {
    const cartItems = document.getElementById("cartItems");
    if (!cartItems) return;

    cartItems.innerHTML = "";
    let subtotal = 0;

    if (cart.length === 0) {
        cartItems.innerHTML = `
        <div class="empty-cart">
        <i class="fa-solid fa-cart-shopping"></i>
        <h2>Your Cart is Empty</h2>
        <p>Add delicious food from Menu.</p>
        <a href="menu.html">Go To Menu</a>
        </div>
        `;
        document.getElementById("subtotal").innerHTML = 0;
        document.getElementById("grandTotal").innerHTML = 0;
        document.getElementById("deliveryFee").innerHTML = 0;
        return;
    }

    cart.forEach((item, index) => {
        subtotal += item.price * item.quantity;

        cartItems.innerHTML += `
<div class="cart-item">
<div class="cart-left">
<img src="${escapeHtml(item.image)}">
<div class="cart-details">
<h3>${escapeHtml(item.name)}</h3>
<p>Fresh &amp; Delicious</p>
<div class="quantity">
<button onclick="decreaseQty(${index})">-</button>
<span>${item.quantity}</span>
<button onclick="increaseQty(${index})">+</button>
</div>
<button class="remove-btn" onclick="removeItem(${index})">Remove</button>
</div>
</div>
<div class="cart-price">₹${item.price * item.quantity}</div>
</div>
`;
    });

    document.getElementById("subtotal").innerHTML = subtotal;
    document.getElementById("grandTotal").innerHTML = subtotal + DELIVERY_FEE;
}

function increaseQty(index) {
    cart[index].quantity++;
    saveCart();
    displayCart();
}

function decreaseQty(index) {
    if (cart[index].quantity > 1) {
        cart[index].quantity--;
    } else {
        cart.splice(index, 1);
    }
    saveCart();
    displayCart();
}

function removeItem(index) {
    cart.splice(index, 1);
    saveCart();
    displayCart();
}

// ================================
// Checkout — sends cart to Flask, which recalculates the total from SQLite
// ================================

async function handleCheckout() {
    if (cart.length === 0) {
        alert("Your Cart is Empty!");
        return;
    }

    // Must be logged in to place an order
    const me = await apiRequest("/api/me");
    if (!me.authenticated) {
        alert("Please login to place your order.");
        sessionStorage.setItem("redirectAfterLogin", "cart.html");
        window.location.href = "login.html";
        return;
    }

    const payload = {
        items: cart.map(item => ({ menu_item_id: item.id, quantity: item.quantity })),
    };

    const result = await apiRequest("/api/orders", "POST", payload);

    if (result.success) {
        alert("Order Placed Successfully! Order #" + result.order.id +
              " — Total ₹" + result.order.total_amount);
        cart = [];
        localStorage.removeItem("cart");
        displayCart();
        window.location.href = "orders.html";
    } else {
        alert(result.message || "Could not place your order. Please try again.");
    }
}

// ================================
// Menu — loaded from the backend (GET /api/menu)
// ================================

// Which grid each backend category belongs to on menu.html
const CATEGORY_TO_GRID = {
    "Veg": "menuGridMain",
    "Non Veg": "menuGridMain",
    "Starters": "menuGridMain",
    "Desserts": "menuGridDesserts",
    "Drinks": "menuGridDrinks",
};

function buildMenuCard(item) {
    const card = document.createElement("div");
    card.className = "menu-card";
    card.dataset.category = item.category;

    card.innerHTML = `
<img src="${escapeHtml(item.image)}" alt="${escapeHtml(item.name)}">
<h3>${escapeHtml(item.name)}</h3>
<p>${escapeHtml(item.description || "")}</p>
<div class="rating">★★★★★</div>
<h2>₹${item.price}</h2>
<button class="add-cart-btn" data-id="${item.id}" data-name="${escapeHtml(item.name)}" data-price="${item.price}" data-image="${escapeHtml(item.image)}">Add to Cart</button>
`;
    return card;
}

async function loadMenu() {
    const mainGrid = document.getElementById("menuGridMain");
    if (!mainGrid) return; // Not on menu.html

    const desertGrid = document.getElementById("menuGridDesserts");
    const drinkGrid = document.getElementById("menuGridDrinks");

    const result = await apiRequest("/api/menu");

    if (!result.success || !result.menu || result.menu.length === 0) {
        mainGrid.innerHTML = "<p class='menu-loading'>No menu items available right now.</p>";
        return;
    }

    mainGrid.innerHTML = "";
    if (desertGrid) desertGrid.innerHTML = "";
    if (drinkGrid) drinkGrid.innerHTML = "";

    result.menu.forEach(item => {
        if (!item.available) return;
        const gridId = CATEGORY_TO_GRID[item.category] || "menuGridMain";
        const grid = document.getElementById(gridId) || mainGrid;
        grid.appendChild(buildMenuCard(item));
    });

    // Event delegation for "Add to Cart" buttons (works for all 3 grids)
    [mainGrid, desertGrid, drinkGrid].forEach(grid => {
        if (!grid) return;
        grid.addEventListener("click", e => {
            const btn = e.target.closest(".add-cart-btn");
            if (!btn) return;
            addToCart(
                parseInt(btn.dataset.id, 10),
                btn.dataset.name,
                parseFloat(btn.dataset.price),
                btn.dataset.image
            );
        });
    });

    setupCategoryFilter();
}

function setupCategoryFilter() {
    const buttons = document.querySelectorAll(".cat-btn");
    if (!buttons.length) return;

    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            buttons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const category = btn.dataset.category;
            const cards = document.querySelectorAll(".menu-page .menu-card, .dessert-section .menu-card, .drink-section .menu-card");

            cards.forEach(card => {
                if (category === "All" || card.dataset.category === category) {
                    card.style.display = "";
                } else {
                    card.style.display = "none";
                }
            });
        });
    });
}

// ================================
// Auth — Login / Signup / Logout
// ================================

async function handleLoginSubmit(e) {
    e.preventDefault();

    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value;

    const result = await apiRequest("/api/login", "POST", { email, password });

    if (result.success) {
        showFormMessage("Login successful! Redirecting...", false);
        const redirectTo = sessionStorage.getItem("redirectAfterLogin");
        sessionStorage.removeItem("redirectAfterLogin");
        setTimeout(() => {
            window.location.href = redirectTo || "index.html";
        }, 700);
    } else {
        showFormMessage(result.message || "Login failed.", true);
    }
}

async function handleSignupSubmit(e) {
    e.preventDefault();

    const name = document.getElementById("signupName").value.trim();
    const email = document.getElementById("signupEmail").value.trim();
    const password = document.getElementById("signupPassword").value;
    const confirmPassword = document.getElementById("signupConfirmPassword").value;

    if (password !== confirmPassword) {
        showFormMessage("Passwords do not match.", true);
        return;
    }

    const result = await apiRequest("/api/register", "POST", { name, email, password });

    if (result.success) {
        showFormMessage("Account created! Redirecting...", false);
        setTimeout(() => { window.location.href = "index.html"; }, 700);
    } else {
        showFormMessage(result.message || "Registration failed.", true);
    }
}

async function logoutUser() {
    await apiRequest("/api/logout", "POST");
    window.location.href = "index.html";
}

// ================================
// Reservation
// ================================

async function handleReservationSubmit(e) {
    e.preventDefault();

    const payload = {
        name: document.getElementById("resName").value.trim(),
        email: document.getElementById("resEmail").value.trim(),
        phone: document.getElementById("resPhone").value.trim(),
        date: document.getElementById("resDate").value,
        time: document.getElementById("resTime").value,
        guests: document.getElementById("resGuests").value,
        special_request: document.getElementById("resSpecialRequest").value.trim(),
    };

    const result = await apiRequest("/api/reservations", "POST", payload);

    if (result.success) {
        showFormMessage(result.message, false);
        document.getElementById("reservationForm").reset();
    } else {
        showFormMessage(result.message || "Could not create your reservation.", true);
    }
}

// ================================
// Contact
// ================================

async function handleContactSubmit(e) {
    e.preventDefault();

    const payload = {
        name: document.getElementById("contactName").value.trim(),
        email: document.getElementById("contactEmail").value.trim(),
        subject: document.getElementById("contactSubject").value.trim(),
        message: document.getElementById("contactMessage").value.trim(),
    };

    const result = await apiRequest("/api/contact", "POST", payload);

    if (result.success) {
        showFormMessage(result.message, false);
        document.getElementById("contactForm").reset();
    } else {
        showFormMessage(result.message || "Could not send your message.", true);
    }
}

// ================================
// Order History (orders.html)
// ================================

async function loadOrderHistory() {
    const container = document.getElementById("orderHistoryList");
    if (!container) return;

    const result = await apiRequest("/api/orders");

    if (!result.success) {
        container.innerHTML = `<div class="empty-cart"><h2>Please login to view your orders.</h2><a href="login.html">Login</a></div>`;
        return;
    }

    if (!result.orders || result.orders.length === 0) {
        container.innerHTML = `<div class="empty-cart"><h2>No orders yet</h2><p>Your placed orders will show up here.</p><a href="menu.html">Go To Menu</a></div>`;
        return;
    }

    container.innerHTML = result.orders.map(order => `
        <div class="order-card">
            <div class="order-card-header">
                <h3>Order #${order.id}</h3>
                <span class="order-status status-${escapeHtml(order.status)}">${escapeHtml(order.status)}</span>
            </div>
            <p class="order-date">${new Date(order.created_at).toLocaleString()}</p>
            <ul class="order-items-list">
                ${order.items.map(it => `<li>${escapeHtml(it.name)} &times; ${it.quantity} — ₹${it.subtotal}</li>`).join("")}
            </ul>
            <p class="order-total">Total: ₹${order.total_amount}</p>
        </div>
    `).join("");
}

// ================================
// Page bootstrap
// ================================

document.addEventListener("DOMContentLoaded", () => {
    // Menu page
    loadMenu();

    // Cart page
    displayCart();
    updateCartBadge();
    const checkoutBtn = document.getElementById("checkoutBtn");
    if (checkoutBtn) {
        checkoutBtn.addEventListener("click", handleCheckout);
    }

    // Login page
    const loginForm = document.getElementById("loginForm");
    if (loginForm) loginForm.addEventListener("submit", handleLoginSubmit);

    // Signup page
    const signupForm = document.getElementById("signupForm");
    if (signupForm) signupForm.addEventListener("submit", handleSignupSubmit);

    // Reservation page
    const reservationForm = document.getElementById("reservationForm");
    if (reservationForm) reservationForm.addEventListener("submit", handleReservationSubmit);

    // Contact page
    const contactForm = document.getElementById("contactForm");
    if (contactForm) contactForm.addEventListener("submit", handleContactSubmit);

    // Order history page
    loadOrderHistory();
});
