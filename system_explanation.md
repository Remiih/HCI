# Inventory Management System - Rubric Compliance Guide

This document explains how the system meets every criterion of the project rubric.

## 1. User Authentication & Authorization (20 Points)

### Authentication (10 pts)

_Criteria: Secure user login with proper password handling (e.g., hashing)._

- **Implementation**:
  - Passwords are hashed using **Argon2**, the modern standard for password security.
  - Secure login form prevents access without valid credentials.
  - System prevents brute-force checks by verifying generic "Invalid Username/Password" messages.

### Authorization (10 pts)

_Criteria: Role-based or permission-based access control to restrict access to resources._

- **Implementation**:
  - **Standard Users (Read-Only)**: Can only view the inventory and use search. The "Add", "Update", and "Delete" interface elements are hidden or disabled.
  - **Admin Users (Full Access)**: Have exclusive access to the "Add Item" form, "Manage Items" panel (Update/Delete), and "Create Admin" tool.
  - **RBAC Logic**: `app.py` checks `st.session_state.role` ('admin' vs 'user') before rendering sensitive UI components.

## 2. CRUD Operations for Data Management (15 Points)

### Create Operation (5 pts)

_Criteria: Secure creation of records with validation and proper access control._

- **Implementation**:
  - **Admins** can add new inventory items via the "Add New Item" expander.
  - **Security**: Uses parameterized SQL queries (`INSERT INTO ... VALUES (?, ?)`) to prevent SQL injection.
  - **Validation**: Item Name is required; Quantity/Price must be non-negative numbers.

### Read Operation (5 pts)

_Criteria: Proper retrieval of data with appropriate access control._

- **Implementation**:
  - All authenticated users can view the "Current Inventory" table.
  - Data is fetched securely using `pd.read_sql_query`.

### Update & Delete Operations (5 pts)

_Criteria: Secure and validated update/delete functionality with proper authorization checks._

- **Implementation**:
  - **Update**: Admins can modify stock quantities instantly using the "Quick Update" tool.
  - **Delete**: Admins can permanently remove items via the "Delete Item" tool.
  - **Authorization**: The dashboard hides these controls for standard users. Server-side logic prevents execution if a non-admin somehow triggered the request.

## 3. Data Validation (10 Points)

### Input Validation and Sanitization (10 pts)

_Criteria: Ensuring input data is correct and within acceptable format, type, and range._

- **Implementation**:
  - **Passwords**: Enforces complexity (Min 8 chars, 1 Upper, 1 Lower, 1 Digit, 1 Special) and max length (72 bytes).
  - **Usernames**: Must be 3-20 characters, alphanumeric only (no spaces/symbols) to prevent injection or formatting exploits.
  - **Inventory Data**: Numeric fields (Price, Quantity) are restricted by UI widgets to numeric input only.

## 4. Verification (10 Points)

### Account Verification (10 pts)

_Criteria: Verification process (email/phone/OTP) for user registration or login._

- **Implementation**:
  - **Mandatory 2FA**: The system requires **Time-based One-Time Password (TOTP)** for every login.
  - **Setup**: During registration, users must scan a QR code with Google Authenticator (or similar app).
  - **Login Verification**: After password check, users must provide the valid 6-digit code to proceed. This effectively stops unauthorized access even if the password is stolen.

## 5. Search and Filter (5 Points)

### Search Functionality (5 pts)

_Criteria: Efficient and secure search capability._

- **Implementation**:
  - A dedicated **Search Bar** filters the inventory table in real-time.
  - Supports searching by **Item Name** OR **Category**.
  - Uses in-memory Pandas filtering for instant response without database lag.

## 6. Security (20 Points)

### Encryption (10 pts)

_Criteria: Ensuring sensitive data is encrypted or hashed._

- **Implementation**:
  - **Passwords**: Hashed with Argon2 (via `passlib`/`argon2-cffi`).
  - **2FA Secrets**: Unique secrets are generated per user.

### Access Control (5 pts)

_Criteria: Fine-grained control over who can access specific data._

- **Implementation**:
  - Session State management ensures unauthenticated users are redirected to login immediately (`st.session_state.authenticated` check).
  - RBAC ensures standard users cannot modify data.

### Logging & Monitoring (5 pts)

_Criteria: Logging of critical actions and monitoring for suspicious activity._

- **Implementation**:
  - **Activity Log**: Records `LOGIN`, `LOGOUT`, `USER_REGISTER`, `ADD_ITEM`, `UPDATE_ITEM`, `DELETE_ITEM`, `ADMIN_CREATE_ADMIN`.
  - **Security**: The "Activity Logs" view on the dashboard is **restricted to Admins only**, preventing regular users from seeing sensitive system activity.

## 7. Interface (5 Points)

_Criteria: User interface is intuitive, user-friendly, and responsive._

- **Implementation**:
  - **Split-Screen Design**: Modern Login/Register pages with a green/white split layout.
  - **Responsiveness**: Layout adapts to different screen sizes securely.
  - **Feedback**: Toasts (Success/Error messages) guide the user through every action.

## 8. Presentation (10 Points)

_Criteria: Professionalism of design, organization, and clarity._

- **Implementation**:
  - Code is modular (separated into `app.py`, `auth.py`, `db.py`) and clean.
  - The application looks professional with the "Green Theme" and consistent styling.
  - All features (Auth -> 2FA -> Dashboard -> Logout) flow logically without errors.
