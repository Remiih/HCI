import streamlit as st
import pandas as pd
import time
import db
import auth

# --- Page Config ---
st.set_page_config(page_title="Inventory System", layout="wide", page_icon="📦")

# --- Custom CSS ---
st.markdown("""
<style>
    /* Main Background - Default Streamlit (Dark) */
    
    /* Buttons (Green) */
    .stButton button {
        background-color: #00e676;
        color: white;
        border: none;
        border-radius: 20px;
        padding: 10px 24px;
        font-weight: bold;
        width: 100%;
        transition: 0.3s;
    }
    .stButton button:hover {
        background-color: #00c853;
        color: white;
    }
    
    /* "New Here" Section styling */
    .green-box {
        background-color: #00e676;
        padding: 50px;
        border-radius: 0px;
        height: 100vh;
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }
    
    /* Typography */
    h1, h2, h3 {
        font-family: 'Arial', sans-serif;
    }
    
    /* OTP Card Styling */
    .otp-card {
        background-color: #00e676;
        padding: 40px;
        border-radius: 10px;
        color: white;
        text-align: center;
        width: 350px;
        margin: auto;
    }
    .otp-card input {
        text-align: center;
        margin-top: 10px;
        margin-bottom: 20px;
        border-radius: 5px;
        border: none;
        padding: 10px;
        width: 100%;
    }
    
    /* Hide Default Header/Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

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
if 'toggle_register' not in st.session_state:
    st.session_state.toggle_register = False

# --- Logout Function ---
def logout():
    st.session_state.clear()
    st.rerun()

# --- Views ---

def login_view():
    
    # Using columns to create the split screen look
    c1, c2 = st.columns([1.2, 1])
    
    # Left Side (White) - Login Form
    with c1:
        st.write("") 
        st.write("")
        st.write("")
        
        # Center container roughly
        with st.container():
            st.markdown("<h1 style='text-align: center;'>Login in to Your Account</h1>", unsafe_allow_html=True)
            st.write("")
            
            # Use smaller width for form elements naturally via columns or just let them expand
            lc1, lc2, lc3 = st.columns([1, 2, 1])
            with lc2:
                username = st.text_input("Username", placeholder="Username", label_visibility="collapsed")
                st.write("")
                password = st.text_input("Password", placeholder="Password", type="password", label_visibility="collapsed")
                st.write("")
                
                if st.button("Sign In"):
                    if len(password.encode('utf-8')) > 72:
                         st.error("Password is too long (max 72 bytes)")
                    else:
                        user = db.get_user(username)
                        if user and auth.verify_password(password, user[2]):
                            st.session_state.username = username
                            st.session_state.auth_step = 'otp'
                            db.add_log(username, "LOGIN_ATTEMPT", "Valid credentials, awaiting 2FA.")
                            st.rerun()
                        else:
                            st.error("Wrong Username/Password.")

    # Right Side (Green) - "New Here?"
    with c2:
        # Apply CSS to the specific column to make it green and center content
        st.markdown("""
        <style>
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-of-type(2) {
            background-color: #00e676;
            border-radius: 20px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-of-type(2) .stButton button {
            background-color: white !important;
            color: #00e676 !important;
            border: none;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.markdown("<h2 style='text-align: center; color: black; font-size: 3em;'>New here?</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: black; font-size: 1.2em;'>Sign up and discover a great amount of new opportunities!</p>", unsafe_allow_html=True)
        st.write("")
        
        # Center button using columns
        bc1, bc2, bc3 = st.columns([1, 2, 1])
        st.write("")
        
        # Center button using columns
        bc1, bc2, bc3 = st.columns([1, 2, 1])
        with bc2:
            if st.button("Sign Up Here"):
                st.session_state.auth_step = 'register'
                st.rerun()

def register_view():
    # Split screen again
    c1, c2 = st.columns([1.2, 1])

    with c1:
        st.write("")
        st.write("")
        st.markdown("<h1 style='text-align: center;'>Create Account</h1>", unsafe_allow_html=True)
        
        lc1, lc2, lc3 = st.columns([1, 2, 1])
        with lc2:
            new_user = st.text_input("Choose Username", placeholder="Username", label_visibility="collapsed")
            st.write("")
            new_pass = st.text_input("Choose Password", placeholder="Password", type="password", label_visibility="collapsed")
            st.write("")
            
            if st.button("Next Step"):
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
                    secret = auth.generate_totp_secret()
                    st.session_state.temp_reg_data = {
                        'username': new_user,
                        'password': new_pass,
                        'secret': secret
                    }
                    st.session_state.auth_step = 'register_otp'
                    st.rerun()

    with c2:
        st.markdown("""
        <style>
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-of-type(2) {
            background-color: #00e676;
            border-radius: 20px;
            padding: 20px;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-of-type(2) .stButton button {
            background-color: white !important;
            color: #00e676 !important;
            border: none;
        }
        </style>
        """, unsafe_allow_html=True)

        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.markdown("<h2 style='text-align: center; color: black; font-size: 3em;'>Welcome Back!</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: black; font-size: 1.2em;'>To keep connected with us please login with your personal info</p>", unsafe_allow_html=True)
        st.write("")
        
        # Center button using columns
        bc1, bc2, bc3 = st.columns([1, 2, 1])
        st.write("")
        
        # Center button using columns
        bc1, bc2, bc3 = st.columns([1, 2, 1])
        with bc2:
            if st.button("Sign In Instead"):
                st.session_state.auth_step = 'login'
                st.rerun()

def register_otp_view():
    st.markdown("""
    <div style='background-color: #00e676; padding: 40px; border-radius: 20px; text-align: center; color: white; width: 50%; margin: auto;'>
        <h2>Scan QR Code</h2>
        <p>Use your authenticator app</p>
    </div>
    """, unsafe_allow_html=True)
    
    data = st.session_state.temp_reg_data
    if not data:
        st.session_state.auth_step = 'login'
        st.rerun()

    uri = auth.get_totp_uri(data['username'], data['secret'])
    qr_image = auth.generate_qr_code(uri)
    
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.image(qr_image, width=200)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        code = st.text_input("Enter 6-digit Code", max_chars=6, label_visibility="collapsed", placeholder="000000")
        if st.button("Verify & Register"):
            if auth.verify_totp(data['secret'], code):
                hashed = auth.hash_password(data['password'])
                if db.add_user(data['username'], hashed, data['secret']):
                    st.success("Registration Successful!")
                    st.session_state.temp_reg_data = {}
                    st.session_state.auth_step = 'login'
                    time.sleep(2)
                    st.rerun()
            else:
                st.error("Invalid Code")

def otp_view():
    # Green Card Style
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1, 1])
    
    with c2:
        st.markdown("""
        <div style='background-color: #00e676; padding: 30px; border-radius: 20px; text-align: center; color: black;'>
            <h3>Authenticator Check</h3>
            <p>Please check your<br>Authenticator App</p>
            <div style='background-color: black; height: 2px; width: 50%; margin: 10px auto;'></div>
        </div>
        """, unsafe_allow_html=True)
        
        code = st.text_input("Place OTP here", max_chars=6, label_visibility="collapsed", placeholder="Place OTP here")
        
        if st.button("Enter"):
            user = db.get_user(st.session_state.username)
            if user:
                secret = user[3]
                if auth.verify_totp(secret, code):
                    st.session_state.authenticated = True
                    st.session_state.auth_step = 'dashboard'
                    db.add_log(st.session_state.username, "LOGIN", "Successful login via 2FA.")
                    st.rerun()
                else:
                    st.error("Incorrect or Expired OTP")
            else:
                st.session_state.auth_step = 'login'
                st.rerun()

def dashboard_view():
    # Reset styles to prevent the login/register page CSS from affecting dashboard buttons
    st.markdown("""
    <style>
    .stButton { margin-top: 0px !important; }
    .stButton button { background-color: #00e676 !important; color: white !important; } 
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.title(f"User: {st.session_state.username}")
    if st.sidebar.button("Logout"):
        db.add_log(st.session_state.username, "LOGOUT", "User logged out.")
        logout()

    st.title("📦 Inventory Dashboard")

    # --- Search ---
    search_query = st.text_input("🔍 Search Inventory", placeholder="Search by name or category...")

    # --- Add Item ---
    with st.expander("➕ Add New Item"):
        with st.form("add_item_form"):
            new_name = st.text_input("Item Name")
            c1, c2, c3 = st.columns(3)
            with c1: new_cat = st.text_input("Category")
            with c2: new_qty = st.number_input("Quantity", min_value=0, step=1)
            with c3: new_price = st.number_input("Price (PHP)", min_value=0.0, step=0.01)
            
            new_desc = st.text_area("Description")
            
            if st.form_submit_button("Add Item"):
                if new_name:
                    db.add_item(new_name, new_cat, new_qty, new_price, new_desc)
                    db.add_log(st.session_state.username, "ADD_ITEM", f"Added {new_name} (Qty: {new_qty})")
                    st.success(f"Added {new_name}")
                    st.rerun()
                else:
                    st.error("Item Name is required")

    # --- View Items ---
    st.subheader("Current Inventory")
    items = db.get_items()
    
    if not items.empty:
        if search_query:
            items = items[
                items['name'].str.contains(search_query, case=False) | 
                items['category'].str.contains(search_query, case=False)
            ]

        display_df = items.copy()
        display_df.columns = ['ID', 'Name', 'Category', 'Quantity', 'Price (PHP)', 'Description']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("Manage Items")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.caption("Delete Item")
            delete_id = st.selectbox("Select Item to Delete", items['id'].tolist(), format_func=lambda x: f"ID: {x} - {items[items['id']==x]['name'].values[0]}")
            
            if st.session_state.username == 'admin':
                if st.button("Delete Selected"):
                    item_name = items[items['id']==delete_id]['name'].values[0]
                    db.delete_item(delete_id)
                    db.add_log(st.session_state.username, "DELETE_ITEM", f"Deleted {item_name} (ID: {delete_id})")
                    st.warning(f"Deleted Item ID {delete_id}")
                    time.sleep(0.5)
                    st.rerun()
            else:
                st.button("Delete Selected", disabled=True, help="Only user 'admin' can delete items.")
                st.caption("⚠ Only 'admin' can delete items.")

        with col2:
             st.caption("Quick Update Quantity")
             edit_id = st.selectbox("Select Item to Update", items['id'].tolist(), key='edit_select', format_func=lambda x: f"ID: {x} - {items[items['id']==x]['name'].values[0]}")
             current_qty = items[items['id']==edit_id]['quantity'].values[0]
             new_qty_val = st.number_input(f"Update Quantity for ID {edit_id}", value=int(current_qty))
             if st.button("Update Quantity"):
                 row = items[items['id']==edit_id].iloc[0]
                 db.update_item(edit_id, row['name'], row['category'], new_qty_val, row['price'], row['description'])
                 db.add_log(st.session_state.username, "UPDATE_ITEM", f"Updated {row['name']} quantity to {new_qty_val}")
                 st.success("Updated")
                 time.sleep(0.5)
                 st.rerun()

    else:
        st.info("No items in inventory.")

    with st.expander("📜 Activity Logs (Security Audit)"):
        st.caption("Monitoring user actions for security and accountability.")
        logs = db.get_logs()
        st.dataframe(logs, use_container_width=True, hide_index=True)

# --- Router ---
if not st.session_state.authenticated:
    if st.session_state.auth_step == 'login':
        login_view()
    elif st.session_state.auth_step == 'register':
        register_view()
    elif st.session_state.auth_step == 'register_otp':
        register_otp_view()
    elif st.session_state.auth_step == 'otp':
        otp_view()
else:
    dashboard_view()
