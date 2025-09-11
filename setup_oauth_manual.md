# Setup Manual Google OAuth pentru CoolBits.ai

## Pasul 1: Accesează Google Cloud Console

1. Mergi la https://console.cloud.google.com/
2. Autentifică-te cu `coolbits.ro@gmail.com`
3. Selectează proiectul `coolbits-ai`

## Pasul 2: Activează Google+ API

1. Mergi la "APIs & Services" > "Library"
2. Caută "Google+ API" sau "Google Identity"
3. Activează API-ul dacă nu este deja activat

## Pasul 3: Creează OAuth 2.0 Credentials

1. Mergi la "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Dacă nu ai OAuth consent screen configurat:
   - Click "Configure Consent Screen"
   - Selectează "External"
   - Completează informațiile de bază:
     - App name: `CoolBits.ai`
     - User support email: `coolbits.ro@gmail.com`
     - Developer contact information: `coolbits.ro@gmail.com`
   - Click "Save and Continue" pentru toate secțiunile
   - Click "Back to Dashboard"

4. Acum creează OAuth Client:
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Selectează "Web application"
   - Name: `CoolBits.ai OAuth Client`
   - Authorized JavaScript origins:
     ```
     https://ogpt-bridge-service-271190369805.europe-west1.run.app
     https://coolbits.ai
     https://www.coolbits.ai
     ```
   - Authorized redirect URIs:
     ```
     https://ogpt-bridge-service-271190369805.europe-west1.run.app/api/auth/callback/google
     https://coolbits.ai/api/auth/callback/google
     https://www.coolbits.ai/api/auth/callback/google
     ```
   - Click "Create"

## Pasul 4: Salvează Credentials

1. Copiază **Client ID** și **Client Secret**
2. Salvează-le într-un loc sigur

## Pasul 5: Setează Variabilele de Mediu în Cloud Run

```bash
gcloud run services update ogpt-bridge-service \
  --region=europe-west1 \
  --set-env-vars="GOOGLE_CLIENT_ID=YOUR_CLIENT_ID,GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET,NEXTAUTH_SECRET=ASsuJDYbw2BgUjuZm84m/wXdkuJz2lqZI8xmcUtrMUg="
```

## Pasul 6: Testează

1. Mergi la https://ogpt-bridge-service-271190369805.europe-west1.run.app/auth/signin
2. Încearcă să te conectezi cu Google
3. Ar trebui să funcționeze fără erori

## Note Importante

- **Client Secret**: Nu îl partaja niciodată public
- **Redirect URIs**: Trebuie să fie exacte, inclusiv protocolul (https://)
- **HTTPS**: Google OAuth necesită HTTPS pentru producție
- **Test Users**: Pentru testare, poți adăuga email-urile tale ca "Test Users" în OAuth consent screen
