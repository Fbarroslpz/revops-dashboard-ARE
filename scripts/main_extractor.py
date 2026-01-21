#!/usr/bin/env python3
"""
Script principal de extracción de datos
Integra HubSpot + Google Calendar + Google Sheets

Autor: Felipe Barros - Vulpes Consulting
Fecha: Enero 2026
"""

import os
import sys
import json
import yaml
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import requests

# Importar extractores
sys.path.append(os.path.dirname(__file__))
from calendar_extractor import CalendarExtractor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/mnt/user-data/outputs/revops-dashboard-ARE/logs/main_extraction.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class HubSpotExtractor:
    """Extrae datos de HubSpot vía API"""
    
    def __init__(self, api_key: str, account_id: str):
        self.api_key = api_key
        self.account_id = account_id
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, endpoint: str, params: dict = None, method: str = "GET") -> dict:
        """Hace request a la API de HubSpot con manejo de errores"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "POST":
                response = requests.post(url, headers=self.headers, json=params)
            else:
                response = requests.get(url, headers=self.headers, params=params)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en request a HubSpot: {e}")
            return {}
    
    def get_contacts_created(self, date: datetime) -> int:
        """Obtiene cantidad de contactos creados en una fecha específica"""
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        start_ts = int(start_of_day.timestamp() * 1000)
        end_ts = int(end_of_day.timestamp() * 1000)
        
        endpoint = "/crm/v3/objects/contacts/search"
        body = {
            "filterGroups": [{
                "filters": [
                    {
                        "propertyName": "createdate",
                        "operator": "GTE",
                        "value": str(start_ts)
                    },
                    {
                        "propertyName": "createdate",
                        "operator": "LT",
                        "value": str(end_ts)
                    }
                ]
            }],
            "properties": ["createdate"],
            "limit": 100
        }
        
        try:
            data = self._make_request(endpoint, params=body, method="POST")
            total = data.get('total', 0)
            logger.info(f"📊 Contactos creados el {date.date()}: {total}")
            return total
        except Exception as e:
            logger.error(f"Error obteniendo contactos creados: {e}")
            return 0


def load_config(config_path: str = "/mnt/user-data/outputs/revops-dashboard-ARE/config/config.yaml") -> dict:
    """Carga la configuración desde archivo YAML"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error cargando configuración: {e}")
        sys.exit(1)


def main():
    """Función principal - Ejecuta extracción completa"""
    logger.info("=" * 80)
    logger.info("🚀 INICIANDO EXTRACCIÓN COMPLETA")
    logger.info("=" * 80)
    
    # Cargar configuración
    config = load_config()
    
    # Validar API key
    api_key = config['hubspot']['api_key']
    if api_key == "TU_API_KEY_AQUI":
        logger.error("❌ ERROR: Debes configurar tu API key de HubSpot en config/config.yaml")
        sys.exit(1)
    
    # Fecha a procesar (ayer)
    yesterday = datetime.now() - timedelta(days=config['extraction']['days_back'])
    logger.info(f"📅 Procesando datos para: {yesterday.date()}")
    
    # ========================================
    # 1. EXTRACCIÓN DE GOOGLE CALENDAR
    # ========================================
    logger.info("\n" + "="*80)
    logger.info("🗓️  PASO 1: Extracción de Google Calendar")
    logger.info("="*80)
    
    calendar_extractor = CalendarExtractor(config)
    calendar_metrics = calendar_extractor.extract_events(yesterday)
    
    # ========================================
    # 2. EXTRACCIÓN DE HUBSPOT
    # ========================================
    logger.info("\n" + "="*80)
    logger.info("📊 PASO 2: Extracción de HubSpot")
    logger.info("="*80)
    
    hubspot_extractor = HubSpotExtractor(
        api_key=api_key,
        account_id=config['hubspot']['account_id']
    )
    
    leads_creados = hubspot_extractor.get_contacts_created(yesterday)
    
    # ========================================
    # 3. CONSOLIDAR DATOS
    # ========================================
    logger.info("\n" + "="*80)
    logger.info("📋 PASO 3: Consolidando datos")
    logger.info("="*80)
    
    consolidated_data = {
        'fecha': yesterday.strftime('%Y-%m-%d'),
        'leads_creados': leads_creados,
        'reuniones': calendar_metrics
    }
    
    # Guardar en JSON para debugging
    output_file = f"/mnt/user-data/outputs/revops-dashboard-ARE/data/extracted_{yesterday.strftime('%Y%m%d')}.json"
    with open(output_file, 'w') as f:
        json.dump(consolidated_data, f, indent=2)
    logger.info(f"💾 Datos guardados en: {output_file}")
    
    # ========================================
    # 4. RESUMEN FINAL
    # ========================================
    logger.info("\n" + "="*80)
    logger.info("✅ RESUMEN DE EXTRACCIÓN")
    logger.info("="*80)
    logger.info(f"Fecha procesada: {yesterday.date()}")
    logger.info(f"Leads creados: {leads_creados}")
    logger.info(f"\nReuniones por setter:")
    
    for setter, metrics in calendar_metrics.items():
        if metrics['agendadas'] > 0:
            show_up = (metrics['realizadas'] / metrics['agendadas']) * 100
            logger.info(f"  {setter:10} | Agendadas: {metrics['agendadas']:2} | Realizadas: {metrics['realizadas']:2} | Show-up: {show_up:.1f}%")
    
    logger.info("\n" + "="*80)
    logger.info("🎉 EXTRACCIÓN COMPLETADA EXITOSAMENTE")
    logger.info("="*80)
    
    return consolidated_data


if __name__ == "__main__":
    main()
