import requests

# =========================
# CONFIGURATION
# =========================
API_KEY = "xJO0oM500D5jdZhh0fF9MuPpkS8YmQbH9N7lPIxO"
BASE_URL = "http://localhost:8080/api/v1"

def get_token():
    response = requests.post(
        f"{BASE_URL}/api_key/token",
        params={"key": API_KEY}
    )

    if response.status_code != 200:
        raise Exception(f"Failed to get token: {response.text}")

    token = response.json()["authToken"]["token"]
    print("✅ New token generated")
    return token


def verify_token(token):
    response = requests.get(
        f"{BASE_URL}/user/me",
        headers={"Girder-Token": token}
    )

    if response.status_code != 200:
        raise Exception("Token verification failed")

    user = response.json()
    print("✅ Logged in as:", user["login"])
    print("Admin:", user["admin"])


if __name__ == "__main__":
    token = get_token()
    verify_token(token)
    print(token)