#!/usr/bin/env python3
"""
Asynchronous Client Examples for Validiz

This example demonstrates how to use the Validiz asynchronous client 
to validate email addresses and process files.
"""

import os
import asyncio
import pandas as pd
from validiz import AsyncValidiz, ValidizError, ValidizAuthError, ValidizConnectionError

from dotenv import load_dotenv

load_dotenv(override=True)

# Set your API key - in production, use environment variables
API_KEY = os.environ.get("VALIDIZ_API_KEY", "your_api_key_here")


async def validate_single_email():
    """Example for validating a single email address asynchronously."""
    print("\n== Validating a Single Email (Async) ==")
    
    # Create a client with context manager to ensure proper cleanup
    async with AsyncValidiz(api_key=API_KEY) as client:
        try:
            # Validate a single email
            results = await client.validate_email("user@example.com")
            
            # Access the first (and only) result
            result = results[0]
            
            # Print the validation results
            print(f"Email: {result.email}")
            print(f"Is valid: {result.is_valid}")
            if not result.is_valid and result.error_message:
                print(f"Error: {result.error_message}")
                
            # Access additional fields
            print(f"Status: {result.status}")
            print(f"Free email: {result.free_email}")
            print(f"Domain: {result.domain}")
            if result.mx_found:
                print(f"MX Records: {', '.join(result.mx_record or [])}")
                
        except ValidizAuthError as e:
            print(f"Authentication error: {e.message}")
        except ValidizConnectionError as e:
            print(f"Connection error: {e.message}")
        except ValidizError as e:
            print(f"API error (status {e.status_code}): {e.message}")


async def validate_multiple_emails():
    """Example for validating multiple email addresses in a single request asynchronously."""
    print("\n== Validating Multiple Emails (Async) ==")
    
    async with AsyncValidiz(api_key=API_KEY) as client:
        try:
            # List of emails to validate
            emails = [
                "user1@example.com",
                "user2@gmail.com",
                "invalid-email",
                "user3@nonexistentdomain.xyz"
            ]
            
            # Validate multiple emails in a single request
            results = await client.validate_email(emails)
            
            # Print the validation results
            print(f"Validated {len(results)} emails:")
            for result in results:
                status = "✅ Valid" if result.is_valid else "❌ Invalid"
                error = f" ({result.error_message})" if not result.is_valid and result.error_message else ""
                print(f"  {result.email}: {status}{error}")
                
        except ValidizError as e:
            print(f"API error: {e.message}")


async def batch_validate_emails():
    """Example for validating multiple emails in parallel using asyncio.gather."""
    print("\n== Batch Validating Emails in Parallel (Async) ==")
    
    async with AsyncValidiz(api_key=API_KEY) as client:
        try:
            # List of emails to validate
            emails = [
                "user1@example.com",
                "user2@gmail.com",
                "invalid-email",
                "user3@nonexistentdomain.xyz"
            ]
            
            # Create a task for each email
            tasks = [client.validate_email(email) for email in emails]
            
            # Process all emails in parallel
            start_time = asyncio.get_event_loop().time()
            results = await asyncio.gather(*tasks)
            end_time = asyncio.get_event_loop().time()
            
            # Process and print results
            print(f"Parallel validation completed in {end_time - start_time:.2f} seconds")
            print(f"Validated {len(emails)} emails in parallel:")
            
            for i, result_list in enumerate(results):
                # Each result is a list with one item
                result = result_list[0]
                status = "✅ Valid" if result.is_valid else "❌ Invalid"
                error = f" ({result.error_message})" if not result.is_valid and result.error_message else ""
                print(f"  {emails[i]}: {status}{error}")
                
        except ValidizError as e:
            print(f"API error: {e.message}")


async def upload_and_process_file():
    """Example for uploading a file for validation and downloading results asynchronously."""
    print("\n== Processing File (Upload, Check Status, Download) Async ==")
    
    async with AsyncValidiz(api_key=API_KEY) as client:
        try:
            # Path to a CSV file containing emails
            # Format: Either a CSV with an 'email' column or one email per line
            file_path = "example_emails.csv"
            
            # Check if the example file exists, if not create it
            if not os.path.exists(file_path):
                print(f"Creating example file: {file_path}")
                with open(file_path, "w") as f:
                    f.write("email\nuser1@example.com\nuser2@gmail.com\ninvalid-email\n")
            
            # Upload the file for processing
            print(f"Uploading file: {file_path}")
            upload_result = await client.upload_file(file_path)
            file_id = upload_result["file_id"]
            print(f"File uploaded with ID: {file_id}")
            
            # Check the file status
            status = await client.get_file_status(file_id)
            print(f"File status: {status['status']}")
            
            # Poll until the file is processed and get a DataFrame
            print("Waiting for file processing to complete...")
            results_df = await client.poll_file_until_complete(
                file_id=file_id,
                interval=5,         # Check every 5 seconds
                max_retries=60,     # Try for up to 5 minutes
                output_path="async_validation_results.csv",  # Save to file
                return_dataframe=True  # Also return as DataFrame
            )
            
            # Print the results summary
            print(f"\nProcessed {len(results_df)} emails:")
            print(f"  Valid emails: {results_df[results_df['is_valid'] == True].shape[0]}")
            print(f"  Invalid emails: {results_df[results_df['is_valid'] == False].shape[0]}")
            print("\nFirst few results:")
            print(results_df.head())
            
        except FileNotFoundError as e:
            print(f"File error: {str(e)}")
        except ValidizError as e:
            print(f"API error: {e.message}")
        except TimeoutError as e:
            print(f"Timeout error: {str(e)}")


async def process_multiple_files():
    """Example for processing multiple files in parallel asynchronously."""
    print("\n== Processing Multiple Files in Parallel (Async) ==")
    
    async with AsyncValidiz(api_key=API_KEY) as client:
        try:
            # Create multiple example files
            files = ["example_emails_1.csv", "example_emails_2.csv", "example_emails_3.csv"]
            for i, file_path in enumerate(files):
                if not os.path.exists(file_path):
                    print(f"Creating example file: {file_path}")
                    with open(file_path, "w") as f:
                        # Each file has slightly different emails
                        f.write(f"email\nuser{i+1}@example.com\nuser{i+1}@gmail.com\ninvalid-email-{i+1}\n")
            
            # Upload all files in parallel
            print("Uploading files in parallel...")
            upload_tasks = [client.upload_file(file) for file in files]
            upload_results = await asyncio.gather(*upload_tasks)
            
            # Get file IDs
            file_ids = [result["file_id"] for result in upload_results]
            for i, file_id in enumerate(file_ids):
                print(f"File {files[i]} uploaded with ID: {file_id}")
            
            # Poll for completion and get results without saving to disk
            print("Waiting for all files to process...")
            poll_tasks = [
                client.poll_file_until_complete(
                    file_id=file_id,
                    interval=5,
                    max_retries=60,
                    output_path=None,  # Don't save to disk
                    return_dataframe=True
                ) 
                for file_id in file_ids
            ]
            
            # Get all results in parallel
            dataframes = await asyncio.gather(*poll_tasks)
            
            # Process and print results
            for i, df in enumerate(dataframes):
                print(f"\nResults for {files[i]}:")
                print(f"  Number of emails: {len(df)}")
                print(f"  Valid emails: {df[df['is_valid'] == True].shape[0]}")
                print(f"  Invalid emails: {df[df['is_valid'] == False].shape[0]}")
            
        except ValidizError as e:
            print(f"API error: {e.message}")
        except Exception as e:
            print(f"Error: {str(e)}")


async def error_handling_examples():
    """Examples of handling different error types asynchronously."""
    print("\n== Error Handling Examples (Async) ==")
    
    # Example with invalid API key
    try:
        async with AsyncValidiz(api_key="invalid_key") as invalid_client:
            await invalid_client.validate_email("user@example.com")
    except ValidizAuthError as e:
        print(f"Authentication error: {e.message}")
    except ValidizError as e:
        print(f"API error: {e.message}")
    
    # Example with connection error (non-existent URL)
    try:
        async with AsyncValidiz(api_key=API_KEY, api_base_url="https://nonexistent.invalid/v1") as bad_url_client:
            await bad_url_client.validate_email("user@example.com")
    except ValidizConnectionError as e:
        print(f"Connection error: {e.message}")
    except ValidizError as e:
        print(f"API error: {e.message}")


async def main():
    """Main function to run all async examples."""
    print("VALIDIZ ASYNCHRONOUS CLIENT EXAMPLES")
    print("===================================")
    print("\nBefore running this example, replace 'your_api_key_here' with your actual API key.")
    print("Alternatively, set the VALIDIZ_API_KEY environment variable.")
    
    # Run the examples
    await validate_single_email()
    await validate_multiple_emails()
    await batch_validate_emails()
    await upload_and_process_file()
    await process_multiple_files()
    await error_handling_examples()
    
    print("\nExamples completed.")


if __name__ == "__main__":
    asyncio.run(main()) 