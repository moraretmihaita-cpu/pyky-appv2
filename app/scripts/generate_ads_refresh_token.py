from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/adwords"]

flow = InstalledAppFlow.from_client_secrets_file(
    "oauth_client.json",
    SCOPES,
)

creds = flow.run_local_server(port=0)

print("\n=== GOOGLE ADS TOKENS ===")
print(f"client_id: {creds.client_id}")
print(f"client_secret: {creds.client_secret}")
print(f"refresh_token: {creds.refresh_token}")
print(f"token: {creds.token}")