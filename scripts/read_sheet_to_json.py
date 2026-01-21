#!/usr/bin/env python3
"""
Script para leer el Google Sheet y generar latest.json
Lee directamente desde el Sheet público usando la API de Google Sheets

Autor: Felipe Barros - Vulpes Consulting
Fecha: Enero 2026
"""

import os
import sys
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ID del Google Sheet
SHEET_ID = "1E15l2Ac6EJsMEWS5SaOJnQHkNs6VQISBF1XfZ4NfrK4"
SHEET_NAME = "ACT comercial"

# Scopes necesarios para Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def read_sheet_with_service_account():
    """
    Lee el Google Sheet usando Service Account
    """
    try:
        # Cargar credenciales
        credentials_path = 'config/google_credentials.json'

        if not os.path.exists(credentials_path):
            print(f"❌ No se encontró {credentials_path}")
            print("💡 Asegúrate de que el archivo de credenciales existe")
            sys.exit(1)

        print(f"🔐 Cargando credenciales desde {credentials_path}...")
        creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)

        # Autenticar con gspread
        client = gspread.authorize(creds)

        print(f"📥 Abriendo Google Sheet...")
        sheet = client.open_by_key(SHEET_ID)
        worksheet = sheet.worksheet(SHEET_NAME)

        # Obtener todos los valores
        print(f"📊 Descargando datos...")
        all_values = worksheet.get_all_values()

        print(f"✅ Descargado {len(all_values)} filas")
        return all_values

    except Exception as e:
        print(f"❌ Error leyendo sheet: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def find_last_column_with_data(rows):
    """Encuentra la última columna que tiene datos (de derecha a izquierda)"""
    # La fila 2 tiene las fechas
    date_row = rows[1] if len(rows) > 1 else []

    # Buscar la última celda no vacía
    last_col = -1
    for i in range(len(date_row) - 1, -1, -1):
        if date_row[i].strip():
            last_col = i
            break

    return last_col


def parse_date(date_str):
    """Parsea fecha en formato DD/MM/YYYY"""
    try:
        return datetime.strptime(date_str.strip(), "%d/%m/%Y")
    except:
        return None


def extract_data_from_column(rows, col_index):
    """Extrae datos de una columna específica"""
    try:
        # Fila 2 tiene la fecha (índice 1 en lista 0-based)
        fecha_str = rows[1][col_index].strip() if len(rows) > 1 and col_index < len(rows[1]) else ""

        if not fecha_str:
            return None

        fecha = parse_date(fecha_str)
        if not fecha:
            return None

        # Extraer valores (recordar que en CSV las filas son 0-indexed)
        def get_value(row_index):
            try:
                val = rows[row_index][col_index].strip()
                return int(val) if val else 0
            except:
                return 0

        # Filas según la estructura del sheet (0-indexed):
        # Fila 3 = índice 2, Fila 4 = índice 3, etc.
        reuniones_agendadas = get_value(2)  # Fila 3
        reuniones_realizadas = get_value(3)  # Fila 4
        clientes_con_reserva = get_value(4)  # Fila 5
        reservas = get_value(5)  # Fila 6

        # Setters
        dani_llamadas = get_value(9)   # Fila 10
        dani_reuniones = get_value(10)  # Fila 11
        tere_llamadas = get_value(11)  # Fila 12
        tere_reuniones = get_value(12)  # Fila 13
        mati_llamadas = get_value(13)  # Fila 14
        mati_reuniones = get_value(14)  # Fila 15
        robot_llamadas = get_value(15)  # Fila 16
        robot_reuniones = get_value(16)  # Fila 17

        leads_creados = get_value(20)  # Fila 21

        # Construir estructura de datos
        data = {
            "fecha": fecha.strftime("%Y-%m-%d"),
            "leads_creados": leads_creados,
            "reuniones": {
                "Daniela": {
                    "agendadas": dani_reuniones,
                    "realizadas": dani_reuniones,  # Por ahora no tenemos el dato de realizadas por setter
                    "llamadas": dani_llamadas
                },
                "Teresa": {
                    "agendadas": tere_reuniones,
                    "realizadas": tere_reuniones,
                    "llamadas": tere_llamadas
                },
                "Matias": {
                    "agendadas": mati_reuniones,
                    "realizadas": mati_reuniones,
                    "llamadas": mati_llamadas
                },
                "Robot": {
                    "agendadas": robot_reuniones,
                    "realizadas": robot_reuniones,
                    "llamadas": robot_llamadas
                }
            },
            "totales": {
                "reuniones_agendadas": reuniones_agendadas,
                "reuniones_realizadas": reuniones_realizadas,
                "clientes_con_reserva": clientes_con_reserva,
                "reservas": reservas
            }
        }

        return data

    except Exception as e:
        print(f"❌ Error extrayendo datos de columna {col_index}: {e}")
        return None


def find_column_for_date(rows, target_date):
    """Busca la columna que corresponde a una fecha específica"""
    # La fila 2 (índice 1) tiene las fechas
    date_row = rows[1] if len(rows) > 1 else []

    target_str = target_date.strftime("%d/%m/%Y")

    for i, cell in enumerate(date_row):
        cell_date = parse_date(cell)
        if cell_date and cell_date.date() == target_date.date():
            return i

    return -1


def main():
    print("=" * 80)
    print("🗄️  LEYENDO GOOGLE SHEET - INFORME DIARIO ARE")
    print("=" * 80)

    # Calcular fecha de ayer
    from datetime import timedelta
    yesterday = datetime.now() - timedelta(days=1)
    print(f"\n📅 Buscando datos para: {yesterday.strftime('%d/%m/%Y')} (AYER)")

    # Leer sheet
    rows = read_sheet_with_service_account()

    # Buscar columna para ayer
    target_col = find_column_for_date(rows, yesterday)

    if target_col == -1:
        print(f"⚠️ No se encontraron datos para {yesterday.strftime('%d/%m/%Y')}")
        print("📝 Intentando con la última columna disponible...")

        # Fallback: usar última columna con datos
        target_col = find_last_column_with_data(rows)

        if target_col == -1:
            print("❌ No se encontraron datos en el sheet")
            sys.exit(1)

        fecha_encontrada = rows[1][target_col] if len(rows) > 1 else "?"
        print(f"✅ Usando última fecha disponible: {fecha_encontrada}")
    else:
        print(f"✅ Encontrada columna {target_col} con datos de ayer")

    # Extraer datos de la columna objetivo
    data = extract_data_from_column(rows, target_col)

    if not data:
        print("❌ No se pudieron extraer los datos")
        sys.exit(1)

    # Crear carpeta data si no existe
    os.makedirs('data', exist_ok=True)

    # Guardar en latest.json
    output_file = 'data/latest.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Datos guardados en: {output_file}")
    print(f"📊 Fecha procesada: {data['fecha']}")
    print(f"📈 Leads creados: {data['leads_creados']}")
    print(f"📞 Total reuniones agendadas: {data['totales']['reuniones_agendadas']}")
    print(f"✅ Total reuniones realizadas: {data['totales']['reuniones_realizadas']}")

    print("\n" + "=" * 80)
    print("✅ PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 80)


if __name__ == "__main__":
    main()
