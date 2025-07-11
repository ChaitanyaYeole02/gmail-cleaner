# Gmail App Password Setup Guide

This guide will help you set up Gmail App Password for the test email generator.

## Why App Password?

Gmail requires an "App Password" for programmatic access (like sending emails via SMTP) instead of your regular Gmail password. This is a security feature.

## Setup Steps

### 1. Enable 2-Factor Authentication

1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Click on "Security" in the left sidebar
3. Under "Signing in to Google", click on "2-Step Verification"
4. Follow the steps to enable 2-factor authentication

### 2. Generate App Password

1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Click on "Security" in the left sidebar
3. Under "Signing in to Google", click on "App passwords"
4. You might need to verify your password again
5. Under "Select app", choose "Mail"
6. Under "Select device", choose "Other (Custom name)"
7. Enter a name like "Gmail Test Email Generator"
8. Click "Generate"
9. **Copy the 16-character password** (it looks like: `abcd efgh ijkl mnop`)

## Using the App Password

When running the test email generator:

```bash
python3 generate_test_emails.py
```

- **Email**: Enter your Gmail address (e.g., `yourname@gmail.com`)
- **Password**: Enter the 16-character app password (not your regular Gmail password)

## Example

```
Enter your Gmail address: yourname@gmail.com
Enter your Gmail app password: abcd efgh ijkl mnop
```

## Troubleshooting

### "Username and Password not accepted"

1. **Make sure 2-Factor Authentication is enabled**
2. **Use the App Password, not your regular password**
3. **Check that the App Password is copied correctly** (16 characters, no spaces)
4. **Try generating a new App Password** if the current one doesn't work

### "Less secure app access"

- This setting is no longer available
- You **must** use App Passwords for programmatic access
- Regular passwords won't work for SMTP

### "App passwords not available"

- Make sure 2-Factor Authentication is enabled first
- App passwords only appear after 2FA is set up

## Security Notes

- **App passwords are secure** - they only allow specific access
- **You can revoke them anytime** from Google Account settings
- **Each app password is unique** and can be deleted individually
- **Never share your app password** - treat it like a regular password

## Alternative: Use Gmail API

If you prefer, you can also use the Gmail API instead of SMTP:

1. Use the existing `credentials.json` file
2. Modify the test email generator to use Gmail API
3. This would be more secure but requires more setup

## Quick Test

After setting up the app password, you can test it with a simple script:

```python
import smtplib

# Test connection
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email@gmail.com', 'your-app-password')
print("✅ Connection successful!")
server.quit()
```

This will verify that your app password is working correctly. 