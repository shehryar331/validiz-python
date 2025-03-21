#!/usr/bin/env python3
"""
Example usage of the asynchronous Validiz client.
"""

import asyncio

from validiz import AsyncValidizClient, ValidizError, ValidizConnectionError


async def validate_email_example(api_key):
    """Example of validating email addresses asynchronously."""
    print("\n=== Async Email Validation Example ===\n")
    
    # Create a client with API key
    async with AsyncValidizClient(api_key=api_key) as client:
        # Validate a single email
        email = "test@example.com"
        print(f"Validating email: {email}")
        
        try:
            results = await client.validate_email(email)
            
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


async def upload_file_example(api_key, file_path):
    """Example of uploading a file for validation asynchronously."""
    print("\n=== Async File Upload Example ===\n")
    
    # Create a client with API key
    async with AsyncValidizClient(api_key=api_key) as client:
        try:
            # Upload the file
            print(f"Uploading file: {file_path}")
            upload_result = await client.upload_file(file_path)
            file_id = upload_result["file_id"]
            print(f"File uploaded successfully! File ID: {file_id}")
            
            # Check file status
            print("\nChecking file status...")
            status = await client.get_file_status(file_id)
            print(f"Status: {status['status']}")
            
            # If the file is already processed, download results
            if status["status"] == "completed":
                print("\nDownloading results...")
                output_file = await client.download_file(file_id)
                print(f"Results downloaded to: {output_file}")
        
        except ValidizError as e:
            print(f"API error: {e.message}")
        except ValidizConnectionError as e:
            print(f"Connection error: {e.message}")
        except FileNotFoundError as e:
            print(f"File error: {str(e)}")


async def check_health_example(api_key):
    """Example of checking the API health asynchronously."""
    print("\n=== Async Health Check Example ===\n")
    
    # Create a client with API key
    async with AsyncValidizClient(api_key=api_key) as client:
        try:
            # Check API health
            print("Checking API health...")
            health = await client.check_health()
            print(f"Status: {health.get('status', 'unknown')}")
            print(f"API version: {health.get('api_version', 'unknown')}")
            print(f"Environment: {health.get('environment', 'unknown')}")
            print(f"Database: {health.get('database', 'unknown')}")
        
        except ValidizError as e:
            print(f"API error: {e.message}")
        except ValidizConnectionError as e:
            print(f"Connection error: {e.message}")


async def parallel_validation_example(api_key):
    """Example of validating multiple emails in parallel."""
    print("\n=== Async Parallel Validation Example ===\n")
    
    # Create a client with API key
    async with AsyncValidizClient(api_key=api_key) as client:
        # List of emails to validate
        emails = [
            "test1@example.com",
            "test2@example.com",
            "test3@example.com",
            "invalid@example",
        ]
        
        print(f"Validating {len(emails)} emails in parallel...")
        
        try:
            # Create tasks for each email
            tasks = [client.validate_email(email) for email in emails]
            
            # Run all tasks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"Error validating {emails[i]}: {str(result)}")
                else:
                    for email_result in result:
                        print(f"Email: {email_result['email']}")
                        print(f"Is valid: {email_result['is_valid']}")
                        print(f"Status: {email_result['status']}")
                        print()
        
        except Exception as e:
            print(f"Unexpected error: {str(e)}")


async def main():
    # Replace with your actual API key
    API_KEY = "your_api_key_here"
    
    # Replace with your actual file path
    FILE_PATH = "emails.csv"
    
    print("Validiz Python Library - Asynchronous Examples")
    print("==============================================")
    
    # Run the examples
    await validate_email_example(API_KEY)
    await upload_file_example(API_KEY, FILE_PATH)
    await check_health_example(API_KEY)
    await parallel_validation_example(API_KEY)
    
    print("\nExamples completed.")


if __name__ == "__main__":
    asyncio.run(main()) 