#!/bin/bash

# Script de setup para subir el proyecto a GitHub
# Ejecutar este script después de crear el repositorio en GitHub

echo "=================================================="
echo "🚀 SETUP GITHUB - RevOps Dashboard ARE"
echo "=================================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "README.md" ]; then
    echo "❌ ERROR: Ejecuta este script desde el directorio del proyecto"
    exit 1
fi

echo "✅ Directorio verificado"
echo ""

# Paso 1: Crear repositorio en GitHub
echo "📋 PASO 1: Crear repositorio en GitHub"
echo "---------------------------------------"
echo "Por favor, ve a: https://github.com/new"
echo ""
echo "Configuración del repositorio:"
echo "  • Repository name: revops-dashboard-are"
echo "  • Visibility: PRIVATE ⚠️ (importante)"
echo "  • NO inicializar con README, .gitignore, ni license"
echo ""
read -p "Presiona ENTER cuando hayas creado el repositorio..."
echo ""

# Paso 2: Pedir tu usuario de GitHub
echo "📋 PASO 2: Configurar remote"
echo "---------------------------------------"
read -p "Ingresa tu usuario de GitHub: " GITHUB_USER
echo ""

# Configurar Git
echo "🔧 Configurando Git..."
git config user.email "fbarroslpz@gmail.com"
git config user.name "Felipe Barros"
echo "✅ Git configurado"
echo ""

# Paso 3: Agregar archivos
echo "📋 PASO 3: Preparar archivos"
echo "---------------------------------------"

# Esperar a que se libere el lock file si existe
if [ -f ".git/index.lock" ]; then
    echo "⚠️  Esperando a que se libere el lock file..."
    sleep 3
    if [ -f ".git/index.lock" ]; then
        echo "⚠️  Removiendo lock file antiguo..."
        rm -f .git/index.lock 2>/dev/null || true
    fi
fi

echo "📦 Agregando archivos al staging..."
git add -A

if [ $? -ne 0 ]; then
    echo "❌ Error agregando archivos"
    exit 1
fi

echo "✅ Archivos agregados"
echo ""

# Paso 4: Commit inicial
echo "📋 PASO 4: Crear commit inicial"
echo "---------------------------------------"
git commit -m "🎉 Initial commit - RevOps Dashboard ARE

✨ Features:
- Automated data extraction from HubSpot and Google Calendar
- Real-time dashboard with Chart.js visualizations
- Google Sheets auto-update integration
- GitHub Actions daily cron (07:00 AM Santiago)
- Vercel deployment ready

📊 Automated Metrics:
- Leads created (HubSpot)
- Meetings scheduled/completed per setter
- Automated no-show detection
- Show-up rates calculation

🎨 Smart Features:
- Setter identification by calendar color
- Robot vs Human distinction
- Responsive design (6 charts)
- Auto-refresh every 5 minutes

📚 Documentation:
- Complete deployment guide
- Google Service Account setup guide
- Troubleshooting guide
- Changelog

⏱️ Impact:
- Time saved: ~13-17 hours/month
- Manual work reduced from 45-60 min/day to 8 min/day

Author: Felipe Barros - Vulpes Consulting
Client: Advisor Real Estate (ARE)
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

if [ $? -ne 0 ]; then
    echo "❌ Error creando commit"
    exit 1
fi

echo "✅ Commit creado"
echo ""

# Paso 5: Agregar remote
echo "📋 PASO 5: Conectar con GitHub"
echo "---------------------------------------"
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/${GITHUB_USER}/revops-dashboard-are.git"

if [ $? -ne 0 ]; then
    echo "❌ Error agregando remote"
    exit 1
fi

echo "✅ Remote agregado"
echo ""

# Paso 6: Renombrar branch a main
echo "📋 PASO 6: Configurar branch main"
echo "---------------------------------------"
git branch -M main
echo "✅ Branch renombrado a main"
echo ""

# Paso 7: Push
echo "📋 PASO 7: Subir código a GitHub"
echo "---------------------------------------"
echo "🚀 Haciendo push..."
echo ""

git push -u origin main

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Error haciendo push"
    echo ""
    echo "Si el error es de autenticación, necesitas:"
    echo "1. Crear un Personal Access Token en GitHub"
    echo "   https://github.com/settings/tokens/new"
    echo ""
    echo "2. Permisos necesarios:"
    echo "   ✓ repo (todos los sub-items)"
    echo "   ✓ workflow"
    echo ""
    echo "3. Cuando hagas push, usa el token como password"
    echo ""
    exit 1
fi

echo ""
echo "=================================================="
echo "✅ ¡REPOSITORIO SUBIDO EXITOSAMENTE!"
echo "=================================================="
echo ""
echo "📍 URL del repositorio:"
echo "   https://github.com/${GITHUB_USER}/revops-dashboard-are"
echo ""
echo "🔍 Verifica que todos los archivos estén ahí:"
echo "   • .github/workflows/daily-extract.yml"
echo "   • scripts/*.py"
echo "   • dashboard/index.html"
echo "   • README.md"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo "   1. Configurar GitHub Secrets (HUBSPOT_API_KEY, GOOGLE_SERVICE_ACCOUNT)"
echo "   2. Seguir DEPLOY_INSTRUCTIONS.md"
echo ""
echo "=================================================="
