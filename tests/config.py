"""Test configuration for Validiz tests."""

# Test API key (fake for unit tests)
TEST_API_KEY = "test_api_key_1234567890"

# Mock data for API responses
MOCK_EMAIL_RESPONSE = [
    {
        "email": "valid@example.com",
        "is_valid": True,
        "status": "valid",
        "sub_status": None,
        "free_email": True,
        "account": "valid",
        "domain": "example.com",
        "smtp_provider": "Google",
        "mx_found": True,
        "mx_record": ["example-com.mail.protection.outlook.com"],
    },
    {
        "email": "invalid@example.com",
        "is_valid": False,
        "status": "invalid",
        "sub_status": "mailbox_not_found",
        "error_message": "Mailbox not found",
        "free_email": True,
        "account": "invalid",
        "domain": "example.com",
        "smtp_provider": "Google",
        "mx_found": True,
        "mx_record": ["example-com.mail.protection.outlook.com"],
    },
]

MOCK_FILE_UPLOAD_RESPONSE = {"file_id": "file_12345", "status": "processing"}

MOCK_FILE_STATUS_RESPONSE = {
    "file_id": "file_12345",
    "status": "completed",
    "total_emails": 100,
    "processed_emails": 100,
    "valid_emails": 80,
    "invalid_emails": 20,
}

MOCK_FILE_STATUS_PROCESSING_RESPONSE = {
    "file_id": "file_12345",
    "status": "processing",
    "total_emails": 100,
    "processed_emails": 50,
    "valid_emails": 40,
    "invalid_emails": 10,
}

MOCK_FILE_STATUS_FAILED_RESPONSE = {
    "file_id": "file_12345",
    "status": "failed",
    "error_message": "Invalid file format",
}

MOCK_FILE_CONTENT = b"email,is_valid,status\nvalid@example.com,True,valid\ninvalid@example.com,False,invalid"
