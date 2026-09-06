# Blood Donor Management System

> A full-stack blood-bank management platform built as a **BCA academic project** and deployed on **Render**.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/atlas)
[![Deployed on Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?logo=render&logoColor=111111)](https://render.com/)

## Overview

The Blood Donor Management System (BDMS) digitises donor registration, blood inventory, donation requests, and hospital coordination in one secure web application. It replaces fragmented, manual processes with role-based dashboards and traceable workflows.

## My Role

**Full-Stack Developer — BCA Project**

- Designed and developed the application workflow from donor registration to donation fulfilment.
- Built Flask routes, business services, forms, templates, and MongoDB data models.
- Implemented authentication, role-based access control, CSRF protection, password hashing, and audit-friendly operations.
- Added production configuration and deployed the application with Gunicorn on Render.

## Key Features

| Role | Capabilities |
| --- | --- |
| **Donor** | Register with an auto-generated Donor ID, manage a profile, check eligibility, view history, find hospitals, and submit donation requests. |
| **Hospital Admin** | Monitor inventory and low-stock alerts, search and assign donors, process requests, record donations, and exchange blood with other hospitals. |
| **Super Admin** | Register, verify, manage, and remove hospitals and oversee donor administration. |

### System capabilities

- Donor eligibility rules for whole blood, platelets, and plasma
- Blood inventory additions, depletion, and low-stock thresholds
- Inter-hospital blood exchange workflow
- Email notifications and optional Twilio SMS integration
- Session-based authentication with protected forms and role-based dashboards
- MongoDB indexes for common donor, hospital, request, and inventory queries

## Tech Stack

- **Backend:** Python, Flask, Flask-Login, Flask-WTF
- **Database:** MongoDB / MongoDB Atlas with PyMongo
- **Frontend:** Jinja2 templates, Bootstrap 5, Tailwind CSS,
- **Notifications:** Flask-Mail, optional Twilio SMS(*Feature taken out for hosting purposes)
- **Deployment:** Gunicorn on Render

## Run Locally

### Prerequisites

- Python 3.11+
- MongoDB locally or a MongoDB Atlas connection

### Setup

```bash
git clone https://github.com/Ohil09/Blood_Donor_Management_System.git
cd Blood_Donor_Management_System

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt
```

Copy `.env.example` to `.env`, configure `SECRET_KEY`, `MONGO_URI`, and `MONGO_DB_NAME`, then start the app:

```bash
python run.py
```

Open `http://localhost:5000`.

## Deployment

The project is configured for Render with the included `Procfile`:

The project is live at : https://blood-donor-management-system-t6hw.onrender.com


## Project Structure

```text
app/
├── models/       # MongoDB document models
├── routes/       # Auth, donor, hospital admin, and super-admin routes
├── services/     # Donation, inventory, exchange, email, and ID services
├── forms/        # WTForms validation and CSRF-protected forms
└── templates/    # Jinja2 UI templates
run.py            # Application entry point
Procfile          # Render/Gunicorn process definition
```

---


