import React, { useEffect, useMemo, useState } from "react";
import "./styles.css";

const API = import.meta.env.VITE_API_URL || "/api/v1";

const authHeader = () => {
  const t = localStorage.getItem("shop_token");
  return t ? { Authorization: `Token ${t}` } : {};
};

const money = (v) =>
  `${Number(v || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })} ETB`;

function Modal({ children, onClose }) {
  return (
    <div
      className="modal-backdrop"
      onMouseDown={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="modal">{children}</div>
    </div>
  );
}

export default function App() {
  const [products, setProducts] = useState([]);
  const [services, setServices] = useState([]);
  const [orders, setOrders] = useState([]);
  const [messages, setMessages] = useState([]);
  const [user, setUser] = useState(null);
  const [page, setPage] = useState("home");
  const [auth, setAuth] = useState(null);
  const [cart, setCart] = useState([]);
  const [notice, setNotice] = useState("");

  const load = async () => {
    try {
      const [p, s] = await Promise.all([
        fetch(`${API}/products/`),
        fetch(`${API}/services/`),
      ]);
      setProducts((await p.json()).results || []);
      setServices((await s.json()).results || []);
    } catch {
      setNotice("Could not connect to the server.");
    }
  };

  const loadUser = async () => {
    const t = localStorage.getItem("shop_token");
    if (!t) return;
    const r = await fetch(`${API}/auth/me/`, { headers: authHeader() });
    if (r.ok) setUser(await r.json());
    else localStorage.removeItem("shop_token");
  };

  useEffect(() => {
    load();
    loadUser();
  }, []);

  const loadAccount = async () => {
    if (!localStorage.getItem("shop_token")) return;
    const [o, m] = await Promise.all([
      fetch(`${API}/me/orders/`, { headers: authHeader() }),
      fetch(`${API}/messages/`, { headers: authHeader() }),
    ]);
    if (o.ok) setOrders((await o.json()).results || []);
    if (m.ok) setMessages((await m.json()).results || []);
  };

  useEffect(() => {
    if (user) loadAccount();
  }, [user]);

  const addToCart = (p) => {
    setCart((c) => {
      const x = c.find((i) => i.product.id === p.id);
      return x
        ? c.map((i) =>
            i.product.id === p.id ? { ...i, quantity: i.quantity + 1 } : i
          )
        : [...c, { product: p, quantity: 1 }];
    });
    setNotice(`${p.name} added to cart.`);
  };

  const cartTotal = useMemo(
    () => cart.reduce((a, i) => a + Number(i.product.price) * i.quantity, 0),
    [cart]
  );

  const logout = async () => {
    await fetch(`${API}/auth/logout/`, {
      method: "POST",
      headers: authHeader(),
    }).catch(() => {});
    localStorage.removeItem("shop_token");
    setUser(null);
    setCart([]);
    setPage("home");
  };

  const submitAuth = async (e, type) => {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const data = Object.fromEntries(f.entries());
    if (type === "register" && data.password !== data.confirm_password)
      return setNotice("Passwords do not match.");
    const r = await fetch(`${API}/auth/${type}/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const d = await r.json();
    if (!r.ok) return setNotice(d.detail || "Request failed.");
    localStorage.setItem("shop_token", d.token);
    setUser(d.user);
    setAuth(null);
    setNotice(
      type === "login" ? "Welcome back." : "Account created successfully."
    );
  };

  const checkout = async () => {
    if (!user) {
      setAuth("login");
      return;
    }
    if (!cart.length) return;
    const r = await fetch(`${API}/orders/`, {
      method: "POST",
      headers: { ...authHeader(), "Content-Type": "application/json" },
      body: JSON.stringify({
        items: cart.map((i) => ({
          product_id: i.product.id,
          quantity: i.quantity,
        })),
      }),
    });
    const d = await r.json();
    if (!r.ok) return setNotice(d.detail || "Could not create order.");
    setCart([]);
    await loadAccount();
    setPage("orders");
    setNotice(`Order created. Total ${money(d.total_amount)}.`);
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const r = await fetch(`${API}/messages/`, {
      method: "POST",
      headers: { ...authHeader(), "Content-Type": "application/json" },
      body: JSON.stringify({
        subject: f.get("subject"),
        message: f.get("message"),
      }),
    });
    if (r.ok) {
      await loadAccount();
      e.currentTarget.reset();
      setNotice("Message sent.");
    } else setNotice("Please log in to send a message.");
  };

  return (
    <div>
      <header className="header">
        <div className="nav wrap">
          <button className="brand" onClick={() => setPage("home")}>
            INVENTORY<span>SHOP</span>
          </button>
          <div className="links">
            <button onClick={() => setPage("home")}>Home</button>
            <button onClick={() => setPage("products")}>Products</button>
            <button onClick={() => setPage("services")}>Services</button>
            <button onClick={() => setPage("contact")}>Contact</button>
            {user && (
              <button onClick={() => setPage("orders")}>My Orders</button>
            )}
            {user?.is_staff && (
              <a
                className="admin-link"
                href="http://127.0.0.1:8000/admin/"
                target="_blank"
                rel="noreferrer"
              >
                Admin
              </a>
            )}
          </div>
          <div className="actions">
            {user ? (
              <>
                <button className="account" onClick={() => setPage("account")}>
                  {user.full_name || user.username}
                </button>
                <button onClick={logout}>Logout</button>
              </>
            ) : (
              <>
                <button onClick={() => setAuth("login")}>Login</button>
                <button className="primary" onClick={() => setAuth("register")}>
                  Create account
                </button>
              </>
            )}
            <button className="cart" onClick={() => setPage("cart")}>
              Cart <b>{cart.reduce((a, i) => a + i.quantity, 0)}</b>
            </button>
          </div>
        </div>
      </header>

      {notice && (
        <div className="notice wrap">
          {notice}
          <button onClick={() => setNotice("")}>×</button>
        </div>
      )}

      {page === "home" && (
        <>
          <section className="hero">
            <div className="wrap hero-grid">
              <div>
                <p className="eyebrow">TRUSTED PRODUCTS • RELIABLE SERVICE</p>
                <h1>
                  ማሚ ባልትና
                  <br />
                  <em>ለማንኛውም አቅርቦት</em>
                </h1>
                <p className="lead">
                  Browse our products, see current prices, place orders online,
                  and follow every order from your account.
                </p>
                <div>
                  <button
                    className="primary big"
                    onClick={() => setPage("products")}
                  >
                    Shop products
                  </button>
                  <button
                    className="ghost big"
                    onClick={() => setPage("services")}
                  >
                    Our services
                  </button>
                </div>
              </div>
              <div className="hero-card">
                <div className="hero-stat">
                  <strong>{products.length}</strong>
                  <span>Products</span>
                </div>
                <div className="hero-stat">
                  <strong>{services.length}</strong>
                  <span>Services</span>
                </div>
                <div className="hero-note">
                  Prices shown are always the current prices published by our
                  admin.
                </div>
              </div>
            </div>
          </section>
          <ProductSection
            products={products.slice(0, 6)}
            addToCart={addToCart}
            onMore={() => setPage("products")}
          />
          <ServiceSection
            services={services.slice(0, 3)}
            onMore={() => setPage("services")}
          />
        </>
      )}

      {page === "products" && (
        <main className="wrap page">
          <h2>All products</h2>
          <p className="muted">Current prices and availability.</p>
          <div className="grid">
            {products.map((p) => (
              <ProductCard key={p.id} p={p} addToCart={addToCart} />
            ))}
          </div>
        </main>
      )}

      {page === "services" && (
        <main className="wrap page">
          <h2>Our services</h2>
          <div className="service-grid">
            {services.map((s) => (
              <div className="service-card" key={s.id}>
                <div className="service-icon">✦</div>
                <h3>{s.name}</h3>
                <p>{s.description}</p>
              </div>
            ))}
          </div>
        </main>
      )}

      {page === "cart" && (
        <main className="wrap page">
          <h2>Your cart</h2>
          {!cart.length ? (
            <Empty text="Your cart is empty." />
          ) : (
            <>
              <div className="cart-list">
                {cart.map((i) => (
                  <div className="cart-row" key={i.product.id}>
                    <div>
                      <b>{i.product.name}</b>
                      <div className="muted">{money(i.product.price)} each</div>
                    </div>
                    <div className="qty">
                      <button
                        onClick={() =>
                          setCart((c) =>
                            c.map((x) =>
                              x.product.id === i.product.id
                                ? {
                                    ...x,
                                    quantity: Math.max(1, x.quantity - 1),
                                  }
                                : x
                            )
                          )
                        }
                      >
                        −
                      </button>
                      <b>{i.quantity}</b>
                      <button
                        onClick={() =>
                          setCart((c) =>
                            c.map((x) =>
                              x.product.id === i.product.id
                                ? { ...x, quantity: x.quantity + 1 }
                                : x
                            )
                          )
                        }
                      >
                        +
                      </button>
                    </div>
                    <strong>
                      {money(Number(i.product.price) * i.quantity)}
                    </strong>
                    <button
                      onClick={() =>
                        setCart((c) =>
                          c.filter((x) => x.product.id !== i.product.id)
                        )
                      }
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
              <div className="checkout">
                <span>Total</span>
                <strong>{money(cartTotal)}</strong>
                <button className="primary" onClick={checkout}>
                  {user ? "Place order" : "Login to order"}
                </button>
              </div>
            </>
          )}
        </main>
      )}

      {page === "orders" && (
        <main className="wrap page">
          <h2>My orders</h2>
          {!orders.length ? (
            <Empty text="You have no orders yet." />
          ) : (
            <div className="order-list">
              {orders.map((o) => (
                <div className="order-card" key={o.id}>
                  <div className="order-head">
                    <b>Order #{String(o.id).slice(0, 8)}</b>
                    <span className={`pill ${o.status.toLowerCase()}`}>
                      {o.status}
                    </span>
                  </div>
                  {o.items.map((i) => (
                    <div className="order-item" key={i.id}>
                      <span>
                        {i.product_name} × {i.quantity}
                      </span>
                      <span>{money(i.subtotal)}</span>
                    </div>
                  ))}
                  <div className="order-total">
                    <span>Payment: {o.payment_status}</span>
                    <strong>{money(o.total_amount)}</strong>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      )}

      {page === "account" && (
        <main className="wrap page">
          <h2>My account</h2>
          <div className="profile-card">
            <p>
              <b>Name:</b> {user?.full_name}
            </p>
            <p>
              <b>Username:</b> {user?.username}
            </p>
            <p>
              <b>Email:</b> {user?.email || "—"}
            </p>
            <button className="primary" onClick={() => setPage("orders")}>
              View my orders
            </button>
          </div>
        </main>
      )}

            {page === "contact" && (
        <main className="wrap page">
          <h2>Contact us</h2>

          <p className="muted">
            Phone:{" "}
            <a href="tel:+251911000000">+251 929295613</a><br />
            <a href="tel:+251911000000">+251 911402079</a>
            <br />
            Email:{" "}
            <a href="mailto:info@inventoryshop.com">
              info@inventoryshop.com
            </a>
          </p>

          <p className="muted">
            Send a message to our team. You can continue the conversation from
            your account.
          </p>
          {user ? (
            <form className="form contact-form" onSubmit={sendMessage}>
              <input name="subject" placeholder="Subject" required />
              <textarea
                name="message"
                rows="6"
                placeholder="Write your message..."
                required
              />
              <button className="primary">Send message</button>
            </form>
          ) : (
            <button className="primary" onClick={() => setAuth("login")}>
              Login to message us
            </button>
          )}
          {user && messages.length > 0 && (
            <div className="messages">
              <h3>Your conversations</h3>
              {messages.map((m) => (
                <div className="message" key={m.id}>
                  <b>{m.subject}</b>
                  <p>{m.message}</p>
                  {m.replies.map((r) => (
                    <div className="reply" key={r.id}>
                      <b>{r.sender_name}</b>
                      <p>{r.message_text}</p>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          )}
        </main>
      )}

            <footer>
        <div className="wrap footer-grid">

          <div>
            <b>INVENTORY SHOP</b>
            <p>Quality products and reliable service.</p>
            <p>
              Phone:{" "}
              <a href="tel:+251911000000">+251 929295613</a><br />
              <a href="tel:+251911000000">+251 911402079</a>
            </p>
            <p>
              Email:{" "}
              <a href="mailto:info@inventoryshop.com">
                info@inventoryshop.com
              </a>
            </p>
          </div>

          <div>
            <b>Quick links</b>
            <button onClick={() => setPage("products")}>Products</button>
            <button onClick={() => setPage("services")}>Services</button>
            <button onClick={() => setPage("contact")}>Contact</button>
          </div>

          <div>
            <b>Account</b>
            <button
              onClick={() => (user ? setPage("orders") : setAuth("login"))}
            >
              My orders
            </button>
          </div>

        </div>
      </footer>

      {auth && (
        <Modal onClose={() => setAuth(null)}>
          <button className="close" onClick={() => setAuth(null)}>
            ×
          </button>
          {auth === "login" ? (
            <form className="form" onSubmit={(e) => submitAuth(e, "login")}>
              <h2>Welcome back</h2>
              <p className="muted">Sign in to place and track orders.</p>
              <input name="username" placeholder="Username" required />
              <input
                name="password"
                type="password"
                placeholder="Password"
                required
              />
              <button className="primary">Login</button>
              <p className="switch">
                No account?{" "}
                <button type="button" onClick={() => setAuth("register")}>
                  Create one
                </button>
              </p>
            </form>
          ) : (
            <form className="form" onSubmit={(e) => submitAuth(e, "register")}>
              <h2>Create your account</h2>
              <input name="full_name" placeholder="Full name" required />
              <input name="username" placeholder="Username" required />
              <input name="email" type="email" placeholder="Email" />
              <input name="phone" placeholder="Phone" />
              <input name="address" placeholder="Address" />
              <input
                name="password"
                type="password"
                placeholder="Password (8+ characters)"
                required
              />
              <input
                name="confirm_password"
                type="password"
                placeholder="Confirm password"
                required
              />
              <button className="primary">Create account</button>
              <p className="switch">
                Already registered?{" "}
                <button type="button" onClick={() => setAuth("login")}>
                  Login
                </button>
              </p>
            </form>
          )}
        </Modal>
      )}
    </div>
  );
}

function ProductSection({ products, addToCart, onMore }) {
  return (
    <section className="wrap section">
      <div className="section-head">
        <div>
          <p className="eyebrow">SHOP</p>
          <h2>Featured products</h2>
        </div>
        <button className="text-btn" onClick={onMore}>
          View all →
        </button>
      </div>
      <div className="grid">
        {products.map((p) => (
          <ProductCard p={p} addToCart={addToCart} key={p.id} />
        ))}
      </div>
    </section>
  );
}

function ProductCard({ p, addToCart }) {
  return (
    <article className="product-card">
      <div className="product-image">
        {p.primary_image ? (
          <img src={p.primary_image} alt={p.name} />
        ) : (
          <span>PRODUCT</span>
        )}
      </div>
      <div className="product-body">
        <div className="availability">
          {p.stock_quantity > 0 && p.is_available ? "IN STOCK" : "UNAVAILABLE"}
        </div>
        <h3>{p.name}</h3>
        <p>{p.description || "Quality product from our inventory."}</p>
        <div className="product-foot">
          <strong>{money(p.price)}</strong>
          <button
            className="primary"
            disabled={!p.stock_quantity || !p.is_available}
            onClick={() => addToCart(p)}
          >
            Order
          </button>
        </div>
      </div>
    </article>
  );
}

function ServiceSection({ services, onMore }) {
  return (
    <section className="section soft">
      <div className="wrap">
        <div className="section-head">
          <div>
            <p className="eyebrow">WHAT WE DO</p>
            <h2>Services</h2>
          </div>
          <button className="text-btn" onClick={onMore}>
            View all →
          </button>
        </div>
        <div className="service-grid">
          {services.map((s) => (
            <div className="service-card" key={s.id}>
              <div className="service-icon">✦</div>
              <h3>{s.name}</h3>
              <p>{s.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Empty({ text }) {
  return <div className="empty">{text}</div>;
}