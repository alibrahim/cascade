import httpx
from flask import Flask, render_template_string

app = Flask(__name__)

GATEWAY_URL = "http://localhost:9004"
AUTH_URL = "http://localhost:9000"
CATALOG_URL = "http://localhost:9001"

TIMEOUT = 5.0

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Food Marketplace Dashboard</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 Helvetica, Arial, sans-serif;
    background: #f3f4f6;
    color: #1f2937;
    padding: 24px;
  }
  h1 {
    font-size: 1.75rem;
    margin-bottom: 24px;
    color: #111827;
  }
  .cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
    gap: 20px;
  }
  .card {
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    padding: 20px;
  }
  .card h2 {
    font-size: 1.1rem;
    margin-bottom: 14px;
    color: #374151;
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 8px;
  }
  .stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  .stat-box {
    background: #f9fafb;
    border-radius: 8px;
    padding: 14px;
    text-align: center;
  }
  .stat-box .value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #111827;
  }
  .stat-box .label {
    font-size: 0.8rem;
    color: #6b7280;
    margin-top: 2px;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.875rem;
  }
  th {
    text-align: left;
    padding: 8px 6px;
    color: #6b7280;
    font-weight: 600;
    border-bottom: 1px solid #e5e7eb;
  }
  td {
    padding: 8px 6px;
    border-bottom: 1px solid #f3f4f6;
  }
  .badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
  }
  .badge-pending   { background: #fef3c7; color: #92400e; }
  .badge-confirmed { background: #dbeafe; color: #1e40af; }
  .badge-delivered { background: #d1fae5; color: #065f46; }
  .badge-cancelled { background: #fee2e2; color: #991b1b; }
  .badge-available   { background: #d1fae5; color: #065f46; }
  .badge-unavailable { background: #fee2e2; color: #991b1b; }
  .notif-list { list-style: none; }
  .notif-list li {
    padding: 10px 0;
    border-bottom: 1px solid #f3f4f6;
    font-size: 0.875rem;
  }
  .notif-list li:last-child { border-bottom: none; }
  .notif-title { font-weight: 600; }
  .notif-time  { color: #9ca3af; font-size: 0.75rem; }
  .error {
    color: #991b1b;
    background: #fee2e2;
    padding: 10px;
    border-radius: 6px;
    font-size: 0.85rem;
  }
</style>
</head>
<body>
<h1>Food Marketplace Dashboard</h1>
<div class="cards">

  <!-- Platform Stats -->
  <div class="card">
    <h2>Platform Stats</h2>
    {% if stats %}
    <div class="stats">
      <div class="stat-box">
        <div class="value">{{ stats.user_count }}</div>
        <div class="label">Users</div>
      </div>
      <div class="stat-box">
        <div class="value">{{ stats.menu_item_count }}</div>
        <div class="label">Menu Items</div>
      </div>
      <div class="stat-box">
        <div class="value">{{ stats.order_count }}</div>
        <div class="label">Orders</div>
      </div>
      <div class="stat-box">
        <div class="value">${{ "%.2f"|format(stats.total_revenue) }}</div>
        <div class="label">Revenue</div>
      </div>
    </div>
    {% else %}
    <p class="error">Could not load platform stats.</p>
    {% endif %}
  </div>

  <!-- Recent Orders -->
  <div class="card">
    <h2>Recent Orders</h2>
    {% if orders %}
    <table>
      <thead>
        <tr><th>Order ID</th><th>Customer</th><th>Total</th><th>Status</th></tr>
      </thead>
      <tbody>
        {% for o in orders[:10] %}
        <tr>
          <td>{{ o.id }}</td>
          <td>{{ o.get("customer_name", o.get("customer_id", "-")) }}</td>
          <td>${{ "%.2f"|format(o.total|float) }}</td>
          <td><span class="badge badge-{{ o.status }}">{{ o.status }}</span></td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    {% else %}
    <p class="error">Could not load orders.</p>
    {% endif %}
  </div>

  <!-- Menu Items -->
  <div class="card">
    <h2>Menu Items</h2>
    {% if items %}
    <table>
      <thead>
        <tr><th>Name</th><th>Category</th><th>Vendor</th><th>Price</th><th>Status</th></tr>
      </thead>
      <tbody>
        {% for i in items[:10] %}
        <tr>
          <td>{{ i.name }}</td>
          <td>{{ i.get("category", "-") }}</td>
          <td>{{ i.get("vendor_name", i.get("vendor_id", "-")) }}</td>
          <td>${{ "%.2f"|format(i.price|float) }}</td>
          <td>
            {% if i.get("available", true) %}
              <span class="badge badge-available">Available</span>
            {% else %}
              <span class="badge badge-unavailable">Unavailable</span>
            {% endif %}
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    {% else %}
    <p class="error">Could not load menu items.</p>
    {% endif %}
  </div>

  <!-- Notifications -->
  <div class="card">
    <h2>Notifications</h2>
    {% if notifications %}
    <ul class="notif-list">
      {% for n in notifications[:5] %}
      <li>
        <div class="notif-title">{{ n.get("title", n.get("type", "Notification")) }}</div>
        <div>{{ n.get("message", "") }}</div>
        <div class="notif-time">{{ n.get("created_at", "") }}</div>
      </li>
      {% endfor %}
    </ul>
    {% else %}
    <p class="error">Could not load notifications.</p>
    {% endif %}
  </div>

</div>
</body>
</html>
"""


def _get(url: str):
    """Synchronous GET helper; returns parsed JSON or None on failure."""
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.json()
    except Exception:
        return None


@app.route("/")
def index():
    # Fetch aggregated stats from gateway
    stats = _get(f"{GATEWAY_URL}/api/v1/dashboard")

    # Fetch table data directly from services (via gateway or direct)
    orders = _get(f"{GATEWAY_URL}/api/v1/dashboard")  # we already have stats
    # For detailed table data, call services directly
    orders_list = _get("http://localhost:9002/api/v1/orders")
    items_list = _get(f"{CATALOG_URL}/api/v1/items")
    users_map = {}
    users = _get(f"{AUTH_URL}/api/v1/users")
    if isinstance(users, list):
        users_map = {u["id"]: u["name"] for u in users}

    # Enrich orders with customer names
    if isinstance(orders_list, list):
        for o in orders_list:
            cid = o.get("customer_id", "")
            o["customer_name"] = users_map.get(cid, cid)

    # Enrich items with vendor names
    if isinstance(items_list, list):
        for i in items_list:
            vid = i.get("vendor_id", "")
            i["vendor_name"] = users_map.get(vid, vid)

    notifications = _get("http://localhost:9003/api/v1/notifications")

    return render_template_string(
        HTML_TEMPLATE,
        stats=stats,
        orders=orders_list or [],
        items=items_list or [],
        notifications=notifications or [],
    )


@app.route("/health")
def health():
    return {"status": "healthy", "service": "dashboard-ui"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9005, debug=False)
