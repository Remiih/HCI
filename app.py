import streamlit as st
import pandas as pd
import time
import db
import auth

# --- Page Config ---
st.set_page_config(page_title="Inventory System", layout="centered", page_icon="📦")

# --- Init DB ---
db.init_db()

# --- Session State Management ---
if 'auth_step' not in st.session_state:
    st.session_state.auth_step = 'login' # login, register_otp, otp, dashboard
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'temp_reg_data' not in st.session_state:
    st.session_state.temp_reg_data = {}

# --- Logout Function ---
def logout():
    st.session_state.clear()
    st.rerun()

# --- Views ---

def login_view():
    st.title("🔐 Inventory Login")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if len(password.encode('utf-8')) > 72:
                     st.error("Password is too long (max 72 bytes)")
                else:
                    user = db.get_user(username)
                    if user and auth.verify_password(password, user[2]): # user[2] is password_hash
                        st.session_state.username = username
                        st.session_state.auth_step = 'otp'
                        st.success("Credentials valid. Please enter OTP.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid username or password")

    with tab2:
        st.subheader("Create New Account")
        with st.form("register_start_form"):
            new_user = st.text_input("Choose Username")
            new_pass = st.text_input("Choose Password", type="password")
            reg_submitted = st.form_submit_button("Next Step")
            
            if reg_submitted:
                pass_valid, pass_msg = auth.validate_password(new_pass)
                user_valid, user_msg = auth.validate_username(new_user)
                
                if not new_user or not new_pass:
                    st.error("Please fill in all fields")
                elif not user_valid:
                    st.error(user_msg)
                elif not pass_valid:
                    st.error(pass_msg)
                elif db.get_user(new_user):
                    st.error("Username already exists")
                else:
                    # Generate Secret and move to OTP confirmation
                    secret = auth.generate_totp_secret()
                    st.session_state.temp_reg_data = {
                        'username': new_user,
                        'password': new_pass,
                        'secret': secret
                    }
                    st.session_state.auth_step = 'register_otp'
                    st.rerun()

def register_otp_view():
    st.title("📱 Setup Authenticator")
    st.warning("Scan this QR code with your Authenticator App (Google Authenticator, Authy, etc.)")
    
    data = st.session_state.temp_reg_data
    if not data:
        st.error("Registration session lost. Please restart.")
        if st.button("Back"):
            st.session_state.auth_step = 'login'
            st.rerun()
        return

    # Generate URI and QR Code
    uri = auth.get_totp_uri(data['username'], data['secret'])
    qr_image = auth.generate_qr_code(uri)
    
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.image(qr_image, caption="Scan me", width=250)
        st.code(data['secret'], language="text") # Backup code
    
    st.info("Enter the 6-digit code from your app to verify and complete registration.")
    
    with st.form("verify_reg_otp"):
        code = st.text_input("Enter 6-digit Code", max_chars=6)
        submitted = st.form_submit_button("Verify & Register")
        
        if submitted:
            if auth.verify_totp(data['secret'], code):
                # Save user to DB
                hashed = auth.hash_password(data['password'])
                if db.add_user(data['username'], hashed, data['secret']):
                    st.success("Registration Successful! Please Login.")
                    st.session_state.temp_reg_data = {}
                    st.session_state.auth_step = 'login'
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("Database Error during registration.")
            else:
                st.error("Invalid Code. Please try again.")
    
    if st.button("Cancel"):
        st.session_state.auth_step = 'login'
        st.session_state.temp_reg_data = {}
        st.rerun()

def otp_view():
    st.title("🔒 Two-Factor Authentication")
    st.info(f"Please enter the code from your authenticator app for user: **{st.session_state.username}**")
    
    with st.form("login_otp_form"):
        code = st.text_input("Enter 6-digit Code", max_chars=6)
        submitted = st.form_submit_button("Verify")
        
        if submitted:
            user = db.get_user(st.session_state.username)
            if not user:
                st.error("User not found (session error).")
                time.sleep(2)
                logout()
            
            secret = user[3] # totp_secret
            if auth.verify_totp(secret, code):
                st.session_state.authenticated = True
                st.session_state.auth_step = 'dashboard'
                st.success("Login Successful!")
                st.rerun()
            else:
                st.error("Invalid Code")

    if st.button("Cancel Login"):
        logout()

def dashboard_view():
    st.sidebar.title(f"User: {st.session_state.username}")
    if st.sidebar.button("Logout"):
        logout()

    st.title("📦 Inventory Dashboard")

    # --- Add Item ---
    with st.expander("➕ Add New Item"):
        with st.form("add_item_form"):
            new_name = st.text_input("Item Name")
            c1, c2, c3 = st.columns(3)
            with c1: new_cat = st.text_input("Category")
            with c2: new_qty = st.number_input("Quantity", min_value=0, step=1)
            with c3: new_price = st.number_input("Price ($)", min_value=0.0, step=0.01)
            
            new_desc = st.text_area("Description")
            
            if st.form_submit_button("Add Item"):
                if new_name:
                    db.add_item(new_name, new_cat, new_qty, new_price, new_desc)
                    st.success(f"Added {new_name}")
                    st.rerun()
                else:
                    st.error("Item Name is required")

    # --- View Items ---
    st.subheader("Current Inventory")
    items = db.get_items()
    
    if not items.empty:
        # Display as a dataframe with editing? 
        # For simplicity in "Delete", let's use a dataframe display and separate delete section, or st.data_editor
        
        # Use data_editor for inline edits if possible, but implementing the save back is tricky without a key.
        # Let's use a simple display and a delete/edit mechanism below.
        
        st.dataframe(items, use_container_width=True)
        
        st.divider()
        st.subheader("Manage Items")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.caption("Delete Item")
            delete_id = st.selectbox("Select Item to Delete", items['id'].tolist(), format_func=lambda x: f"ID: {x} - {items[items['id']==x]['name'].values[0]}")
            if st.button("Delete Selected"):
                db.delete_item(delete_id)
                st.warning(f"Deleted Item ID {delete_id}")
                time.sleep(0.5)
                st.rerun()

        with col2:
             # Edit Quantity Shortcut
             st.caption("Quick Update Quantity")
             edit_id = st.selectbox("Select Item to Update", items['id'].tolist(), key='edit_select', format_func=lambda x: f"ID: {x} - {items[items['id']==x]['name'].values[0]}")
             current_qty = items[items['id']==edit_id]['quantity'].values[0]
             new_qty_val = st.number_input(f"Update Quantity for ID {edit_id}", value=int(current_qty))
             if st.button("Update Quantity"):
                 # We need to get other values to pass to update_item, or modify update_item to be partial.
                 # Current db.update_item requires all fields.
                 # Let's fetch the full item first.
                 row = items[items['id']==edit_id].iloc[0]
                 db.update_item(edit_id, row['name'], row['category'], new_qty_val, row['price'], row['description'])
                 st.success("Updated")
                 time.sleep(0.5)
                 st.rerun()

    else:
        st.info("No items in inventory.")

# --- Router ---
if not st.session_state.authenticated:
    if st.session_state.auth_step == 'login':
        login_view()
    elif st.session_state.auth_step == 'register_otp':
        register_otp_view()
    elif st.session_state.auth_step == 'otp':
        otp_view()
else:
    dashboard_view()
