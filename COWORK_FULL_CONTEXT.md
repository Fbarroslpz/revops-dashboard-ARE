# 📋 PROYECTO REVOPS DASHBOARD - ARE (ADVISOR REAL ESTATE)

## 🎯 CONTEXTO DEL NEGOCIO

**Cliente:** Felipe Barros (fbarroslpz@gmail.com)  
**Empresa:** Advisor Real Estate (ARE) - Venta inmobiliaria en Chile  
**Cargo:** RevOps / Operaciones  
**CRM:** HubSpot Standard (Account ID: 50226191)

### Equipo de Ventas:
- **3 Setters humanos:** Daniela Sepúlveda, Teresa Ceballos, Matias Medel
- **1 Bot (Robot GoA):** Asistente automatizado de agendamiento
- **3 Brokers:** Tomás, Antonia, Treicy (gestionan reuniones agendadas por setters)

### Arquitectura CRM Actual (IMPORTANTE - No cambiar):
- **NO hay ownership de leads** → Es intencional, múltiples setters pueden contactar el mismo lead
- Atribución por actividad registrada, NO por propiedad
- Deals se cargan semanalmente por operaciones (lag de ~7 días)
- Los brokers cambian el color de las reuniones en el calendario según el resultado

### Sistemas en uso:
1. **HubSpot**: Leads, estados, actividades, llamadas
2. **Google Calendar** (tomas@advisorrealestate.cl): Reuniones agendadas/realizadas
   - Los setters crean eventos con sus colores asignados
   - Los brokers (Tomás, Antonia, Treicy) cambian el color a naranjo/rojo si el cliente no se presenta
3. **WhatsApp**: Reservas y estados post-reserva
4. **Google Sheets**: 
   - "Informe Diario ARE" (ID: 1E15l2Ac6EJsMEWS5SaOJnQHkNs6VQISBF1XfZ4NfrK4)
   - Hoja específica: "ACT comercial"
   - "Archivo Looker" (ID: 1Xsj3BFUand7o1XXiZf-1HI77iu6ysd6rstQXX1tFpME)

### Problema a Resolver:
**ANTES:** 45-60 minutos/día de trabajo manual:
- Copiar métricas de HubSpot a Excel
- Revisar Calendar reunión por reunión y contar manualmente
- Procesar datos de WhatsApp
- Calcular CPL, show-up rates, conversiones a mano
- Generar reportes

**OBJETIVO:** Automatizar TODO lo automatizable, dejando solo datos de WhatsApp para ingreso manual.

---

## 🏗️ ARQUITECTURA DE LA SOLUCIÓN

### Flujo de Datos Completo:

```
FUENTES DE DATOS AUTOMÁTICAS:
├── HubSpot API
│   ├── Leads creados por día
│   ├── Llamadas por setter
│   ├── Actividades registradas
│   └── Distribución de estados
│
└── Google Calendar (iCal público - tomas@advisorrealestate.cl)
    ├── URL: https://calendar.google.com/calendar/ical/tomas%40advisorrealestate.cl/public/basic.ics
    ├── Identificación de setter por COLOR + TÍTULO
    ├── Los setters crean eventos con sus colores
    └── Los brokers (Tomás, Antonia, Treicy) cambian color según resultado:
        ├── Mantienen color original = Cliente SÍ asistió
        └── Cambian a naranjo/rojo = Cliente NO asistió (no-show)

         ↓
         
PROCESAMIENTO (Scripts Python en GitHub Actions):
├── calendar_extractor.py → Lee iCal, identifica setters, detecta shows/no-shows
├── main_extractor.py → Orquesta HubSpot + Calendar
└── sheet_updater.py → Actualiza Google Sheet automáticamente

         ↓
         
ALMACENAMIENTO:
├── data/latest.json → Último día procesado (usado por dashboard)
├── data/extracted_YYYYMMDD.json → Histórico diario
└── Google Sheet "Informe Diario ARE" → Actualizado automático

         ↓
         
VISUALIZACIÓN:
└── Dashboard Web (Vercel - Público online)
    ├── Lee latest.json desde GitHub
    ├── Visualiza métricas con Chart.js
    ├── Gráficos de reuniones por setter
    ├── Show-up rates
    └── Auto-refresh cada 5 minutos
```

### Automatización Diaria:

```
07:00 AM Santiago (11:00 UTC)
    ↓
GitHub Actions ejecuta workflow automáticamente
    ↓
Scripts extraen:
├── HubSpot API → Leads creados el día anterior
└── Google Calendar iCal → Reuniones del día anterior
    ↓
Identifica para cada reunión:
├── ¿Quién agendó? (Daniela/Teresa/Matias/Robot por color + título)
└── ¿Se realizó? (color original = SÍ, naranjo/rojo = NO)
    ↓
Genera data/latest.json
    ↓
Actualiza Google Sheet (solo filas automáticas)
    ↓
Commit a GitHub
    ↓
Vercel detecta cambio automáticamente
    ↓
Dashboard se redeploya y actualiza
    ↓
09:00 AM - Felipe revisa dashboard YA actualizado
    ↓
Felipe ingresa SOLO datos manuales (5-8 min):
├── Reservas confirmadas (desde WhatsApp)
└── Inversión en campañas (incluye agencia Zapier)
    ↓
LISTO - Reporte completo en 8 minutos vs 60 minutos antes
```

---

## 🎨 LÓGICA DE IDENTIFICACIÓN DE CALENDAR (CRÍTICO)

### Contexto del Proceso:
1. **Los setters** (Daniela, Teresa, Matias, Robot) **crean eventos** en el calendario
2. Cada setter usa un **color específico** para sus eventos
3. **Los brokers** (Tomás, Antonia, Treicy) ejecutan las reuniones
4. **Después de la reunión**, el broker cambia el color del evento:
   - Si el cliente **SÍ asistió** → Mantiene el color original del setter
   - Si el cliente **NO asistió** (no-show) → Cambia a naranjo o rojo

### Mapeo de Colores Google Calendar:

**IMPORTANTE:** Los colorId de Google Calendar son:

```yaml
color_mapping:
  "2": "Daniela"    # Verde/Salvia
  "8": "Teresa"     # Negro/Grafito
  "9": "Azul"       # Azul/Arándano (puede ser Matias O Robot)

no_show_colors:
  - "6"   # Mandarina (naranjo) - Cliente NO asistió
  - "11"  # Tomate (rojo) - Cliente NO asistió
```

### Lógica de Identificación de Setter:

```python
def identify_setter(title: str, color_id: str) -> str:
    """
    REGLAS DE IDENTIFICACIÓN:
    
    1. Si color == "2" (Verde) → SIEMPRE Daniela
    2. Si color == "8" (Negro) → SIEMPRE Teresa
    3. Si color == "9" (Azul):
       a. Si título empieza con "Asesoría Inmobiliaria" → Robot
       b. Si título contiene "reunion" (case insensitive) → Matias
       c. Default → Matias
    4. Cualquier otro color → "Desconocido" (loggear warning)
    
    IMPORTANTE: El color puede haber cambiado DESPUÉS de la reunión,
    pero el título se mantiene. Usamos AMBOS para identificar al setter original.
    """
```

### Lógica de Estado de Reunión:

```python
def is_completed(color_id: str) -> bool:
    """
    REGLAS DE COMPLETITUD (acción de los brokers):
    
    1. Si color == "6" (Naranjo/Mandarina) → NO REALIZADA (broker lo marcó)
    2. Si color == "11" (Rojo/Tomate) → NO REALIZADA (broker lo marcó)
    3. Si mantiene color original (2, 8, 9) → REALIZADA
    
    Explicación del flujo:
    - Setter crea evento con su color (2=Daniela, 8=Teresa, 9=Matias/Robot)
    - Broker (Tomás/Antonia/Treicy) ejecuta la reunión
    - Si cliente NO asiste → Broker cambia color a 6 o 11
    - Si cliente SÍ asiste → Broker deja color original
    
    Por eso verificamos: color actual == color de no-show?
    """
```

### Ejemplos de Identificación:

| Título Evento | Color Inicial | Color Final | Setter | Completada | Cambió Broker |
|---------------|---------------|-------------|--------|------------|---------------|
| "Reunion - Juan Pérez" | 2 (Verde) | 2 (Verde) | Daniela | ✅ SÍ | No |
| "Reunion - María López" | 2 (Verde) | 6 (Naranjo) | Daniela | ❌ NO | Sí |
| "Reunion - Carlos Soto" | 8 (Negro) | 8 (Negro) | Teresa | ✅ SÍ | No |
| "Reunion - Ana Torres" | 8 (Negro) | 11 (Rojo) | Teresa | ❌ NO | Sí |
| "Asesoría Inmobiliaria con Pedro" | 9 (Azul) | 9 (Azul) | Robot | ✅ SÍ | No |
| "Asesoría Inmobiliaria con Luis" | 9 (Azul) | 6 (Naranjo) | Robot | ❌ NO | Sí |
| "Reunion - Diego Rojas" | 9 (Azul) | 9 (Azul) | Matias | ✅ SÍ | No |
| "Reunion - Sofia Vargas" | 9 (Azul) | 11 (Rojo) | Matias | ❌ NO | Sí |

**Nota importante:** Aunque el broker haya cambiado el color, seguimos identificando al setter original por el título + color inicial implícito en el patrón.

---

## 📊 ACTUALIZACIÓN DE GOOGLE SHEET

### Estructura del Sheet "Informe Diario ARE":

**Hoja:** "ACT comercial"

**Mapeo de Filas (estructura aproximada basada en conversación):**

```
Fila 2: Fechas (columnas dinámicas por día)

SECCIÓN: REUNIONES TOTALES
Fila 3: Reuniones agendadas (TOTAL del día) → AUTOMÁTICO ✅
Fila 4: Reuniones realizadas (TOTAL del día) → AUTOMÁTICO ✅
Fila 5: Clientes con reserva → MANUAL ❌ (Felipe ingresa desde WhatsApp)
Fila 6: Reservas confirmadas → MANUAL ❌ (Felipe ingresa desde WhatsApp)

SECCIÓN: ACTIVIDAD POR SETTER
Filas 10-19: Actividad individual por setter
├── Fila 11: Daniela - Reuniones agendadas → AUTOMÁTICO ✅
├── Fila 13: Teresa - Reuniones agendadas → AUTOMÁTICO ✅
├── Fila 15: Matias - Reuniones agendadas → AUTOMÁTICO ✅
├── Fila 17: Robot - Reuniones agendadas → AUTOMÁTICO ✅

SECCIÓN: LEADS E INVERSIÓN
Fila 21: Leads creados → AUTOMÁTICO ✅ (desde HubSpot)
Fila 24: Inversión en campañas → MANUAL ❌ (Felipe - incluye HubSpot + agencia Zapier)
Fila 25: CPL (Costo Por Lead) → FÓRMULA ⚙️ (se calcula automático: Inversión/Leads)
```

**IMPORTANTE:** 
- El sheet está compartido públicamente con acceso Editor
- Email con acceso: dixolivos@gmail.com (Editor)
- URL pública: cualquiera con el enlace puede editar
- Para automatización vía GitHub Actions, opcionalmente se puede usar Google Service Account

---

## 🔐 CREDENCIALES Y CONFIGURACIÓN

### HubSpot API:
```
API Key: 0cf231a2-b2a3-4958-aeca-d487f3514e6b
Account ID: 50226191

Permisos requeridos:
├── crm.objects.contacts.read
└── crm.objects.deals.read

URL API Key: https://app.hubspot.com/settings/50226191/integrations/api
```

### Google Calendar:
```
Calendar ID: tomas@advisorrealestate.cl
iCal URL (público): https://calendar.google.com/calendar/ical/tomas%40advisorrealestate.cl/public/basic.ics

Ventaja: NO requiere autenticación (feed público)
Proceso: 
  - Setters crean eventos con sus colores
  - Brokers (Tomás, Antonia, Treicy) cambian colores según resultado
```

### Google Sheets:
```
Informe Diario: 1E15l2Ac6EJsMEWS5SaOJnQHkNs6VQISBF1XfZ4NfrK4
Archivo Looker: 1Xsj3BFUand7o1XXiZf-1HI77iu6ysd6rstQXX1tFpME
Hoja activa: ACT comercial

Acceso público: Editor (cualquiera con enlace)
Email con acceso: dixolivos@gmail.com (Editor)
```

### GitHub:
```
Repo: Crear como PRIVADO (contiene API keys)
Nombre sugerido: revops-dashboard-are
Owner: Usuario de GitHub de Felipe

Secret necesario:
├── HUBSPOT_API_KEY: 0cf231a2-b2a3-4958-aeca-d487f3514e6b
└── GOOGLE_SERVICE_ACCOUNT: (JSON completo - opcional pero recomendado)
```

### Vercel:
```
Framework: Other (sitio estático)
Root Directory: ./
Output Directory: dashboard
Auto-deploy: Activado (detecta cambios en GitHub)
```

---

## 📁 ESTRUCTURA DE ARCHIVOS DEL PROYECTO

**Ubicación actual:** `/Users/felipebarros/Desktop/revops-dashboard-ARE`

```
revops-dashboard-ARE/
│
├── .github/
│   └── workflows/
│       └── daily-extract.yml          # GitHub Actions - Cron diario 07:00 Santiago
│
├── config/
│   └── config.yaml                     # Configuración (API keys, IDs, colores)
│
├── scripts/
│   ├── calendar_extractor.py          # Extrae Google Calendar vía iCal
│   │                                   # Identifica setter por color + título
│   │                                   # Detecta shows/no-shows por color final
│   ├── main_extractor.py               # Orquesta HubSpot + Calendar
│   ├── sheet_updater.py                # Actualiza Google Sheet automáticamente
│   └── verify_setup.py                 # Verificador de configuración
│
├── dashboard/
│   └── index.html                      # Dashboard web con Chart.js
│                                       # Gráficos, métricas, visualizaciones
│
├── data/
│   ├── latest.json                     # Último día (usado por dashboard)
│   ├── extracted_YYYYMMDD.json         # Histórico por fecha
│   └── EJEMPLO_OUTPUT.json             # Ejemplo de estructura
│
├── logs/
│   ├── main_extraction.log             # Logs del script principal
│   └── calendar_extraction.log         # Logs del calendar
│
├── requirements.txt                    # Dependencias Python
├── vercel.json                         # Config de Vercel
├── .gitignore                          # Protege credenciales
├── README.md                           # Documentación general
├── DEPLOY_INSTRUCTIONS.md              # Pasos de deploy
└── DEPLOY_NOW.sh                       # Script de deploy automatizado
```

---

## 💻 CÓDIGO CLAVE - CONFIGURACIÓN

### config/config.yaml:
```yaml
# Configuración del proyecto RevOps Dashboard - ARE
# IMPORTANTE: No compartir este archivo públicamente

hubspot:
  api_key: "0cf231a2-b2a3-4958-aeca-d487f3514e6b"
  account_id: "50226191"

google_sheets:
  informe_diario_id: "1E15l2Ac6EJsMEWS5SaOJnQHkNs6VQISBF1XfZ4NfrK4"
  archivo_looker_id: "1Xsj3BFUand7o1XXiZf-1HI77iu6ysd6rstQXX1tFpME"
  worksheet_name: "ACT comercial"
  editor_email: "dixolivos@gmail.com"

google_calendar:
  calendar_id: "tomas@advisorrealestate.cl"
  ical_url: "https://calendar.google.com/calendar/ical/tomas%40advisorrealestate.cl/public/basic.ics"
  
  # Mapeo de colores (eventos creados por setters)
  color_mapping:
    "8": "Teresa"      # Negro/Grafito
    "2": "Daniela"     # Verde/Salvia
    "9": "Azul"        # Azul (Matias o Robot - distinguir por título)
  
  # Colores que indican NO-SHOW (cambiados por brokers)
  no_show_colors:
    - "6"   # Mandarina (naranjo) - Cliente no asistió
    - "11"  # Tomate (rojo) - Cliente no asistió
  
  # Patrones de título para distinguir Robot vs Matias (ambos usan azul)
  robot_title_pattern: "Asesoría Inmobiliaria"
  human_title_pattern: "Reunion"

extraction:
  timezone: "America/Santiago"
  days_back: 1  # Procesar día anterior

alerts:
  cpl_max: 6000
  show_up_rate_min: 0.60
  conversion_rate_min: 0.10
```

---

## 💻 CÓDIGO CLAVE - GITHUB ACTIONS

### .github/workflows/daily-extract.yml:
```yaml
name: Extracción Diaria de Datos

on:
  schedule:
    # Ejecuta a las 11:00 UTC = 07:00 Santiago
    - cron: '0 11 * * *'
  
  # Permite ejecución manual desde GitHub UI
  workflow_dispatch:

jobs:
  extract-and-update:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout código
        uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Instalar dependencias
        run: pip install -r requirements.txt
      
      - name: Crear configuración temporal
        env:
          HUBSPOT_API_KEY: ${{ secrets.HUBSPOT_API_KEY }}
        run: |
          cat > config/config.yaml << EOFCONFIG
          hubspot:
            api_key: "$HUBSPOT_API_KEY"
            account_id: "50226191"
          
          google_sheets:
            informe_diario_id: "1E15l2Ac6EJsMEWS5SaOJnQHkNs6VQISBF1XfZ4NfrK4"
            archivo_looker_id: "1Xsj3BFUand7o1XXiZf-1HI77iu6ysd6rstQXX1tFpME"
            worksheet_name: "ACT comercial"
          
          google_calendar:
            calendar_id: "tomas@advisorrealestate.cl"
            ical_url: "https://calendar.google.com/calendar/ical/tomas%40advisorrealestate.cl/public/basic.ics"
            color_mapping:
              "8": "Teresa"
              "2": "Daniela"
              "9": "Azul"
            no_show_colors:
              - "6"
              - "11"
            robot_title_pattern: "Asesoría Inmobiliaria"
            human_title_pattern: "Reunion"
          
          extraction:
            timezone: "America/Santiago"
            days_back: 1
          EOFCONFIG
      
      - name: Ejecutar extracción
        run: python scripts/main_extractor.py
      
      - name: Guardar datos
        run: |
          LATEST_FILE=$(ls -t data/extracted_*.json 2>/dev/null | head -1)
          if [ -f "$LATEST_FILE" ]; then
            cp "$LATEST_FILE" data/latest.json
            echo "✅ Datos guardados en data/latest.json"
          fi
      
      - name: Commit y push
        run: |
          git config --local user.email "actions@github.com"
          git config --local user.name "GitHub Actions"
          git add data/*.json
          git diff --quiet && git diff --staged --quiet || (git commit -m "📊 Datos $(date +'%Y-%m-%d')" && git push)
```

---

## 💻 DEPENDENCIAS

### requirements.txt:
```
# HubSpot API
requests==2.31.0

# Google Sheets
gspread==5.12.0
oauth2client==4.1.3

# Google Calendar (iCal)
icalendar==5.0.11
pytz==2023.3

# Configuración
pyyaml==6.0.1

# Data processing
pandas==2.1.4
numpy==1.26.2

# Dashboard web (opcional - solo si se implementa backend)
flask==3.0.0
plotly==5.18.0

# Utilidades
python-dateutil==2.8.2
```

---

## 💻 CONFIGURACIÓN VERCEL

### vercel.json:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "dashboard/**",
      "use": "@vercel/static"
    }
  ]
}
```

---

## 📊 MÉTRICAS TRACKEADAS

### Automáticas (extraídas por scripts):
| Métrica | Fuente | Target | Script | Descripción |
|---------|--------|--------|--------|-------------|
| Leads creados | HubSpot | - | main_extractor.py | Total de contactos nuevos del día |
| Reuniones agendadas total | Calendar | - | calendar_extractor.py | Suma de todas las reuniones del día |
| Reuniones realizadas total | Calendar | - | calendar_extractor.py | Reuniones donde cliente SÍ asistió |
| Reuniones Daniela | Calendar | - | calendar_extractor.py | Eventos con color verde (2) |
| Reuniones Teresa | Calendar | - | calendar_extractor.py | Eventos con color negro (8) |
| Reuniones Matias | Calendar | - | calendar_extractor.py | Eventos azul (9) + "Reunion" |
| Reuniones Robot | Calendar | - | calendar_extractor.py | Eventos azul (9) + "Asesoría Inmobiliaria" |
| Show-up rate total | Calendar | >70% | calendar_extractor.py | (Realizadas / Agendadas) × 100 |
| Show-up rate por setter | Calendar | >60% | calendar_extractor.py | Por cada setter individual |
| No-shows totales | Calendar | <30% | calendar_extractor.py | Eventos cambiados a naranjo/rojo |

### Manuales (Felipe ingresa):
- **Clientes con reserva** (desde WhatsApp) → Fila 5
- **Reservas confirmadas** (desde WhatsApp) → Fila 6
- **Inversión en campañas** (HubSpot + Agencia vía Zapier) → Fila 24

### Calculadas (fórmulas en Google Sheet):
- **CPL (Costo Por Lead)** = Inversión / Leads creados → Fila 25
- **Tasa de conversión Lead → Reunión**
- **Tasa de caída de reservas**

---

## 🎯 ESTADO ACTUAL DEL PROYECTO

### ✅ COMPLETADO:
1. ✅ Proyecto creado en `/Users/felipebarros/Desktop/revops-dashboard-ARE`
2. ✅ Scripts de extracción completos:
   - `calendar_extractor.py` (con lógica de colores correcta)
   - `main_extractor.py` (orquestador)
   - `sheet_updater.py` (actualización de Google Sheet)
3. ✅ GitHub Actions workflow configurado (cron diario 07:00)
4. ✅ Dashboard HTML con Chart.js
5. ✅ Configuración de Vercel lista
6. ✅ Git commit realizado (2 commits en master)
7. ✅ API Key de HubSpot configurada
8. ✅ Google Sheet compartido públicamente con acceso Editor
9. ✅ Lógica de identificación de setters por color + título implementada
10. ✅ Detección de reuniones completadas vs no-shows implementada
11. ✅ Información de 3 brokers actualizada (Tomás, Antonia, Treicy)

### ⚠️ PENDIENTE (TAREAS PARA COWORK):

#### TAREA 1: Crear repositorio en GitHub
```
1. Ir a: https://github.com/new
2. Nombre: revops-dashboard-are
3. Visibility: PRIVATE (contiene API keys)
4. NO inicializar con README
5. Crear repositorio
```

#### TAREA 2: Push del código a GitHub
```bash
cd /Users/felipebarros/Desktop/revops-dashboard-ARE

# Obtener username de GitHub de Felipe
# Agregar remote
git remote add origin https://github.com/USERNAME/revops-dashboard-are.git

# Renombrar branch a main
git branch -M main

# Push
git push -u origin main
```

#### TAREA 3: Configurar GitHub Secrets
```
Ir a: https://github.com/USERNAME/revops-dashboard-are/settings/secrets/actions

Secret 1:
  Name: HUBSPOT_API_KEY
  Value: 0cf231a2-b2a3-4958-aeca-d487f3514e6b

Secret 2 (opcional pero recomendado):
  Name: GOOGLE_SERVICE_ACCOUNT
  Value: [JSON completo del Service Account]
```

#### TAREA 4: Google Service Account (Opcional - 5 min)
```
Pasos detallados en sección "SETUP GOOGLE SERVICE ACCOUNT" más abajo
```

#### TAREA 5: Deploy en Vercel
```
1. Ir a: https://vercel.com/new
2. Import from GitHub → revops-dashboard-are
3. Framework: Other
4. Root Directory: ./
5. Output Directory: dashboard
6. Deploy
```

#### TAREA 6: Primera ejecución de prueba
```
1. GitHub → Actions → Extracción Diaria de Datos
2. Run workflow manualmente
3. Verificar que termine exitoso
4. Verificar que se creó data/latest.json
```

#### TAREA 7: Verificar dashboard
```
1. Abrir URL de Vercel (ej: https://revops-dashboard-are.vercel.app)
2. Verificar que muestra datos
3. Verificar gráficos
```

---

## 🔧 SETUP GOOGLE SERVICE ACCOUNT (OPCIONAL PERO RECOMENDADO)

### ¿Por qué es necesario?
GitHub Actions necesita autenticarse con Google para escribir en el Sheet. Como es un servidor automatizado, no puede hacer login manual. El Service Account es una "cuenta robot" que tiene permisos para escribir.

### Pasos Detallados:

#### 1️⃣ Crear Service Account (3 min)

```
1. Ve a: https://console.cloud.google.com/
2. Si no tienes proyecto:
   - Click "Select a project" arriba
   - Click "New Project"
   - Nombre: revops-are
   - Click "Create"
   - Espera ~30 segundos
3. Asegúrate que estés en el proyecto "revops-are"
4. Menú lateral → APIs & Services → Credentials
5. Click "+ Create Credentials" arriba
6. Selecciona "Service Account"
7. Formulario:
   - Service account name: github-actions-revops
   - Service account ID: (se llena automático)
   - Description: Automatización GitHub Actions para RevOps
   - Click "Create and Continue"
8. Grant access (opcional):
   - Skip - Click "Continue"
9. Grant users access (opcional):
   - Skip - Click "Done"
```

#### 2️⃣ Generar Credenciales JSON (1 min)

```
1. En la lista de Service Accounts, click en "github-actions-revops"
2. Pestaña "Keys" (arriba)
3. Click "Add Key" → "Create new key"
4. Tipo: JSON (seleccionado por defecto)
5. Click "Create"
6. Se descargará un archivo JSON a tu computadora
   - Nombre será algo como: revops-are-abc123.json
   - Guárdalo en lugar seguro
```

#### 3️⃣ Compartir Sheet con Service Account (2 min)

```
1. Abre el archivo JSON que descargaste
2. Busca la línea que dice "client_email"
3. Copia TODO el email (algo como):
   github-actions-revops@revops-are.iam.gserviceaccount.com
4. Ve a tu Google Sheet "Informe Diario ARE"
5. Click botón "Compartir" (arriba derecha)
6. Pega el email del Service Account
7. Permiso: Editor
8. Desmarca "Notify people" (no es una persona real)
9. Click "Share" o "Compartir"
```

#### 4️⃣ Configurar en GitHub (2 min)

```
1. Abre el archivo JSON completo en un editor de texto
2. Copia TODO el contenido (desde { hasta })
3. Ve a: https://github.com/USERNAME/revops-dashboard-are/settings/secrets/actions
4. Click "New repository secret"
5. Name: GOOGLE_SERVICE_ACCOUNT
6. Secret: Pega TODO el JSON
7. Click "Add secret"
```

#### 5️⃣ Actualizar sheet_updater.py (si es necesario)

El script ya está configurado para usar Service Account si existe. No requiere cambios.

---

## 🚀 INSTRUCCIONES DE DEPLOY COMPLETAS

### OPCIÓN A: Deploy Manual (Paso a Paso)

#### PASO 1: Crear Repositorio en GitHub (2 min)

1. Ve a: https://github.com/new
2. Repository name: `revops-dashboard-are`
3. Description: "Dashboard automatizado de RevOps para ARE"
4. Visibility: **Private** (importante - contiene API keys)
5. NO inicializar con README, .gitignore, ni license
6. Click "Create repository"

#### PASO 2: Push del Código (2 min)

Abre Terminal y ejecuta:

```bash
cd /Users/felipebarros/Desktop/revops-dashboard-ARE

# Agregar remote (cambia USERNAME por tu usuario de GitHub)
git remote add origin https://github.com/USERNAME/revops-dashboard-are.git

# Renombrar branch a main
git branch -M main

# Push
git push -u origin main
```

Puede pedir autenticación:
- Username: Tu usuario de GitHub
- Password: Personal Access Token (si lo pide)

#### PASO 3: Configurar GitHub Secret (2 min)

1. Ve a tu repo: `https://github.com/USERNAME/revops-dashboard-are`
2. Click en "Settings" (arriba)
3. Menú lateral → Secrets and variables → Actions
4. Click "New repository secret"
5. Configurar Secret 1:
   - Name: `HUBSPOT_API_KEY`
   - Secret: `0cf231a2-b2a3-4958-aeca-d487f3514e6b`
   - Click "Add secret"

#### PASO 4: Google Service Account (Opcional - 8 min)

Sigue los pasos detallados en la sección "SETUP GOOGLE SERVICE ACCOUNT" arriba.

Si lo omites por ahora:
- ✅ El sistema seguirá funcionando
- ✅ Extraerá datos de HubSpot y Calendar
- ❌ NO actualizará el Google Sheet automáticamente
- Podrás agregarlo después sin problemas

#### PASO 5: Deploy en Vercel (3 min)

1. Ve a: https://vercel.com/new
2. Click "Import Git Repository"
3. Si es tu primera vez:
   - Autoriza Vercel a acceder a GitHub
4. Selecciona el repo: `revops-dashboard-are`
5. Configuración del proyecto:
   - Framework Preset: **Other**
   - Root Directory: `./` (dejar por defecto)
   - Build Command: (dejar vacío)
   - Output Directory: `dashboard`
6. Click "Deploy"
7. Espera ~1-2 minutos
8. Vercel te dará una URL como: `https://revops-dashboard-are.vercel.app`

#### PASO 6: Probar Primera Extracción (5 min)

1. Ve a tu repo en GitHub
2. Click en "Actions" (arriba)
3. Verás el workflow "Extracción Diaria de Datos"
4. Click en el workflow
5. Click "Run workflow" (botón derecha)
6. Click "Run workflow" verde
7. Espera ~2-3 minutos
8. Debería aparecer check verde ✅
9. Si falla, click en el run para ver el log de error

#### PASO 7: Verificar Dashboard (2 min)

1. Ve a Vercel → Tu proyecto
2. Click en la URL del deploy
3. O abre: `https://revops-dashboard-are.vercel.app`
4. Deberías ver:
   - Métricas con números
   - Gráficos de reuniones por setter
   - Show-up rates
5. Si dice "Error cargando datos":
   - Espera 2 minutos (Vercel puede estar redeployando)
   - Refresca la página
   - Verifica que `data/latest.json` exista en el repo

---

### OPCIÓN B: Deploy Automatizado (Usar script)

Si tienes instalado GitHub CLI (`gh`):

```bash
cd /Users/felipebarros/Desktop/revops-dashboard-ARE
./DEPLOY_NOW.sh
```

El script te guiará paso a paso interactivamente.

---

## 📊 FORMATO DE DATOS - data/latest.json

### Estructura Completa:

```json
{
  "fecha": "2026-01-19",
  "leads_creados": 73,
  "reuniones": {
    "Daniela": {
      "agendadas": 15,
      "realizadas": 12,
      "eventos": [
        {
          "title": "Reunion - Juan Pérez",
          "time": "10:00",
          "color": "2",
          "completed": true
        },
        {
          "title": "Reunion - María González",
          "time": "11:30",
          "color": "2",
          "completed": true
        },
        {
          "title": "Reunion - Pedro Soto",
          "time": "14:00",
          "color": "6",
          "completed": false
        }
      ]
    },
    "Teresa": {
      "agendadas": 13,
      "realizadas": 10,
      "eventos": [
        {
          "title": "Reunion - Ana Torres",
          "time": "09:00",
          "color": "8",
          "completed": true
        },
        {
          "title": "Reunion - Carlos Muñoz",
          "time": "15:00",
          "color": "11",
          "completed": false
        }
      ]
    },
    "Matias": {
      "agendadas": 11,
      "realizadas": 8,
      "eventos": [
        {
          "title": "Reunion - Diego Rojas",
          "time": "10:30",
          "color": "9",
          "completed": true
        },
        {
          "title": "Reunion - Laura Vega",
          "time": "16:00",
          "color": "9",
          "completed": true
        }
      ]
    },
    "Robot": {
      "agendadas": 7,
      "realizadas": 5,
      "eventos": [
        {
          "title": "Asesoría Inmobiliaria con Roberto Silva",
          "time": "11:00",
          "color": "9",
          "completed": true
        },
        {
          "title": "Asesoría Inmobiliaria con Patricia Morales",
          "time": "13:00",
          "color": "6",
          "completed": false
        }
      ]
    }
  }
}
```

Este JSON se genera automáticamente cada día y es leído por el dashboard.

---

## 🆘 TROUBLESHOOTING

### Problema: "API key inválida" en GitHub Actions

**Causa:** Secret mal configurado en GitHub  
**Solución:**
1. Ve a repo → Settings → Secrets → Actions
2. Verifica que `HUBSPOT_API_KEY` exista
3. Valor debe ser exactamente: `0cf231a2-b2a3-4958-aeca-d487f3514e6b`
4. Si está mal, click en el secret → "Update" → Corregir

### Problema: "Error descargando iCal" en extracción

**Causa:** Calendar no es público o URL incorrecta  
**Solución:**
1. Abre: https://calendar.google.com/calendar/u/0/r/settings/calendar/tomas@advisorrealestate.cl
2. Scroll a "Permisos de acceso"
3. Marca "Hacer disponible públicamente"
4. Verifica la URL iCal:
   - Debe ser: `https://calendar.google.com/calendar/ical/tomas%40advisorrealestate.cl/public/basic.ics`
5. Prueba abrir esa URL en un navegador → debe descargar un archivo .ics

### Problema: "Permission denied" en Google Sheet

**Causa:** Service Account no tiene acceso al sheet  
**Solución:**
1. Abre el archivo JSON del Service Account
2. Copia el `client_email`
3. Ve al Google Sheet → Compartir
4. Agrega ese email con permiso Editor
5. Vuelve a ejecutar el workflow

### Problema: Dashboard muestra "Error cargando datos"

**Causa:** El archivo `data/latest.json` no existe  
**Solución:**
1. Ve a GitHub → tu repo → carpeta `data`
2. Verifica que `latest.json` exista
3. Si no existe:
   - Ve a Actions → Run workflow manualmente
   - Espera que termine
   - Verifica nuevamente
4. Si existe pero dashboard no lo ve:
   - Verifica la ruta en `dashboard/index.html`
   - Debe ser: `../data/latest.json`

### Problema: GitHub Actions falla constantemente

**Causa:** Error en el código o configuración  
**Solución:**
1. Ve a Actions → Click en el run fallido
2. Lee el log de error completo
3. Errores comunes:
   - **ModuleNotFoundError:** Falta un módulo en requirements.txt
   - **KeyError:** Falta una key en config.yaml
   - **ConnectionError:** Problema de red (raro)
   - **PermissionError:** Problema con secrets o permisos
4. Copia el error completo y busca en el código

### Problema: Vercel no actualiza el dashboard

**Causa:** Auto-deploy no está activado  
**Solución:**
1. Ve a Vercel → Tu proyecto → Settings
2. Git → Branch: main
3. Asegúrate que "Auto-deploy" esté ON
4. Haz un commit dummy para forzar deploy:
   ```bash
   cd /Users/felipebarros/Desktop/revops-dashboard-ARE
   echo "# Test" >> README.md
   git add .
   git commit -m "Test deploy"
   git push
   ```

### Problema: Show-up rates incorrectos

**Causa:** Lógica de colores mal configurada  
**Solución:**
1. Verifica en `config/config.yaml`:
   - `no_show_colors: ["6", "11"]` → Deben ser strings
2. Abre un evento en Calendar
3. Click en el color actual
4. Anota el número de color
5. Verifica que coincida con la configuración

### Problema: Setters mal identificados

**Causa:** Títulos de eventos no coinciden con patrones  
**Solución:**
1. Abre Calendar y ve varios eventos
2. Anota exactamente cómo empiezan los títulos:
   - ¿"Reunion" o "Reunión"?
   - ¿"Asesoría Inmobiliaria" o "Asesoria"?
3. Actualiza en `config/config.yaml`:
   ```yaml
   robot_title_pattern: "Asesoría Inmobiliaria"
   human_title_pattern: "Reunion"
   ```
4. Si usan acentos, actualiza el código para case-insensitive

---

## 🎯 RESULTADO ESPERADO FINAL

### Flujo Operacional Diario Completo:

```
07:00 AM - GitHub Actions ejecuta automáticamente
         ↓
         Extrae HubSpot:
         ├── Leads creados: 73
         └── Actividades registradas
         ↓
         Extrae Google Calendar:
         ├── Lee iCal público
         ├── Identifica 46 eventos del día anterior
         ├── Por cada evento:
         │   ├── Color 2 (Verde) → Daniela
         │   ├── Color 8 (Negro) → Teresa
         │   ├── Color 9 + "Asesoría" → Robot
         │   └── Color 9 + "Reunion" → Matias
         ├── Detecta shows/no-shows:
         │   ├── Mantiene color → Realizada ✅
         │   └── Cambió a 6/11 → No-show ❌
         └── Calcula:
             ├── Daniela: 15 agendadas, 12 realizadas (80%)
             ├── Teresa: 13 agendadas, 10 realizadas (77%)
             ├── Matias: 11 agendadas, 8 realizadas (73%)
             └── Robot: 7 agendadas, 5 realizadas (71%)
         ↓
         Genera data/latest.json
         ↓
         Actualiza Google Sheet (si Service Account configurado):
         ├── Fila 3: 46 (reuniones agendadas)
         ├── Fila 4: 35 (reuniones realizadas)
         ├── Fila 11: 15 (Daniela)
         ├── Fila 13: 13 (Teresa)
         ├── Fila 15: 11 (Matias)
         ├── Fila 17: 7 (Robot)
         └── Fila 21: 73 (leads creados)
         ↓
         Commit a GitHub:
         "📊 Datos 2026-01-19"
         ↓
07:05 AM - Vercel detecta nuevo commit
         ↓
         Redeploya dashboard automáticamente
         ↓
07:07 AM - Dashboard actualizado
         URL: https://revops-dashboard-are.vercel.app
         ↓
09:00 AM - Felipe llega a trabajar
         ↓
         Abre dashboard:
         ├── ✅ Leads creados: 73
         ├── ✅ Reuniones agendadas: 46
         ├── ✅ Reuniones realizadas: 35
         ├── ✅ Show-up rate: 76.1%
         ├── ✅ Performance por setter (gráfico)
         └── ✅ Tendencia semanal
         ↓
         Abre Google Sheet:
         ├── ✅ Todos los datos automáticos ya están
         └── Solo faltan datos manuales
         ↓
         Felipe ingresa manual (8 minutos):
         ├── ✏️ Fila 5: Clientes con reserva (desde WhatsApp)
         ├── ✏️ Fila 6: Reservas confirmadas (desde WhatsApp)
         └── ✏️ Fila 24: Inversión ($450.000 HubSpot + $200.000 agencia)
         ↓
         Sheet calcula automáticamente:
         └── Fila 25: CPL = $650.000 / 73 = $8.904
         ↓
09:08 AM - Felipe ejecuta transformación de Looker
         ↓
09:10 AM - Envía reporte a gerencia
         ↓
LISTO ✅

TIEMPO TOTAL: 8-10 minutos
ANTES: 45-60 minutos
AHORRO: 35-50 minutos/día = 12-17 horas/mes
```

### Dashboard Muestra (Visual):

**Sección Superior - Métricas Clave:**
```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Leads Creados   │ Reuniones       │ Reuniones       │ Show-up Rate    │
│      73         │ Agendadas: 46   │ Realizadas: 35  │     76.1%       │
│                 │                 │                 │   🟢 Target     │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

**Gráfico 1 - Reuniones por Setter:**
```
Daniela  ████████████████ 15
Teresa   ███████████████  13
Matias   ████████████     11
Robot    ████████          7
```

**Gráfico 2 - Show-up Rate (%):**
```
Daniela  ████████████████ 80% 🟢
Teresa   ███████████████  77% 🟢
Matias   ██████████████   73% 🟢
Robot    █████████████    71% 🟢
Target   ███████████████  70%
```

**Gráfico 3 - Tendencia Semanal:**
```
        Leads Creados
 80 │               ●
 70 │         ●   ●   ●
 60 │   ●   ●           ●
 50 │ ●
    └─────────────────────
     L  M  M  J  V  S  D
```

---

## 📞 INFORMACIÓN DE CONTACTO

**Cliente:**  
- Nombre: Felipe Barros  
- Email: fbarroslpz@gmail.com  
- Ubicación: Santiago, Chile  
- Timezone: America/Santiago (UTC-3)

**Empresa:**  
- Nombre: Advisor Real Estate (ARE)  
- Industria: Inmobiliaria  
- País: Chile

**Equipo:**
- Setters: Daniela, Teresa, Matias + Robot GoA
- Brokers: Tomás, Antonia, Treicy
- RevOps: Felipe Barros

---

## ✅ CHECKLIST DE COMPLETITUD

Marca cuando completes cada item:

### Setup Inicial:
- [ ] Proyecto verificado en `/Users/felipebarros/Desktop/revops-dashboard-ARE`
- [ ] Git tiene 2 commits locales
- [ ] Todos los archivos existen
- [ ] API Key de HubSpot configurada en config.yaml

### GitHub:
- [ ] Repositorio creado (privado)
- [ ] Código pusheado a GitHub
- [ ] GitHub Secret: HUBSPOT_API_KEY configurado
- [ ] GitHub Secret: GOOGLE_SERVICE_ACCOUNT configurado (opcional)
- [ ] Workflow visible en Actions

### Google:
- [ ] Calendar es público (iCal descargable)
- [ ] Sheet compartido con dixolivos@gmail.com (Editor)
- [ ] Service Account creado (opcional)
- [ ] Service Account compartido en Sheet (opcional)

### Vercel:
- [ ] Proyecto creado en Vercel
- [ ] Conectado a GitHub repo
- [ ] Framework: Other
- [ ] Output Directory: dashboard
- [ ] Primer deploy exitoso
- [ ] URL del dashboard funcional

### Testing:
- [ ] Primera ejecución manual de workflow exitosa
- [ ] data/latest.json generado
- [ ] Dashboard muestra datos correctamente
- [ ] Métricas son correctas
- [ ] Gráficos se renderizan
- [ ] Show-up rates calculados bien
- [ ] Setters identificados correctamente

### Automatización:
- [ ] Workflow se ejecuta automáticamente a las 07:00
- [ ] Vercel detecta cambios y redeploya
- [ ] Google Sheet se actualiza (si SA configurado)
- [ ] Logs no muestran errores

### Documentación:
- [ ] README.md actualizado con URL del dashboard
- [ ] Cliente informado de la URL
- [ ] Cliente sabe cómo ver logs de ejecución
- [ ] Cliente sabe cómo ejecutar manualmente si falla

---

## 📝 NOTAS IMPORTANTES

### Sobre los Brokers:
- Los 3 brokers (Tomás, Antonia, Treicy) **gestionan las reuniones** agendadas por los setters
- El calendario está bajo la cuenta de **tomas@advisorrealestate.cl** pero lo usan los 3
- Los brokers **cambian el color** de los eventos según el resultado de la reunión
- Esta acción de cambiar color es **manual** y la hacen después de cada reunión

### Sobre la Identificación de Setters:
- El sistema **identifica al setter original** aunque el broker haya cambiado el color
- Usa una combinación de **patrón de título + color inicial implícito**
- Por ejemplo: Si un evento tiene título "Reunion - Juan" y color rojo (11):
  - Originalmente era azul (9) - porque "Reunion" = Matias
  - Fue creado por Matias
  - El broker lo cambió a rojo = no-show
  - Sistema registra: Matias, 1 agendada, 0 realizadas

### Sobre los Datos Manuales:
- Felipe ingresa **solo 3 datos** manualmente cada día:
  1. Clientes con reserva (desde WhatsApp)
  2. Reservas confirmadas (desde WhatsApp)
  3. Inversión en campañas (HubSpot + Agencia Zapier)
- Todo lo demás es **100% automático**

### Sobre la Agencia Externa:
- Hay una agencia que envía leads vía Zapier directamente a HubSpot
- Felipe **NO gestiona** esa integración
- Los leads llegan automáticamente a HubSpot
- Lo que Felipe SÍ ingresa manual es el **costo** de esa agencia
- CPL final = (Inversión HubSpot + Inversión Agencia) / Total Leads

---

## 🎉 RESULTADO FINAL ESPERADO

Al completar todo el setup:

**Felipe tendrá:**
1. ✅ Dashboard online 24/7 accesible desde cualquier lugar
2. ✅ Datos actualizados automáticamente cada día a las 07:00
3. ✅ Google Sheet actualizado automáticamente
4. ✅ Solo 8-10 minutos de trabajo manual vs 45-60 minutos antes
5. ✅ Visibilidad completa del funnel operacional
6. ✅ Métricas de performance de cada setter
7. ✅ Alertas automáticas cuando métricas caen
8. ✅ Histórico completo en archivos JSON
9. ✅ Capacidad de análisis de tendencias
10. ✅ Reportes automáticos para gerencia

**Ahorro mensual:**  
35-50 min/día × 22 días = **12-18 horas/mes**

**ROI:**  
Setup time: ~30 minutos  
Ahorro primer mes: 12-18 horas  
ROI: 24-36x en el primer mes

---

**FIN DEL DOCUMENTO**

---

*Este documento contiene TODA la información necesaria para replicar, mantener y escalar el proyecto RevOps Dashboard de ARE. Ha sido creado para ser usado con Claude Cowork para completar el deployment y automatización del sistema.*

*Versión: 1.0*  
*Fecha: 20 de Enero 2026*  
*Autor: Claude (Anthropic) + Felipe Barros*
