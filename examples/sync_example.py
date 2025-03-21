#!/usr/bin/env python3
"""
Example usage of the synchronous Validiz client.
"""

from validiz import Validiz, ValidizError, ValidizConnectionError


def validate_email_example(api_key):
    """Example of validating email addresses."""
    print("\n=== Email Validation Example ===\n")
    
    # Create a client with API key
    client = Validiz(api_key=api_key)
    
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
    client = Validiz(api_key=api_key)
    
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


def poll_file_example(api_key, file_path):
    """Example of uploading a file and polling for completion."""
    print("\n=== File Upload with Polling Example ===\n")
    
    # Create a client with API key
    client = Validiz(api_key=api_key)
    
    try:
        # Upload the file
        print(f"Uploading file: {file_path}")
        upload_result = client.upload_file(file_path)
        file_id = upload_result["file_id"]
        print(f"File uploaded successfully! File ID: {file_id}")
        
        # Poll for completion and get results as DataFrame
        print("\nPolling for completion...")
        print("This might take a while depending on the file size and server load...")
        
        # Poll for completion with a timeout of 5 minutes (polling every 10 seconds)
        df = client.poll_file_until_complete(
            file_id=file_id,
            interval=10,
            max_retries=30
        )
        
        # Process and display results
        print("\nFile processing completed!")
        print(f"Number of emails processed: {len(df)}")
        
        # Count valid and invalid emails
        valid_count = df[df['is_valid'] == True].shape[0] if 'is_valid' in df.columns else 0
        invalid_count = df[df['is_valid'] == False].shape[0] if 'is_valid' in df.columns else 0
        
        print(f"Valid emails: {valid_count}")
        print(f"Invalid emails: {invalid_count}")
        
        # Display first few rows
        if not df.empty:
            print("\nSample of results:")
            print(df.head())
    
    except ValidizError as e:
        print(f"API error: {e.message}")
    except ValidizConnectionError as e:
        print(f"Connection error: {e.message}")
    except TimeoutError as e:
        print(f"Timeout error: {str(e)}")
    except FileNotFoundError as e:
        print(f"File error: {str(e)}")


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
    poll_file_example(API_KEY, FILE_PATH)
    
    print("\nExamples completed.") 