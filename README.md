# 📊 RevOps Dashboard - Advisor Real Estate (ARE)

> Sistema automatizado de extracción y visualización de métricas de ventas
>
> [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
> [![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
>
> ---
>
> ## 🎯 Problema Resuelto
>
> **ANTES:** 45-60 min/día de trabajo manual
> **DESPUÉS:** 8 min/día (ahorro de 80%)
> **RESULTADO:** ~13-17 horas/mes ahorradas
>
> ### Automatizado
> - ✅ Extracción de HubSpot (leads)
> - - ✅ Extracción de Calendar (reuniones por setter)
>   - - ✅ Dashboard auto-actualizado
>     - - ✅ Google Sheet actualizado
>      
>       - ### Manual (solo)
>       - - ✏️ Reservas (WhatsApp - 5 min)
>         - - ✏️ Inversión campañas (3 min)
>          
>           - ---
>
> ## 🚀 Inicio Rápido
>
> ### 1. Clonar
> ```bash
> git clone https://github.com/Fbarroslpz/revops-dashboard-ARE.git
> cd revops-dashboard-ARE
> pip install -r requirements.txt
> ```
>
> ### 2. Configurar
> Ver guía completa: **[DEPLOY_INSTRUCTIONS.md](./DEPLOY_INSTRUCTIONS.md)**
>
> Resumen:
> - Configurar GitHub Secrets (`HUBSPOT_API_KEY`, `GOOGLE_SERVICE_ACCOUNT`)
> - - Configurar Google Service Account ([guía](./GOOGLE_SERVICE_ACCOUNT_SETUP.md))
>   - - Deploy en Vercel
>    
>     - ### 3. Listo
>     - Dashboard en: `https://revops-dashboard-are.vercel.app`
>    
>     - ---
>
> ## ✨ Características
>
> - ⏰ Ejecución automática diaria (07:00 AM)
> - - 🎨 Identificación de setters por color
>   - - ✅ Detección automática de no-shows
>     - - 🤖 Distinción Robot vs Humano
>       - - 📱 Diseño responsive
>         - - 📊 6 visualizaciones (Chart.js)
>          
>           - ---
>
> ## 🏗️ Arquitectura
>
> ```
> GitHub Actions (07:00 AM)
>     ↓
> Extrae HubSpot + Calendar
>     ↓
> Genera latest.json
>     ↓
> Actualiza Google Sheet
>     ↓
> Commit a GitHub
>     ↓
> Vercel redeploya
>     ↓
> Dashboard actualizado
> ```
>
> ---
>
> ## 📊 Métricas
>
> ### Automáticas
> - Leads creados (HubSpot)
> - - Reuniones agendadas/realizadas (Calendar)
>   - - Show-up rates por setter
>     - - No-shows automáticos
>      
>       - ### Manuales
>       - - Reservas (WhatsApp)
>         - - Inversión campañas
>          
>           - ### Calculadas
>           - - CPL (Cost Per Lead)
>             - - Tasas de conversión
>               - - Distribución por setter
>                
>                 - ---
>
> ## 📁 Estructura
>
> ```
> .github/workflows/    → GitHub Actions (cron diario)
> scripts/              → Extractores Python
> dashboard/            → Dashboard web (HTML)
> data/                 → JSON generados
> config/               → Configuración (NO commitear con API keys)
> ```
>
> ---
>
> ## 🎨 Lógica de Calendar
>
> ### Colores
> - Verde (2) → Daniela
> - - Negro (8) → Teresa
>   - - Azul (9) → Matias O Robot
>    
>     - ### No-Shows
>     - - Naranjo (6) → NO REALIZADA
>       - - Rojo (11) → NO REALIZADA
>         - - Color original → REALIZADA
>          
>           - ---
>
> ## 📚 Documentación
>
> - [DEPLOY_INSTRUCTIONS.md](./DEPLOY_INSTRUCTIONS.md) - Deploy completo
> - - [GOOGLE_SERVICE_ACCOUNT_SETUP.md](./GOOGLE_SERVICE_ACCOUNT_SETUP.md) - Service Account
>   - - [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Problemas comunes
>     - - [CHANGELOG.md](./CHANGELOG.md) - Historial de versiones
>      
>       - ---
>
> ## 👤 Autor
>
> **Felipe Barros**
> Email: fbarroslpz@gmail.com
> Proyecto: Advisor Real Estate (ARE)
>
> ---
>
> ## 📝 Licencia
>
> MIT License - 2026
