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
    
    h1, h2, h3 {
        font-family: 'Arial', sans-serif;
    }
    
    /* Admin Badge */
    .admin-badge {
        background-color: #ffca28;
        color: black;
        padding: 5px 10px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 0.8em;
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
                            st.session_state.role = user[4] # role is at index 4 now
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
                        'secret': secret,
                        'role': 'user' # Default to user
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
                # Use the role from temp data (defaults to 'user', but enables flexibility)
                role = data.get('role', 'user') 
                if db.add_user(data['username'], hashed, data['secret'], role):
                    st.success("Registration Successful!")
                    db.add_log(data['username'], "USER_REGISTER", f"New user registered as {role}")
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
                    st.session_state.role = user[4] # Refresh role from DB
                    st.session_state.authenticated = True
                    st.session_state.auth_step = 'dashboard'
                    db.add_log(st.session_state.username, "LOGIN", "Successful login via 2FA.")
                    st.rerun()
                    st.rerun()
                else:
                    st.error("Incorrect or Expired OTP")
            else:
                st.session_state.auth_step = 'login'
                st.rerun()

# --- Confirmation Dialogs ---

@st.dialog("Confirm Deletion")
def confirm_delete_dialog(item_id, item_name):
    st.warning(f"Are you sure you want to delete **{item_name}** (ID: {item_id})?")
    st.write("This action cannot be undone.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Yes, Delete", type="primary"):
            db.delete_item(item_id)
            db.add_log(st.session_state.username, "DELETE_ITEM", f"Deleted {item_name} (ID: {item_id})")
            st.success(f"Deleted Item ID {item_id}")
            time.sleep(1)
            st.rerun()
    with c2:
        if st.button("Cancel"):
            st.rerun()

@st.dialog("Confirm New Item")
def confirm_add_item_dialog(name, cat, qty, price, desc):
    st.write("Please confirm the following item details:")
    st.write(f"- **Name:** {name}")
    st.write(f"- **Category:** {cat}")
    st.write(f"- **Quantity:** {qty}")
    st.write(f"- **Price:** PHP {price:,.2f}")
    st.write(f"- **Description:** {desc}")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Confirm and Add", type="primary"):
            db.add_item(name, cat, qty, price, desc)
            db.add_log(st.session_state.username, "ADD_ITEM", f"Added {name} (Qty: {qty})")
            st.success(f"Added {name}")
            time.sleep(1)
            st.rerun()
    with c2:
        if st.button("Cancel"):
            st.rerun()

@st.dialog("Confirm Update")
def confirm_update_item_dialog(item_id, name, cat, qty, price, desc):
    st.write(f"Are you sure you want to update item **{name}** (ID: {item_id})?")
    st.write("New Details:")
    st.write(f"- **Category:** {cat}")
    st.write(f"- **Quantity:** {qty}")
    st.write(f"- **Price:** PHP {price:,.2f}")
    st.write(f"- **Description:** {desc}")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Confirm Update", type="primary"):
            db.update_item(item_id, name, cat, qty, price, desc)
            db.add_log(st.session_state.username, "UPDATE_ITEM", f"Updated {name} (ID: {item_id}) details.")
            st.success("Item Updated Successfully!")
            time.sleep(1)
            st.rerun()
    with c2:
        if st.button("Cancel"):
            st.rerun()

@st.dialog("Confirm Admin Creation")
def confirm_create_admin_dialog(new_admin_user, new_admin_pass):
    st.warning(f"Are you sure you want to create a new Administrator: **{new_admin_user}**?")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Yes, Create Admin", type="primary"):
             secret = auth.generate_totp_secret()
             hashed = auth.hash_password(new_admin_pass)
             if db.add_user(new_admin_user, hashed, secret, role='admin'):
                 db.add_log(st.session_state.username, "ADMIN_CREATE_ADMIN", f"Created new admin: {new_admin_user}")
                 st.success(f"Admin '{new_admin_user}' created!")
                 st.warning("⚠️ Please scan this QR code immediately. It will not be shown again.")
                 
                 uri = auth.get_totp_uri(new_admin_user, secret)
                 qr = auth.generate_qr_code(uri)
                 st.image(qr, width=200, caption=f"TOTP Setup for {new_admin_user}")
                 st.write(f"Secret Key: `{secret}`")
                 if st.button("Done"):
                     st.rerun()
             else:
                 st.error("Database Error")
    with c2:
        if st.button("Cancel"):
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
    
    # Show Role Badge
    role = st.session_state.get('role', 'user')
    if role == 'admin':
        st.sidebar.markdown('<span class="admin-badge">ADMIN ACCESS</span>', unsafe_allow_html=True)
    else:
        st.sidebar.caption("Standard User (Read-Only)")

    if st.sidebar.button("Logout"):
        db.add_log(st.session_state.username, "LOGOUT", "User logged out.")
        logout()

    st.title("📦 Inventory Dashboard")

    # --- Search ---
    search_query = st.text_input("🔍 Search Inventory", placeholder="Search by name or category...")
    
    # Fetch items early for category dropdowns
    items = db.get_items()

    # --- Add Item (ADMIN ONLY) ---
    if role == 'admin':
        with st.expander("➕ Add New Item"):
            with st.form("add_item_form"):
                new_name = st.text_input("Item Name")
                
                # Smart Category Selection
                existing_cats = []
                if not items.empty and 'category' in items.columns:
                     existing_cats = items['category'].dropna().unique().tolist()
                
                cat_options = ["➕ Create New Category"] + existing_cats
                selected_cat = st.selectbox("Category", cat_options)
                
                if selected_cat == "➕ Create New Category":
                    new_cat = st.text_input("Enter New Category Name")
                else:
                    new_cat = selected_cat

                c1, c2 = st.columns(2)
                with c1: new_qty = st.number_input("Quantity", min_value=0, step=1)
                with c2: new_price = st.number_input("Price (PHP)", min_value=0.0, step=0.01)
                
                new_desc = st.text_area("Description")
                
                if st.form_submit_button("Add Item"):
                    if new_name:
                        confirm_add_item_dialog(new_name, new_cat, new_qty, new_price, new_desc)
                    else:
                        st.error("Item Name is required")
    
    # --- Admin User Creation (ADMIN ONLY) ---
    if role == 'admin':
        with st.expander("🛡️ Create Admin User"):
             st.info("Create a new Administrator account.")
             with st.form("create_admin_form"):
                 new_admin_user = st.text_input("New Admin Username")
                 new_admin_pass = st.text_input("New Admin Password", type="password")
                 
                 if st.form_submit_button("Create Admin"):
                    pass_admin, msg_admin = auth.validate_password(new_admin_pass)
                    if not new_admin_user or not new_admin_pass:
                        st.error("Fields cannot be empty")
                    elif not pass_admin:
                        st.error(msg_admin)
                    elif db.get_user(new_admin_user):
                         st.error("User already exists")
                    else:
                         confirm_create_admin_dialog(new_admin_user, new_admin_pass)


    # --- View Items ---
    st.subheader("Current Inventory")
    # items already fetched at top

    
    if not items.empty:
        if search_query:
            items = items[
                items['name'].str.contains(search_query, case=False) | 
                items['category'].str.contains(search_query, case=False)
            ]

        display_df = items.copy()
        display_df.columns = ['ID', 'Name', 'Category', 'Quantity', 'Price (PHP)', 'Description']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # --- Manage Items (ADMIN ONLY) ---
        if role == 'admin':
             st.divider()
             st.subheader("Manage Items")
             
             col1, col2 = st.columns(2)
             
             with col1:
                 st.caption("Delete Item")
                 delete_id = st.selectbox("Select Item to Delete", items['id'].tolist(), format_func=lambda x: f"ID: {x} - {items[items['id']==x]['name'].values[0]}")
                 
                 if st.button("Delete Selected"):
                     item_name = items[items['id']==delete_id]['name'].values[0]
                     confirm_delete_dialog(delete_id, item_name)
     
             with col2:
                  st.caption("Edit Item Details")
                  edit_id = st.selectbox("Select Item to Edit", items['id'].tolist(), key='edit_select', format_func=lambda x: f"ID: {x} - {items[items['id']==x]['name'].values[0]}")
                  
                  # Pre-fill logic
                  current_item = items[items['id']==edit_id].iloc[0]
                  
                  with st.form(key=f"edit_form_{edit_id}"):
                      upd_name = st.text_input("Name", value=current_item['name'])
                      
                      # Category Logic for Edit
                      existing_cats = items['category'].dropna().unique().tolist()
                      cat_options = ["➕ Create New Category"] + existing_cats
                      
                      # Handle current category selection
                      current_cat_index = 0
                      if current_item['category'] in existing_cats:
                          current_cat_index = cat_options.index(current_item['category'])
                      
                      selected_cat_edit = st.selectbox("Category", cat_options, index=current_cat_index)
                      if selected_cat_edit == "➕ Create New Category":
                          upd_cat = st.text_input("New Category Name", value=current_item['category'])
                      else:
                          upd_cat = selected_cat_edit
                          
                      c1, c2 = st.columns(2)
                      with c1: upd_qty = st.number_input("Quantity", value=int(current_item['quantity']), min_value=0)
                      with c2: upd_price = st.number_input("Price (PHP)", value=float(current_item['price']), min_value=0.0, step=0.01)
                      
                      upd_desc = st.text_area("Description", value=current_item['description'] if current_item['description'] else "")
                      
                      if st.form_submit_button("Update Item"):
                           confirm_update_item_dialog(edit_id, upd_name, upd_cat, upd_qty, upd_price, upd_desc)
        else:
            st.info("🔒 You are in View-Only mode. Contact an Admin to make changes.")

    else:
        st.info("No items in inventory.")

    # --- Activity Logs (ADMIN ONLY) ---
    if role == 'admin':
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
