// Dependency-light chat SPA. All requests are same-origin ("/api/..."), served
// through CloudFront's /api/* behavior to the API Gateway origin. No secrets or
// API keys live in the browser — all auth-sensitive work is server-side.

const log = document.getElementById("log");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("message");
const clearBtn = document.getElementById("clearChat");

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

// Render the receipt-download link. The `url` is an OPAQUE presigned URL from
// the server-side side channel (data.receipt), never parsed from the assistant's
// reply text. Built via createElement + textContent (no innerHTML) so no value
// is interpolated into markup.
function renderReceipt(receipt) {
  const box = document.createElement("div");
  box.className = "receipt";

  const label = document.createElement("div");
  label.textContent = "Receipt for " + receipt.orderId;
  box.appendChild(label);

  const link = document.createElement("a");
  link.href = receipt.url;
  link.target = "_blank";
  link.rel = "noopener";
  link.textContent = "Download receipt";
  box.appendChild(link);

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
    if (data.placedOrder && data.placedOrder.orderId) {
      append(
        "sys",
        "Order placed: " +
          data.placedOrder.orderId +
          " — " +
          data.placedOrder.summary
      );
      if (window.refreshRecentOrders) window.refreshRecentOrders();
    }
    if (data.receipt && data.receipt.url) {
      renderReceipt(data.receipt);
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

// Clear-chat control: resets the panel to a clean, ready-to-chat state.
// No chat history is persisted (no localStorage/sessionStorage keys, no in-memory
// array) — the whole conversation lives in #log, so emptying it (which also drops
// any .pending refund box) is the full reset. This is DOM + input only and makes
// NO /api call.
if (clearBtn) {
  clearBtn.addEventListener("click", function () {
    log.textContent = "";
    messageInput.value = "";
    messageInput.disabled = false;
    const submitBtn = chatForm.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.disabled = false;
    messageInput.focus();
  });
}

chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = messageInput.value.trim();
  if (!text) return;
  messageInput.value = "";
  sendMessage(text);
});
