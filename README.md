## 🥬 Grocery Store Management System

A complete **end-to-end Grocery Store Management web application** built with **Django + PostgreSQL**, featuring customer shopping, cart management, secure checkout, order tracking, and a powerful manager dashboard with live sales analytics and inventory controls.

---

### 🧩 Key Features

#### 👩‍💻 Customer Side

* 🛍️ Browse and search products by category, price, or keyword
* 🧺 Add to cart, update quantity, and manage wishlist
* 📦 Place orders with address and promo code integration
* 💳 Simulated payment system
* 📜 View order history and order details

#### 🧑‍💼 Manager Side

* 🧾 Manager login and secure access
* 📊 Dashboard showing total products, orders, and sales
* 🔢 Low stock alert system
* ➕ Add/Edit/Delete/Restock products
* 🧮 View monthly and yearly sales analytics (interactive charts)
* 📦 View and update order statuses (Pending → Delivered)
* 💰 Sales & Order management page with revenue summary

---

### ⚙️ Tech Stack

| Category           | Technologies Used                                                |
| ------------------ | ---------------------------------------------------------------- |
| **Backend**        | Django 5.2, Python 3.12                                          |
| **Database**       | PostgreSQL                                                       |
| **Frontend**       | HTML5, CSS3, Bootstrap 5, Chart.js                               |
| **API**            | Django REST Framework (for cart & promo code)                    |
| **Authentication** | Django’s built-in Auth system (custom roles: Manager & Customer) |
| **ORM**            | Django ORM                                                       |
| **Other Tools**    | Django Filters, Messages Framework, Crispy Forms (optional)      |

---

### 🏗️ Database Design (PostgreSQL ER Diagram)

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    USER ||--o{ ADDRESS : has
    USER ||--o{ CARTITEM : adds
    USER ||--o{ WISHLISTITEM : saves

    ORDER ||--|{ ORDERITEM : contains
    ORDER ||--|| PAYMENT : has
    ORDER }o--|| SHIPPINGADDRESS : ships_to
    ORDER }o--|| PROMOCODE : applies

    PRODUCT ||--o{ CARTITEM : included_in
    PRODUCT ||--o{ ORDERITEM : purchased_in
    PRODUCT ||--o{ WISHLISTITEM : wished_by

    USER {
        int id
        string username
        string email
        string password
        string role
    }

    PRODUCT {
        int id
        string name
        string category
        text description
        decimal price
        int stock
        int sold_count
        string image_url
        string image_path
        datetime created_at
    }

    ORDER {
        int id
        decimal total_price
        string status
        datetime created_at
        int user_id
        int promo_code_id
        int shipping_address_id
    }

    ORDERITEM {
        int id
        int order_id
        int product_id
        int quantity
        decimal price_when_bought
    }

    PAYMENT {
        int id
        int order_id
        decimal amount
        bool paid
        string method
        datetime created_at
    }

    CARTITEM {
        int id
        int user_id
        int product_id
        int quantity
        datetime added_at
    }

    WISHLISTITEM {
        int id
        int user_id
        int product_id
        datetime added_at
    }

    SHIPPINGADDRESS {
        int id
        int user_id
        string full_name
        string phone
        string address_line1
        string street
        string city
        string postal_code
        string country
    }

    PROMOCODE {
        int id
        string code
        int discount_percent
        bool active
        datetime created_at
        datetime expires_at
    }
```

---

### 📂 Project Structure

```
groceryapp/
├── accounts/               # User accounts, login, register, address management
├── products/               # Product CRUD, manager panel, dashboard
├── orders/                 # Cart, orders, wishlist, checkout, payments
├── templates/
│   ├── base.html           # Shared layout
│   ├── manager/            # Manager templates (dashboard, reports, etc.)
│   ├── orders/             # Cart, checkout, order detail
│   ├── products/           # Product list, detail
│   └── accounts/           # Login, register, address forms
├── static/                 # CSS, JS, and images
├── manage.py
└── README.md
```

---

### 🧠 Core Functional Flow

#### 🛍️ For Customers

1. Register/Login
2. Browse products
3. Add to cart
4. Apply promo code (optional)
5. Choose address and checkout
6. Place order and simulate payment
7. View order history

#### 🧑‍💼 For Managers

1. Login as `role = 'manager'`
2. Access manager dashboard
3. Manage products (add/edit/restock/delete)
4. View low stock items
5. View all orders and update their statuses
6. Access analytics dashboard for sales overview

---

### 💾 Setup Instructions

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/grocery-store-django.git
cd grocery-store-django
```

#### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate     # On Linux/Mac
venv\Scripts\activate        # On Windows
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure PostgreSQL Database

Create a new database in PostgreSQL and update `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'grocerydb',
        'USER': 'postgres',
        'PASSWORD': 'yourpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 6. Create a Superuser

```bash
python manage.py createsuperuser
```

#### 7. Run the Server

```bash
python manage.py runserver
```

Visit **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** 🎉

---

### 📊 Manager Dashboard Overview

* **Overview Page:** Displays total products, low stock count, total sales, and top sellers
* **Sales Dashboard:** Monthly and yearly analytics with live Chart.js graphs
* **Orders Management:** See all customer orders and update statuses inline
* **Low Stock Alerts:** Automatically highlights items with stock < 5

---

### 🧩 Future Enhancements

* ✅ Export sales data to CSV
* ✅ Generate invoice PDF for each order
* ✅ Email notifications for order status updates
* ✅ Integrate Razorpay/Stripe for live payments
* ✅ Add customer analytics (top buyers, repeat customers)

---

### 👨‍💻 Author

**Yami (Cybersecurity & Software Engineer)**

> A complete Django + PostgreSQL E-Commerce project — built from scratch with love, logic, and coffee ☕

---

### 📜 License

MIT License © 2025 — Free to use, modify, and share with attribution.

---
