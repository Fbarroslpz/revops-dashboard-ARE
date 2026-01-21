#!/bin/bash
# Script para limpiar el repositorio de GitHub y dejarlo listo para Antigravity

echo "🗑️ Limpiando repositorio de GitHub..."
echo ""

# Navegar al directorio del proyecto
cd "$(dirname "$0")"

# Verificar que estamos en un repositorio git
if [ ! -d ".git" ]; then
    echo "❌ ERROR: No estamos en un repositorio git"
    exit 1
fi

echo "⚠️  ADVERTENCIA: Esto eliminará TODOS los archivos del repositorio en GitHub"
echo "Los archivos locales en tu Mac se mantendrán, pero se eliminarán del repositorio remoto."
echo ""
read -p "¿Estás seguro? (escribe 'SI' para continuar): " confirmacion

if [ "$confirmacion" != "SI" ]; then
    echo "❌ Operación cancelada"
    exit 0
fi

echo ""
echo "🗑️ Eliminando archivos del repositorio..."

# Obtener todos los archivos trackeados por git (excepto .git)
git ls-files | while read file; do
    git rm "$file" 2>/dev/null || true
done

# Verificar si hay cambios
if git diff --staged --quiet; then
    echo "ℹ️ No hay archivos para eliminar (repositorio ya está vacío)"
else
    echo "📝 Creando commit de limpieza..."
    git commit -m "🗑️ Limpiar repositorio para subida via Antigravity"

    echo "📤 Haciendo push al repositorio..."
    git push

    echo ""
    echo "✅ Repositorio limpiado exitosamente!"
    echo ""
    echo "🎯 Próximos pasos:"
    echo "1. Sube los archivos usando Antigravity"
    echo "2. Avísale a Claude cuando termines"
fi

echo ""
echo "✅ ¡Listo para Antigravity!"
