# Blood Donor Management System (BDMS)

> A full-stack web application to digitise, centralise, and streamline blood bank operations — connecting donors, hospitals, and administrators on a single platform.

## Overview

The Blood Donor Management System (BDMS) is a full-stack, web-based application engineered to replace fragile paper-based blood bank processes with an intelligent, database-driven platform.

According to the WHO, approximately 118.5 million blood donations are collected globally each year, yet demand consistently outpaces supply — especially in developing nations. Every two seconds, a patient somewhere requires a blood transfusion.

BDMS directly addresses this by providing:

- Real-time blood inventory visibility across hospitals
- Automated donor eligibility tracking (enforcing 56-day inter-donation intervals)
- Electronic donation request processing
- Inter-hospital emergency blood exchange
- A unified admin dashboard for data-driven decision making

## Features

### Donor
- Self-registration with auto-generated Donor ID (`BDMS-XXXXXX`)
- Personal dashboard with donation history and eligibility status
- Profile management (edit personal info, change password)
- View and track donation requests

### Hospital Admin
- Dashboard with real-time KPIs — total blood units, low-stock alerts, pending requests
- Donor search by blood group, city, and eligibility
- Accept / reject / fulfil donation requests with audit trail
- Manage blood inventory (add stock / deplete stock)
- Cross-hospital blood exchange requests

### Super Admin
- Register and manage hospitals (create, verify, delete with cascade cleanup)

### System
- Automatic donor eligibility enforcement (56 days whole blood · 7 days platelets · 28 days plasma)
- Low-stock alerts when blood group inventory falls below threshold
- Email notifications for registration, requests, and fulfilment
- Role-based access control (RBAC) with session management
- Audit logging of all critical operations
- CSRF protection on all forms

## Getting Started

### Prerequisites
- Python 3.11+
- MongoDB 4.x (local or [MongoDB Atlas](https://www.mongodb.com/atlas))
- Git

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/bdms.git
cd bdms

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env

# 5. Run the application
python run.py
```

The application will be available at `http://localhost:5000`
