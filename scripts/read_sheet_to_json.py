#!/usr/bin/env python3
"""
Script para leer el Google Sheet y generar latest.json
Extrae TODOS los datos acumulados desde el inicio hasta AYER

Autor: Felipe Barros - Vulpes Consulting
Fecha: Enero 2026
"""

import os
import sys
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

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


def parse_date(date_str):
    """Parsea fecha en formato DD/MM/YYYY"""
    try:
        return datetime.strptime(date_str.strip(), "%d/%m/%Y")
    except:
        return None


def find_yesterday_column(rows, yesterday):
    """
    Encuentra la última columna que contiene datos hasta AYER
    Retorna el índice de la columna de ayer (o la última disponible)
    """
    date_row = rows[1] if len(rows) > 1 else []

    last_valid_col = -1

    for i in range(len(date_row)):
        cell = date_row[i].strip()
        if not cell:
            continue

        fecha = parse_date(cell)
        if fecha:
            # Si la fecha es <= ayer, es válida
            if fecha.date() <= yesterday.date():
                last_valid_col = i
            # Si la fecha es > ayer, paramos
            elif fecha.date() > yesterday.date():
                break

    return last_valid_col


def extract_all_data_until_yesterday(rows, last_col_index):
    """
    Extrae TODOS los datos desde el inicio hasta la columna de AYER
    Retorna una lista con todos los días
    """
    all_days = []

    # Empezar desde la primera columna con fecha (normalmente columna 0 o 1)
    # Buscar la primera columna que tenga una fecha válida
    date_row = rows[1] if len(rows) > 1 else []
    first_col = -1

    for i in range(len(date_row)):
        if parse_date(date_row[i]):
            first_col = i
            break

    if first_col == -1:
        print("❌ No se encontró ninguna columna con fechas válidas")
        return []

    print(f"📅 Extrayendo datos desde columna {first_col} hasta {last_col_index}")

    # Extraer datos de cada columna
    for col_idx in range(first_col, last_col_index + 1):
        data = extract_data_from_column(rows, col_idx)
        if data:
            all_days.append(data)

    return all_days


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

        # Extraer valores (recordar que las filas son 0-indexed)
        def get_value(row_index):
            try:
                if row_index < len(rows) and col_index < len(rows[row_index]):
                    val = rows[row_index][col_index].strip()
                    return int(val) if val else 0
                return 0
            except:
                return 0

        def get_money_value(row_index):
            try:
                if row_index < len(rows) and col_index < len(rows[row_index]):
                    val = rows[row_index][col_index].strip()
                    # Remover símbolos de moneda y puntos/comas
                    val = val.replace('$', '').replace('.', '').replace(',', '').strip()
                    return int(val) if val else 0
                return 0
            except:
                return 0

        def get_decimal_value(row_index):
            try:
                if row_index < len(rows) and col_index < len(rows[row_index]):
                    val = rows[row_index][col_index].strip()
                    # Remover símbolos de moneda y convertir coma a punto
                    val = val.replace('$', '').replace('.', '').replace(',', '.').strip()
                    return float(val) if val else 0.0
                return 0.0
            except:
                return 0.0

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
        llamadas_realizadas = get_value(21)  # Fila 22
        reuniones_agendadas_dia = get_value(22)  # Fila 23
        inversion_campanas = get_money_value(23)  # Fila 24
        costo_por_lead = get_decimal_value(24)  # Fila 25

        # Construir estructura de datos
        data = {
            "fecha": fecha.strftime("%Y-%m-%d"),
            "leads_creados": leads_creados,
            "llamadas_realizadas": llamadas_realizadas,
            "reuniones_agendadas_dia": reuniones_agendadas_dia,
            "inversion_campanas": inversion_campanas,
            "costo_por_lead": round(costo_por_lead, 3),
            "reuniones": {
                "Daniela": {
                    "agendadas": dani_reuniones,
                    "realizadas": dani_reuniones,
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
        print(f"⚠️  Error extrayendo datos de columna {col_index}: {e}")
        return None


def main():
    print("=" * 80)
    print("🗄️  LEYENDO GOOGLE SHEET - INFORME DIARIO ARE")
    print("📊 Extrayendo TODOS los datos acumulados hasta AYER")
    print("=" * 80)

    # Calcular fecha de ayer
    yesterday = datetime.now() - timedelta(days=1)
    print(f"\n📅 Fecha límite: {yesterday.strftime('%d/%m/%Y')} (AYER)")
    print(f"📊 Se extraerán TODOS los datos desde el inicio hasta esta fecha")

    # Leer sheet
    rows = read_sheet_with_service_account()

    # Encontrar la última columna válida (hasta ayer)
    last_col = find_yesterday_column(rows, yesterday)

    if last_col == -1:
        print("❌ No se encontraron datos hasta ayer")
        sys.exit(1)

    fecha_limite = rows[1][last_col] if len(rows) > 1 else "?"
    print(f"✅ Última fecha válida encontrada: {fecha_limite} (columna {last_col})")

    # Extraer TODOS los datos desde el inicio hasta ayer
    all_data = extract_all_data_until_yesterday(rows, last_col)

    if not all_data:
        print("❌ No se pudieron extraer los datos")
        sys.exit(1)

    print(f"\n✅ Se extrajeron {len(all_data)} días de datos")
    print(f"📅 Desde: {all_data[0]['fecha']}")
    print(f"📅 Hasta: {all_data[-1]['fecha']}")

    # Crear estructura final
    output_data = {
        "fecha_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fecha_ultimo_dato": all_data[-1]['fecha'],
        "total_dias": len(all_data),
        "datos": all_data
    }

    # Crear carpeta data si no existe
    os.makedirs('data', exist_ok=True)

    # Guardar en latest.json
    output_file = 'data/latest.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Datos guardados en: {output_file}")
    print(f"📊 Total días procesados: {len(all_data)}")
    print(f"📈 Último día: {all_data[-1]['fecha']}")
    print(f"📞 Leads totales último día: {all_data[-1]['leads_creados']}")

    print("\n" + "=" * 80)
    print("✅ PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 80)


if __name__ == "__main__":
    main()
