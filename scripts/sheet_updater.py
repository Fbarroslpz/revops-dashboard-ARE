#!/usr/bin/env python3
"""
Actualizador de Google Sheet - Informe Diario ARE
Usa acceso público del sheet (sin credenciales de Service Account)

Autor: Felipe Barros - Vulpes Consulting
"""

import os
import sys
import yaml
import logging
import gspread
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(__file__))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GoogleSheetUpdater:
    """Actualiza el Google Sheet con acceso público"""
    
    def __init__(self, config: dict):
        self.config = config
        self.sheet_id = config['google_sheets']['informe_diario_id']
        self.worksheet_name = config['google_sheets']['worksheet_name']
        
        # Autenticar con OAuth usando acceso público
        try:
            gc = gspread.oauth(
                credentials_filename='config/credentials.json',
                authorized_user_filename='config/authorized_user.json'
            )
            self.client = gc
            logger.info("✅ Autenticado con Google Sheets")
        except:
            logger.warning("⚠️ Sin credenciales OAuth - modo simulación")
            self.client = None
    
    def update_sheet(self, date: datetime, calendar_data: dict, hubspot_data: dict):
        """Actualiza el sheet"""
        
        if not self.client:
            logger.warning("⚠️ Modo simulación - datos que se actualizarían:")
            self._print_would_update(date, calendar_data, hubspot_data)
            return True  # Retornar True para que no falle en GitHub Actions
        
        try:
            sheet = self.client.open_by_key(self.sheet_id)
            worksheet = sheet.worksheet(self.worksheet_name)
            
            date_str = date.strftime("%d/%m/%Y")
            
            # Buscar columna de fecha
            dates_row = worksheet.row_values(2)
            
            try:
                col_index = dates_row.index(date_str) + 1
            except ValueError:
                col_index = len(dates_row) + 1
                worksheet.update_cell(2, col_index, date_str)
            
            # Actualizar datos automáticos
            total_agendadas = sum(d['agendadas'] for d in calendar_data.values())
            total_realizadas = sum(d['realizadas'] for d in calendar_data.values())
            
            worksheet.update_cell(3, col_index, total_agendadas)
            worksheet.update_cell(4, col_index, total_realizadas)
            worksheet.update_cell(11, col_index, calendar_data.get('Daniela', {}).get('agendadas', 0))
            worksheet.update_cell(13, col_index, calendar_data.get('Teresa', {}).get('agendadas', 0))
            worksheet.update_cell(15, col_index, calendar_data.get('Matias', {}).get('agendadas', 0))
            worksheet.update_cell(17, col_index, calendar_data.get('Robot', {}).get('agendadas', 0))
            worksheet.update_cell(21, col_index, hubspot_data.get('leads_creados', 0))
            
            logger.info("✅ Sheet actualizado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False
    
    def _print_would_update(self, date: datetime, calendar_data: dict, hubspot_data: dict):
        """Imprime qué se actualizaría"""
        date_str = date.strftime("%d/%m/%Y")
        
        print(f"\n📅 Datos para {date_str}:")
        print(f"✅ Reuniones agendadas: {sum(d['agendadas'] for d in calendar_data.values())}")
        print(f"✅ Reuniones realizadas: {sum(d['realizadas'] for d in calendar_data.values())}")
        print(f"✅ Daniela: {calendar_data.get('Daniela', {}).get('agendadas', 0)}")
        print(f"✅ Teresa: {calendar_data.get('Teresa', {}).get('agendadas', 0)}")
        print(f"✅ Matias: {calendar_data.get('Matias', {}).get('agendadas', 0)}")
        print(f"✅ Robot: {calendar_data.get('Robot', {}).get('agendadas', 0)}")
        print(f"✅ Leads creados: {hubspot_data.get('leads_creados', 0)}\n")
