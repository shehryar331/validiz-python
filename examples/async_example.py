#!/usr/bin/env python3
"""
Example usage of the asynchronous Validiz client.
"""

import asyncio

from validiz import AsyncValidiz, ValidizConnectionError, ValidizError


async def validate_email_example(api_key):
    """Example of validating email addresses asynchronously."""
    print("\n=== Async Email Validation Example ===\n")

    # Create a client with API key
    async with AsyncValidiz(api_key=api_key) as client:
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
                if not result["is_valid"] and result.get("error_message"):
                    print(f"Error message: {result['error_message']}")
                print()

                # Display additional information
                print("Additional information:")
                print(f"Free email: {result.get('free_email', 'N/A')}")
                print(f"Account: {result.get('account', 'N/A')}")
                print(f"Domain: {result.get('domain', 'N/A')}")
                print(f"SMTP provider: {result.get('smtp_provider', 'N/A')}")
                print(f"MX found: {result.get('mx_found', 'N/A')}")
                mx_records = result.get("mx_record", [])
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
    async with AsyncValidiz(api_key=api_key) as client:
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


async def poll_file_example(api_key, file_path):
    """Example of uploading a file and polling for completion asynchronously."""
    print("\n=== Async File Upload with Polling Example ===\n")

    # Create a client with API key
    async with AsyncValidiz(api_key=api_key) as client:
        try:
            # Upload the file
            print(f"Uploading file: {file_path}")
            upload_result = await client.upload_file(file_path)
            file_id = upload_result["file_id"]
            print(f"File uploaded successfully! File ID: {file_id}")

            # Poll for completion and get results as DataFrame
            print("\nPolling for completion...")
            print(
                "This might take a while depending on the file size and server load..."
            )

            # Poll for completion with a timeout of 5 minutes (polling every 10 seconds)
            df = await client.poll_file_until_complete(
                file_id=file_id, interval=10, max_retries=30
            )

            # Process and display results
            print("\nFile processing completed!")
            print(f"Number of emails processed: {len(df)}")

            # Count valid and invalid emails
            valid_count = df[df["is_valid"]].shape[0] if "is_valid" in df.columns else 0
            invalid_count = (
                df[~df["is_valid"]].shape[0] if "is_valid" in df.columns else 0
            )

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


async def parallel_validation_example(api_key):
    """Example of validating multiple emails in parallel."""
    print("\n=== Async Parallel Validation Example ===\n")

    # Create a client with API key
    async with AsyncValidiz(api_key=api_key) as client:
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


async def batch_file_processing_example(api_key, file_paths):
    """Example of processing multiple files in parallel."""
    print("\n=== Async Batch File Processing Example ===\n")

    if not file_paths:
        print("No files provided. Skipping example.")
        return

    # Create a client with API key
    async with AsyncValidiz(api_key=api_key) as client:
        try:
            print(f"Processing {len(file_paths)} files in parallel...")

            # Upload all files
            upload_tasks = []
            for file_path in file_paths:
                print(f"Uploading file: {file_path}")
                upload_tasks.append(client.upload_file(file_path))

            # Wait for all uploads to complete
            upload_results = await asyncio.gather(*upload_tasks, return_exceptions=True)

            # Process each upload result
            file_ids = []
            for i, result in enumerate(upload_results):
                if isinstance(result, Exception):
                    print(f"Error uploading {file_paths[i]}: {str(result)}")
                else:
                    file_id = result["file_id"]
                    file_ids.append(file_id)
                    print(
                        f"File {file_paths[i]} uploaded successfully! File ID: {file_id}"
                    )

            if not file_ids:
                print("No files were uploaded successfully.")
                return

            # Poll for completion in parallel
            print("\nPolling for completion...")
            poll_tasks = [
                client.poll_file_until_complete(file_id, interval=10)
                for file_id in file_ids
            ]
            result_dfs = await asyncio.gather(*poll_tasks, return_exceptions=True)

            # Process results
            for i, result in enumerate(result_dfs):
                if isinstance(result, Exception):
                    print(f"Error processing file {file_ids[i]}: {str(result)}")
                else:
                    print(f"\nResults for file ID {file_ids[i]}:")
                    print(f"Number of emails processed: {len(result)}")

                    # Count valid and invalid emails
                    valid_count = (
                        result[result["is_valid"]].shape[0]
                        if "is_valid" in result.columns
                        else 0
                    )
                    invalid_count = (
                        result[~result["is_valid"]].shape[0]
                        if "is_valid" in result.columns
                        else 0
                    )

                    print(f"Valid emails: {valid_count}")
                    print(f"Invalid emails: {invalid_count}")

        except Exception as e:
            print(f"Unexpected error: {str(e)}")


async def main():
    # Replace with your actual API key
    API_KEY = "your_api_key_here"

    # Replace with your actual file path
    FILE_PATH = "emails.csv"

    # For batch processing example
    MULTIPLE_FILES = ["emails1.csv", "emails2.csv", "emails3.csv"]

    print("Validiz Python Library - Asynchronous Examples")
    print("==============================================")

    # Run the examples
    await validate_email_example(API_KEY)
    await upload_file_example(API_KEY, FILE_PATH)
    await poll_file_example(API_KEY, FILE_PATH)
    await parallel_validation_example(API_KEY)
    await batch_file_processing_example(API_KEY, MULTIPLE_FILES)

    print("\nExamples completed.")


if __name__ == "__main__":
    asyncio.run(main())
