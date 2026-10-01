import React, { useEffect, useMemo, useRef, useState } from 'react';

// Baked-in fallback version. Shown only if GET /health does not return a
// version (e.g. offline `vite preview`). The real version is served by the
// container's /health endpoint (app.py APP_VERSION) and overrides this.
const VERSION = 'v1';

// User-facing app name. Single source of truth for the header, document.title,
// and the architecture diagram alt text. A demo edit flips this one line to
// 'BeanThere Cafe'.
export const APP_NAME = 'Coffee Shop';

// Hardcoded menu. The SPA is a demo storefront; prices are fixed client-side
// and the server recomputes loyalty points from the posted total.
const MENU = [
  { id: 'espresso', name: 'Espresso', price: 3.0 },
  { id: 'latte', name: 'Latte', price: 4.5 },
  { id: 'cold-brew', name: 'Cold Brew', price: 4.0 },
  { id: 'mocha', name: 'Mocha', price: 5.0 },
];

// This demo's services, reflected in the UI (NOT session3's Cognito/ElastiCache).
const SERVICES = [
  ['CodePipeline', 'S3 source → build → deploy orchestration'],
  ['CodeBuild', 'docker build + push to ECR'],
  ['ECR', 'container image registry'],
  ['ECS / Fargate', 'runs the container task'],
  ['ALB', 'routes to the Fargate service'],
  ['CloudFront', 'public edge in front of the ALB'],
  ['DynamoDB', 'stores orders'],
  ['SQS', 'order buffer queue'],
  ['AppConfig', 'runtime feature config'],
  ['SSM Parameter Store', 'supplies the loyalty rate'],
  ['Secrets Manager', 'application secrets'],
];

// Polling cadence for GET /order/{id} while an order brews.
const POLL_MS = 3500;

// Render an epoch-second createdAt as a short local time.
function fmtTime(createdAt) {
  if (!createdAt && createdAt !== 0) return '—';
  const d = new Date(Number(createdAt) * 1000);
  if (Number.isNaN(d.getTime())) return '—';
  return d.toLocaleTimeString();
}

// Summarise an order's items for the recent-orders table.
function fmtItems(order) {
  const items = Array.isArray(order.items) ? order.items : [];
  const count = items.reduce((s, it) => s + (Number(it.qty) || 0), 0);
  const label = count === 1 ? '1 item' : `${count} items`;
  const total = Number(order.total || 0).toFixed(2);
  return `${label} · $${total}`;
}

function StatusBadge({ status }) {
  const s = (status || '').toUpperCase();
  const cls = s === 'READY' ? 'ready' : s === 'BREWING' ? 'brewing' : 'received';
  return <span className={`status-badge ${cls}`}>{s || 'RECEIVED'}</span>;
}

export default function App() {
  const [cart, setCart] = useState({});
  const [log, setLog] = useState([]);
  const [busy, setBusy] = useState(false);
  const [version, setVersion] = useState(VERSION);
  const [current, setCurrent] = useState(null); // { orderId, status, points, total, createdAt }
  const [recent, setRecent] = useState([]);
  const [recentError, setRecentError] = useState(null);

  const pollRef = useRef(null);

  // Keep the browser tab title in sync with the user-facing app name.
  useEffect(() => {
    document.title = APP_NAME;
  }, []);

  const push = (line) =>
    setLog((l) => [{ t: new Date().toLocaleTimeString(), line }, ...l].slice(0, 40));

  const total = useMemo(
    () => MENU.reduce((s, m) => s + m.price * (cart[m.id] || 0), 0),
    [cart]
  );

  // Read the running app version from the same-origin health endpoint.
  useEffect(() => {
    fetch('/health')
      .then((r) => r.json())
      .then((d) => {
        if (d && d.version) {
          setVersion(d.version);
          push(`GET /health → version ${d.version}`);
        }
      })
      .catch(() => push('GET /health failed — using baked-in version'));
  }, []);

  // Load the recent-orders list on first mount.
  useEffect(() => {
    loadRecent();
  }, []);

  // Stop any in-flight polling when the component unmounts.
  useEffect(() => () => stopPolling(), []);

  function stopPolling() {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }

  async function loadRecent() {
    try {
      const r = await fetch('/orders');
      const d = await r.json();
      if (!r.ok) {
        setRecentError(d.error || `error ${r.status}`);
        push(`GET /orders → ${r.status} ${d.error || 'error'}`);
        return;
      }
      setRecent(Array.isArray(d.orders) ? d.orders : []);
      setRecentError(null);
    } catch (e) {
      setRecentError(e.message);
      push(`GET /orders failed: ${e.message}`);
    }
  }

  // Poll GET /order/{id} until the order reaches READY, then stop.
  function startPolling(orderId, lastStatus) {
    stopPolling();
    let seen = lastStatus;
    pollRef.current = setInterval(async () => {
      try {
        const r = await fetch(`/order/${encodeURIComponent(orderId)}`);
        const d = await r.json();
        if (!r.ok) {
          push(`GET /order/${orderId} → ${r.status} ${d.error || 'error'}`);
          return;
        }
        setCurrent(d);
        if (d.status !== seen) {
          seen = d.status;
          push(`order ${orderId} → ${d.status}`);
          // Reflect the new status in the recent-orders list too.
          loadRecent();
        }
        if (d.status === 'READY') {
          stopPolling();
        }
      } catch (e) {
        push(`poll error: ${e.message}`);
      }
    }, POLL_MS);
  }

  const inc = (id) => setCart((c) => ({ ...c, [id]: (c[id] || 0) + 1 }));
  const dec = (id) => setCart((c) => ({ ...c, [id]: Math.max(0, (c[id] || 0) - 1) }));

  async function placeOrder() {
    if (total <= 0) {
      push('add something to the cart first');
      return;
    }
    const roundedTotal = Number(total.toFixed(2));
    // Build items from the cart: id, name, qty, price (per FEAT-001 shape).
    const items = MENU.filter((m) => (cart[m.id] || 0) > 0).map((m) => ({
      id: m.id,
      name: m.name,
      qty: cart[m.id],
      price: m.price,
    }));
    setBusy(true);
    try {
      const r = await fetch('/order', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ items, total: roundedTotal }),
      });
      const d = await r.json();
      if (!r.ok) {
        push(`POST /order → ${r.status} ${d.error || 'error'}`);
      } else {
        push(`POST /order → ${d.orderId} earned ${d.points} loyalty points`);
        setCurrent(d);
        setCart({});
        startPolling(d.orderId, d.status);
        loadRecent();
      }
    } catch (e) {
      push(`order error: ${e.message}`);
    }
    setBusy(false);
  }

  return (
    <div className="wrap">
      <header>
        <h1>{`☕ ${APP_NAME}`}</h1>
        <span className="tag">live · {version}</span>
      </header>

      <details className="diagram">
        <summary>▸ Architecture diagram — how this demo ships to Fargate</summary>
        <div className="diagram-body">
          <img src="/architecture.svg" alt={`${APP_NAME} architecture diagram`} />
          <p className="hint">
            <a href="/architecture.svg" target="_blank" rel="noreferrer">
              Open full size ↗
            </a>
          </p>
        </div>
      </details>

      <div className="grid">
        <section className="card">
          <h2>Menu <em>(order → /order)</em></h2>
          <ul className="menu">
            {MENU.map((m) => (
              <li key={m.id}>
                <span>
                  {m.name} · ${m.price.toFixed(2)}
                </span>
                <span className="qty">
                  <button onClick={() => dec(m.id)} disabled={busy}>−</button>
                  {cart[m.id] || 0}
                  <button onClick={() => inc(m.id)} disabled={busy}>+</button>
                </span>
              </li>
            ))}
          </ul>
          <p className="total">
            Total: <b>${total.toFixed(2)}</b>
          </p>
          <button onClick={placeOrder} disabled={busy || total <= 0}>
            Place order
          </button>

          {current && (
            <div className="current-order">
              <div className="current-order-head">
                <span>Order <code>{current.orderId}</code></span>
                <StatusBadge status={current.status} />
              </div>
              <p className="hint">
                ${Number(current.total || 0).toFixed(2)} · {current.points} points ·
                placed {fmtTime(current.createdAt)}
                {current.status !== 'READY' ? ' · brewing…' : ' · ready for pickup'}
              </p>
            </div>
          )}
        </section>

        <section className="card services">
          <h2>AWS services in this demo</h2>
          <ul>
            {SERVICES.map(([n, d]) => (
              <li key={n}>
                <b>{n}</b>
                <span>{d}</span>
              </li>
            ))}
          </ul>
        </section>
      </div>

      <section className="card recent">
        <h2 className="recent-head">
          Recent orders <em>(latest 10)</em>
          <button className="refresh" onClick={loadRecent} disabled={busy}>
            Refresh
          </button>
        </h2>
        {recentError && (
          <p className="hint">Could not load orders: {recentError}</p>
        )}
        {!recentError && recent.length === 0 ? (
          <p className="hint">No orders yet. Place one above.</p>
        ) : (
          !recentError && (
            <div className="recent-scroll">
              <table className="recent-table">
                <thead>
                  <tr>
                    <th>Placed</th>
                    <th>Order ID</th>
                    <th>Items / Total</th>
                    <th>Points</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {recent.map((o) => (
                    <tr key={o.orderId}>
                      <td>{fmtTime(o.createdAt)}</td>
                      <td><code>{o.orderId}</code></td>
                      <td>{fmtItems(o)}</td>
                      <td>{o.points}</td>
                      <td><StatusBadge status={o.status} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        )}
      </section>

      <section className="card log">
        <h2>Activity log</h2>
        <ul>
          {log.length === 0 ? (
            <li className="hint">No activity yet. Place an order above.</li>
          ) : (
            log.map((l, i) => (
              <li key={i}>
                <span className="ts">{l.t}</span> {l.line}
              </li>
            ))
          )}
        </ul>
      </section>
    </div>
  );
}
