# Expense Management System

The Expense Management System is a SaaS solution designed to streamline and automate corporate Travel & Expense (T&E) workflows. It reduces operational friction, enhances data accuracy, and ensures compliance by replacing manual reimbursement processes. This repository contains the decoupled frontend client, a lightweight Vanilla JavaScript Single Page Application (SPA) that integrates with a backend RESTful API.

## Overview

This system optimizes expense tracking and reimbursement for organizations through the following key features:

- **Multi-Tenant Onboarding**: Admins can create company tenants, define default currencies based on country selection, and configure organizational settings.
- **Role-Based Access Control (RBAC)**:
  - **System Administrator**: Full oversight to manage users, approval hierarchies, and resolve escalations.
  - **Approving Manager**: Dedicated dashboard to review and action expense claims in the company's default currency.
  - **Individual Contributor**: Submit expense claims in multiple currencies and track submission status (In Process, Approved, Rejected).
- **Configurable Approval Workflows**: Dynamic, multi-level approval chains to route claims through organizational hierarchies.
- **Stateful Dashboards**: Persona-specific interfaces that persist session data and streamline user interactions.

## System Architecture

The system employs a decoupled architecture for scalability, maintainability, and independent deployment of frontend and backend components.

### Frontend

- **Core**: Vanilla JavaScript (ES6+) and HTML5 for a lightweight SPA with no framework dependencies.
- **Styling**: CSS3 with a custom design system using CSS Variables for theming and maintainability.
- **Routing**: Browser History API for seamless, multi-page-like navigation.
- **State Management**: Global application scope for client-side state, eliminating external library overhead.

### Backend (Designed)

- **Framework**: Django with Django REST Framework for a secure, scalable RESTful API.
- **Authentication**: JSON Web Tokens (JWT) for stateless, secure client-server communication.
- **Database**: PostgreSQL for robust relational data management.
- **Caching**: Redis for performance optimization of frequent queries (e.g., user lists, expense reports).

## Getting Started

Follow these steps to set up the frontend for local development.

### Prerequisites

- Code editor (e.g., Visual Studio Code)
- Live Server extension for VS Code
- Backend server running at `http://127.0.0.1:8000` (use a `.env` file for secrets like database credentials and `SECRET_KEY`)

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/Ary778/Odoo.git
   ```
2. Navigate to the frontend directory:
   ```bash
   cd Odoo/frontend
   ```
3. Launch the development server:
   - Right-click `index.html` in VS Code and select `Open with Live Server`.

## Product Roadmap

Planned features for future sprints:

- OCR Integration: Automate receipt data entry using services like AWS Textract or Google Cloud Vision.
- Advanced Rules Engine: Support conditional logic for approval workflows based on expense categories or amounts.
- Third-Party Integrations: Sync with accounting platforms like QuickBooks or Xero.
- Analytics & Reporting: Generate insights on spending patterns, budget adherence, and approval cycle times.
- CI/CD Pipeline: Automate testing and deployments with GitHub Actions.

## Contribution Guidelines

Contributions are welcome. Please adhere to the following:

- **Branch Naming**: Use `feature/<feature-name>`, `bugfix/<bug-name>`, or `hotfix/<fix-name>`.
- **Commit Messages**: Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.
- **Code Style**: Adhere to existing conventions. ESLint/Prettier configurations will be added for consistency.

## License

Distributed under the MIT License. See `LICENSE` for details.

## Contributors

- Jash Parekh
- Aryan Suthar
