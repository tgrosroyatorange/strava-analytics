import requests
import webbrowser
from urllib.parse import urlparse, parse_qs

# Remplacez par vos vraies valeurs
CLIENT_ID = "VOTRE_CLIENT_ID"
CLIENT_SECRET = "VOTRE_CLIENT_SECRET"

# Étape 1: Autorisation
auth_url = f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=read,activity:read"

print("1. Ouvrez cette URL dans votre navigateur :")
print(auth_url)
print("\n2. Autorisez l'application")
print("3. Copiez l'URL complète de redirection ici :")

# L'utilisateur colle l'URL de redirection
redirect_url = input("URL de redirection : ")

# Extraire le code
parsed_url = urlparse(redirect_url)
code = parse_qs(parsed_url.query)['code'][0]

# Étape 2: Échanger le code contre un token
token_url = "https://www.strava.com/oauth/token"
payload = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'code': code,
    'grant_type': 'authorization_code'
}

response = requests.post(token_url, data=payload)
token_data = response.json()

print("\n=== TOKENS À SAUVEGARDER ===")
print(f"ACCESS_TOKEN: {token_data['access_token']}")
print(f"REFRESH_TOKEN: {token_data['refresh_token']}")
print("===============================")
