import streamlit as st
from app.core.db import SessionLocal
from app.models.models import User, Role
from app.ui.menu import ACLMenu
from app.ui.panels import render_current_panel
from datetime import datetime


def login_form():
    """Login form component"""
    st.title("🔐 Login to CoolBits.ai")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

        if submit_button:
            if authenticate_user(username, password):
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")


def authenticate_user(username, password):
    """Authenticate user and set session"""
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(username=username).first()

        if user and user.check_password(password) and user.is_active:
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()

            # Set session state
            st.session_state["user_id"] = user.id
            st.session_state["current_panel"] = "user_panel"

            return True
        else:
            return False

    except Exception as e:
        st.error(f"Authentication error: {e}")
        return False
    finally:
        db.close()


def main():
    """Main application"""
    # Initialize ACL menu
    acl_menu = ACLMenu()

    # Check if user is logged in
    if "user_id" not in st.session_state:
        # Show login form
        login_form()
    else:
        # Render navigation and current panel
        acl_menu.render_navigation()
        render_current_panel()


if __name__ == "__main__":
    main()
