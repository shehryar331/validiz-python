#!/usr/bin/env python3
"""
Example usage of the synchronous Validiz client.
"""

from validiz import ValidizClient, ValidizError, ValidizConnectionError


def validate_email_example(api_key):
    """Example of validating email addresses."""
    print("\n=== Email Validation Example ===\n")
    
    # Create a client with API key
    client = ValidizClient(api_key=api_key)
    
    # Validate a single email
    email = "test@example.com"
    print(f"Validating email: {email}")
    
    try:
        results = client.validate_email(email)
        
        for result in results:
            print(f"Email: {result['email']}")
            print(f"Is valid: {result['is_valid']}")
            print(f"Status: {result['status']}")
            print(f"Sub-status: {result['sub_status']}")
            if not result['is_valid'] and result.get('error_message'):
                print(f"Error message: {result['error_message']}")
            print()
            
            # Display additional information
            print("Additional information:")
            print(f"Free email: {result.get('free_email', 'N/A')}")
            print(f"Account: {result.get('account', 'N/A')}")
            print(f"Domain: {result.get('domain', 'N/A')}")
            print(f"SMTP provider: {result.get('smtp_provider', 'N/A')}")
            print(f"MX found: {result.get('mx_found', 'N/A')}")
            mx_records = result.get('mx_record', [])
            if mx_records:
                print(f"MX records: {', '.join(mx_records)}")
    
    except ValidizError as e:
        print(f"API error: {e.message}")
    except ValidizConnectionError as e:
        print(f"Connection error: {e.message}")


def upload_file_example(api_key, file_path):
    """Example of uploading a file for validation."""
    print("\n=== File Upload Example ===\n")
    
    # Create a client with API key
    client = ValidizClient(api_key=api_key)
    
    try:
        # Upload the file
        print(f"Uploading file: {file_path}")
        upload_result = client.upload_file(file_path)
        file_id = upload_result["file_id"]
        print(f"File uploaded successfully! File ID: {file_id}")
        
        # Check file status
        print("\nChecking file status...")
        status = client.get_file_status(file_id)
        print(f"Status: {status['status']}")
        
        # If the file is already processed, download results
        if status["status"] == "completed":
            print("\nDownloading results...")
            output_file = client.download_file(file_id)
            print(f"Results downloaded to: {output_file}")
    
    except ValidizError as e:
        print(f"API error: {e.message}")
    except ValidizConnectionError as e:
        print(f"Connection error: {e.message}")
    except FileNotFoundError as e:
        print(f"File error: {str(e)}")


def check_health_example(api_key):
    """Example of checking the API health."""
    print("\n=== Health Check Example ===\n")
    
    # Create a client with API key
    client = ValidizClient(api_key=api_key)
    
    try:
        # Check API health
        print("Checking API health...")
        health = client.check_health()
        print(f"Status: {health.get('status', 'unknown')}")
        print(f"API version: {health.get('api_version', 'unknown')}")
        print(f"Environment: {health.get('environment', 'unknown')}")
        print(f"Database: {health.get('database', 'unknown')}")
    
    except ValidizError as e:
        print(f"API error: {e.message}")
    except ValidizConnectionError as e:
        print(f"Connection error: {e.message}")


if __name__ == "__main__":
    # Replace with your actual API key
    API_KEY = "your_api_key_here"
    
    # Replace with your actual file path
    FILE_PATH = "emails.csv"
    
    print("Validiz Python Library - Synchronous Examples")
    print("=============================================")
    
    # Run the examples
    validate_email_example(API_KEY)
    upload_file_example(API_KEY, FILE_PATH)
    check_health_example(API_KEY)
    
    print("\nExamples completed.") 