# 🚀 User Roles & ACL - Code Skeleton
## CoolBits.ai Feature #1 Implementation

---

## 📋 **DATABASE MODELS**

### **1. User Model (`models/user.py`):**
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import hashlib
import secrets

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    role = relationship("Role", back_populates="users")
    
    def set_password(self, password):
        """Hash and set password"""
        salt = secrets.token_hex(16)
        self.password_hash = hashlib.pbkdf2_hmac('sha256', 
                                                password.encode('utf-8'), 
                                                salt.encode('utf-8'), 
                                                100000).hex() + ':' + salt
    
    def check_password(self, password):
        """Check password against hash"""
        if ':' not in self.password_hash:
            return False
        hash_part, salt = self.password_hash.split(':')
        test_hash = hashlib.pbkdf2_hmac('sha256', 
                                       password.encode('utf-8'), 
                                       salt.encode('utf-8'), 
                                       100000).hex()
        return hash_part == test_hash
    
    def has_permission(self, permission):
        """Check if user has specific permission"""
        return self.role.has_permission(permission)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
```

### **2. Role Model (`models/role.py`):**
```python
from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    permissions = Column(Text)  # JSON string of permissions
    is_active = Column(Boolean, default=True)
    
    # Relationships
    users = relationship("User", back_populates="role")
    
    # Permission constants
    PERMISSIONS = {
        'user': [
            'view_user_panel',
            'access_basic_ai',
            'view_own_profile'
        ],
        'business': [
            'view_user_panel',
            'view_business_panel',
            'access_business_ai',
            'view_business_reports',
            'manage_business_data'
        ],
        'agency': [
            'view_user_panel',
            'view_business_panel',
            'view_agency_panel',
            'access_agency_ai',
            'manage_agency_clients',
            'view_agency_reports'
        ],
        'dev': [
            'view_user_panel',
            'view_business_panel',
            'view_agency_panel',
            'view_dev_panel',
            'access_dev_tools',
            'manage_rag_system',
            'view_system_logs'
        ],
        'admin': [
            'view_user_panel',
            'view_business_panel',
            'view_agency_panel',
            'view_dev_panel',
            'view_admin_panel',
            'access_ai_board',
            'manage_users',
            'manage_roles',
            'view_system_logs',
            'manage_system_settings',
            'access_all_features'
        ]
    }
    
    def has_permission(self, permission):
        """Check if role has specific permission"""
        role_permissions = self.PERMISSIONS.get(self.name, [])
        return permission in role_permissions or 'access_all_features' in role_permissions
    
    def get_permissions(self):
        """Get all permissions for this role"""
        return self.PERMISSIONS.get(self.name, [])
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': self.get_permissions(),
            'is_active': self.is_active
        }
```

---

## 🔐 **AUTHENTICATION MIDDLEWARE**

### **3. Auth Middleware (`middleware/auth.py`):**
```python
from functools import wraps
from flask import request, jsonify, session, redirect, url_for
from models.user import User
from models.role import Role
from database import db
import json

class AuthMiddleware:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        app.before_request(self.load_user)
    
    def load_user(self):
        """Load current user from session"""
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user and user.is_active:
                request.current_user = user
            else:
                session.pop('user_id', None)
                request.current_user = None
        else:
            request.current_user = None
    
    def login_required(self, f):
        """Decorator to require login"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user') or not request.current_user:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def role_required(self, *roles):
        """Decorator to require specific roles"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not hasattr(request, 'current_user') or not request.current_user:
                    if request.is_json:
                        return jsonify({'error': 'Authentication required'}), 401
                    return redirect(url_for('auth.login'))
                
                if request.current_user.role.name not in roles:
                    if request.is_json:
                        return jsonify({'error': 'Insufficient permissions'}), 403
                    return redirect(url_for('auth.unauthorized'))
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def permission_required(self, permission):
        """Decorator to require specific permission"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not hasattr(request, 'current_user') or not request.current_user:
                    if request.is_json:
                        return jsonify({'error': 'Authentication required'}), 401
                    return redirect(url_for('auth.login'))
                
                if not request.current_user.has_permission(permission):
                    if request.is_json:
                        return jsonify({'error': 'Insufficient permissions'}), 403
                    return redirect(url_for('auth.unauthorized'))
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator

# Global auth instance
auth = AuthMiddleware()
```

---

## 🎨 **UI COMPONENTS**

### **4. Navigation Component (`components/navigation.py`):**
```python
import streamlit as st
from models.user import User
from models.role import Role

class NavigationComponent:
    def __init__(self):
        self.menu_items = {
            'user': [
                {'name': 'User Panel', 'page': 'user_panel', 'icon': '👤'},
                {'name': 'Profile', 'page': 'profile', 'icon': '⚙️'},
                {'name': 'Basic AI', 'page': 'basic_ai', 'icon': '🤖'}
            ],
            'business': [
                {'name': 'User Panel', 'page': 'user_panel', 'icon': '👤'},
                {'name': 'Business Panel', 'page': 'business_panel', 'icon': '💼'},
                {'name': 'Business AI', 'page': 'business_ai', 'icon': '🧠'},
                {'name': 'Reports', 'page': 'business_reports', 'icon': '📊'}
            ],
            'agency': [
                {'name': 'User Panel', 'page': 'user_panel', 'icon': '👤'},
                {'name': 'Business Panel', 'page': 'business_panel', 'icon': '💼'},
                {'name': 'Agency Panel', 'page': 'agency_panel', 'icon': '🏢'},
                {'name': 'Agency AI', 'page': 'agency_ai', 'icon': '🎯'},
                {'name': 'Clients', 'page': 'agency_clients', 'icon': '👥'},
                {'name': 'Reports', 'page': 'agency_reports', 'icon': '📈'}
            ],
            'dev': [
                {'name': 'User Panel', 'page': 'user_panel', 'icon': '👤'},
                {'name': 'Business Panel', 'page': 'business_panel', 'icon': '💼'},
                {'name': 'Agency Panel', 'page': 'agency_panel', 'icon': '🏢'},
                {'name': 'Dev Panel', 'page': 'dev_panel', 'icon': '💻'},
                {'name': 'Dev Tools', 'page': 'dev_tools', 'icon': '🔧'},
                {'name': 'RAG System', 'page': 'rag_system', 'icon': '🔍'},
                {'name': 'System Logs', 'page': 'system_logs', 'icon': '📋'}
            ],
            'admin': [
                {'name': 'User Panel', 'page': 'user_panel', 'icon': '👤'},
                {'name': 'Business Panel', 'page': 'business_panel', 'icon': '💼'},
                {'name': 'Agency Panel', 'page': 'agency_panel', 'icon': '🏢'},
                {'name': 'Dev Panel', 'page': 'dev_panel', 'icon': '💻'},
                {'name': 'Admin Panel', 'page': 'admin_panel', 'icon': '⚡'},
                {'name': 'AI Board', 'page': 'ai_board', 'icon': '🎯'},
                {'name': 'User Management', 'page': 'user_management', 'icon': '👥'},
                {'name': 'System Settings', 'page': 'system_settings', 'icon': '⚙️'},
                {'name': 'System Logs', 'page': 'system_logs', 'icon': '📋'}
            ]
        }
    
    def render_navigation(self, current_user):
        """Render navigation menu based on user role"""
        if not current_user:
            return self.render_guest_navigation()
        
        role_name = current_user.role.name
        menu_items = self.menu_items.get(role_name, [])
        
        st.sidebar.title("🎯 CoolBits.ai")
        st.sidebar.write(f"Welcome, **{current_user.username}**")
        st.sidebar.write(f"Role: **{current_user.role.name.title()}**")
        st.sidebar.divider()
        
        # Render menu items
        for item in menu_items:
            if st.sidebar.button(f"{item['icon']} {item['name']}", key=f"nav_{item['page']}"):
                st.session_state.current_page = item['page']
                st.rerun()
        
        st.sidebar.divider()
        if st.sidebar.button("🚪 Logout"):
            st.session_state.current_user = None
            st.session_state.current_page = 'login'
            st.rerun()
    
    def render_guest_navigation(self):
        """Render navigation for guests"""
        st.sidebar.title("🎯 CoolBits.ai")
        st.sidebar.write("Please log in to access the system")
        st.sidebar.divider()
        
        if st.sidebar.button("🔐 Login"):
            st.session_state.current_page = 'login'
            st.rerun()
```

---

## 🌱 **DATABASE SEEDING**

### **5. Database Seeder (`database/seed.py`):**
```python
from models.user import User
from models.role import Role
from database import db
from app import app

def seed_database():
    """Seed database with initial data"""
    with app.app_context():
        # Create roles
        roles_data = [
            {'name': 'user', 'description': 'Basic user with limited access'},
            {'name': 'business', 'description': 'Business user with business panel access'},
            {'name': 'agency', 'description': 'Agency user with client management'},
            {'name': 'dev', 'description': 'Developer with technical tools'},
            {'name': 'admin', 'description': 'Administrator with full access'}
        ]
        
        for role_data in roles_data:
            role = Role.query.filter_by(name=role_data['name']).first()
            if not role:
                role = Role(**role_data)
                db.session.add(role)
        
        db.session.commit()
        
        # Create test users
        users_data = [
            {
                'username': 'andrei',
                'email': 'andrei@coolbits.ro',
                'password': 'coolbits2025',
                'role_name': 'admin'
            },
            {
                'username': 'business_user',
                'email': 'business@coolbits.ro',
                'password': 'business2025',
                'role_name': 'business'
            },
            {
                'username': 'agency_user',
                'email': 'agency@coolbits.ro',
                'password': 'agency2025',
                'role_name': 'agency'
            },
            {
                'username': 'dev_user',
                'email': 'dev@coolbits.ro',
                'password': 'dev2025',
                'role_name': 'dev'
            }
        ]
        
        for user_data in users_data:
            user = User.query.filter_by(username=user_data['username']).first()
            if not user:
                role = Role.query.filter_by(name=user_data['role_name']).first()
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    role_id=role.id
                )
                user.set_password(user_data['password'])
                db.session.add(user)
        
        db.session.commit()
        print("✅ Database seeded successfully!")

if __name__ == "__main__":
    seed_database()
```

---

## 🧪 **TESTING FRAMEWORK**

### **6. Test Suite (`tests/test_auth.py`):**
```python
import pytest
from app import app
from models.user import User
from models.role import Role
from database import db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_user_creation(client):
    """Test user creation"""
    role = Role(name='user', description='Test role')
    db.session.add(role)
    db.session.commit()
    
    user = User(username='testuser', email='test@example.com', role_id=role.id)
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    
    assert user.username == 'testuser'
    assert user.check_password('password123')
    assert not user.check_password('wrongpassword')

def test_role_permissions(client):
    """Test role permissions"""
    admin_role = Role(name='admin', description='Admin role')
    user_role = Role(name='user', description='User role')
    
    assert admin_role.has_permission('access_all_features')
    assert admin_role.has_permission('view_admin_panel')
    assert not user_role.has_permission('view_admin_panel')

def test_login_flow(client):
    """Test login flow"""
    # Create test user
    role = Role(name='user', description='Test role')
    db.session.add(role)
    db.session.commit()
    
    user = User(username='testuser', email='test@example.com', role_id=role.id)
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    
    # Test login
    response = client.post('/auth/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    assert 'access_token' in response.get_json()

def test_acl_middleware(client):
    """Test ACL middleware"""
    # Create admin user
    admin_role = Role(name='admin', description='Admin role')
    db.session.add(admin_role)
    db.session.commit()
    
    admin_user = User(username='admin', email='admin@example.com', role_id=admin_role.id)
    admin_user.set_password('admin123')
    db.session.add(admin_user)
    db.session.commit()
    
    # Login as admin
    login_response = client.post('/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    
    token = login_response.get_json()['access_token']
    
    # Test admin access
    response = client.get('/admin/panel', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    
    # Test unauthorized access
    response = client.get('/admin/panel')
    assert response.status_code == 401
```

---

## 🚀 **IMPLEMENTATION CHECKLIST**

### **Phase 1: Database Setup**
- [ ] Create User model
- [ ] Create Role model
- [ ] Set up database migrations
- [ ] Seed initial data

### **Phase 2: Authentication**
- [ ] Implement login system
- [ ] Create session management
- [ ] Add password hashing
- [ ] Implement logout

### **Phase 3: Authorization**
- [ ] Create ACL middleware
- [ ] Implement role-based access
- [ ] Add permission checking
- [ ] Create decorators

### **Phase 4: UI Integration**
- [ ] Update navigation component
- [ ] Implement role-based menus
- [ ] Add user profile display
- [ ] Create login/logout UI

### **Phase 5: Testing**
- [ ] Write unit tests
- [ ] Create integration tests
- [ ] Test all user roles
- [ ] Verify ACL functionality

---

## 📋 **NEXT STEPS**

1. **Create database models** using the provided schemas
2. **Implement authentication system** with login/logout
3. **Add ACL middleware** for role-based access
4. **Update UI components** to show role-appropriate menus
5. **Seed test data** with all user roles
6. **Write comprehensive tests** for all functionality

**Ready for @oCursor to implement!** 🚀
