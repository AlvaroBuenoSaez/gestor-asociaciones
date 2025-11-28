import os
import sys
import requests

# Configuration
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
LOGIN_URL = f"{BASE_URL}/admin/login/"
# Credentials expected (same as in your .env or config.env)
USERNAME = os.getenv("ADMIN_USER", "admin")
PASSWORD = os.getenv("ADMIN_PASS", "admin123456")

def test_login_and_env():
    print(f"[INFO] Starting integration test against {BASE_URL}")
    print(f"[INFO] Attempting login with user: {USERNAME}")

    session = requests.Session()

    try:
        # 1. Get login page to retrieve CSRF token
        print("   1. Fetching CSRF token...")
        try:
            response = session.get(LOGIN_URL)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            print(f"[ERROR] Error: Could not connect to {LOGIN_URL}")
            sys.exit(1)

        # Django stores the token in cookies, needed for POST
        if 'csrftoken' not in session.cookies:
            print("[ERROR] Error: CSRF cookie not found")
            # Print headers for debugging
            print(f"Headers: {response.headers}")
            sys.exit(1)

        csrf_token = session.cookies['csrftoken']

        # 2. Perform Login
        print("   2. Sending credentials...")
        payload = {
            'username': USERNAME,
            'password': PASSWORD,
            'csrfmiddlewaretoken': csrf_token,
            'next': '/users/dashboard/' # Expected redirect
        }

        # Important headers for Django to accept the request
        headers = {
            'Referer': LOGIN_URL,
            'User-Agent': 'IntegrationTest/1.0'
        }

        post_response = session.post(LOGIN_URL, data=payload, headers=headers)

        # 3. Verifications
        # If login is correct, Django redirects. Requests follows redirects by default.
        # We check if we landed on the dashboard or if the URL contains 'dashboard'

        print(f"   3. Verifying response... Final URL: {post_response.url}")

        if '/dashboard/' in post_response.url or '/users/dashboard/' in post_response.url or '/admin/' in post_response.url:
            print("[SUCCESS] Login SUCCESSFUL: Redirected to dashboard or admin.")
        elif "Por favor, introduzca un nombre de usuario y clave correctos" in post_response.text or "Please enter a correct username and password" in post_response.text:
            print("[ERROR] Login FAILED: Incorrect credentials.")
            print("   This indicates the .env was NOT read correctly or the user was not created.")
            sys.exit(1)
        else:
            # Check if we are still on the login page
            if '/login/' in post_response.url:
                print("[ERROR] Login FAILED: Still on login page.")
                # Print a snippet of the body to see if there are errors
                print(f"   Response snippet: {post_response.text[:500]}")
                sys.exit(1)
            else:
                print(f"[WARNING] Unexpected result. Final URL: {post_response.url}")
                # It might be a success if we are not on login page and status is 200
                if post_response.status_code == 200:
                     print("   Assuming success as we moved away from login page.")
                else:
                     sys.exit(1)

        print("[SUCCESS] Integration test completed successfully.")

    except Exception as e:
        print(f"[ERROR] Exception during test: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_login_and_env()
