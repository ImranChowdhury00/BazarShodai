# BazarShodai
Single Vendor E-commerce Platform, built using Django, offering secure login with email authentication and secure payment with SSLCommerz.

---

### Features:

* **Secure Authentication:** Managed by the `accounts` app, including signup, login, and secure password reset.
* **Email Verification:** Ensures a valid user base through email verification links upon registration.
* **Product details:** Managed by the `products` app, supporting categories, product details, and image uploads.
* **Dynamic Shopping Cart:** Handled by the `carts` app, allowing users to add, update, and remove items with session and database persistence.

* **Order Flow:** Managed by the `order` app, covering checkout, transaction logging, and order status updates (Pending, Processing, Shipped, Delivered).
* **Secure Payments:** Integrated with **SSLCommerz** for reliable and secure payment processing.


---
##  Project Structure (4 Apps)

The project is logically divided into four main Django applications for clear separation and the project smooth.

| App | Primary Responsibilities |
| :--- | :--- |
| **`accounts`** | User registration, authentication, user profiles, and email verification. |
| **`products`** | Defines Product models, Categories, product image management, and catagory views. |
| **`carts`** | Manages the user's shopping cart state, quantity updates, and calculating cart totals. |
| **`orders`** | Handles the checkout process, payment integration with SSLCommerz, order creation, and order history tracking. |

## Technology used :
| Technology | Description |
| :--- | :--- |
| **Backend Framework** | Django (Python) |
| **Database** | SQLite |
| **Payment Gateway** | SSLCommerz |
| **Email Service** | Google SMTP |
| **Frontend** | [ HTML, CSS, JS, Bootstrap ] |

---
## Getting Started
<h4>Follow this steps sequentially to set up and run the project on local machine.</h4>

### Project pre-requisites:

* **Python 3.x**
* **pip (python package installer)**

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ImranChowdhury00/BazarShodai.git
```
2. **Create and active virtual environment**
```bash
pip install virtualenv
virtualenv env
Source ./env/Scripts/activate
```
3. **Install dependencies**
```bash
pip install -r requirements.txt
```
4. **Database migration**
* Apply migrations
```bash
python manage.py makemigrations
python manage.py migrate
```
* (optinal) create superuser for admin panel
```bash
py manage.py createsuperuser
```
5. **Environment variables**

Create a folder named `.env` in the root directory and add you secret keys. **This is very secured folder. Don't share this folder.**
```bash
DELIVERY_CHARGE=120

# email configuration
EMAIL_HOST_USER='[your_host_email_addess]'
EMAIL_HOST_PASSWORD='[your_host_email_password]'

# sslcommerz configuration
SSLCOMMERZ_STORE_ID = '[your_sslcommerz_store_id]'
SSLCOMMERZ_STORE_PASS = '[you_sslcommerz_store_password]'
```
### Running the server

1. Start django development server
```bash
python manage.py runserver
```
2. open your browser and navigate to : `http://127.0.0.1:8000/`

---
## Authentication details

### Email verification flow:

* upon registration , user receives and email including **verification link**.
* account remains inactive until the user clicks the verification link.
* This prevents spam and ensure valid customer.
---

## Payment Integration (SSLCommerz)

### How it Works:

1.  When a user proceeds to checkout, the system generates a unique transaction ID.
2.  The user is redirected to the **SSLCommerz payment portal**.
3.  Upon successful payment, SSLCommerz sends a **success confirmation** back to the defined endpoint (`succes_url` or `failed_url`).

---