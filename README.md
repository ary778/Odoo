Expensify – Enterprise Expense Management API:
<p align="center"> <img alt="Python" src="https://img.shields.io/badge/python-3.11-blue.svg"> <img alt="Django" src="https://img.shields.io/badge/django-5.2-green.svg"> <img alt="DRF" src="https://img.shields.io/badge/DRF-3.15-red.svg"> <img alt="PostgreSQL" src="https://img.shields.io/badge/postgresql-16-blue.svg"> <img alt="License" src="https://img.shields.io/badge/license-MIT-lightgrey.svg"> </p>
Overview:

Expensify is a robust, scalable, and secure backend built with Django and Django REST Framework, designed to simplify enterprise expense management.
It eliminates manual reimbursement challenges by providing a full-featured RESTful API with multi-level approvals, dynamic rules, and role-based control.

Key Features:
<u>Role-Based Access Control</u>

Fine-grained permissions for Admin, Manager, and Employee roles.

<u>Dynamic Approval Workflows</u>

Admins can define multi-step approval sequences (e.g., Manager → Finance → Director).

<u>Conditional Rule Engine</u>

Supports advanced logic such as:

Auto-approval by percentage of approvers.

Approval by specific roles (e.g., CFO).

<u>Secure Authentication</u>

Uses JWT (JSON Web Tokens) for secure, stateless API authentication.

<u>User & Company Management</u>

Automatically creates a Company and Admin on first signup.

Admins can manage all users within their company.

<u>Email Notifications</u>

Sends automatic onboarding emails to new users.

<u>Currency Conversion</u>

Integrates with an external API to display expenses in the manager’s default currency.

<u>OCR Integration (Mock)</u>

Ready-to-use endpoint for receipt scanning & data extraction.

Tech Stack & Architecture:

Expensify follows a clean API-first, decoupled architecture, ensuring separation of backend logic from any frontend client.

Layer	Technology / Tool	Description
Backend Language	Python 3.11	Core programming language
Framework	Django 5.2	High-level web framework
API Toolkit	Django REST Framework	For RESTful endpoints
Database	PostgreSQL 16	Open-source relational DB
Authentication	Simple JWT	Secure, token-based auth
CORS	django-cors-headers	Enables cross-origin requests
Architecture Overview:
<u>Service Layer</u>

Complex logic (like create_approval_workflow, evaluate_conditional_rules) is abstracted into services.py, keeping views.py and models.py clean and modular.

<u>RESTful API</u>

The backend exposes stateless, modular REST endpoints, perfect for frontend or mobile integrations.

<u>Custom User Model</u>

Extends Django’s user to include role-based access and company association.

Getting Started:
Prerequisites

Python 3.10+

PostgreSQL installed and running

Code editor like VS Code

Backend Installation & Setup:
1️⃣ Clone the Repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name/backend

2️⃣ Create and Activate Virtual Environment
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Set Up the Database

Open psql and create a new database:

CREATE DATABASE expense_db;

5️⃣ Configure Environment Variables

Create a .env file in the backend directory (make sure it's in your .gitignore):

# .env
DB_NAME=expense_db
DB_USER=your_postgres_user
DB_PASSWORD=your_postgres_password

EMAIL_USER=youremail@gmail.com
EMAIL_PASSWORD=your16charactergoogleapppassword

6️⃣ Run Database Migrations
python manage.py makemigrations
python manage.py migrate

7️⃣ Start the Development Server
python manage.py runserver


API Base URL: http://127.0.0.1:8000/api/

API Endpoints Overview:
Endpoint	Method	Description	Auth Required
/api/signup/	POST	Create a new Company and Admin user	❌ No
/api/token/	POST	Obtain JWT token	❌ No
/api/expenses/	GET, POST	List or create expenses	✅ Yes
/api/users/	GET, POST	List or create users (Admin only for POST)	✅ Yes
/api/approvals/	GET	List pending approvals for logged-in manager	✅ Yes
/api/approvals/{id}/act/	POST	Approve or reject a specific approval task	✅ Yes
/api/workflows/	GET, POST	Manage multi-step approval workflows (Admin only)	✅ Yes
/api/rules/	GET, POST	Manage conditional approval rules (Admin only)	✅ Yes
Design Philosophy:

“A backend should be invisible but indispensable — fast, modular, and secure.”

Expensify’s architecture prioritizes:

Clean separation of concerns

Reusable service logic

Security-first design

Scalable approval systems

License:

This project is licensed under the MIT License – see the LICENSE
 file for details.

Contributing:

Pull requests are welcome!
For major changes, please open an issue first to discuss your proposal.

⭐ Support

If you find this project useful, consider giving it a ⭐ on GitHub — it helps others discover it!
