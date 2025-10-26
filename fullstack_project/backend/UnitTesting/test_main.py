from app.schemas.user import User, UserCreate
from app.schemas.authentication import LoginRequest
import pytest
from app.services.users_service import create_user, authenticate_user
from app.schemas.requests import Request, RequestCreate
from fastapi import HTTPException

def test_create_user_success():
    # Arrange
    test_request = UserCreate(
        email = "test",
        password = "123",
        username = "  hello world  ",
        is_admin = "no",
        department = "test",
        age = 0,
        firstname = 'john',
        lastname = 'doe'
    )
    
    # Act
    result = create_user(test_request)
    
    # Assert
    assert isinstance(result, User)
    assert result.username == "hello world"
    assert result.firstname == "john"
    assert result.hash_password != "123"
        
def test_authenticate_user():
    test = LoginRequest(
        username_email= "test",
        password= "123"
    )
    
    result = authenticate_user(test)
    
    assert result.username == "hello world"
    assert result.firstname == "john"
    assert result.lastname == "doe"
    
if __name__ == "__main__":
    pytest.main([__file__])