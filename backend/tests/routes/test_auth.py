import pytest
from flask_jwt_extended import decode_token
from app.extensions import bcrypt

class TestAuthRoutes:
    """Test cases for authentication routes."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post('/api/auth/register', json={
            'email': 'newuser@test.com',
            'password': 'password123'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'User created successfully'
    
    def test_register_missing_fields(self, client):
        """Test registration with missing fields."""
        # Missing password
        response = client.post('/api/auth/register', json={
            'email': 'test@test.com'
        })
        assert response.status_code == 400
        assert 'Missing email or password' in response.get_json()['error']
        
        # Missing email
        response = client.post('/api/auth/register', json={
            'password': 'password123'
        })
        assert response.status_code == 400
    
    def test_register_duplicate_email(self, client, sample_user):
        """Test registration with existing email."""
        response = client.post('/api/auth/register', json={
            'email': sample_user.email,
            'password': 'password123'
        })
        
        assert response.status_code == 409
        assert 'User already exists' in response.get_json()['error']
    
    def test_login_success(self, client, session):
        """Test successful login."""
        # Create a user with known password
        from app.models.user import User
        password = 'testpass123'
        user = User(
            email='login@test.com',
            password_hash=bcrypt.generate_password_hash(password).decode('utf-8')
        )
        session.add(user)
        session.commit()
        
        response = client.post('/api/auth/login', json={
            'email': 'login@test.com',
            'password': password
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert data['user']['email'] == 'login@test.com'
        assert data['user']['id'] == str(user.id)
    
    def test_login_invalid_credentials(self, client, sample_user):
        """Test login with invalid credentials."""
        # Wrong password
        response = client.post('/api/auth/login', json={
            'email': sample_user.email,
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        assert 'Invalid credentials' in response.get_json()['error']
        
        # Non-existent email
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@test.com',
            'password': 'password'
        })
        
        assert response.status_code == 401
        assert 'Invalid credentials' in response.get_json()['error']
    
    def test_me_authenticated(self, client, auth_headers, sample_user):
        """Test /me endpoint with authentication."""
        response = client.get('/api/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == str(sample_user.id)
        assert data['email'] == sample_user.email
    
    def test_me_unauthenticated(self, client):
        """Test /me endpoint without authentication."""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
    
    def test_me_invalid_token(self, client):
        """Test /me endpoint with invalid token."""
        headers = {'Authorization': 'Bearer invalid_token'}
        response = client.get('/api/auth/me', headers=headers)
        
        assert response.status_code == 422  # Invalid token format
    
    def test_logout(self, client):
        """Test logout endpoint."""
        response = client.post('/api/auth/logout')
        
        assert response.status_code == 200
        assert response.get_json()['message'] == 'Logged out'