import requests

BASE_URL = "http://127.0.0.1:8000"

def translate(text, source, target):
    try:
        res = requests.post(
            f"{BASE_URL}/translate",
            json={
                "text": text,
                "source": source,
                "target": target
            },
            timeout=10
        )

        # Debug info (remove later if you want)
        print("STATUS:", res.status_code)
        print("RESPONSE:", res.text)

        if res.status_code != 200:
            return f"API Error {res.status_code}: {res.text}"

        try:
            data = res.json()
            return data.get("translated", "")
        except ValueError:
            return f"Invalid JSON response: {res.text}"

    except requests.exceptions.RequestException as e:
        return f"Request failed: {str(e)}"