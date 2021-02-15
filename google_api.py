# import google.oauth2.credentials
import google_auth_oauthlib.flow

SCOPES = ['https://www.googleapis.com/auth/presentations.readonly']

client_config = {
    "web": {"client_id": "",
            "project_id": "",
            "auth_uri": "",
            "token_uri": "",
            "auth_provider_x509_cert_url": "",
            "client_secret": "",
            "javascript_origins": [""]
            }
}

# Use the client_secret.json file to identify the application requesting
# authorization. The client ID (from that file) and access scopes are required.
flow = google_auth_oauthlib.flow.Flow.from_client_config(
    client_config=client_config,
    scopes=SCOPES)

# Indicate where the API server will redirect the user after the user completes
# the authorization flow. The redirect URI is required. The value must exactly
# match one of the authorized redirect URIs for the OAuth 2.0 client, which you
# configured in the API Console. If this value doesn't match an authorized URI,
# you will get a 'redirect_uri_mismatch' error.
flow.redirect_uri = 'https://www.example.com/oauth2callback'

# Generate URL for request to Google's OAuth 2.0 server.
# Use kwargs to set optional request parameters.
authorization_url, state = flow.authorization_url(
    # Enable offline access so that you can refresh an access token without
    # re-prompting the user for permission. Recommended for web server apps.
    access_type='offline',
    # Enable incremental authorization. Recommended as a best practice.
    include_granted_scopes='true')


print(authorization_url)


# Success Response

"""
A partir daqui é possivel pegar o code e gerar o Token, que pode ser salvo
em alguma tabela do cliente ou não (vou pensar)

https://www.example.com/oauth2callback?
state=7tHk3Mfv8XQzZHh9fofUy74w8oJNwA &
code=4/0AY0e-g6a2AgYG3SYVFQ9nkI9Qj6tGdBDiYkwy_nWeDZfA8NHZOs3AgrZ3AMJSUVnCld9eQ &
scope=https://www.googleapis.com/auth/presentations.readonly
"""
