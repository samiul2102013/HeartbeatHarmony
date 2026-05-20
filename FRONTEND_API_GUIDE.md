# Frontend Integration Guide: Authentication Flow

This guide provides the API endpoints and request/response structures for integrating the authentication flow into the mobile/web frontend.

## Base URL
`https://hewlett-butler-away-dicke.trycloudflare.com/api/accounts/auth`

---

## 1. Registration
**Endpoint**: `POST /register/`
**Payload**:
```json
{
  "email": "user@example.com",
  "password": "yourpassword",
  "first_name": "John",
  "last_name": "Doe"
}
```

---

## 2. Login (Two-Step Verification)
**Endpoint**: `POST /login/`
**Payload**:
```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

### Responses:
- **Case A: Email Not Verified** (Requires OTP)
  ```json
  {
    "success": true,
    "data": {
      "detail": "Please verify your email with the OTP sent to your email.",
      "email": "user@example.com",
      "verified": false
    }
  }
  ```
- **Case B: Success** (Returns Tokens)
  ```json
  {
    "success": true,
    "data": {
      "user": { ...profile data... },
      "refresh": "REFRESH_TOKEN",
      "access": "ACCESS_TOKEN"
    }
  }
  ```

---

## 3. Password Reset Flow

### Step 1: Request Reset (Forgot Password)
**Endpoint**: `POST /forgot-password/`
**Payload**:
```json
{
  "email": "user@example.com"
}
```

### Step 2: Verify OTP
**Endpoint**: `POST /verify-reset-otp/`
**Payload**:
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

### Step 3: Final Reset
**Endpoint**: `POST /reset-password/`
**Payload**:
```json
{
  "email": "user@example.com",
  "otp": "123456",
  "new_password": "NewSecurePassword123!"
}
```

---

## 4. Email Verification (Post-Registration)
**Endpoint**: `POST /verify-email/`
**Payload**:
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

---

## Development Notes
- **OTP Bypass**: In development mode, you can use `123456` as the OTP for any request to bypass actual email checks.
- **Headers**: All requests must include `Content-Type: application/json`.
- **Authorization**: For protected routes (Profile, etc.), use the header: `Authorization: Bearer <ACCESS_TOKEN>`.
