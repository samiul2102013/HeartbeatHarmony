# Flutter Auth — What Needs to Change (Based on Last Commit: `otp fix`)

## What Changed in the Last Commit

| File | What Changed |
|------|-------------|
| `serializers.py` | Removed `password2` field — registration no longer needs a confirm-password field |
| `utils.py` | OTP is now **real random** (was hardcoded `123456`). Also added a **5-min reuse window** — same OTP is reused if resent within 5 minutes |
| `views.py` | `ForgotPassword` response structure changed — `detail` moved to `message` key. `ResetPassword` now checks expiry separately for token vs OTP paths |
| `settings.py` | Minor config additions (likely dev bypass settings) |

---

## Flutter Changes Required

### 1. Registration Screen — Remove `password2` / Confirm Password Field

**Before (what you were sending):**
```json
{
  "email": "user@example.com",
  "password": "Pass@123",
  "password2": "Pass@123"
}
```

**Now (what to send):**
```json
{
  "email": "user@example.com",
  "password": "Pass@123"
}
```

- Remove the confirm password `TextFormField` from the UI, OR keep it for UX validation only (client-side) but **do not send `password2` in the API request body**.

---

### 2. Login Flow — Handle Unverified Email OTP Gate

Login returns two different shapes depending on verification status.

**If email is NOT verified** → response looks like:
```json
{
  "status": "success",
  "data": {
    "detail": "Please verify your email with the OTP sent to your email.",
    "email": "user@example.com",
    "verified": false
  }
}
```
→ Flutter must detect `verified: false` and **navigate to the OTP verification screen**, passing the `email` along.

**If email IS verified** → response looks like:
```json
{
  "status": "success",
  "data": {
    "user": { ... },
    "refresh": "...",
    "access": "..."
  }
}
```
→ Store tokens and navigate to home.

**Action:** Check for `data.verified == false` after login and branch accordingly.

---

### 3. Email Verification (OTP Screen)

Send to `POST /auth/verify-email/`:
```json
{
  "otp": "847291",
  "email": "user@example.com"
}
```
No `token` field needed for mobile — OTP method is the right path.

**Important:** OTP is now truly random (not `123456` anymore). Remove any hardcoded test OTP from Flutter dev/test code.

The 5-min reuse window means if the user hits "Resend", they may get the **same OTP** — that's expected behavior, not a bug.

---

### 4. Forgot Password Flow — Response Structure Changed

`POST /auth/forgot-password/` response:
```json
{
  "status": "success",
  "message": "If this email exists, a reset OTP will be sent.",
  "data": {
    "token": "uuid-here-if-email-exists"
  }
}
```

**What changed:** The message is now in the top-level `message` key, not inside `data.detail`.

**Action:** If Flutter was reading `response['data']['detail']` for the success message, switch to `response['message']`.

The `token` in `data` is optional (only present if the email exists). For mobile flow, use the **OTP path** (not token), so you can ignore `token`.

---

### 5. Reset Password — Two Paths, Use OTP Path for Mobile

**Recommended mobile flow:**

Step 1 — Forgot password:
```
POST /auth/forgot-password/   { "email": "..." }
```

Step 2 — Verify OTP:
```
POST /auth/verify-reset-otp/   { "email": "...", "otp": "123456" }
```

Step 3 — Reset password:
```
POST /auth/reset-password/   { "email": "...", "otp": "123456", "new_password": "NewPass@1" }
```

**New error to handle in Step 3:**
```json
{ "detail": "Reset OTP has expired. Please request a new one." }
```
OTP expires after **1 hour**. Show an error and redirect back to forgot-password screen.

---

### 6. Token Refresh

`POST /auth/token/refresh/`  
Send `{ "refresh": "..." }` → get new `access` token.  
No changes here, but make sure your Dio/http interceptor is handling 401s and auto-refreshing.

---

## Auth Flow Summary (for reference)

```
Register → OTP sent to email
    ↓
Verify Email (POST /auth/verify-email/ with otp + email)
    ↓
Login → if verified: get tokens | if not: OTP screen again
    ↓
Forgot Password → Verify OTP → Reset Password
```

---

## Overall Auth Logic Assessment

**The auth logic is solid.** Here's the quick verdict:

| Area | Status | Notes |
|------|--------|-------|
| Registration | ✅ OK | `password2` removed cleanly, username auto-generated from email |
| Login | ✅ OK | Handles unverified users gracefully, returns clear `verified: false` flag |
| Email OTP Verification | ✅ OK | Real random OTP now, 5-min reuse window is a good anti-spam touch |
| Resend Verification | ✅ OK | Authenticated endpoint, regenerates both token and OTP |
| Forgot Password | ✅ OK | No user enumeration leak, response structure is clean |
| Verify Reset OTP | ✅ OK | Expiry check in place, dev bypass supported |
| Reset Password | ✅ OK | Both token and OTP paths work, expiry checked per path now (this was the bug fixed in this commit) |
| Token Refresh | ✅ OK | Standard SimpleJWT |

**One thing to watch:** `ForgotPasswordSerializer` raises a `ValidationError` if the email doesn't exist, but `ForgotPasswordView` catches that and returns a 200 anyway — so no user enumeration. That's intentional and correct, but slightly unusual. Flutter doesn't need to do anything special here.
