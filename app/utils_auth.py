import os
import re
import json
import urllib.request
import urllib.parse
from flask import url_for, session, redirect, current_app

def send_real_sms_otp(phone, otp):
    """
    Real SMS OTP Dispatch Handler.
    Supports Twilio SMS and Fast2SMS API.
    Returns (True, success_message) or (False, error_message).
    """
    twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    twilio_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_phone = os.environ.get('TWILIO_PHONE_NUMBER')
    fast2sms_key = os.environ.get('FAST2SMS_API_KEY')

    clean_digits = re.sub(r'[^0-9]', '', phone)
    if clean_digits.startswith('91') and len(clean_digits) == 12:
        clean_digits = clean_digits[2:]

    # 1. Twilio SMS Integration
    if twilio_sid and twilio_token and twilio_phone:
        try:
            import base64
            auth_header = "Basic " + base64.b64encode(f"{twilio_sid}:{twilio_token}".encode('utf-8')).decode('utf-8')
            payload = urllib.parse.urlencode({
                'From': twilio_phone,
                'To': f'+91{clean_digits}',
                'Body': f'Your AVYRO verification OTP is: {otp}. Valid for 5 minutes. Do not share this code with anyone.'
            }).encode('utf-8')

            req = urllib.request.Request(
                f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json",
                data=payload,
                headers={
                    'Authorization': auth_header,
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                if res_data.get('sid'):
                    return True, f"SMS OTP delivered via Twilio (SID: {res_data['sid']})."
                else:
                    return False, "Twilio SMS dispatch declined."
        except urllib.error.HTTPError as e:
            try:
                err_body = json.loads(e.read().decode('utf-8'))
                err_msg = err_body.get('message') or f"HTTP Error {e.code}"
            except Exception:
                err_msg = f"HTTP Error {e.code}"
            print(f"[SMS ERROR] Twilio HTTP error: {err_msg}")
            return False, f"Twilio SMS Delivery Error: {err_msg}"
        except Exception as e:
            print(f"[SMS ERROR] Twilio exception: {e}")
            return False, f"Twilio SMS Error: {str(e)}"

    # 2. Fast2SMS Integration
    if fast2sms_key:
        try:
            url = "https://www.fast2sms.com/dev/bulkV2"
            payload = {
                "variables_values": str(otp),
                "route": "otp",
                "numbers": clean_digits
            }
            headers = {
                'authorization': fast2sms_key,
                'Content-Type': 'application/json'
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=8) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                if res_data.get('return') is True or res_data.get('status_code') == 200:
                    return True, "SMS OTP delivered via Fast2SMS carrier network."
                else:
                    msg = res_data.get('message')
                    if isinstance(msg, list):
                        msg = ", ".join(msg)
                    err_msg = msg or "Fast2SMS provider declined OTP dispatch."
                    print(f"[SMS ERROR] Fast2SMS failure: {err_msg}")
                    return False, f"SMS Delivery Error: {err_msg}"
        except Exception as e:
            print(f"[SMS ERROR] Fast2SMS exception: {e}")
            return False, f"SMS service network error: {str(e)}"

    # 3. Missing Credentials Reporting
    missing = []
    if not twilio_sid: missing.append('TWILIO_ACCOUNT_SID')
    if not twilio_token: missing.append('TWILIO_AUTH_TOKEN')
    if not twilio_phone: missing.append('TWILIO_PHONE_NUMBER')
    missing_str = ", ".join(missing)

    print(f"[SMS SECURITY WARN] OTP request for {phone} rejected because SMS credentials are missing: {missing_str}")
    return False, f"OTP service is not configured. Missing environment variables: {missing_str}"


def get_google_auth_url(next_url=None):
    """
    Generates Real Google OAuth 2.0 Authorization URL.
    """
    client_id = os.environ.get('GOOGLE_CLIENT_ID') or getattr(current_app.config, 'GOOGLE_CLIENT_ID', None)
    if not client_id:
        return None, "GOOGLE_CLIENT_ID environment variable not configured."

    redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI') or url_for('auth.google_callback', _external=True)
    
    scope = "https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email"
    import secrets
    state = secrets.token_hex(16)
    session['oauth_state'] = state
    if next_url:
        session['oauth_next'] = next_url

    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': scope,
        'state': state,
        'access_type': 'online',
        'prompt': 'select_account'
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    return auth_url, None


def exchange_google_code_for_user(code):
    """
    Exchanges Google OAuth Authorization Code for User Profile.
    """
    client_id = os.environ.get('GOOGLE_CLIENT_ID') or getattr(current_app.config, 'GOOGLE_CLIENT_ID', None)
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET') or getattr(current_app.config, 'GOOGLE_CLIENT_SECRET', None)
    redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI') or url_for('auth.google_callback', _external=True)

    if not client_id or not client_secret:
        return None, "Google OAuth Credentials (GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET) missing."

    token_url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }).encode('utf-8')

    try:
        req = urllib.request.Request(token_url, data=data, method='POST')
        with urllib.request.urlopen(req, timeout=10) as resp:
            tokens = json.loads(resp.read().decode('utf-8'))
            access_token = tokens.get('access_token')

        if not access_token:
            return None, "Failed to retrieve access token from Google."

        userinfo_url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}"
        user_req = urllib.request.Request(userinfo_url)
        with urllib.request.urlopen(user_req, timeout=10) as user_resp:
            user_data = json.loads(user_resp.read().decode('utf-8'))
            return user_data, None
    except Exception as e:
        print(f"Google OAuth Token exchange error: {e}")
        return None, f"Google OAuth authentication error: {str(e)}"
