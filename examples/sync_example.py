#!/usr/bin/env python3
"""
Synchronous Client Examples for Validiz

This example demonstrates how to use the Validiz synchronous client
to validate email addresses and process files.
"""

import os

from dotenv import load_dotenv

from validiz import Validiz, ValidizAuthError, ValidizConnectionError, ValidizError

load_dotenv(override=True)

# Set your API key - in production, use environment variables
API_KEY = os.environ.get("VALIDIZ_API_KEY", "your_api_key_here")


def validate_single_email():
    """Example for validating a single email address."""
    print("\n== Validating a Single Email ==")

    # Initialize the client
    client = Validiz(api_key=API_KEY)

    try:
        # Validate a single email
        results = client.validate_email("user@example.com")

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


def validate_multiple_emails():
    """Example for validating multiple email addresses in a single request."""
    print("\n== Validating Multiple Emails ==")

    # Initialize the client
    client = Validiz(api_key=API_KEY)

    try:
        # List of emails to validate
        emails = [
            "user1@example.com",
            "user2@gmail.com",
            "invalid-email",
            "user3@nonexistentdomain.xyz",
        ]

        # Validate multiple emails in a single request
        results = client.validate_email(emails)

        # Print the validation results
        print(f"Validated {len(results)} emails:")
        for result in results:
            status = "✅ Valid" if result.is_valid else "❌ Invalid"
            error = (
                f" ({result.error_message})"
                if not result.is_valid and result.error_message
                else ""
            )
            print(f"  {result.email}: {status}{error}")

    except ValidizError as e:
        print(f"API error: {e.message}")


def upload_and_process_file():
    """Example for uploading a file for validation and downloading results."""
    print("\n== Processing File (Upload, Check Status, Download) ==")

    # Initialize the client
    client = Validiz(api_key=API_KEY)

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
        upload_result = client.upload_file(file_path)
        file_id = upload_result["file_id"]
        print(f"File uploaded with ID: {file_id}")

        # Check the file status
        status = client.get_file_status(file_id)
        print(f"File status: {status['status']}")

        # Poll until the file is processed and get a DataFrame
        print("Waiting for file processing to complete...")
        results_df = client.poll_file_until_complete(
            file_id=file_id,
            interval=5,  # Check every 5 seconds
            max_retries=60,  # Try for 5 minutes (60 * 5 = 300 seconds)
            return_dataframe=True,  # Also return as DataFrame
        )

        # Ensure we have a DataFrame with proper typing
        from pandas import DataFrame

        if not isinstance(results_df, DataFrame):
            raise TypeError("Expected DataFrame but got a different type")

        # Print the results summary
        print(f"\nProcessed {len(results_df)} emails:")
        print(f"  Valid emails: {results_df[results_df['is_valid']].shape[0]}")
        print(f"  Invalid emails: {results_df[~results_df['is_valid']].shape[0]}")
        print("\nFirst few results:")
        print(results_df.head())

    except FileNotFoundError as e:
        print(f"File error: {str(e)}")
    except ValidizError as e:
        print(f"API error: {e.message}")
    except TimeoutError as e:
        print(f"Timeout error: {str(e)}")


def error_handling_examples():
    """Examples of handling different error types."""
    print("\n== Error Handling Examples ==")

    # Example with invalid API key
    try:
        invalid_client = Validiz(api_key="invalid_key")
        invalid_client.validate_email("user@example.com")
    except ValidizAuthError as e:
        print(f"Authentication error: {e.message}")
    except ValidizError as e:
        print(f"API error: {e.message}")

    # Example with connection error (non-existent URL)
    try:
        bad_url_client = Validiz(
            api_key=API_KEY, api_base_url="https://nonexistent.invalid/v1"
        )
        bad_url_client.validate_email("user@example.com")
    except ValidizConnectionError as e:
        print(f"Connection error: {e.message}")
    except ValidizError as e:
        print(f"API error: {e.message}")


if __name__ == "__main__":
    print("VALIDIZ SYNCHRONOUS CLIENT EXAMPLES")
    print("==================================")
    print(
        "\nBefore running this example, replace 'your_api_key_here' with your actual API key."
    )
    print("Alternatively, set the VALIDIZ_API_KEY environment variable.")

    # Run the examples
    validate_single_email()
    validate_multiple_emails()
    upload_and_process_file()
    error_handling_examples()

    print("\nExamples completed.")
