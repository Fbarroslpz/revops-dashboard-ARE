#!/bin/bash
# Script para organizar archivos del proyecto RevOps Dashboard en las carpetas correctas

echo "🚀 Organizando archivos del proyecto RevOps Dashboard..."
echo ""

# Navegar al directorio del proyecto
cd "$(dirname "$0")"

# Crear carpetas necesarias
echo "📁 Creando estructura de carpetas..."
mkdir -p .github/workflows
mkdir -p scripts
mkdir -p dashboard
mkdir -p data
mkdir -p config
mkdir -p logs

echo "✅ Carpetas creadas"
echo ""

# Mover archivos Python a scripts/
echo "🐍 Moviendo archivos Python a scripts/..."
mv -f calendar_extractor.py scripts/ 2>/dev/null || true
mv -f main_extractor.py scripts/ 2>/dev/null || true
mv -f sheet_updater.py scripts/ 2>/dev/null || true
mv -f utils.py scripts/ 2>/dev/null || true
mv -f verify_setup.py scripts/ 2>/dev/null || true

# Mover index.html a dashboard/
echo "🎨 Moviendo index.html a dashboard/..."
mv -f index.html dashboard/ 2>/dev/null || true

# Mover archivos JSON a data/
echo "📊 Moviendo archivos JSON a data/..."
mv -f latest.json data/ 2>/dev/null || true
mv -f EJEMPLO_OUTPUT.json data/ 2>/dev/null || true

# Mover config.yaml a config/
echo "⚙️ Moviendo config.yaml a config/..."
mv -f config.yaml config/ 2>/dev/null || true

# Crear .gitignore si no existe
if [ ! -f ".gitignore" ]; then
    echo "📝 Creando .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Credenciales y configuración sensible
config/config.yaml
config/google_credentials.json
*.env
.env.*
credentials.json
token.json

# Logs
logs/*.log
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
EOF
fi

echo ""
echo "✅ Archivos organizados correctamente!"
echo ""
echo "📂 Estructura final:"
tree -L 2 -I '__pycache__|*.pyc|.git' . 2>/dev/null || find . -maxdepth 2 -not -path '*/\.*' -type d

echo ""
echo "🎯 Próximos pasos:"
echo "1. Ejecuta: git status"
echo "2. Verifica que los archivos estén en las carpetas correctas"
echo "3. Ejecuta: git add ."
echo "4. Ejecuta: git commit -m '🗂️ Organizar archivos en carpetas'"
echo "5. Ejecuta: git push"
echo ""
echo "✅ ¡Listo!"
