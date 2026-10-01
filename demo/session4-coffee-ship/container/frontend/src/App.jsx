import React, { useEffect, useMemo, useState } from 'react';

// Baked-in fallback version. Shown only if GET /health does not return a
// version (e.g. offline `vite preview`). The real version is served by the
// container's /health endpoint (app.py APP_VERSION) and overrides this.
const VERSION = 'v1';

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
  ['DynamoDB', 'order + loyalty storage'],
  ['SQS', 'order buffer queue'],
  ['AppConfig', 'runtime feature config'],
  ['SSM Parameter Store', 'loyalty + app parameters'],
  ['Secrets Manager', 'application secrets'],
];

function genOrderId() {
  const rand = Math.random().toString(36).slice(2, 8);
  return `ord-${Date.now().toString(36)}-${rand}`;
}

export default function App() {
  const [cart, setCart] = useState({});
  const [log, setLog] = useState([]);
  const [busy, setBusy] = useState(false);
  const [version, setVersion] = useState(VERSION);

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

  const inc = (id) => setCart((c) => ({ ...c, [id]: (c[id] || 0) + 1 }));
  const dec = (id) => setCart((c) => ({ ...c, [id]: Math.max(0, (c[id] || 0) - 1) }));

  async function placeOrder() {
    if (total <= 0) {
      push('add something to the cart first');
      return;
    }
    const orderId = genOrderId();
    const roundedTotal = Number(total.toFixed(2));
    setBusy(true);
    try {
      const r = await fetch('/order', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ orderId, total: roundedTotal }),
      });
      const d = await r.json();
      if (!r.ok) {
        push(`POST /order → ${r.status} ${d.error || 'error'}`);
      } else {
        push(`POST /order → ${d.orderId} earned ${d.points} loyalty points`);
        setCart({});
      }
    } catch (e) {
      push(`order error: ${e.message}`);
    }
    setBusy(false);
  }

  return (
    <div className="wrap">
      <header>
        <h1>☕ Coffee Ship</h1>
        <span className="tag">live · {version}</span>
      </header>

      <details className="diagram">
        <summary>▸ Architecture diagram — how this demo ships to Fargate</summary>
        <div className="diagram-body">
          <img src="/architecture.svg" alt="Coffee Ship architecture diagram" />
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
