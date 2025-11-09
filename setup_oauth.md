# Setup Google OAuth pentru CoolBits.ai

## 1. Configurare Google Cloud Console

### Pasul 1: Accesează Google Cloud Console
1. Mergi la https://console.cloud.google.com/
2. Selectează proiectul `coolbits-ai`

### Pasul 2: Activează Google+ API
1. Mergi la "APIs & Services" > "Library"
2. Caută "Google+ API" sau "Google Identity"
3. Activează API-ul

### Pasul 3: Creează OAuth 2.0 Credentials
1. Mergi la "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Selectează "Web application"
4. Configurează:
   - **Name**: `CoolBits.ai OAuth Client`
   - **Authorized JavaScript origins**:
     ```
     https://ogpt-bridge-service-271190369805.europe-west1.run.app
     https://coolbits.ai
     https://www.coolbits.ai
     ```
   - **Authorized redirect URIs**:
     ```
     https://ogpt-bridge-service-271190369805.europe-west1.run.app/api/auth/callback/google
     https://coolbits.ai/api/auth/callback/google
     https://www.coolbits.ai/api/auth/callback/google
     ```

### Pasul 4: Salvează Credentials
1. Click "Create"
2. Salvează **Client ID** și **Client Secret**

## 2. Setare Variabile de Mediu în Cloud Run

### Pasul 1: Setează variabilele de mediu
```bash
gcloud run services update ogpt-bridge-service \
  --region=europe-west1 \
  --set-env-vars="GOOGLE_CLIENT_ID=YOUR_CLIENT_ID,GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET,NEXTAUTH_SECRET=YOUR_RANDOM_SECRET,DATABASE_URL=YOUR_DATABASE_URL"
```

### Pasul 2: Generează NEXTAUTH_SECRET
```bash
openssl rand -base64 32
```

## 3. Testare

După configurare, testează:
1. Mergi la https://ogpt-bridge-service-271190369805.europe-west1.run.app/auth/signin
2. Încearcă să te conectezi cu Google
3. Ar trebui să funcționeze fără erori

## 4. Note Importante

- **NEXTAUTH_SECRET**: Trebuie să fie același pentru toate instanțele
- **Redirect URIs**: Trebuie să includă toate domeniile pe care va rula aplicația
- **HTTPS**: Google OAuth necesită HTTPS pentru producție
