import React, { useEffect, useState } from 'react';
import {
  signUp, confirmSignUp, signIn, signOut,
  getCurrentUser, fetchAuthSession, fetchUserAttributes,
} from 'aws-amplify/auth';

const SERVICES = [
  ['Cognito', 'sign-in + temporary AWS credentials'],
  ['ElastiCache', 'menu cache (lazy loading + TTL)'],
  ['SQS', 'order buffer + dead-letter queue'],
  ['SNS', 'fan-out to subscribers'],
  ['EventBridge', 'content-based event routing'],
  ['CloudWatch', 'custom metric + alarm'],
  ['CloudWatch Logs', 'structured JSON logs'],
  ['CloudTrail', 'API-call audit trail'],
];

export default function App({ config }) {
  const api = (config.apiUrl || '').replace(/\/$/, '');
  const [user, setUser] = useState(null);
  const [custName, setCustName] = useState('');
  const [log, setLog] = useState([]);
  const [menu, setMenu] = useState([]);
  const [menuSource, setMenuSource] = useState('');
  const [cart, setCart] = useState({});
  const [orders, setOrders] = useState([]);
  const [allOrders, setAllOrders] = useState([]);
  const [busy, setBusy] = useState(false);

  async function loadAllOrders() {
    try {
      const r = await fetch(`${api}/orders`);
      const d = await r.json();
      const latest = (d.orders || []).slice(0, 20); // show only the latest 20
      setAllOrders(latest);
      push(`GET /orders → ${d.count ?? 0} order(s) in DynamoDB, showing latest ${latest.length}`);
    } catch (e) { push(`orders error: ${e.message}`); }
  }

  const push = (line) => setLog((l) => [{ t: new Date().toLocaleTimeString(), line }, ...l].slice(0, 40));

  useEffect(() => {
    getCurrentUser().then((u) => setUser(u)).catch(() => setUser(null));
    loadAllOrders();
  }, []);

  // Resolve a friendly customer name from Cognito attributes (nickname or the
  // email local part) whenever the signed-in user changes. Never the UUID.
  useEffect(() => {
    if (!user) { setCustName(''); return; }
    fetchUserAttributes()
      .then((a) => {
        const email = a.email || user.signInDetails?.loginId || '';
        setCustName(a.nickname || (email.includes('@') ? email.split('@')[0] : email) || 'guest');
      })
      .catch(() => {
        const login = user.signInDetails?.loginId || '';
        setCustName(login.includes('@') ? login.split('@')[0] : (login || 'guest'));
      });
  }, [user]);

  async function loadMenu() {
    setBusy(true);
    try {
      const r = await fetch(`${api}/menu`);
      const d = await r.json();
      setMenu(d.items || []);
      setMenuSource(d.source);
      push(`GET /menu → served from ${d.source.toUpperCase()} (ElastiCache lazy-load)`);
    } catch (e) { push(`menu error: ${e.message}`); }
    setBusy(false);
  }

  async function placeOrder(simulateFailure = false) {
    const items = Object.entries(cart).filter(([, q]) => q > 0)
      .map(([id, qty]) => ({ id, qty }));
    if (!items.length) { push('add something to the cart first'); return; }
    const total = items.reduce((s, it) => {
      const m = menu.find((x) => x.id === it.id); return s + (m ? m.price * it.qty : 0);
    }, 0);
    setBusy(true);
    try {
      const r = await fetch(`${api}/orders`, {
        method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ customerId: custName || 'guest', items, total, simulateFailure }),
      });
      const d = await r.json();
      push(`POST /orders → ${d.orderId} QUEUED in SQS${simulateFailure ? ' (will fail → DLQ)' : ''}`);
      setOrders((o) => [{ id: d.orderId, status: 'QUEUED', failing: simulateFailure }, ...o]);
      setCart({});
      loadAllOrders();
      setTimeout(() => { trackOrder(d.orderId); loadAllOrders(); }, 4000);
    } catch (e) { push(`order error: ${e.message}`); }
    setBusy(false);
  }

  async function trackOrder(id) {
    try {
      const r = await fetch(`${api}/orders/${id}`);
      const d = await r.json();
      setOrders((o) => o.map((x) => x.id === id ? { ...x, status: d.status || x.status } : x));
      push(`GET /orders/${id} → ${d.status} (worker: SNS + EventBridge + CloudWatch metric)`);
    } catch (e) { push(`track error: ${e.message}`); }
  }

  if (!config.apiUrl) {
    return <div className="wrap"><h1>BeanThere</h1><p className="warn">
      No runtime config found. Deploy the stack and upload <code>config.js</code>.</p></div>;
  }

  return (
    <div className="wrap">
      <header>
        <h1>☕ BeanThere</h1>
        <span className="tag">live</span>
        <a className="dash-link"
           href="https://cloudwatch.amazonaws.com/dashboard.html?dashboard=beanthere-CoreServices&context=eyJSIjoidXMtZWFzdC0xIiwiRCI6ImN3LWRiLTg3NTY5MjYwODk4MSIsIlUiOiJ1cy1lYXN0LTFfU0NUNmVEM1h0IiwiQyI6IjVxMm9xdjA2M3V2MHAydWhzdWZuMXVrZ2pzIiwiSSI6InVzLWVhc3QtMTo2ZWYxOWRhMi1hMTVhLTRmZDMtODc1ZS00NjIyMjYxOTRhNGEiLCJNIjoiUHVibGljIn0="
           target="_blank" rel="noreferrer">📊 CloudWatch dashboard ↗</a>
        {user
          ? <button onClick={() => signOut().then(() => setUser(null))}>Sign out</button>
          : null}
      </header>

      <details className="diagram">
        <summary>▸ Architecture diagram — how the 8 core services connect</summary>
        <div className="diagram-body">
          <img src="/architecture.svg" alt="BeanThere architecture diagram" />
          <p className="hint">
            <a href="/architecture.svg" target="_blank" rel="noreferrer">Open full size ↗</a>
          </p>
        </div>
      </details>

      <div className="grid">
        <section className="card">
          <h2>1 · Sign in <em>(Cognito)</em></h2>
          {user
            ? <p className="ok">Signed in as <b>{custName || user.signInDetails?.loginId || 'user'}</b>. A Cognito
                identity pool can now vend temporary AWS credentials for this user.</p>
            : <AuthPanel onSignedIn={setUser} push={push} />}
        </section>

        <section className="card">
          <h2>2 · Menu <em>(ElastiCache)</em></h2>
          <button onClick={loadMenu} disabled={busy}>Load menu</button>
          {menuSource && <span className={`pill ${menuSource}`}>source: {menuSource}</span>}
          <ul className="menu">
            {menu.map((m) => (
              <li key={m.id}>
                <span>{m.name} · ${m.price.toFixed(2)}</span>
                <span className="qty">
                  <button onClick={() => setCart((c) => ({ ...c, [m.id]: Math.max(0, (c[m.id] || 0) - 1) }))}>−</button>
                  {cart[m.id] || 0}
                  <button onClick={() => setCart((c) => ({ ...c, [m.id]: (c[m.id] || 0) + 1 }))}>+</button>
                </span>
              </li>
            ))}
          </ul>
        </section>

        <section className="card">
          <h2>3 · Order <em>(SQS → SNS → EventBridge → CloudWatch)</em></h2>
          <button onClick={() => placeOrder(false)} disabled={busy || !user}>Place order</button>
          <button className="ghost" onClick={() => placeOrder(true)} disabled={busy || !user}>
            Place a failing order (→ DLQ)</button>
          {!user && <p className="hint">Sign in to place an order.</p>}
          <ul className="orders">
            {orders.map((o) => (
              <li key={o.id}>
                <code>{o.id}</code>
                <span className={`status ${o.status}`}>{o.status}</span>
                {o.failing && <span className="pill database">dlq path</span>}
                <button className="link" onClick={() => trackOrder(o.id)}>refresh</button>
              </li>
            ))}
          </ul>
        </section>

        <section className="card services">
          <h2>Core services</h2>
          <ul>
            {SERVICES.map(([n, d]) => <li key={n}><b>{n}</b><span>{d}</span></li>)}
          </ul>
        </section>
      </div>

      <section className="card orders-table">
        <h2>All orders <em>(DynamoDB · latest 20)</em>
          <button className="link" onClick={loadAllOrders}>refresh</button>
        </h2>
        {allOrders.length === 0
          ? <p className="hint">No orders yet. Place one above.</p>
          : <table>
              <thead>
                <tr><th>Placed</th><th>Customer</th><th>Order ID</th><th>Status</th><th className="num">Total</th></tr>
              </thead>
              <tbody>
                {allOrders.map((o) => (
                  <tr key={o.orderId}>
                    <td>{o.placedAt ? new Date(o.placedAt).toLocaleString() : '—'}</td>
                    <td>{o.customerId || '—'}</td>
                    <td><code>{o.orderId}</code></td>
                    <td><span className={`status ${o.status}`}>{o.status || '—'}</span></td>
                    <td className="num">${Number(o.total || 0).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>}
      </section>

      <section className="card log">
        <h2>Activity log</h2>
        <ul>{log.map((l, i) => <li key={i}><span className="ts">{l.t}</span> {l.line}</li>)}</ul>
      </section>
    </div>
  );
}

function AuthPanel({ onSignedIn, push }) {
  const [mode, setMode] = useState('signin');
  const [email, setEmail] = useState('');
  const [pw, setPw] = useState('');
  const [code, setCode] = useState('');
  const [msg, setMsg] = useState('');

  async function doSignUp() {
    try {
      await signUp({ username: email, password: pw, options: { userAttributes: { email } } });
      setMode('confirm'); setMsg('Check your email for a verification code.');
      push('Cognito signUp → confirmation code sent');
    } catch (e) { setMsg(e.message); }
  }
  async function doConfirm() {
    try {
      await confirmSignUp({ username: email, confirmationCode: code });
      setMode('signin'); setMsg('Confirmed. You can sign in now.');
      push('Cognito confirmSignUp → account verified');
    } catch (e) { setMsg(e.message); }
  }
  async function doSignIn() {
    try {
      await signIn({ username: email, password: pw });
      const s = await fetchAuthSession();
      onSignedIn(await getCurrentUser());
      push(`Cognito signIn → JWT issued (idToken ${s.tokens?.idToken ? 'present' : 'missing'})`);
    } catch (e) { setMsg(e.message); }
  }

  return (
    <div className="auth">
      <input placeholder="email" value={email} onChange={(e) => setEmail(e.target.value)} />
      {mode !== 'confirm' && <input placeholder="password" type="password" value={pw} onChange={(e) => setPw(e.target.value)} />}
      {mode === 'confirm' && <input placeholder="verification code" value={code} onChange={(e) => setCode(e.target.value)} />}
      {mode === 'signin' && <>
        <button onClick={doSignIn}>Sign in</button>
        <button className="link" onClick={() => setMode('signup')}>need an account?</button>
      </>}
      {mode === 'signup' && <>
        <button onClick={doSignUp}>Sign up</button>
        <button className="link" onClick={() => setMode('signin')}>have an account?</button>
      </>}
      {mode === 'confirm' && <button onClick={doConfirm}>Confirm</button>}
      {msg && <p className="hint">{msg}</p>}
    </div>
  );
}
