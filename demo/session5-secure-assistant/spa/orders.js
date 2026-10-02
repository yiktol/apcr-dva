// Recent Orders panel. Polls the same-origin, parameterless GET /api/orders and
// renders the newest orders on the storefront page. All requests are relative
// ("/api/..."), served through CloudFront's /api/* behavior to API Gateway.
//
// STORED-XSS INVARIANT: order fields (orderId, summary, total, status) are
// rendered via textContent / createElement ONLY — never innerHTML (and never a
// template string assigned to innerHTML). The summary is read back from a stored
// DynamoDB attribute, so this panel must stay XSS-safe even if what summary may
// contain changes in the future.

// Map an order status to its badge CSS class.
function badgeClass(status) {
  if (status === "PREPARING") return "badge badge-preparing";
  if (status === "READY") return "badge badge-ready";
  return "badge badge-received";
}

// Pure render: clear the list, then build one row per order with DOM nodes only.
function renderOrders(listEl, orders) {
  if (!listEl) return;
  listEl.textContent = "";
  for (let i = 0; i < orders.length; i++) {
    const order = orders[i];

    const row = document.createElement("li");
    row.className = "order-row";

    const idEl = document.createElement("span");
    idEl.className = "order-id";
    idEl.textContent = order.orderId;

    const summaryEl = document.createElement("span");
    summaryEl.className = "order-summary";
    summaryEl.textContent = order.summary;

    const totalEl = document.createElement("span");
    totalEl.className = "order-total";
    totalEl.textContent = "$" + order.total;

    const badgeEl = document.createElement("span");
    badgeEl.className = badgeClass(order.status);
    badgeEl.textContent = order.status;

    row.appendChild(idEl);
    row.appendChild(summaryEl);
    row.appendChild(totalEl);
    row.appendChild(badgeEl);
    listEl.appendChild(row);
  }
}

// Fetch the newest orders and render them. On a non-OK response or a network
// error, leave the previously rendered list in place (no destructive clear) and
// wait for the next poll tick.
async function refreshRecentOrders() {
  try {
    const res = await fetch("/api/orders");
    if (!res.ok) return;
    const data = await res.json();
    renderOrders(document.getElementById("recentOrders"), data.orders || []);
  } catch (e) {
    // Keep the last-rendered list; the next tick will retry.
  }
}

// Expose the chat hook at top-level evaluation (NOT inside DOMContentLoaded) so
// it exists before any chat message can place an order. app.js guards with
// `if (window.refreshRecentOrders)`.
window.refreshRecentOrders = refreshRecentOrders;

document.addEventListener("DOMContentLoaded", () => {
  refreshRecentOrders();
  setInterval(refreshRecentOrders, 10000);
});
