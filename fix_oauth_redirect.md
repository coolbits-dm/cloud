# Fix OAuth Redirect URI Mismatch

## Problema
Eroarea `redirect_uri_mismatch` înseamnă că URL-ul de redirect nu se potrivește cu cel configurat în Google Cloud Console.

## Soluția

### Pasul 1: Verifică URL-ul exact
NextAuth folosește acest URL pentru callback:
```
https://ogpt-bridge-service-271190369805.europe-west1.run.app/api/auth/callback/google
```

### Pasul 2: Actualizează Google Cloud Console

1. Mergi la https://console.cloud.google.com/
2. Selectează proiectul `coolbits-ai`
3. Mergi la "APIs & Services" > "Credentials"
4. Click pe OAuth 2.0 Client ID-ul tău
5. În secțiunea "Authorized redirect URIs", asigură-te că ai:
   ```
   https://ogpt-bridge-service-271190369805.europe-west1.run.app/api/auth/callback/google
   ```
6. Click "Save"

### Pasul 3: Testează din nou
După salvare, încearcă să te conectezi din nou la:
https://ogpt-bridge-service-271190369805.europe-west1.run.app/auth/signin

## Note Importante
- URL-ul trebuie să fie exact, inclusiv protocolul (https://)
- Nu adăuga slash la sfârșit
- Asigură-te că nu ai spații în URL
