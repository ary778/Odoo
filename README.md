Expensify - Enterprise Expense Management API
<p align="center">
<img alt="Python" src="https://img.shields.io/badge/python-3.11-blue.svg">
<img alt="Django" src="https://img.shields.io/badge/django-5.2-green.svg">
<img alt="DRF" src="https://img.shields.io/badge/DRF-3.15-red.svg">
<img alt="PostgreSQL" src="https://img.shields.io/badge/postgresql-16-blue.svg">
<img alt="License" src="https://img.shields.io/badge/license-MIT-lightgrey.svg">
</p>

A robust, scalable, and secure backend for a modern expense management platform, built with Django and Django REST Framework.

About The Project
Expensify is a powerful backend solution designed to solve the common challenges of manual expense reimbursement. It provides a full-featured RESTful API to handle complex, multi-level approval workflows, conditional rules, and role-based permissions, eliminating time-consuming and error-prone manual processes. 

Key Features

Role-Based Access Control: Granular permissions for Admin, Manager, and Employee roles. 



Dynamic Approval Workflows: Admins can define custom, multi-step approval sequences (e.g., Manager → Finance → Director). 


Conditional Rule Engine: Supports advanced approval logic, such as auto-approval based on a percentage of approvers or approval by a specific high-level user (e.g., CFO). 

Secure Authentication: Uses JSON Web Tokens (JWT) for secure, stateless API authentication.


User & Company Management: Automated company and admin creation on first signup, with full user management capabilities for admins. 


Email Notifications: Automatic email notifications are sent to new users upon account creation.


Currency Conversion: Integrated with an external API to display expense amounts in the manager's default currency. 



OCR Integration (Mock): Includes a ready-to-use endpoint for integrating OCR to auto-read receipt data. 

Tech Stack & Architecture
This project is built with an API-first, decoupled architecture, ensuring a clean separation between the business logic on the backend and the user interface.

Backend
Technology	Description
Python 3.11	Core programming language.
Django 5.2	High-level web framework for rapid development.
Django REST Framework	Powerful toolkit for building Web APIs.
PostgreSQL	Robust, open-source relational database.
Simple JWT	JSON Web Token authentication for DRF.
django-cors-headers	Handles Cross-Origin Resource Sharing (CORS).

Export to Sheets
Architecture
Service Layer: Complex business logic (e.g., create_approval_workflow, evaluate_conditional_rules) is abstracted into a dedicated services.py file to keep views and models clean.

RESTful API: The application exposes a set of well-defined, stateless RESTful endpoints.

Custom User Model: Extends Django's default user to include roles and company relationships.

Getting Started
Follow these steps to get the backend running locally.

Prerequisites
Python 3.10+

PostgreSQL installed and running

A code editor like VS Code

Backend Installation & Setup
Clone the repository

Bash

git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name/backend
Create and activate a virtual environment

Bash

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies

Bash

pip install -r requirements.txt
Set up the database

Open psql and create the database:

SQL

CREATE DATABASE expense_db;
Configure Environment Variables

Create a .env file in the backend directory.

Add your database and email credentials. This file should be in your .gitignore!

Code snippet

# .env
DB_NAME=expense_db
DB_USER=your_postgres_user
DB_PASSWORD=your_postgres_password

EMAIL_USER=youremail@gmail.com
EMAIL_PASSWORD=your16charactergoogleapppassword
Run Database Migrations

Bash

python manage.py makemigrations
python manage.py migrate
Run the development server

Bash

python manage.py runserver
The API will be available at http://127.0.0.1:8000/api/.

API Endpoints Overview
Endpoint	Method	Description	Auth Required
/api/signup/	POST	Creates a new Company and Admin user.	No
/api/token/	POST	Obtains JWT for a user.	No
/api/expenses/	GET, POST	List all relevant expenses or create a new one.	Yes
/api/users/	GET, POST	List or create users (Admin only for POST).	Yes
/api/approvals/	GET	List pending approvals for the logged-in manager.	Yes
/api/approvals/{id}/act/	POST	Approve or reject a specific approval task.	Yes
/api/workflows/	GET, POST	List or create multi-step approval workflows (Admin only).	Yes
/api/rules/	GET, POST	List or create conditional approval rules (Admin only).	Yes
