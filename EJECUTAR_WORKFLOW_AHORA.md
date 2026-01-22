# ▶️ EJECUTAR WORKFLOW AHORA

## 🎯 Script actualizado y listo

El script `read_sheet_to_json.py` ha sido modificado para:
- ✅ Extraer **TODOS** los datos desde el 22/12/2022 hasta AYER
- ✅ Generar un JSON con el histórico completo
- ✅ Actualizar automáticamente cada día

## 📋 PASOS PARA EJECUTAR:

### 1. Ve a GitHub Actions
Abre este link en tu navegador:
```
https://github.com/Fbarroslpz/revops-dashboard-ARE/actions/workflows/daily-extract.yml
```

### 2. Ejecutar workflow
1. Haz clic en el botón gris **"Run workflow"** (lado derecho)
2. Se abrirá un dropdown
3. Deja el valor por defecto (branch: main, days_back: 1)
4. Haz clic en el botón verde **"Run workflow"**

### 3. Monitorear ejecución
- Después de unos segundos aparecerá una nueva ejecución en la lista
- Haz clic en ella para ver el progreso en tiempo real
- Debería completarse en ~40-60 segundos

## ✅ RESULTADO ESPERADO:

Si todo funciona correctamente, verás:
```
✅ Se extrajeron XXX días de datos
📅 Desde: 2022-12-22
📅 Hasta: 2026-01-20
✅ Datos guardados en: data/latest.json
```

Y verás un nuevo commit en el repositorio:
```
🤖 Update: latest.json con datos del 21/01/2026
```

## 📊 ESTRUCTURA DEL JSON GENERADO:

```json
{
  "fecha_actualizacion": "2026-01-21 16:30:00",
  "fecha_ultimo_dato": "2026-01-20",
  "total_dias": 400,
  "datos": [
    {
      "fecha": "2022-12-22",
      "leads_creados": 45,
      "reuniones": {
        "Daniela": {...},
        "Teresa": {...},
        "Matias": {...},
        "Robot": {...}
      },
      "totales": {...}
    },
    {
      "fecha": "2022-12-23",
      ...
    },
    ...
    {
      "fecha": "2026-01-20",
      "leads_creados": 87,
      ...
    }
  ]
}
```

## 🔄 FUNCIONAMIENTO DIARIO:

A partir de mañana:
- **Cada día a las 07:00 AM** (Chile) el workflow se ejecutará automáticamente
- Leerá el Google Sheet actualizado
- Extraerá todos los datos hasta el día anterior
- Generará el nuevo `latest.json`
- Commiteará y pusheará los cambios

Por ejemplo:
- **Hoy 21/01** → Datos hasta 20/01
- **Mañana 22/01** → Datos hasta 21/01 (incluirá los de hoy)
- **Pasado 23/01** → Datos hasta 22/01 (incluirá los de mañana)

---

## 🚨 SI HAY ALGÚN ERROR:

1. Revisa los logs del workflow en GitHub Actions
2. Verifica que el secret `GOOGLE_SERVICE_ACCOUNT` esté configurado
3. Asegúrate de que el Service Account tenga acceso al Google Sheet
4. Si el error persiste, avísame con el mensaje de error exacto

---

## 📱 PRÓXIMO PASO:

Una vez que el workflow se ejecute exitosamente y genere `latest.json` con todos los datos históricos, el siguiente paso es:

### ✅ Deploy del Dashboard en Vercel

Esto permitirá visualizar todos los datos en un dashboard online profesional.

---

**¿Listo para ejecutar?** Ve al link de arriba y dale click a "Run workflow" 🚀
