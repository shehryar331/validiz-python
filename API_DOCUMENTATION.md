# Email Validator Pro - API Documentation

This guide serves as a reference for integrating Email Validator Pro into your website. Follow the instructions below to authenticate users, validate emails, and handle errors effectively.

---

## Base URLs

The application uses two different domains for API and frontend functionality:

- **API Endpoints (Validation Services):**
```
https://api.validiz.com/v1
```

- **Frontend/Authentication Endpoints:**
```
https://frontend.validiz.com
```

Use the appropriate domain based on the endpoint you're calling. API endpoints are prefixed with `/v1` and use the API domain, while authentication and frontend endpoints use the frontend domain.

---

## Authentication Methods

The application uses two different authentication methods:

1. **JWT Authentication** - Used for frontend endpoints
   - Format: `Authorization: Bearer <access_token>`
   - Obtained via sign in, sign up, or token refresh

2. **API Key Authentication** - Used for API endpoints
   - Format: `X-API-Key: <api_key>`
   - Obtained via the Generate API Key endpoint

---

## Authentication

Authentication endpoints allow you to create accounts, log in, and manage tokens. These endpoints are critical for securing your API calls from the front end.

**NOTE: All authentication endpoints use the frontend domain (frontend.validiz.com)**

### 1. Sign Up

**Create a new user account.**

#### Request

```http
POST https://frontend.validiz.com/auth/signup
Content-Type: application/json
```

```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string",
  "first_name": "string",
  "last_name": "string",
  "role": "user", // "user" or "admin"
  "admin_secret": "string" // Required only for admin role
}
```

#### Response (201 Created)

```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```

---

### 2. Sign In

**Authenticate an existing user.**

#### Request

```http
POST https://frontend.validiz.com/auth/signin
Content-Type: application/json
```

```json
{
  "email": "user@example.com",
  "password": "string"
}
```

#### Response (200 OK)

```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```

---

### 3. Refresh Token

**Obtain a new access token using your refresh token.**

#### Request

```http
POST https://frontend.validiz.com/auth/refresh
Content-Type: application/json
```

```json
{
  "refresh_token": "string"
}
```

#### Response (200 OK)

```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```

---

### 4. Get User Profile

**Get the current user's profile information.**

#### Request

```http
GET https://frontend.validiz.com/auth/user
Authorization: Bearer <access_token>
```

#### Response (200 OK)

```json
{
  "_id": "string",
  "username": "string",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "role": "string",
  "email_credits": 5000,
  "api_credits": 1000,
  "api_key": "string",
  "status": "active",
  "created_at": "datetime"
}
```

---

### 5. Change Password

**Change a user's password using their current password for verification.**

#### Request

```http
POST https://frontend.validiz.com/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "current_password": "string",
  "new_password": "string"
}
```

#### Response (200 OK)

```json
{
  "message": "Password changed successfully"
}
```

---

### 6. Update Profile

**Update a user's first name and last name.**

#### Request

```http
POST https://frontend.validiz.com/auth/update-profile
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "first_name": "string",
  "last_name": "string"
}
```

#### Response (200 OK)

```json
{
  "_id": "string",
  "username": "string",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "role": "string",
  "email_credits": 5000,
  "api_credits": 1000,
  "api_key": "string",
  "status": "active",
  "created_at": "datetime"
}
```

---

### 7. Forgot Password

**Request a password reset.**

#### Request

```http
POST https://frontend.validiz.com/auth/forgot-password
Content-Type: application/json
```

```json
{
  "email": "user@example.com"
}
```

#### Response (200 OK)

```json
{
  "message": "Password reset instructions sent to your email"
}
```

---

### 8. Reset Password

**Reset a user's password using OTP.**

#### Request

```http
POST https://frontend.validiz.com/auth/reset-password
Content-Type: application/json
```

```json
{
  "email": "user@example.com",
  "otp": "string",
  "new_password": "string"
}
```

#### Response (200 OK)

```json
{
  "message": "Password reset successful"
}
```

---

### 9. Generate API Key

**Generate or regenerate an API key for the authenticated user.**

#### Request

```http
POST https://frontend.validiz.com/auth/generate-api-key
Authorization: Bearer <access_token>
```

#### Response (200 OK)

```json
{
  "api_key": "string",
  "credits_remaining": 1000
}
```

---

### 10. Google OAuth Authentication

**Authenticate users with their Google account.**

#### Backend Endpoints

##### 1. Initiate Google Login

```http
GET https://frontend.validiz.com/auth/google/login?redirect_uri={frontend_url}
```

Query Parameters:

- **redirect_uri**: URL encoded frontend page URL where the user should be redirected after authentication

##### 2. Google Callback

```http
GET https://frontend.validiz.com/auth/google/callback?code={code}&state={state}
```

This endpoint is used internally by the Google OAuth flow. It will redirect back to the frontend URL specified in the initial login request with the authentication tokens as URL parameters.

#### Frontend Implementation

Here's a complete example of implementing Google authentication in your frontend:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Google Auth Example</title>
  </head>
  <body>
    <button id="loginGoogle">Login with Google</button>

    <script>
      // Function to get URL parameters after OAuth redirect
      function getUrlParams() {
        const params = new URLSearchParams(window.location.search);
        return Object.fromEntries(params.entries());
      }

      // Handle Google login button click
      document
        .getElementById("loginGoogle")
        .addEventListener("click", function () {
          const currentUrl = window.location.href.split("?")[0]; // Get base URL without query params
          const redirectUri = encodeURIComponent(currentUrl);
          window.location.href = `https://frontend.validiz.com/auth/google/login?redirect_uri=${redirectUri}`;
        });

      // Check if we're returning from Google OAuth
      const urlParams = getUrlParams();
      if (urlParams.access_token && urlParams.refresh_token) {
        // Store tokens securely
        localStorage.setItem("access_token", urlParams.access_token);
        localStorage.setItem("refresh_token", urlParams.refresh_token);

        // Clean up the URL
        window.history.replaceState(
          {},
          document.title,
          window.location.pathname
        );

        // Redirect to dashboard or handle successful login
        console.log("Successfully logged in with Google!");
      }
    </script>
  </body>
</html>
```

---

## OTP System

The One-Time Password (OTP) system provides endpoints for sending and verifying OTPs, which are commonly used for email verification, password resets, and two-factor authentication.

**NOTE: All OTP endpoints use the frontend domain (frontend.validiz.com)**

### 1. Send OTP

**Send a one-time password to the specified email address.**

#### Request

```http
POST https://frontend.validiz.com/otp/send
Content-Type: application/json
```

```json
{
  "email": "user@example.com"
}
```

#### Response (200 OK)

```json
{
  "message": "OTP sent successfully"
}
```

---

### 2. Verify OTP

**Verify a one-time password for the specified email.**

#### Request

```http
POST https://frontend.validiz.com/otp/verify
Content-Type: application/json
```

```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

#### Response (200 OK)

```json
{
  "message": "Email verified successfully"
}
```

#### Error Responses

- **404 Not Found**: No OTP found for this email
- **400 Bad Request**: OTP has expired
- **400 Bad Request**: Invalid OTP

---

## Frontend Email Validation

Endpoints for validating emails through the web interface. These endpoints require JWT authentication (except for the free validation endpoint).

**NOTE: All frontend validation endpoints use the frontend domain (frontend.validiz.com)**

### 1. Validate Email (Free)

**Validate a single email without authentication (rate limited).**

#### Request

```http
POST https://frontend.validiz.com/validate/email/free
Content-Type: application/json
```

```json
{
  "emails": ["user@example.com"]
}
```

#### Response (200 OK)

```json
{
  "email": "user@example.com",
  "is_valid": true,
  "error_message": null,
  "status": "valid",
  "sub_status": "mailbox_exists",
  "free_email": true,
  "account": "user",
  "domain": "example.com",
  "smtp_provider": "Google",
  "mx_found": true,
  "mx_record": ["mx.example.com"]
}
```

---

### 2. Validate Email(s)

**Validate one or more emails with JWT authentication.**

#### Request

```http
POST https://frontend.validiz.com/validate/email
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "emails": ["user@example.com", "another@example.com"]
}
```

#### Response (200 OK)

Returns an array of validation results:

```json
[
  {
    "email": "user@example.com",
    "is_valid": true,
    "error_message": null,
    "status": "valid",
    "sub_status": "mailbox_exists",
    "free_email": true,
    "account": "user",
    "domain": "example.com",
    "smtp_provider": "Google",
    "mx_found": true,
    "mx_record": ["mx.example.com"]
  },
  {
    "email": "another@example.com",
    "is_valid": false,
    "error_message": "Domain does not exist",
    "status": "invalid",
    "sub_status": "domain_not_found",
    "free_email": false,
    "account": "another",
    "domain": "example.com",
    "smtp_provider": null,
    "mx_found": false,
    "mx_record": []
  }
]
```

---

### 3. Upload File for Validation

**Upload a file containing email addresses for bulk validation.**

#### Request

```http
POST https://frontend.validiz.com/validate/file
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

Form Data:
- `file`: CSV or XLSX file containing email addresses (one per line or in a column)

#### Response (200 OK)

```json
{
  "file_id": "string",
  "original_filename": "string",
  "status": "pending",
  "created_at": "datetime"
}
```

---

### 4. Get File Status

**Check the status of a file validation job.**

#### Request

```http
GET https://frontend.validiz.com/validate/file/{file_id}/status
Authorization: Bearer <access_token>
```

#### Response (200 OK)

```json
{
  "file_id": "string",
  "original_filename": "string",
  "status": "completed", // "pending", "processing", "completed", "failed", "downloaded", "deleted"
  "created_at": "datetime",
  "completed_at": "datetime",
  "error_message": null
}
```

---

### 5. Download Processed File

**Download the results of a completed file validation job.**

#### Request

```http
GET https://frontend.validiz.com/validate/file/{file_id}/download
Authorization: Bearer <access_token>
```

#### Response (200 OK)

A downloadable CSV file containing all the processed email validation results.

---

## Email Validation API

These endpoints provide email validation capabilities and require API key authentication.

**NOTE: All email validation endpoints use the API domain (api.validiz.com) and require the X-API-Key header for authentication**

### 1. Validate Single Email

**Validate a single email address or batch of email addresses.**

#### Request

```http
POST https://api.validiz.com/v1/validate/email
X-API-Key: <api_key>
Content-Type: application/json
```

```json
{
  "emails": ["user@example.com"]
}
```

#### Response (200 OK)

```json
{
  "email": "user@example.com",
  "is_valid": true,
  "error_message": null,
  "status": "valid",
  "sub_status": "mailbox_exists",
  "free_email": true,
  "account": "user",
  "domain": "example.com",
  "smtp_provider": "Google",
  "mx_found": true,
  "mx_record": ["mx.example.com"]
}
```

---

### 2. Validate File

**Upload a file containing email addresses for validation.**

#### Request

```http
POST https://api.validiz.com/v1/validate/file
X-API-Key: <api_key>
Content-Type: multipart/form-data
```

Form Data:
- `file`: CSV or TXT file containing email addresses (one per line)

#### Response (202 Accepted)

```json
{
  "file_id": "string",
  "original_filename": "string",
  "status": "pending",
  "created_at": "datetime"
}
```

---

### 3. Get File Status

**Check the status of a file validation job.**

#### Request

```http
GET https://api.validiz.com/v1/validate/file/{file_id}/status
X-API-Key: <api_key>
```

#### Response (200 OK)

```json
{
  "file_id": "string",
  "status": "completed", // "pending", "processing", "completed", "failed", "downloaded", "deleted"
  "original_filename": "string",
  "created_at": "datetime",
  "completed_at": "datetime",
  "error_message": null
}
```

---

### 4. Download Processed File

**Download the results of a completed file validation job.**

#### Request

```http
GET https://api.validiz.com/v1/validate/file/{file_id}/download
X-API-Key: <api_key>
```

#### Response (200 OK)

A downloadable CSV file containing all the processed email validation results.

---

## Admin Endpoints

These endpoints are for administrative purposes and require admin role authentication.

**NOTE: All admin endpoints use the frontend domain (frontend.validiz.com)**

### 1. List All Uploads

**Get a list of all file uploads in the system.**

#### Request

```http
GET https://frontend.validiz.com/admin/uploads
Authorization: Bearer <access_token>
```

#### Response (200 OK)

```json
[
  {
    "file_id": "string",
    "original_filename": "string",
    "status": "completed",
    "created_at": "datetime",
    "completed_at": "datetime",
    "error_message": null
  }
]
```

---

### 2. List Recent Files

**Get a list of file uploads with optional filtering.**

#### Request

```http
GET https://frontend.validiz.com/admin/files
Authorization: Bearer <access_token>
```

Query Parameters:
- **days**: Number of days to look back (default: 7)
- **status**: Filter by status

#### Response (200 OK)

```json
[
  {
    "file_id": "string",
    "original_filename": "string",
    "status": "completed",
    "created_at": "datetime",
    "completed_at": "datetime",
    "error_message": null
  }
]
```

---

### 3. Delete File Upload

**Delete a file upload.**

#### Request

```http
DELETE https://frontend.validiz.com/admin/files/{file_id}
Authorization: Bearer <access_token>
```

#### Response (200 OK)

```json
{
  "message": "File deleted successfully"
}
```

---

### 4. Get File Statistics

**Get statistics about file uploads.**

#### Request

```http
GET https://frontend.validiz.com/admin/files/stats
Authorization: Bearer <access_token>
```

Query Parameters:
- **days**: Number of days to look back (default: 7)

#### Response (200 OK)

```json
{
  "total_files": 100,
  "status_counts": {
    "pending": 5,
    "processing": 10,
    "completed": 80,
    "failed": 5
  },
  "daily_uploads": [
    {
      "date": "2023-05-01",
      "count": 15
    },
    {
      "date": "2023-05-02",
      "count": 20
    }
  ]
}
```

---

### 5. List All Users

**Get a list of all registered users.**

#### Request

```http
GET https://frontend.validiz.com/admin/users
Authorization: Bearer <access_token>
```

#### Response (200 OK)

```json
[
  {
    "_id": "string",
    "username": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "role": "string",
    "email_credits": 5000,
    "api_credits": 1000,
    "status": "active",
    "created_at": "datetime"
  }
]
```

---

### 6. Set API Credits

**Set the API credits for a user.**

#### Request

```http
POST https://frontend.validiz.com/admin/user/{user_id}/set-api-credits?credits=1000
Authorization: Bearer <access_token>
```

Query Parameters:
- **credits**: Number of credits to set

#### Response (200 OK)

```json
{
  "message": "API credits set successfully"
}
```

---

### 7. Set Email Credits

**Set the email credits for a user.**

#### Request

```http
POST https://frontend.validiz.com/admin/user/{user_id}/set-email-credits?credits=1000
Authorization: Bearer <access_token>
```

Query Parameters:
- **credits**: Number of credits to set

#### Response (200 OK)

```json
{
  "message": "Email credits set successfully"
}
```

---

### 8. Set User Status

**Set the status for a user (active or inactive).**

#### Request

```http
POST https://frontend.validiz.com/admin/user/{user_id}/set-status?status=active
Authorization: Bearer <access_token>
```

Query Parameters:
- **status**: New status for the user ("active" or "inactive")

#### Response (200 OK)

```json
{
  "message": "User status set successfully"
}
```

---

## Health Check

### 1. API Health Check

**Check the health status of the API and its dependencies.**

#### Request

```http
GET https://api.validiz.com/health
```

#### Response (200 OK)

```json
{
  "status": "healthy",
  "api_version": "1.0.0",
  "environment": "production",
  "database": "connected"
}
```

#### Response (503 Service Unavailable)

```json
{
  "status": "degraded",
  "api_version": "1.0.0",
  "environment": "production",
  "database": "disconnected",
  "database_error": "Error message"
}
```

---

## Error Handling

All API endpoints follow a consistent error response format:

```json
{
  "error": "Error message describing the issue"
}
```

For certain error types, a more detailed error format may be returned:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

### Common Error Codes

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 400 | BAD_REQUEST | Invalid request format or parameters |
| 401 | UNAUTHORIZED | Authentication required or invalid credentials |
| 403 | FORBIDDEN | Insufficient permissions or invalid API key |
| 404 | NOT_FOUND | Resource not found |
| 409 | CONFLICT | Resource conflict (e.g., duplicate username/email) |
| 422 | VALIDATION_ERROR | Request validation failed |
| 429 | RATE_LIMITED | Too many requests |
| 500 | INTERNAL_ERROR | Server-side error |
| 503 | SERVICE_UNAVAILABLE | Service temporarily unavailable |

---

## Rate Limits

- Free validation endpoints: 5 requests per hour per IP address
- JWT authenticated endpoints: 100 requests per hour per user
- API key authenticated endpoints: Unlimited (limited by available credits)

### Credit System
- Each email validation costs 1 credit
- Each file upload validation costs 1 credit per email in the file
- Default API credits for new accounts: 1000
- Default Email credits for new accounts: 5000
- Google OAuth sign-up bonus: 1000 email credits

---

## Best Practices

1. **Token Management**

   - Store tokens securely
   - Implement token refresh logic
   - Handle token expiration gracefully

2. **API Key Security**

   - Keep your API key secret and secure
   - Don't hardcode API keys in client-side code
   - Regenerate API keys if compromised

3. **Error Handling**

   - Implement proper error handling for all API calls
   - Handle rate limits appropriately

4. **File Processing**

   - Keep files under 10MB
   - Include proper email column headers
   - Monitor file processing status

5. **Security**
   - Use HTTPS for all requests
   - Implement proper CORS policies

6. **Domain Usage**
   - Use `api.validiz.com` for all validation services (paths starting with `/v1`)
   - Use `frontend.validiz.com` for authentication and user management functionality

---

## Support

For technical support or inquiries:

- Email: [shehryardev@paklogics.com](mailto:shehryardev@paklogics.com)
