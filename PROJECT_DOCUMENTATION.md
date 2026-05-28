# PROJECT SYNOPSIS

## Smart Blood Donor Management System

**Submitted By:** Ohil09 (BCA Final Year Student)  
**Academic Year:** 2025 – 2026  
**Project Type:** Academic Final Year Project  
**Actual Technology Stack:** Python Flask · HTML · Tailwind CSS · MongoDB · PyMongo · Flask-Login · Flask-WTF  
**Date of Submission:** 04 March 2026

---

## Table of Contents

1. Introduction
2. Importance
3. Methodology
4. Project Objectives
5. Analysis & Interpretation
6. Conclusion
7. User Interface & Features
8. Testing & Validation

---

## 1. Introduction

The Smart Blood Donor Management System (BDMS) is a full-stack, web-based application engineered to digitize, centralize, and streamline every facet of blood-bank operations — spanning donor registration, real-time blood inventory tracking, donation request processing, and administrative governance. The system is designed to serve blood banks, hospitals, and broader healthcare organisations as a unified, responsive digital platform that bridges the gap between blood donors, recipients, and medical administrators.

Blood is an irreplaceable, life-critical resource. There is no synthetic substitute. According to the World Health Organization (WHO), approximately 118.5 million blood donations are collected globally each year, yet demand consistently outpaces supply — particularly in developing nations. Every two seconds, a patient somewhere in the world requires a blood transfusion: trauma victims, surgical patients, individuals with chronic anaemia, cancer patients undergoing chemotherapy, and mothers experiencing complicated deliveries are among those whose lives depend on timely blood availability.

Despite this critical demand, the vast majority of blood banks in Tier-2 and Tier-3 cities continue to rely on paper-based registers, disconnected spreadsheets, and telephone-based coordination. These legacy systems are inherently fragile: records are lost, inventory data is delayed or incorrect, donor eligibility is not tracked systematically, and emergency cross-hospital communication is slow and unreliable. The consequences of these inefficiencies are measured in human lives.

The Smart BDMS is conceived as a direct, practical answer to these systemic failures. By replacing fragmented manual processes with an intelligent, database-driven web platform, the system provides healthcare administrators with real-time visibility into blood stock, empowers donors through self-service dashboards and automated eligibility reminders, and equips hospital administrators with the tools to broadcast emergency requests, process donation requisitions instantly, and generate analytical reports for strategic decision-making. The system is built as a BCA-level academic project with deployment-grade architecture, making it both educationally rigorous and practically viable.

---

## 2. Importance

### 2.1 Addressing Operational Inefficiencies

Traditional blood bank management systems are characterised by deeply entrenched operational and administrative challenges:

- **Manual, Paper-Based Record Keeping:** Blood banks maintain donor data, blood stock records, and donation histories in physical registers or rudimentary spreadsheets. These systems are prone to data entry errors, physical damage, and slow searching. Cross-referencing donor records manually during emergencies wastes critical time.

- **Inefficient Donor Tracking and Eligibility Management:** Determining whether a donor is medically eligible to donate again is tracked manually, if at all. Staff must check individual records, which is time-consuming and error-prone.

- **Delayed Emergency Response:** In emergencies requiring rare blood groups (e.g., AB−, B−), locating an eligible donor or a hospital with adequate stock involves multiple phone calls across institutions. There is no centralised visibility into inter-hospital blood reserves, resulting in avoidable delays that can be fatal.

- **Inaccurate and Fragmented Blood Inventory:** Real-time knowledge of available blood units — broken down by blood group (A+, A−, B+, B−, AB+, AB−, O+, O−) — is unavailable in paper systems. Stock data is typically updated intermittently, meaning that inventory levels displayed may be hours or days out of date. Critical shortages may go unnoticed until a request cannot be fulfilled.

- **Absence of Automated Donor Engagement:** There is no automated mechanism to re-engage past donors when they become eligible again, to notify them of upcoming blood donation camps, or to broadcast urgent appeals for critical blood groups.

- **Lack of Data Analytics and Reporting:** Without structured data, administrators cannot identify trends (e.g., which blood groups are chronically in short supply), predict future demand, or make evidence-based decisions about outreach campaigns.

### 2.2 Why This System Matters

By digitizing and centralizing blood bank operations, this system:
- **Saves lives** by reducing the time to locate and deliver blood during medical emergencies
- **Protects donor health** by automatically enforcing donation intervals (56 days whole blood, 7 days platelets, 28 days plasma)
- **Optimizes inventory** through real-time tracking and low-stock alerts
- **Enables data-driven decision-making** through reporting and analytics
- **Facilitates inter-hospital cooperation** during blood shortages through an exchange network
- **Increases donor engagement** through automated notifications and self-service dashboards

---

## 3. Methodology

The Smart BDMS follows a structured, modular development approach using the Flask web framework, MongoDB NoSQL database, and a three-tier role-based access control model.

### 3.1 Architecture Overview

**Backend Framework:** Flask 3.0.3 (Python microframework for building web applications)

**Database:** MongoDB 4.x (NoSQL document-oriented database via PyMongo 4.7.3)
- Chosen for flexible schema design and rapid iterative development
- Stores all entities (users, hospitals, inventory, donations, requests) as JSON documents
- Supports complex queries and indexing for performance optimization

**Frontend:** HTML + Jinja2 templating (server-side rendering) + Tailwind CSS (utility-first CSS framework)

**Authentication & Security:**
- Flask-Login 0.6.3 for session management and user authentication
- Werkzeug password hashing (bcrypt-based) for secure credential storage
- Flask-WTF 1.2.1 with CSRF protection for all forms
- WTForms 3.1.2 for form validation

**Notifications:**
- Flask-Mail 0.10.0 for automated email notifications (SMTP)
- Twilio 9.2.3 for SMS notifications to donors

**Supporting Libraries:**
- python-dotenv 1.0.1 for environment variable management
- python-dateutil 2.9.0 for date/time handling
- itsdangerous 2.2.0 for cryptographic signing

### 3.2 Role-Based Access Control (RBAC) Model

The system implements three distinct user roles with graduated permissions:

**1. Donor Role**
- Register and create a donor account with personal and medical information
- View personal eligibility status and next eligible donation date
- View personal donation history (past donations and blood types donated)
- Submit donation offers to nearby blood banks or hospitals
- Receive automated SMS/email notifications when eligible for re-donation
- Receive notifications about upcoming blood donation camps
- View system announcements and urgent blood appeals

**2. Hospital Admin Role**
- Manage hospital blood inventory by blood group (A+, A−, B+, B−, AB+, AB−, O+, O−)
- Process donation requests from patients/doctors
- Record donations received from donors (update inventory)
- Track donation requests and their fulfillment status
- View inventory analytics and stock trends
- Initiate inter-hospital blood exchange requests during shortages
- Generate reports on donation patterns, inventory levels, and request fulfillment

**3. Superadmin Role**
- System-wide administrative access
- Create and manage hospital accounts
- Create and manage hospital admin accounts
- View system-wide analytics and reporting
- Monitor all donations, requests, and inventory across hospitals
- Manage system configuration and business rules

### 3.3 Core Data Models

The system manages the following primary entities (MongoDB collections):

**User Model**
- Stores donor and admin user information
- Fields: user_id (auto-generated), name, email, phone, password (hashed), role (donor/admin/superadmin), blood_group, medical_history, last_donation_date, created_at, updated_at
- Implements Flask-Login UserMixin for session management

**Hospital Model**
- Represents blood bank or hospital institutions
- Fields: hospital_id (auto-generated), name, address, phone, email, created_by (superadmin), created_at
- Linked to hospital admins for operational management

**Inventory Model**
- Tracks available blood units by blood group per hospital
- Fields: hospital_id, blood_group (O+, O−, A+, A−, B+, B−, AB+, AB−), units_available (integer), last_updated
- Low-stock threshold: 5 units per blood group (configurable via config.py)

**Donation Model**
- Records completed blood donations
- Fields: donation_id, donor_id, hospital_id, blood_group, donation_date, donation_type (whole_blood/platelets/plasma), status
- Used for tracking eligibility and donation history

**DonationRequest Model**
- Represents patient blood transfusion requests from doctors/hospitals
- Fields: request_id, hospital_id, blood_group, units_required, urgency (routine/urgent/critical), status (pending/fulfilled/rejected), created_at, fulfilled_at
- Linked to inventory for fulfillment tracking

**InterHospitalRequest Model**
- Represents emergency blood exchange requests between hospitals
- Fields: request_id, requesting_hospital_id, fulfilling_hospital_id, blood_group, units_requested, status, created_at
- Enables inter-hospital cooperation during shortages

**ExchangeRequest Model**
- Manages blood exchange agreements between hospitals
- Tracks temporary transfers of blood units with return obligations
- Supports emergency response coordination

### 3.4 Business Rules & Eligibility Intervals

The system enforces the following medical guidelines:

- **Whole Blood Donation Interval:** 56 days minimum between donations
- **Platelet Donation Interval:** 7 days minimum (can donate more frequently)
- **Plasma Donation Interval:** 28 days minimum
- **Low Stock Threshold:** 5 units per blood group per hospital (triggers admin notifications)
- **Donor Eligibility Status:** Automatically calculated based on last_donation_date and donation_type

### 3.5 Key Features by Module

**Authentication Module (auth.py - 135 lines)**
- Donor registration: collects personal, contact, and medical information
- Hospital admin registration: restricted to superadmin account creation
- Login: secure password verification with session management
- Logout: session termination and cleanup

**Donor Module (donor.py - 384 lines)**
- Dashboard: displays donor eligibility status, donation history, next eligible date
- Profile management: view/update personal information
- Donation offers: submit availability to blood banks
- Notification settings: manage SMS/email preferences
- Donation history: view complete record of past donations with blood types

**Hospital Admin Module (admin.py - 830 lines)**
- Inventory Management: add/update/delete blood units by blood group
- Donation Request Processing: create, view, and fulfill patient blood requests
- Request Fulfillment: record completed donations and update inventory
- Inter-Hospital Exchange: initiate emergency blood exchange requests
- Analytics & Reporting: view charts and statistics on inventory, donations, request patterns
- Donation Assignment: assign donors to specific requests (matching blood group)
- Emergency Broadcast: send urgent appeals for specific blood groups

**Superadmin Module (superadmin.py - 171 lines)**
- Hospital Management: create, activate, and manage hospital accounts
- Admin Account Creation: create superadmin-level accounts for hospital administrators
- System-Wide Analytics: cross-hospital reporting and trend analysis
- Configuration Management: update business rules and thresholds

**Services Layer**
The system abstracts business logic into reusable services:
- **DonationService:** Calculates eligibility, records donations, enforces intervals
- **InventoryService:** Manages stock tracking, low-stock alerts, fulfillment logic
- **EmailService:** Sends automated notifications (eligibility reminders, urgent appeals, confirmations)
- **ExchangeService:** Manages inter-hospital blood exchange coordination
- **AssignmentService:** Matches donors to requests by blood group and eligibility

---

## 4. Project Objectives

### 4.1 Primary Objectives

1. **Digitize Donor Management**
   - Eliminate paper-based donor records
   - Maintain comprehensive donor history and eligibility tracking
   - Enable rapid donor search and contact

2. **Centralize Blood Inventory**
   - Provide real-time visibility into blood stock by blood group per hospital
   - Implement automated low-stock alerts
   - Enable data-driven restocking decisions

3. **Streamline Request Processing**
   - Enable doctors/hospitals to submit blood requests electronically
   - Automate request fulfillment and inventory updates
   - Track request status from submission to fulfillment

4. **Enforce Medical Safety Standards**
   - Automatically track donation intervals (56 days whole blood, 7 days platelets, 28 days plasma)
   - Prevent medically ineligible donors from donating
   - Maintain audit trails for safety compliance

5. **Enable Emergency Response**
   - Facilitate rapid location of compatible blood during medical emergencies
   - Enable inter-hospital coordination during shortages
   - Support emergency blood exchange network

6. **Engage and Retain Donors**
   - Automate notifications when donors become eligible for re-donation
   - Notify donors of upcoming blood camps
   - Broadcast urgent appeals for critical blood groups
   - Maintain donor engagement through personalized communication

7. **Generate Actionable Intelligence**
   - Provide analytics on donation patterns, inventory trends, and request patterns
   - Support evidence-based decision-making for outreach campaigns
   - Identify blood group shortages for targeted donor recruitment

### 4.2 Secondary Objectives

- Provide a scalable, maintainable codebase for future enhancements
- Demonstrate best practices in web application development (MVC architecture, service layer separation)
- Create a deployment-ready system suitable for real-world blood bank operations
- Develop a user-friendly interface for both technical and non-technical users

---

## 5. Analysis & Interpretation

### 5.1 System Architecture

The Smart BDMS follows a three-tier architecture:

```
┌─────────────────────────────────────────┐
│      Presentation Layer (Frontend)      │
│  HTML + Jinja2 Templates + Tailwind CSS │
└─────────────────┬───────────────────────┘
                  │ HTTP/Session
┌─────────────────▼───────────────────────┐
│      Application Layer (Backend)        │
│  Flask Framework + Route Handlers       │
│  Authentication (Flask-Login)           │
│  Business Services (DonationService,    │
│   InventoryService, EmailService, etc)  │
└─────────────────┬───────────────────────┘
                  │ PyMongo Driver
┌─────────────────▼───────────────────────┐
│       Data Layer (Persistence)          │
│  MongoDB 4.x (Document Database)        │
│  Collections: users, hospitals,         │
│   inventory, donations, requests, etc   │
└─────────────────────────────────────────┘
```

### 5.2 Data Flow Diagrams

**Donor Registration & Eligibility Flow:**
```
New Donor → Registration Form → Validation → MongoDB User Store
                                  ↓
                         Password Hashing (Werkzeug)
                                  ↓
                    Auto-Generate Donor ID
                                  ↓
                       Send Confirmation Email
                                  ↓
                    Donor Account Active
                    (eligible to donate immediately)
```

**Donation Request Fulfillment Flow:**
```
Doctor/Admin Creates Request
         ↓
   Blood Group Match
         ↓
  Inventory Check (InventoryService)
         ↓
  Sufficient Stock? ──Yes──→ Deduct from Inventory
         │                        ↓
        No                  Mark Request Fulfilled
         ↓                        ↓
  Low Stock Alert           Send Confirmation Email
  (EmailService)                  ↓
         ↓                   Update Analytics
   Notify Hospital Admin
```

**Donor Eligibility Calculation:**
```
Last Donation Date + Type
         ↓
  Determine Interval Requirement
  (56 days whole blood, 7 days platelets, 28 days plasma)
         ↓
  Calculate Next Eligible Date
         ↓
  Current Date >= Next Eligible? ──Yes──→ Eligible (can donate)
                   │
                  No ──→ Not Yet Eligible
                         (notify when eligible)
```

**Inter-Hospital Exchange Flow:**
```
Hospital A (Low Stock) Creates Exchange Request
              ↓
  System Identifies Hospital B (Has Surplus)
              ↓
  Hospital B Receives Request (Admin Notification)
              ↓
  Hospital B Accepts Exchange
              ↓
  Physical Blood Transfer Initiated
              ↓
  Inventory Updated Both Hospitals
              ↓
  Email Confirmation to Both Admins
```

### 5.3 Database Structure

MongoDB Collections and Sample Document Structure:

**users Collection**
```json
{
  "_id": ObjectId,
  "user_id": "DONOR_001",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "9876543210",
  "password_hash": "$2b$12$...",
  "role": "donor",
  "blood_group": "O+",
  "medical_conditions": ["None"],
  "last_donation_date": ISODate("2025-12-15"),
  "last_donation_type": "whole_blood",
  "created_at": ISODate("2025-01-01"),
  "updated_at": ISODate("2025-12-15")
}
```

**hospitals Collection**
```json
{
  "_id": ObjectId,
  "hospital_id": "HOSP_001",
  "name": "City Medical Center",
  "address": "123 Main St, City, State 12345",
  "phone": "1234567890",
  "email": "admin@citymedical.com",
  "created_by": "superadmin_user_id",
  "created_at": ISODate("2025-01-01"),
  "is_active": true
}
```

**inventory Collection**
```json
{
  "_id": ObjectId,
  "hospital_id": "HOSP_001",
  "blood_group": "O+",
  "units_available": 12,
  "last_updated": ISODate("2025-12-28"),
  "low_stock_alert_sent": false
}
```

**donations Collection**
```json
{
  "_id": ObjectId,
  "donation_id": "DONA_001",
  "donor_id": "DONOR_001",
  "hospital_id": "HOSP_001",
  "blood_group": "O+",
  "donation_date": ISODate("2025-12-15"),
  "donation_type": "whole_blood",
  "status": "completed",
  "recorded_by": "admin_user_id"
}
```

**donation_requests Collection**
```json
{
  "_id": ObjectId,
  "request_id": "REQ_001",
  "hospital_id": "HOSP_001",
  "patient_name": "Jane Smith",
  "blood_group": "A-",
  "units_required": 3,
  "urgency": "urgent",
  "status": "fulfilled",
  "created_at": ISODate("2025-12-28T10:30:00Z"),
  "fulfilled_at": ISODate("2025-12-28T11:15:00Z"),
  "created_by": "admin_user_id"
}
```

**inter_hospital_requests Collection**
```json
{
  "_id": ObjectId,
  "request_id": "INTER_001",
  "requesting_hospital_id": "HOSP_001",
  "fulfilling_hospital_id": "HOSP_002",
  "blood_group": "AB-",
  "units_requested": 2,
  "status": "fulfilled",
  "created_at": ISODate("2025-12-28"),
  "fulfilled_at": ISODate("2025-12-28")
}
```

### 5.4 Key Implementation Details

**Password Security**
- All passwords hashed using Werkzeug security (bcrypt-based)
- Plain-text passwords never stored or logged
- Password verification using secure comparison methods

**Session Management**
- Flask-Login manages user sessions
- Session tokens generated securely
- Automatic session expiration
- CSRF protection on all state-changing requests via Flask-WTF

**Email Notifications**
- Sent via Flask-Mail using SMTP
- Async delivery (non-blocking)
- Templates for various notification types (eligibility, requests, appeals, confirmations)
- Error handling and delivery tracking

**SMS Notifications**
- Sent via Twilio API
- Used for urgent alerts and critical notifications
- Fallback to email if SMS delivery fails

**Inventory Tracking**
- Real-time updates via InventoryService
- Low-stock alerts triggered when units fall below threshold (5 units)
- Audit trail maintained for all inventory changes
- Stock deduction on request fulfillment (atomic transaction-like operations)

---

## 6. Conclusion

The Smart Blood Donor Management System represents a significant modernization of blood bank operations, addressing chronic inefficiencies in donor tracking, inventory management, emergency response, and donor engagement. By replacing paper-based systems with an intelligent, real-time digital platform, the system has the potential to:

1. **Save lives** through faster emergency blood location and delivery
2. **Protect donor health** through automated eligibility enforcement
3. **Optimize resources** through real-time inventory visibility
4. **Enable data-driven decisions** through analytics and reporting
5. **Strengthen inter-hospital cooperation** during blood shortages
6. **Engage donors** through personalized, automated communication

The system is built with modern web technologies (Flask, MongoDB, Tailwind CSS) and follows best practices in security, usability, and maintainability. With proper deployment and adoption by blood banks and hospitals, the Smart BDMS has the potential to become an essential infrastructure for efficient blood donation management in healthcare systems worldwide.

### 6.1 Future Enhancements

Potential areas for expansion in future versions:
- Mobile app (iOS/Android) for donor self-service
- Advanced analytics with machine learning for demand prediction
- Integration with hospital ERP systems
- Real-time blood type compatibility checking (crossmatching records)
- Geolocation-based donor search for rapid response
- Blockchain-based blood unit tracking for traceability
- Multi-language support for regional adoption

---

## 7. User Interface & Features

### 7.1 Donor Portal

**Dashboard**
- Displays current eligibility status (Eligible / Not Eligible Until [Date])
- Shows last donation date and blood type donated
- Displays donation history with dates and blood types
- Quick-access buttons for "Donate Now" and "Update Profile"
- Notification center for alerts and blood camp announcements

**Profile Management**
- View and edit personal information (name, email, phone)
- View medical history and conditions
- Update emergency contact information
- Manage notification preferences (SMS/Email)

**Donation History**
- Complete list of past donations with dates, blood types, and hospital names
- Filter by date range or blood type
- Download donation certificate (proof of donation)

**Donation Offers**
- Submit availability to donate at nearby blood banks
- Select preferred blood bank from list
- Indicate preferred donation date/time
- Receive confirmation when blood bank accepts offer

### 7.2 Hospital Admin Portal

**Dashboard**
- Real-time inventory summary (units available by blood group)
- List of pending donation requests (patients waiting for blood)
- List of recent donations received
- Low-stock alerts highlighting critical blood groups
- Quick-access to key operations

**Inventory Management**
- Add new blood units (with blood group, collection date)
- Update available units (manual adjustment)
- View inventory history and trends
- Set low-stock thresholds (default 5 units)
- Export inventory reports

**Donation Requests**
- Create new request (blood group, units needed, urgency, patient details)
- View all requests (pending, fulfilled, rejected)
- Fulfill request (select donor or inter-hospital source)
- Mark request as fulfilled (with fulfillment date and details)
- Generate request fulfillment reports

**Donor Assignment**
- Search donors by blood group and eligibility status
- Assign eligible donors to specific requests
- Send notification to assigned donors
- Track assignment status and response

**Inter-Hospital Exchange**
- View requests from other hospitals
- Send exchange request to nearby hospitals during shortages
- Accept/reject exchange requests from other hospitals
- Track exchange status and blood transfer details

**Analytics & Reports**
- Inventory trends (chart showing stock levels over time)
- Donation patterns (donors per month, blood groups requested)
- Request fulfillment rates
- Emergency response times
- Export reports as PDF/CSV

### 7.3 Superadmin Portal

**Hospital Management**
- Create new hospital accounts with basic information
- Activate/deactivate hospitals
- View all hospitals and their contact details
- Monitor hospital activity and performance

**Admin Account Management**
- Create hospital admin accounts (linked to specific hospitals)
- Assign superadmin permissions
- View admin activity logs
- Reset admin passwords if needed

**System-Wide Analytics**
- Cross-hospital inventory summary
- Total donations by month/blood group
- Inter-hospital exchange activity
- System usage metrics

---

## 8. Testing & Validation

### 8.1 Test Coverage

The system includes comprehensive testing across multiple layers:

**Unit Tests**
- Model validation tests (donor registration, blood group validation)
- Service layer tests (DonationService eligibility calculation, InventoryService stock management)
- Authentication tests (login, logout, session management)

**Integration Tests**
- End-to-end donor registration workflow
- Donation request creation and fulfillment
- Inter-hospital exchange coordination
- Email notification delivery

**User Acceptance Tests**
- Donor portal functionality (registration, eligibility check, history viewing)
- Admin portal functionality (inventory management, request processing)
- Superadmin portal functionality (hospital management)

### 8.2 Security Testing

- CSRF protection validation (all forms)
- SQL injection protection (MongoDB query parameterization)
- XSS prevention (template escaping)
- Password hashing verification (Werkzeug bcrypt)
- Session security testing (timeout, fixation attacks)

### 8.3 Performance Testing

- Database query optimization (MongoDB indexes on frequently searched fields)
- Request handling under load (multi-concurrent requests)
- Email delivery performance (queue handling)
- Page load times (frontend optimization)

### 8.4 Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## Bibliography & References

### Primary Technologies
1. Flask 3.0.3 Documentation - https://flask.palletsprojects.com/
2. MongoDB Documentation - https://docs.mongodb.com/
3. PyMongo 4.7.3 Documentation - https://pymongo.readthedocs.io/
4. Flask-Login 0.6.3 - https://flask-login.readthedocs.io/
5. Flask-WTF 1.2.1 - https://flask-wtf.readthedocs.io/
6. Werkzeug 3.0.3 - https://werkzeug.palletsprojects.com/
7. Jinja2 3.1.4 - https://jinja.palletsprojects.com/

### Security & Authentication
8. OWASP Top 10 Web Application Security Risks - https://owasp.org/www-project-top-ten/
9. CSRF Protection Best Practices - https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
10. Password Storage Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

### Domain Knowledge - Blood Banking
11. WHO Guidelines on Blood Safety and Availability - https://www.who.int/teams/regulation-prequalification/blood-products/who-guidelines-on-blood-safety-and-availability
12. FDA Blood Donor Eligibility Guidelines - https://www.fda.gov/vaccines-blood-biologics/blood-blood-products/donor-eligibility
13. Transfusion Medicine Best Practices - American Association of Blood Banks (AABB)

### Frontend & UI
14. Tailwind CSS 3.x Documentation - https://tailwindcss.com/docs
15. HTML5 Specification - https://html.spec.whatwg.org/
16. Responsive Web Design Best Practices - https://www.w3.org/WAI/

### Database Design
17. MongoDB Best Practices - https://docs.mongodb.com/manual/administration/
18. NoSQL Database Design Patterns - https://redis.com/glossary/nosql-database/

---

**Project Status:** Complete as of March 2026  
**Maintainer:** Ohil09  
**License:** [As specified in project repository]  
**Last Updated:** May 2026

