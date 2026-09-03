import React, { useEffect, useMemo, useState } from "react";
import "./styles.css";

/* =========================================================
   API CONFIGURATION
   ========================================================= */

const API = (import.meta.env.VITE_API_URL || "/api/v1").replace(/\/$/, "");

const API_ORIGIN = API.startsWith("http")
  ? new URL(API).origin
  : window.location.origin;

/* =========================================================
   AUTH HELPERS
   ========================================================= */

const getToken = () => localStorage.getItem("shop_token");

const authHeader = () => {
  const t = getToken();
  return t ? { Authorization: `Token ${t}` } : {};
};

const apiFetch = async (url, options = {}) => {
  const headers = { ...(options.headers || {}) };
  const token = getToken();

  if (token) {
    headers.Authorization = `Token ${token}`;
  }

  const r = await fetch(url, {
    ...options,
    headers,
  });

  if (r.status === 401) {
    localStorage.removeItem("shop_token");
    window.dispatchEvent(new Event("auth-expired"));
  }

  return r;
};

/* =========================================================
   IMAGE URL HELPER
   ========================================================= */

const getImageUrl = (image) => {
  if (!image) return null;

  // Django already returned a complete URL.
  if (image.startsWith("http://") || image.startsWith("https://")) {
    return image;
  }

  // Django returned something such as /media/products/image.jpg
  if (image.startsWith("/")) {
    return `${API_ORIGIN}${image}`;
  }

  // Django returned something such as media/products/image.jpg
  return `${API_ORIGIN}/${image}`;
};

/* =========================================================
   MONEY
   ========================================================= */

const money = (v) =>
  `${Number(v || 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })} ETB`;

/* =========================================================
   MODAL
   ========================================================= */

function Modal({ children, onClose }) {
  return (
    <div
      className="modal-backdrop"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) {
          onClose();
        }
      }}
    >
      <div className="modal">{children}</div>
    </div>
  );
}

/* =========================================================
   MAIN APP
   ========================================================= */

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

  /* =======================================================
     LOAD PRODUCTS + SERVICES
     ======================================================= */

  const load = async () => {
    try {
      const [p, s] = await Promise.all([
        fetch(`${API}/products/`),
        fetch(`${API}/services/`),
      ]);

      if (!p.ok || !s.ok) {
        throw new Error("Failed to load data");
      }

      const productData = await p.json();
      const serviceData = await s.json();

      setProducts(productData.results || productData || []);
      setServices(serviceData.results || serviceData || []);
    } catch {
      setNotice("Could not connect to the server.");
    }
  };

  /* =======================================================
     LOAD CURRENT USER
     ======================================================= */

  const loadUser = async () => {
    const t = getToken();

    if (!t) {
      setUser(null);
      return;
    }

    try {
      const r = await apiFetch(`${API}/auth/me/`);

      if (r.ok) {
        setUser(await r.json());
      } else {
        localStorage.removeItem("shop_token");
        setUser(null);
      }
    } catch {
      setUser(null);
    }
  };

  useEffect(() => {
    load();
    loadUser();
  }, []);

  /* =======================================================
     LOAD CUSTOMER ACCOUNT DATA
     ======================================================= */

  const loadAccount = async () => {
    if (!getToken()) {
      setOrders([]);
      setMessages([]);
      return;
    }

    try {
      const [o, m] = await Promise.all([
        apiFetch(`${API}/me/orders/`),
        apiFetch(`${API}/messages/`),
      ]);

      if (o.ok) {
        const data = await o.json();
        setOrders(data.results || data || []);
      }

      if (m.ok) {
        const data = await m.json();
        setMessages(data.results || data || []);
      }
    } catch {
      setNotice("Could not load your account data.");
    }
  };

  useEffect(() => {
    if (user) {
      loadAccount();
    }
  }, [user]);

  /* =======================================================
     AUTH EXPIRED EVENT
     ======================================================= */

  useEffect(() => {
    const handleAuthExpired = () => {
      setUser(null);
      setOrders([]);
      setMessages([]);
      setCart([]);
      setAuth("login");
      setNotice("Your login session has expired. Please log in again.");
    };

    window.addEventListener("auth-expired", handleAuthExpired);

    return () => {
      window.removeEventListener("auth-expired", handleAuthExpired);
    };
  }, []);

  /* =======================================================
     CART
     ======================================================= */

  const addToCart = (p) => {
    setCart((c) => {
      const existing = c.find((i) => i.product.id === p.id);

      if (existing) {
        return c.map((i) =>
          i.product.id === p.id
            ? {
                ...i,
                quantity: i.quantity + 1,
              }
            : i
        );
      }

      return [
        ...c,
        {
          product: p,
          quantity: 1,
        },
      ];
    });

    setNotice(`${p.name} added to cart.`);
  };

  const cartTotal = useMemo(
    () =>
      cart.reduce(
        (total, item) =>
          total + Number(item.product.price || 0) * item.quantity,
        0
      ),
    [cart]
  );

  /* =======================================================
     LOGOUT
     ======================================================= */

  const logout = async () => {
    await fetch(`${API}/auth/logout/`, {
      method: "POST",
      headers: authHeader(),
    }).catch(() => {});

    localStorage.removeItem("shop_token");

    setUser(null);
    setCart([]);
    setOrders([]);
    setMessages([]);
    setPage("home");
    setNotice("You have been logged out.");
  };

  /* =======================================================
     LOGIN / REGISTER
     ======================================================= */

  const submitAuth = async (e, type) => {
    e.preventDefault();

    const f = new FormData(e.currentTarget);
    const data = Object.fromEntries(f.entries());

    if (
      type === "register" &&
      data.password !== data.confirm_password
    ) {
      setNotice("Passwords do not match.");
      return;
    }

    try {
      const r = await fetch(`${API}/auth/${type}/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      const d = await r.json().catch(() => ({}));

      if (!r.ok) {
        setNotice(
          d.detail ||
            d.error ||
            d.message ||
            "Authentication request failed."
        );
        return;
      }

      if (!d.token) {
        setNotice(
          "Login succeeded but the server did not return a token."
        );
        return;
      }

      localStorage.setItem("shop_token", d.token);

      setUser(d.user || null);
      setAuth(null);

      setNotice(
        type === "login"
          ? "Welcome back."
          : "Account created successfully."
      );

      await loadAccount();
    } catch {
      setNotice("Could not connect to the server.");
    }
  };

  /* =======================================================
     CHECKOUT
     ======================================================= */

  const checkout = async () => {
    if (!user) {
      setAuth("login");
      return;
    }

    if (!cart.length) {
      setNotice("Your cart is empty.");
      return;
    }

    if (!getToken()) {
      setUser(null);
      setAuth("login");
      setNotice(
        "Your login session has expired. Please log in again."
      );
      return;
    }

    try {
      const r = await apiFetch(`${API}/orders/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          items: cart.map((i) => ({
            product_id: i.product.id,
            quantity: i.quantity,
          })),
        }),
      });

      const d = await r.json().catch(() => ({}));

      if (!r.ok) {
        setNotice(
          d.detail ||
            d.error ||
            "Could not create order."
        );
        return;
      }

      setCart([]);

      await loadAccount();

      setPage("orders");

      setNotice(
        `Order created. Total ${money(d.total_amount)}.`
      );
    } catch {
      setNotice("Could not connect to the server.");
    }
  };

  /* =======================================================
     SEND MESSAGE
     ======================================================= */

  const sendMessage = async (e) => {
    e.preventDefault();

    if (!getToken()) {
      setAuth("login");
      return;
    }

    const f = new FormData(e.currentTarget);

    try {
      const r = await apiFetch(`${API}/messages/`, {
        method: "POST",
        headers: {
          ...authHeader(),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          subject: f.get("subject"),
          message: f.get("message"),
        }),
      });

      if (r.ok) {
        await loadAccount();
        e.currentTarget.reset();
        setNotice("Message sent.");
      } else {
        const d = await r.json().catch(() => ({}));

        setNotice(
          d.detail ||
            d.error ||
            "Could not send message."
        );
      }
    } catch {
      setNotice("Could not connect to the server.");
    }
  };

  /* =======================================================
     RENDER
     ======================================================= */

  return (
    <div>
      {/* ===================================================
          HEADER
          =================================================== */}

      <header className="header">
        <div className="nav wrap">
          <button
            className="brand"
            onClick={() => setPage("home")}
          >
            INVENTORY<span>SHOP</span>
          </button>

          <div className="links">
            <button onClick={() => setPage("home")}>
              Home
            </button>

            <button onClick={() => setPage("products")}>
              Products
            </button>

            <button onClick={() => setPage("services")}>
              Services
            </button>

            <button onClick={() => setPage("contact")}>
              Contact
            </button>

            {user && (
              <button onClick={() => setPage("orders")}>
                My Orders
              </button>
            )}

            {/* =================================================
                STEP 12 — OWNER DASHBOARD
                Only staff users see this.
                ================================================= */}

            {user?.is_staff && (
              <>
                <a
                  className="admin-link"
                  href="/owner/"
                  target="_blank"
                  rel="noreferrer"
                >
                  Owner Dashboard
                </a>

                <a
                  className="admin-link"
                  href="/admin/"
                  target="_blank"
                  rel="noreferrer"
                >
                  Admin
                </a>
              </>
            )}
          </div>

          <div className="actions">
            {user ? (
              <>
                <button
                  className="account"
                  onClick={() => setPage("account")}
                >
                  {user.full_name || user.username}
                </button>

                <button onClick={logout}>
                  Logout
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => setAuth("login")}
                >
                  Login
                </button>

                <button
                  className="primary"
                  onClick={() => setAuth("register")}
                >
                  Create account
                </button>
              </>
            )}

            <button
              className="cart"
              onClick={() => setPage("cart")}
            >
              Cart{" "}
              <b>
                {cart.reduce(
                  (a, i) => a + i.quantity,
                  0
                )}
              </b>
            </button>
          </div>
        </div>
      </header>

      {/* =====================================================
          NOTICE
          ===================================================== */}

      {notice && (
        <div className="notice wrap">
          {notice}

          <button
            onClick={() => setNotice("")}
          >
            ×
          </button>
        </div>
      )}

      {/* =====================================================
          HOME
          ===================================================== */}

      {page === "home" && (
        <>
          <section className="hero">
            <div className="wrap hero-grid">
              <div>
                <p className="eyebrow">
                  TRUSTED PRODUCTS • RELIABLE SERVICE
                </p>

                <h1>
                  ማሚ ባልትና
                  <br />
                  <em>ለማንኛውም አቅርቦት</em>
                </h1>

                <p className="lead">
                  Browse our products, see current prices,
                  place orders online, and follow every order
                  from your account.
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
                  Prices shown are always the current prices
                  published by our admin.
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

      {/* =====================================================
          PRODUCTS
          ===================================================== */}

      {page === "products" && (
        <main className="wrap page">
          <h2>All products</h2>

          <p className="muted">
            Current prices and availability.
          </p>

          <div className="grid">
            {products.map((p) => (
              <ProductCard
                key={p.id}
                p={p}
                addToCart={addToCart}
              />
            ))}
          </div>
        </main>
      )}

      {/* =====================================================
          SERVICES
          ===================================================== */}

      {page === "services" && (
        <main className="wrap page">
          <h2>Our services</h2>

          <div className="service-grid">
            {services.map((s) => (
              <div
                className="service-card"
                key={s.id}
              >
                <div className="service-icon">
                  ✦
                </div>

                <h3>{s.name}</h3>

                <p>{s.description}</p>
              </div>
            ))}
          </div>
        </main>
      )}

      {/* =====================================================
          CART
          ===================================================== */}

      {page === "cart" && (
        <main className="wrap page">
          <h2>Your cart</h2>

          {!cart.length ? (
            <Empty text="Your cart is empty." />
          ) : (
            <>
              <div className="cart-list">
                {cart.map((i) => (
                  <div
                    className="cart-row"
                    key={i.product.id}
                  >
                    <div>
                      <b>{i.product.name}</b>

                      <div className="muted">
                        {money(i.product.price)} each
                      </div>
                    </div>

                    <div className="qty">
                      <button
                        onClick={() =>
                          setCart((c) =>
                            c.map((x) =>
                              x.product.id === i.product.id
                                ? {
                                    ...x,
                                    quantity: Math.max(
                                      1,
                                      x.quantity - 1
                                    ),
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
                                ? {
                                    ...x,
                                    quantity:
                                      x.quantity + 1,
                                  }
                                : x
                            )
                          )
                        }
                      >
                        +
                      </button>
                    </div>

                    <strong>
                      {money(
                        Number(i.product.price) *
                          i.quantity
                      )}
                    </strong>

                    <button
                      onClick={() =>
                        setCart((c) =>
                          c.filter(
                            (x) =>
                              x.product.id !==
                              i.product.id
                          )
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

                <strong>
                  {money(cartTotal)}
                </strong>

                <button
                  className="primary"
                  onClick={checkout}
                >
                  {user
                    ? "Place order"
                    : "Login to order"}
                </button>
              </div>
            </>
          )}
        </main>
      )}

      {/* =====================================================
          ORDERS
          ===================================================== */}

      {page === "orders" && (
        <main className="wrap page">
          <h2>My orders</h2>

          {!orders.length ? (
            <Empty text="You have no orders yet." />
          ) : (
            <div className="order-list">
              {orders.map((o) => (
                <div
                  className="order-card"
                  key={o.id}
                >
                  <div className="order-head">
                    <b>
                      Order #
                      {String(o.id).slice(0, 8)}
                    </b>

                    <span
                      className={`pill ${String(
                        o.status || ""
                      ).toLowerCase()}`}
                    >
                      {o.status}
                    </span>
                  </div>

                  {(o.items || []).map((i) => (
                    <div
                      className="order-item"
                      key={i.id}
                    >
                      <span>
                        {i.product_name} ×{" "}
                        {i.quantity}
                      </span>

                      <span>
                        {money(i.subtotal)}
                      </span>
                    </div>
                  ))}

                  <div className="order-total">
                    <span>
                      Payment: {o.payment_status}
                    </span>

                    <strong>
                      {money(o.total_amount)}
                    </strong>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      )}

      {/* =====================================================
          ACCOUNT
          ===================================================== */}

      {page === "account" && (
        <main className="wrap page">
          <h2>My account</h2>

          <div className="profile-card">
            <p>
              <b>Name:</b>{" "}
              {user?.full_name || "—"}
            </p>

            <p>
              <b>Username:</b>{" "}
              {user?.username || "—"}
            </p>

            <p>
              <b>Email:</b>{" "}
              {user?.email || "—"}
            </p>

            <button
              className="primary"
              onClick={() => setPage("orders")}
            >
              View my orders
            </button>
          </div>
        </main>
      )}

      {/* =====================================================
          CONTACT
          ===================================================== */}

      {page === "contact" && (
        <main className="wrap page">
          <h2>Contact us</h2>

          <p className="muted">
            Phone:{" "}
            <a href="tel:+251929295613">
              +251 929295613
            </a>

            <br />

            <a href="tel:+251911402079">
              +251 911402079
            </a>

            <br />

            Email:{" "}
            <a href="mailto:info@inventoryshop.com">
              info@inventoryshop.com
            </a>
          </p>

          <p className="muted">
            Send a message to our team. You can continue
            the conversation from your account.
          </p>

          {user ? (
            <form
              className="form contact-form"
              onSubmit={sendMessage}
            >
              <input
                name="subject"
                placeholder="Subject"
                required
              />

              <textarea
                name="message"
                rows="6"
                placeholder="Write your message..."
                required
              />

              <button className="primary">
                Send message
              </button>
            </form>
          ) : (
            <button
              className="primary"
              onClick={() => setAuth("login")}
            >
              Login to message us
            </button>
          )}

          {user && messages.length > 0 && (
            <div className="messages">
              <h3>Your conversations</h3>

              {messages.map((m) => (
                <div
                  className="message"
                  key={m.id}
                >
                  <b>{m.subject}</b>

                  <p>{m.message}</p>

                  {(m.replies || []).map((r) => (
                    <div
                      className="reply"
                      key={r.id}
                    >
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

      {/* =====================================================
          FOOTER
          ===================================================== */}

      <footer>
        <div className="wrap footer-grid">
          <div>
            <b>INVENTORY SHOP</b>

            <p>
              Quality products and reliable service.
            </p>

            <p>
              Phone:{" "}
              <a href="tel:+251929295613">
                +251 929295613
              </a>

              <br />

              <a href="tel:+251911402079">
                +251 911402079
              </a>
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

            <button
              onClick={() => setPage("products")}
            >
              Products
            </button>

            <button
              onClick={() => setPage("services")}
            >
              Services
            </button>

            <button
              onClick={() => setPage("contact")}
            >
              Contact
            </button>
          </div>

          <div>
            <b>Account</b>

            <button
              onClick={() =>
                user
                  ? setPage("orders")
                  : setAuth("login")
              }
            >
              My orders
            </button>
          </div>
        </div>
      </footer>

      {/* =====================================================
          AUTH MODAL
          ===================================================== */}

      {auth && (
        <Modal onClose={() => setAuth(null)}>
          <button
            className="close"
            onClick={() => setAuth(null)}
          >
            ×
          </button>

          {auth === "login" ? (
            <form
              className="form"
              onSubmit={(e) =>
                submitAuth(e, "login")
              }
            >
              <h2>Welcome back</h2>

              <p className="muted">
                Sign in to place and track orders.
              </p>

              <input
                name="username"
                placeholder="Username"
                required
              />

              <input
                name="password"
                type="password"
                placeholder="Password"
                required
              />

              <button className="primary">
                Login
              </button>

              <p className="switch">
                No account?{" "}
                <button
                  type="button"
                  onClick={() =>
                    setAuth("register")
                  }
                >
                  Create one
                </button>
              </p>
            </form>
          ) : (
            <form
              className="form"
              onSubmit={(e) =>
                submitAuth(e, "register")
              }
            >
              <h2>Create your account</h2>

              <input
                name="full_name"
                placeholder="Full name"
                required
              />

              <input
                name="username"
                placeholder="Username"
                required
              />

              <input
                name="email"
                type="email"
                placeholder="Email"
              />

              <input
                name="phone"
                placeholder="Phone"
              />

              <input
                name="address"
                placeholder="Address"
              />

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

              <button className="primary">
                Create account
              </button>

              <p className="switch">
                Already registered?{" "}
                <button
                  type="button"
                  onClick={() =>
                    setAuth("login")
                  }
                >
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

/* =========================================================
   PRODUCT SECTION
   ========================================================= */

function ProductSection({
  products,
  addToCart,
  onMore,
}) {
  return (
    <section className="wrap section">
      <div className="section-head">
        <div>
          <p className="eyebrow">SHOP</p>

          <h2>Featured products</h2>
        </div>

        <button
          className="text-btn"
          onClick={onMore}
        >
          View all →
        </button>
      </div>

      <div className="grid">
        {products.map((p) => (
          <ProductCard
            p={p}
            addToCart={addToCart}
            key={p.id}
          />
        ))}
      </div>
    </section>
  );
}

/* =========================================================
   PRODUCT CARD
   STEP 8 — IMAGE DISPLAY FIX
   ========================================================= */

function ProductCard({ p, addToCart }) {
  const imageUrl = getImageUrl(p.primary_image);

  return (
    <article className="product-card">
      <div className="product-image">
        {imageUrl ? (
          <>
            <img
              src={imageUrl}
              alt={p.name}
              onError={(e) => {
                e.currentTarget.style.display = "none";

                const fallback =
                  e.currentTarget.parentElement.querySelector(
                    ".image-fallback"
                  );

                if (fallback) {
                  fallback.style.display = "flex";
                }
              }}
            />

            <span
              className="image-fallback"
              style={{
                display: "none",
              }}
            >
              NO IMAGE
            </span>
          </>
        ) : (
          <span className="image-fallback">
            NO IMAGE
          </span>
        )}
      </div>

      <div className="product-body">
        <div className="availability">
          {p.stock_quantity > 0 && p.is_available
            ? "IN STOCK"
            : "UNAVAILABLE"}
        </div>

        <h3>{p.name}</h3>

        <p>
          {p.description ||
            "Quality product from our inventory."}
        </p>

        <div className="product-foot">
          <strong>{money(p.price)}</strong>

          <button
            className="primary"
            disabled={
              !p.stock_quantity ||
              !p.is_available
            }
            onClick={() => addToCart(p)}
          >
            Order
          </button>
        </div>
      </div>
    </article>
  );
}

/* =========================================================
   SERVICES
   ========================================================= */

function ServiceSection({
  services,
  onMore,
}) {
  return (
    <section className="section soft">
      <div className="wrap">
        <div className="section-head">
          <div>
            <p className="eyebrow">
              WHAT WE DO
            </p>

            <h2>Services</h2>
          </div>

          <button
            className="text-btn"
            onClick={onMore}
          >
            View all →
          </button>
        </div>

        <div className="service-grid">
          {services.map((s) => (
            <div
              className="service-card"
              key={s.id}
            >
              <div className="service-icon">
                ✦
              </div>

              <h3>{s.name}</h3>

              <p>{s.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* =========================================================
   EMPTY STATE
   ========================================================= */

function Empty({ text }) {
  return (
    <div className="empty">
      {text}
    </div>
  );
}