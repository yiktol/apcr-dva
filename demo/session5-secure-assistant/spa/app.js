// Dependency-light chat SPA. All requests are same-origin ("/api/..."), served
// through CloudFront's /api/* behavior to the API Gateway origin. No secrets or
// API keys live in the browser — all auth-sensitive work is server-side.

const log = document.getElementById("log");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("message");
const orderIdInput = document.getElementById("orderId");
const receiptBtn = document.getElementById("receiptBtn");

function append(cls, text) {
  const el = document.createElement("div");
  el.className = "msg " + cls;
  el.textContent = text;
  log.appendChild(el);
  log.scrollTop = log.scrollHeight;
  return el;
}

// Render the pending-refund confirmation UI. The `token` is treated as an
// OPAQUE string produced by the server-side side channel — never parsed from
// the assistant's reply text — and only echoed back to the confirm endpoint.
function renderPendingRefund(pending) {
  const box = document.createElement("div");
  box.className = "pending";
  box.innerHTML =
    "<div><strong>Refund pending confirmation</strong></div>" +
    "<div>Order " +
    pending.orderMasked +
    " — amount " +
    pending.amountMasked +
    "</div>" +
    "<div>No money has moved yet.</div>";
  const btn = document.createElement("button");
  btn.type = "button";
  btn.textContent = "Confirm refund";
  btn.addEventListener("click", () => confirmRefund(pending.token, btn));
  box.appendChild(btn);
  log.appendChild(box);
  log.scrollTop = log.scrollHeight;
}

async function sendMessage(text) {
  append("user", text);
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    if (!res.ok) {
      append("sys", data.error || "Something went wrong.");
      return;
    }
    append("bot", data.reply || "");
    if (data.pendingRefund && data.pendingRefund.token) {
      renderPendingRefund(data.pendingRefund);
    }
  } catch (e) {
    append("sys", "Network error. Please try again.");
  }
}

async function confirmRefund(token, btn) {
  btn.disabled = true;
  try {
    const res = await fetch("/api/refunds/confirm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: token }),
    });
    const data = await res.json();
    if (res.ok) {
      append("sys", "Refund confirmed.");
    } else {
      append("sys", data.error || "Could not confirm the refund.");
      btn.disabled = false;
    }
  } catch (e) {
    append("sys", "Network error confirming the refund.");
    btn.disabled = false;
  }
}

async function downloadReceipt(orderId) {
  if (!orderId) {
    append("sys", "Enter an order id first (e.g. ORD-000123).");
    return;
  }
  try {
    const res = await fetch(
      "/api/receipts/" + encodeURIComponent(orderId) + "/url"
    );
    const data = await res.json();
    if (res.ok && data.url) {
      // Open the short-lived presigned URL in a new tab.
      window.open(data.url, "_blank", "noopener");
    } else {
      append("sys", data.error || "Could not get a receipt URL.");
    }
  } catch (e) {
    append("sys", "Network error getting the receipt URL.");
  }
}

chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = messageInput.value.trim();
  if (!text) return;
  messageInput.value = "";
  sendMessage(text);
});

receiptBtn.addEventListener("click", () => {
  downloadReceipt(orderIdInput.value.trim());
});
