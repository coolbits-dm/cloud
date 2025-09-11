from app.core.db import SessionLocal
from app.models.models import User


def update_passwords():
    db = SessionLocal()
    try:
        # Update passwords for all users
        users_data = [
            ("andrei", "coolBits32!"),
            ("business_user", "business2025"),
            ("agency_user", "agency2025"),
            ("dev_user", "dev2025"),
        ]

        for username, password in users_data:
            user = db.query(User).filter_by(username=username).first()
            if user:
                user.set_password(password)
                print(f"✅ Updated password for {username}")
            else:
                print(f"❌ User {username} not found")

        db.commit()
        print("✅ All passwords updated successfully!")

    except Exception as e:
        print(f"❌ Error updating passwords: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    update_passwords()
