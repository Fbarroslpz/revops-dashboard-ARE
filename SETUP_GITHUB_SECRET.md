# 🔐 Configurar GitHub Secret para Service Account

## Paso 1: Copiar las credenciales

Las credenciales del Service Account están en: `config/google_credentials.json`

Contenido completo (copiar TODO desde la primera llave hasta la última):
```json
{
  "type": "service_account",
  "project_id": "gen-lang-client-0049746107",
  "private_key_id": "1c0a65699c2999bcbf79c9c13e4acf76e8f3539e",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCO7T46bc94r4Cc\n0ihGzitSrAm4IyQeQ7cubYNb/bqMgKGiI1jBEaqJ0lgLJnoQqHKcaJLB4Ray18Zb\nB1BjkI03TGlZLPGypeXnXWHSikzyPIVf91Zzh1Mhdeq6cFLA1yLKW56FqlmY/q2k\n3TMKGaLwhYrsRx0Vsu/LrhJLv5aBqtJ6YXkxjQw8RhcB2tgyiuWvuZvuSr35hv25\nK0OWDAezM2YFOp7rfVjQnz1QpXj9+FblS+U0guDiVHMkIUfTnCDF6N5S/HM0pwjN\nfeVGxE611z2ZbVpVJUa3WAteBAa17bG+EjtjVZiET0ysf6IGwfPXI2XRRbMCd+H0\n9eQqF8g1AgMBAAECggEACNKZREcSBwuiX0vTw6cnYnePNAgrSxj3/kwxTyTm9pRc\nJeOTr3tVMSPEXo/V+iBDzubfpEsuOQT70BOwAS1jojW7zQ7qrpHyEqmfh70UyeE1\nhHqCoigI2ChswGx9lzzQf3hPXUXqOPkDpAkphOaXOcysijBLmdLNXZ/VrkpZ0pAu\nv5am4J4Z/DyziFt5lEnSoVSKtXCLvi69Bna47060Rhx2Vi3V+2teLoc8Uh0bkaqJ\nSPGAOMXDIJj14/t4EtNWUUeZf0wKu133w+36P+U/Ko2xjscmhGZg5PS/E/WG0kWM\n1YmjUDz/Mjg2KOC+IKz58E6xvAeGY+WpVTpO8CKoMwKBgQDJOehq/HUplYXrkm9U\n2v/3uiovWk6j7sFfI/EklTwog9lF8Y0t2M5T8boAlDJu47RdoKWWhDVC5BzpGKig\nIjLMqtDt0xjbmWOcALMP2gQNrO4Lumt56loXZghpsvJIV9Ey6221We3/FDohygn/\nWMdz1zLTrp1UKmcuIzBTXMihPwKBgQC11NbvDnZK+p3i6ZT3MPrITD5Dy49wJuaz\nrI/PFBJv+1IfqBccAh0ewkQy37uMB/iL/AyW38OsNVQUUM27UqeunulQ6dlm+z8t\nRe1HRh5hIWjCuKV4CIaycdQC8tKKZU0+/8t7YcF+NrGCRNWxxu+byx++WqTtQtDO\nd6bdP34FiwKBgQC8Tk16ONAnXv5YycsXfG2G1Jb/gyIOdLJOpyLVmjYWr/PWaUo1\neirzEUV/ny9m5/10lI4Awa3Z8ABB/cpnODmTn9IujJo5flxhs6HdlqauaYLGROio\nyS8PsHL0/vmNy2hAn2ImEIcQakxQLHKYmurjM6Ijx8cA6UFvQozJpg02HwKBgEza\nbQ4VmsIOM3WZLLFeLmFCeH7HJxVMG+6NXSs1XKWgIBHpRfs8mXpKufCWx/pj1BW2\nrsuGQHolACimDo7CXMVdvVfJv23be9Ry3dtmM6jyKglDagzV7bi2i9nDMGH2dzPN\ngf/gTZw/Gb/pwDin0NaUgBJA1bzCpObfg9O35lgJAoGAGvEtCO7N3JWOLqfTziIT\nuox15hIQBKB/EBR3Co5/kBoSkTujjjwV4TqyGmObE29UHq8WUyob7bM8akjGaYsp\nGEjA4OcvyyRxVBWI6eMTNuwSypX8A7g+cAJ6qBFCnS9d+NMCBMTQjgcoJyx6cOfg\nEYz5zvRvV2aY8h8NutEGiUA=\n-----END PRIVATE KEY-----\n",
  "client_email": "revops-dashboard-are@gen-lang-client-0049746107.iam.gserviceaccount.com",
  "client_id": "105070908778499162937",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/revops-dashboard-are%40gen-lang-client-0049746107.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
```

## Paso 2: Ir a GitHub Secrets

1. Ve a: https://github.com/Fbarroslpz/revops-dashboard-ARE/settings/secrets/actions
2. Haz clic en **"New repository secret"**

## Paso 3: Crear el Secret

- **Name**: `GOOGLE_SERVICE_ACCOUNT`
- **Value**: Pega todo el contenido JSON de arriba (desde `{` hasta `}`)
- Haz clic en **"Add secret"**

## Paso 4: Ejecutar el Workflow manualmente

1. Ve a: https://github.com/Fbarroslpz/revops-dashboard-ARE/actions
2. Haz clic en **"📊 Extracción Diaria de Datos - RevOps ARE"** en el listado de workflows
3. Haz clic en el botón **"Run workflow"** (botón azul)
4. Deja el valor por defecto (1 día atrás)
5. Haz clic en **"Run workflow"**

## Paso 5: Verificar la ejecución

1. Después de unos segundos, aparecerá una nueva ejecución en la lista
2. Haz clic en ella para ver los logs en tiempo real
3. Si todo funciona correctamente, verás:
   - ✅ Extracción completada
   - El contenido de latest.json con datos reales del Google Sheet
   - Un commit automático con el nuevo latest.json

## ¿Qué hace el workflow?

1. **Descarga el repositorio**
2. **Instala Python y dependencias**
3. **Configura las credenciales del Service Account** (desde el Secret)
4. **Ejecuta `scripts/read_sheet_to_json.py`**:
   - Lee el Google Sheet "Informe Diario ARE"
   - Busca los datos de AYER
   - Genera `data/latest.json` con los datos
5. **Commitea y pushea** el nuevo latest.json al repositorio
6. **Limpia las credenciales** (seguridad)
7. **Sube los logs** como artefactos para debugging

---

## 🎯 Resultado esperado

Después de ejecutar el workflow, deberías ver un nuevo commit en el repositorio con el mensaje:
```
🤖 Update: latest.json con datos del 20/01/2026
```

Y el archivo `data/latest.json` tendrá datos reales del Google Sheet, como:
```json
{
  "fecha": "2026-01-20",
  "leads_creados": 87,
  "reuniones": {
    "Daniela": {
      "agendadas": 12,
      "realizadas": 12,
      "llamadas": 73
    },
    ...
  }
}
```
