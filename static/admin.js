// =====================================================================
// TASTY HEAVEN — ADMIN DASHBOARD
// =====================================================================
// Relies on apiRequest(), escapeHtml() and logoutUser() defined in app.js
// (app.js is loaded before this file on admin.html).
// =====================================================================

let adminMenuItems = [];

function showAdminMessage(text, isError = false) {
    const box = document.getElementById("adminFormMessage");
    if (!box) return;
    box.textContent = text;
    box.className = "form-message " + (isError ? "form-error" : "form-success");
    box.style.display = "block";
    setTimeout(() => { box.style.display = "none"; }, 4000);
}

// ---------------------------------------------------------------------
// Guard: verify the logged-in user is actually an admin before showing
// any dashboard content or firing off admin API calls.
// ---------------------------------------------------------------------
async function verifyAdminAccess() {
    const me = await apiRequest("/api/me");

    if (!me.authenticated || me.user.role !== "admin") {
        document.getElementById("adminGuard").style.display = "block";
        document.getElementById("adminContent").style.display = "none";
        return false;
    }
    return true;
}

// ---------------------------------------------------------------------
// Tabs
// ---------------------------------------------------------------------
function setupAdminTabs() {
    const buttons = document.querySelectorAll(".admin-tab-btn");
    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            buttons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            document.querySelectorAll(".admin-tab-panel").forEach(panel => {
                panel.style.display = panel.id === btn.dataset.tab ? "block" : "none";
            });
        });
    });
}

// ---------------------------------------------------------------------
// Stats
// ---------------------------------------------------------------------
async function loadAdminStats() {
    const result = await apiRequest("/api/admin/stats");
    if (!result.success) return;

    document.getElementById("statUsers").textContent = result.stats.total_users;
    document.getElementById("statOrders").textContent = result.stats.total_orders;
    document.getElementById("statReservations").textContent = result.stats.total_reservations;
    document.getElementById("statPending").textContent = result.stats.pending_reservations;
    document.getElementById("statRevenue").textContent = result.stats.total_revenue;
}

// ---------------------------------------------------------------------
// Menu management
// ---------------------------------------------------------------------
async function loadAdminMenu() {
    const tbody = document.querySelector("#menuTable tbody");
    const result = await apiRequest("/api/menu");

    if (!result.success || result.menu.length === 0) {
        tbody.innerHTML = "<tr><td colspan='5'>No menu items yet.</td></tr>";
        return;
    }

    adminMenuItems = result.menu;

    tbody.innerHTML = result.menu.map(item => `
        <tr>
            <td>${escapeHtml(item.name)}</td>
            <td>${escapeHtml(item.category)}</td>
            <td>₹${item.price}</td>
            <td>${item.available ? "Yes" : "No"}</td>
            <td>
                <button class="admin-btn-small" onclick="editMenuItem(${item.id})">Edit</button>
                <button class="admin-btn-small admin-btn-danger" onclick="deleteMenuItem(${item.id})">Delete</button>
            </td>
        </tr>
    `).join("");
}

function editMenuItem(id) {
    const item = adminMenuItems.find(i => i.id === id);
    if (!item) return;

    document.getElementById("menuItemForm").style.display = "flex";
    document.getElementById("menuItemId").value = item.id;
    document.getElementById("menuItemName").value = item.name;
    document.getElementById("menuItemDescription").value = item.description || "";
    document.getElementById("menuItemPrice").value = item.price;
    document.getElementById("menuItemImage").value = item.image || "";
    document.getElementById("menuItemCategory").value = item.category;
    document.getElementById("menuItemAvailable").checked = !!item.available;

    document.getElementById("menuItemForm").scrollIntoView({ behavior: "smooth" });
}

async function deleteMenuItem(id) {
    if (!confirm("Delete this menu item? This cannot be undone.")) return;

    const result = await apiRequest(`/api/menu/${id}`, "DELETE");
    if (result.success) {
        showAdminMessage("Menu item deleted.");
        loadAdminMenu();
    } else {
        showAdminMessage(result.message || "Could not delete item.", true);
    }
}

async function handleMenuItemFormSubmit(e) {
    e.preventDefault();

    const id = document.getElementById("menuItemId").value;

    const payload = {
        name: document.getElementById("menuItemName").value.trim(),
        description: document.getElementById("menuItemDescription").value.trim(),
        price: parseFloat(document.getElementById("menuItemPrice").value),
        image: document.getElementById("menuItemImage").value.trim(),
        category: document.getElementById("menuItemCategory").value,
        available: document.getElementById("menuItemAvailable").checked,
    };

    let result;
    if (id) {
        result = await apiRequest(`/api/menu/${id}`, "PUT", payload);
    } else {
        result = await apiRequest("/api/menu", "POST", payload);
    }

    if (result.success) {
        showAdminMessage(id ? "Menu item updated." : "Menu item created.");
        resetMenuItemForm();
        loadAdminMenu();
    } else {
        showAdminMessage(result.message || "Could not save item.", true);
    }
}

function resetMenuItemForm() {
    document.getElementById("menuItemForm").reset();
    document.getElementById("menuItemId").value = "";
    document.getElementById("menuItemAvailable").checked = true;
    document.getElementById("menuItemForm").style.display = "none";
}

// ---------------------------------------------------------------------
// Orders
// ---------------------------------------------------------------------
const ORDER_STATUSES = ["placed", "preparing", "out-for-delivery", "delivered", "cancelled"];

async function loadAdminOrders() {
    const tbody = document.querySelector("#ordersTable tbody");
    const result = await apiRequest("/api/admin/orders");

    if (!result.success || result.orders.length === 0) {
        tbody.innerHTML = "<tr><td colspan='7'>No orders yet.</td></tr>";
        return;
    }

    tbody.innerHTML = result.orders.map(order => `
        <tr>
            <td>#${order.id}</td>
            <td>User #${order.user_id}</td>
            <td>${order.items.map(it => `${escapeHtml(it.name)} x${it.quantity}`).join(", ")}</td>
            <td>₹${order.total_amount}</td>
            <td>${escapeHtml(order.status)}</td>
            <td>${new Date(order.created_at).toLocaleString()}</td>
            <td>
                <select id="orderStatus_${order.id}">
                    ${ORDER_STATUSES.map(s => `<option value="${s}" ${s === order.status ? "selected" : ""}>${s}</option>`).join("")}
                </select>
                <button class="admin-btn-small" onclick="updateOrderStatus(${order.id})">Update</button>
            </td>
        </tr>
    `).join("");
}

async function updateOrderStatus(orderId) {
    const status = document.getElementById(`orderStatus_${orderId}`).value;
    const result = await apiRequest(`/api/admin/orders/${orderId}`, "PUT", { status });

    if (result.success) {
        showAdminMessage(`Order #${orderId} updated to "${status}".`);
        loadAdminStats();
    } else {
        showAdminMessage(result.message || "Could not update order.", true);
    }
}

// ---------------------------------------------------------------------
// Reservations
// ---------------------------------------------------------------------
const RESERVATION_STATUSES = ["pending", "confirmed", "cancelled"];

async function loadAdminReservations() {
    const tbody = document.querySelector("#reservationsTable tbody");
    const result = await apiRequest("/api/admin/reservations");

    if (!result.success || result.reservations.length === 0) {
        tbody.innerHTML = "<tr><td colspan='7'>No reservations yet.</td></tr>";
        return;
    }

    tbody.innerHTML = result.reservations.map(r => `
        <tr>
            <td>${escapeHtml(r.name)}</td>
            <td>${escapeHtml(r.email)}<br>${escapeHtml(r.phone)}</td>
            <td>${escapeHtml(r.reservation_date)} ${escapeHtml(r.reservation_time)}</td>
            <td>${escapeHtml(r.guests)}</td>
            <td>${escapeHtml(r.special_request || "-")}</td>
            <td>${escapeHtml(r.status)}</td>
            <td>
                <select id="resStatus_${r.id}">
                    ${RESERVATION_STATUSES.map(s => `<option value="${s}" ${s === r.status ? "selected" : ""}>${s}</option>`).join("")}
                </select>
                <button class="admin-btn-small" onclick="updateReservationStatus(${r.id})">Update</button>
            </td>
        </tr>
    `).join("");
}

async function updateReservationStatus(reservationId) {
    const status = document.getElementById(`resStatus_${reservationId}`).value;
    const result = await apiRequest(`/api/admin/reservations/${reservationId}`, "PUT", { status });

    if (result.success) {
        showAdminMessage(`Reservation #${reservationId} updated to "${status}".`);
        loadAdminStats();
    } else {
        showAdminMessage(result.message || "Could not update reservation.", true);
    }
}

// ---------------------------------------------------------------------
// Users
// ---------------------------------------------------------------------
async function loadAdminUsers() {
    const tbody = document.querySelector("#usersTable tbody");
    const result = await apiRequest("/api/admin/users");

    if (!result.success || result.users.length === 0) {
        tbody.innerHTML = "<tr><td colspan='4'>No users yet.</td></tr>";
        return;
    }

    tbody.innerHTML = result.users.map(u => `
        <tr>
            <td>${escapeHtml(u.name)}</td>
            <td>${escapeHtml(u.email)}</td>
            <td>${escapeHtml(u.role)}</td>
            <td>${new Date(u.created_at).toLocaleDateString()}</td>
        </tr>
    `).join("");
}

// ---------------------------------------------------------------------
// Contact messages
// ---------------------------------------------------------------------
async function loadAdminMessages() {
    const tbody = document.querySelector("#messagesTable tbody");
    const result = await apiRequest("/api/admin/contact-messages");

    if (!result.success || result.messages.length === 0) {
        tbody.innerHTML = "<tr><td colspan='5'>No messages yet.</td></tr>";
        return;
    }

    tbody.innerHTML = result.messages.map(m => `
        <tr>
            <td>${escapeHtml(m.name)}</td>
            <td>${escapeHtml(m.email)}</td>
            <td>${escapeHtml(m.subject || "-")}</td>
            <td>${escapeHtml(m.message)}</td>
            <td>${new Date(m.created_at).toLocaleString()}</td>
        </tr>
    `).join("");
}

// ---------------------------------------------------------------------
// Bootstrap
// ---------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", async () => {
    const ok = await verifyAdminAccess();
    if (!ok) return;

    setupAdminTabs();

    loadAdminStats();
    loadAdminMenu();
    loadAdminOrders();
    loadAdminReservations();
    loadAdminUsers();
    loadAdminMessages();

    document.getElementById("showAddMenuFormBtn").addEventListener("click", () => {
        resetMenuItemForm();
        document.getElementById("menuItemForm").style.display = "flex";
    });

    document.getElementById("cancelMenuFormBtn").addEventListener("click", resetMenuItemForm);

    document.getElementById("menuItemForm").addEventListener("submit", handleMenuItemFormSubmit);
});
