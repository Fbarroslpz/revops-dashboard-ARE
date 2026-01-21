# 📊 Estado del Proyecto RevOps Dashboard - ARE

**Fecha**: 21 de Enero 2026
**Status**: ✅ Fase 1 Completada - Pendiente configuración de Secret en GitHub

---

## ✅ Lo que hemos completado

### 1. Script de Extracción de Google Sheet ✅
- **Archivo**: `scripts/read_sheet_to_json.py`
- **Funcionalidad**:
  - Lee directamente el Google Sheet "Informe Diario ARE"
  - Busca automáticamente los datos de AYER (fecha actual - 1 día)
  - Extrae todas las métricas por setter (Daniela, Teresa, Matias, Robot)
  - Genera `data/latest.json` con la estructura correcta para el dashboard
- **Estado**: ✅ Completo y commiteado

### 2. GitHub Actions Workflow Simplificado ✅
- **Archivo**: `.github/workflows/daily-extract.yml`
- **Funcionalidad**:
  - Se ejecuta diariamente a las 07:00 AM Chile (11:00 UTC)
  - También se puede ejecutar manualmente desde GitHub Actions UI
  - Instala dependencias Python
  - Ejecuta el script de extracción
  - Commitea y pushea `latest.json` automáticamente
  - Limpia credenciales sensibles después de la ejecución
  - Sube logs como artefactos para debugging
- **Estado**: ✅ Workflow simplificado y commiteado

### 3. Estructura de Datos ✅
- **Google Sheet identificado**:
  - Sheet ID: `1E15l2Ac6EJsMEWS5SaOJnQHkNs6VQISBF1XfZ4NfrK4`
  - Sheet Name: "ACT comercial"
  - Estructura mapeada (fila por fila)
- **Formato de salida**: JSON con estructura completa por setter
- **Estado**: ✅ Completamente documentado

### 4. Service Account Configurado ✅
- **Email**: `revops-dashboard-are@gen-lang-client-0049746107.iam.gserviceaccount.com`
- **Archivo**: `config/google_credentials.json` (en .gitignore)
- **Estado**: ✅ Credenciales disponibles localmente

---

## ⏳ Pendiente (Requiere acción manual)

### 1. Configurar GitHub Secret 🔴 URGENTE
**Qué hacer**: Seguir las instrucciones en `SETUP_GITHUB_SECRET.md`

**Resumen rápido**:
1. Ve a: https://github.com/Fbarroslpz/revops-dashboard-ARE/settings/secrets/actions
2. Crea un nuevo secret:
   - Name: `GOOGLE_SERVICE_ACCOUNT`
   - Value: Todo el contenido de `config/google_credentials.json`
3. Guarda el secret

**Por qué es necesario**: El workflow de GitHub Actions necesita este secret para autenticarse con Google Sheets API.

### 2. Ejecutar el Workflow por Primera Vez 🔴 URGENTE
**Qué hacer**:
1. Ve a: https://github.com/Fbarroslpz/revops-dashboard-ARE/actions
2. Selecciona "📊 Extracción Diaria de Datos - RevOps ARE"
3. Click en "Run workflow"
4. Ejecutar

**Resultado esperado**:
- Se generará `data/latest.json` con datos reales del Google Sheet
- Se creará un commit automático: `🤖 Update: latest.json con datos del 20/01/2026`

### 3. Deploy en Vercel ⚪ PRÓXIMO
**Estado**: Pendiente hasta que latest.json tenga datos reales

**Qué hacer**:
1. Conectar el repositorio de GitHub con Vercel
2. Configurar el build:
   - Framework Preset: Other
   - Root Directory: `dashboard`
3. Deploy

**URL esperada**: `https://revops-dashboard-are.vercel.app`

---

## 🔄 Cambios Principales vs. Plan Original

### Antes (Plan Original):
- Extraer datos de HubSpot API
- Extraer datos de Google Calendar
- Generar JSON
- Actualizar Google Sheet
- Desplegar dashboard

### Ahora (Enfoque Simplificado):
1. ✅ **Leer Google Sheet** (que tú actualizas manualmente)
2. ✅ **Generar latest.json** para el dashboard
3. ⏳ **Desplegar dashboard** (Vercel)
4. 🔮 **Futuro**: Automatizar HubSpot/Calendar (cuando lo necesites)

**Razón del cambio**: Tú pediste priorizar la visualización de los datos existentes del Google Sheet, ya que solo te toma 5 minutos al día actualizarlo manualmente. La automatización completa con HubSpot puede venir después.

---

## 📈 Próximos Pasos

1. **TÚ**: Configurar el secret `GOOGLE_SERVICE_ACCOUNT` en GitHub (ver `SETUP_GITHUB_SECRET.md`)
2. **TÚ**: Ejecutar el workflow manualmente por primera vez
3. **VERIFICAR**: Que `latest.json` tenga datos reales
4. **YO**: Hacer deploy en Vercel
5. **VERIFICAR**: Que el dashboard muestre los datos correctamente

---

## 📝 Archivos Importantes

- ✅ `scripts/read_sheet_to_json.py` - Script principal de extracción
- ✅ `.github/workflows/daily-extract.yml` - Workflow automatizado
- ✅ `SETUP_GITHUB_SECRET.md` - Instrucciones para configurar el secret
- ✅ `config/google_credentials.json` - Credenciales del Service Account (NO en git)
- ⏳ `data/latest.json` - Datos para el dashboard (se generará después del workflow)
- ✅ `dashboard/index.html` - Dashboard web (listo para deployment)

---

## 🎯 Estado del Objetivo Principal

**Objetivo**: Visualizar los datos del Google Sheet en un dashboard online mejor que Looker Studio

**Progreso**:
- ✅ Script de lectura de Google Sheet: **100%**
- ✅ Workflow automatizado: **100%**
- ⏳ Configuración de Secret: **0%** (requiere acción manual)
- ⏳ Generación de datos reales: **0%** (depende de ejecutar workflow)
- ⏳ Deploy del dashboard: **0%** (esperando datos reales)

**Bloqueadores actuales**:
- Necesitas configurar el secret `GOOGLE_SERVICE_ACCOUNT` en GitHub
- Una vez configurado, ejecutar el workflow manualmente

**Tiempo estimado para completar**: 5-10 minutos una vez que configures el secret
