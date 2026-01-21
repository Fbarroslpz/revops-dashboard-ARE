# Changelog

Todas las modificaciones notables de este proyecto serán documentadas en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [1.0.0] - 2026-01-20

### 🎉 Lanzamiento Inicial

#### Agregado
- **Sistema de extracción automática**
  - Extractor de Google Calendar vía iCal público
  - Extractor de HubSpot vía API
  - Orquestador principal (`main_extractor.py`)
  - Actualizador de Google Sheets

- **Dashboard web**
  - Diseño responsive con Chart.js
  - 6 visualizaciones diferentes (bar, pie, doughnut, radar)
  - Auto-refresh cada 5 minutos
  - Indicadores visuales de show-up rates
  - Detalle por setter

- **Automatización**
  - GitHub Actions workflow (cron diario 07:00 AM)
  - Auto-commit de datos extraídos
  - Auto-deploy en Vercel
  - Ejecución manual disponible

- **Inteligencia de datos**
  - Identificación de setters por color de evento
  - Detección automática de no-shows
  - Distinción Robot vs Humano por patrón de título
  - Cálculo de métricas (show-up rate, conversiones)

- **Documentación**
  - README.md completo
  - GOOGLE_SERVICE_ACCOUNT_SETUP.md (guía detallada)
  - DEPLOY_INSTRUCTIONS.md (paso a paso)
  - TROUBLESHOOTING.md (problemas comunes)
  - CHANGELOG.md (este archivo)

- **Utilidades**
  - `utils.py` con retry logic y validaciones
  - Manejo robusto de errores
  - Logging comprehensivo
  - Ejemplo de datos (latest.json)

- **Seguridad**
  - .gitignore configurado para credenciales
  - .env.example para configuración segura
  - Secrets de GitHub para API keys
  - Service Account de Google Cloud

#### Métricas Soportadas
- Leads creados (HubSpot)
- Reuniones agendadas por setter (Calendar)
- Reuniones realizadas por setter (Calendar)
- Show-up rate total y por setter
- No-shows detectados automáticamente

#### Setters Configurados
- Daniela Sepúlveda (color verde)
- Teresa Ceballos (color negro)
- Matias Medel (color azul)
- Robot GoA (color azul + patrón de título)

---

## [Unreleased]

### Planeado para futuras versiones

#### En consideración
- Histórico de métricas (últimos 7/30 días)
- Gráfico de tendencias de leads
- Alertas automáticas por email/Slack
- Integración con WhatsApp Business API
- Export de reportes a PDF
- Dashboards personalizados por rol
- Comparación mes a mes
- Predicción de metas usando ML

---

## Notas de Versión

### Versión 1.0.0 - Contexto
Esta versión inicial resuelve el problema de trabajo manual diario (45-60 min/día) automatizando:
- Extracción de HubSpot y Google Calendar
- Generación de dashboard visual
- Actualización de Google Sheets

Ahorro estimado: ~13-17 horas/mes de trabajo repetitivo.

---

## Historial de Decisiones Técnicas

### ¿Por qué Python?
- Excelentes librerías para APIs (requests, gspread)
- Fácil procesamiento de datos (pandas)
- Compatible con GitHub Actions

### ¿Por qué iCal público en vez de Google Calendar API?
- NO requiere OAuth (flujo más simple)
- NO requiere renovación de tokens
- Acceso público ya configurado
- Menos complejidad de autenticación

### ¿Por qué Vercel en vez de GitHub Pages?
- Auto-deploy más rápido
- Mejor manejo de SPA
- Logs de deployment
- Preview branches

### ¿Por qué Chart.js en vez de D3.js?
- Más simple de usar
- Menor curva de aprendizaje
- Suficiente para las necesidades actuales
- Mejor documentación

### ¿Por qué GitHub Actions en vez de servidor dedicado?
- Costo: $0 (vs servidor ~$10/mes)
- Mantenimiento: 0 (GitHub lo maneja)
- Escalabilidad: Automática
- Logs: Integrados

---

## Contribuyentes

- **Felipe Barros** - Desarrollo completo - [fbarroslpz@gmail.com](mailto:fbarroslpz@gmail.com)

---

## Agradecimientos

- Equipo de Advisor Real Estate por la colaboración
- Tomas (tomas@advisorrealestate.cl) por compartir el calendario
- Setters: Daniela, Teresa, Matias por feedback durante testing

---

[1.0.0]: https://github.com/TU_USUARIO/revops-dashboard-are/releases/tag/v1.0.0
[Unreleased]: https://github.com/TU_USUARIO/revops-dashboard-are/compare/v1.0.0...HEAD
