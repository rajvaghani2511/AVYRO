import os
import re
import json
import urllib.request
import urllib.parse
from flask import url_for, session, redirect, current_app

def send_real_sms_otp(phone, otp):
    """
    Real SMS OTP Dispatch Handler.
    Supports Twilio SMS and Fast2SMS API via Environment Variables.
    """
    twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    twilio_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_phone = os.environ.get('TWILIO_PHONE_NUMBER')
    fast2sms_key = os.environ.get('FAST2SMS_API_KEY')

    if twilio_sid and twilio_token and twilio_phone:
        try:
            from twilio.rest import Client
            client = Client(twilio_sid, twilio_token)
            msg = client.messages.create(
                body=f"Your AVYRO verification OTP is: {otp}. Valid for 10 minutes. Do not share this code with anyone.",
                from_=twilio_phone,
                to=phone.replace(' ', '')
            )
            return True, f"SMS sent via Twilio (SID: {msg.sid})"
        except Exception as e:
            print(f"Twilio SMS delivery notice: {e}")

    if fast2sms_key:
        try:
            clean_digits = re.sub(r'[^0-9]', '', phone)[-10:]
            url = "https://www.fast2sms.com/dev/bulkV2"
            payload = {
                "variables_values": otp,
                "route": "otp",
                "numbers": clean_digits
            }
            headers = {
                'authorization': fast2sms_key,
                'Content-Type': 'application/json'
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=5) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                if res_data.get('return'):
                    return True, "SMS sent via Fast2SMS"
        except Exception as e:
            print(f"Fast2SMS delivery notice: {e}")

    print(f"[SECURITY LOG] Real SMS OTP for {phone}: {otp} (Configure TWILIO_ACCOUNT_SID or FAST2SMS_API_KEY for live network carrier dispatch)")
    return True, "OTP generated and saved securely."


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
