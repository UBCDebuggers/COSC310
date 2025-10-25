import pytest
from app.services.requests_service import create_request
from app.schemas.requests import Request, RequestCreate
from fastapi import HTTPException

def test_create_request_success():
    # Arrange
    test_request = RequestCreate(
        userid="123test",
        details="this is a test",
        request_type="TEST",
        error_code=300
    )
    
    # Act
    result = create_request(test_request)
    
    # Assert
    assert isinstance(result, Request)
    assert result.userid == "123test"
    assert result.details == "this is a test"
    assert result.request_type == "TEST"
    assert result.error_code == 300
    assert result.requestid is not None  # UUID should be generated
    assert result.timestamp is not None  # Timestamp should be set

def test_create_request_strips_whitespace():
    # Arrange
    test_request = RequestCreate(
        userid="123test",
        details="  test with spaces  ",
        request_type=" TEST  ",
        error_code=300
    )
    result = create_request(test_request)
    
    # Assert
    assert result.details == "test with spaces"
    assert result.request_type == "TEST"

def test_create_request_with_null_error_code():
    # Arrange
    test_request = RequestCreate(
        userid="123test",
        details="test without error",
        request_type="TEST",
        error_code=None
    )
    
    # Act
    result = create_request(test_request)
    
    # Assert
    assert result.error_code is None

if __name__ == "__main__":
    pytest.main([__file__])