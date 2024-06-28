import webbrowser
import html

class ThreadAPI:

    API_BASE_URL: str = "https://graph.threads.net"
    REDIRECT_URI: str = "https://threads-sample.meta:5000/callback"
    AUTH_URL: str = "https://threads.net/oauth/authorize"

    AUTH_CODE: str | None = None
    SHORT_LIVED_TOKEN: str | None = None
    LONG_LIVED_TOKEN: str | None = None

    SCOPES: str = "threads_basic,threads_content_publish"

    USER_ID: int = 0

    def __init__(self, client_id: str, client_secret: str):
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.REDIRECT_URI = html.escape(self.REDIRECT_URI)

        print(f"Client ID: {self.CLIENT_ID}")
        print(f"Client Secret: {self.CLIENT_SECRET}")
        print(f"Redirect URI: {self.REDIRECT_URI}")

    def get_auth_url(self) -> str:
        """Generate the authorization URL to start the OAuth process."""
        url = (f"{self.AUTH_URL}?client_id={self.CLIENT_ID}"
               f"&redirect_uri={self.REDIRECT_URI}"
               f"&scope={self.SCOPES}"
               f"&response_type=code")
        return url

    def open_auth_page(self):
        """Open the authorization page in the default web browser."""
        url = self.get_auth_url()
        webbrowser.open(url)
        print("Please navigate to the provided URL to authorize this application.")

# Example usage
api = ThreadAPI('CLIENT_ID', 'CLIENT_SECRET')
api.open_auth_page()
