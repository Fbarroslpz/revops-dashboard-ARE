#!/usr/bin/env python3
"""
Extractor de Google Calendar vía feed iCal público
Identifica reuniones por setter usando colores y títulos
NO requiere autenticación OAuth

Autor: Felipe Barros
Fecha: Enero 2026
"""

import os
import sys
import yaml
import logging
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from icalendar import Calendar
import pytz

# Configurar logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/calendar_extraction.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class CalendarExtractor:
    """Extrae reuniones del calendario público de ARE"""
    
    def __init__(self, config: dict):
        self.config = config
        self.ical_url = config['google_calendar']['ical_url']
        self.timezone = pytz.timezone(config['extraction']['timezone'])
        
        # Mapeo de colores
        self.color_mapping = config['google_calendar']['color_mapping']
        self.no_show_colors = config['google_calendar']['no_show_colors']
        
        # Patrones de títulos
        self.robot_pattern = config['google_calendar']['robot_title_pattern']
        self.human_pattern = config['google_calendar']['human_title_pattern']
    
    def download_ical(self) -> Calendar:
        """Descarga el feed iCal del calendario público"""
        try:
            logger.info(f"Descargando iCal desde: {self.ical_url}")
            response = requests.get(self.ical_url, timeout=30)
            response.raise_for_status()
            
            cal = Calendar.from_ical(response.content)
            logger.info("✅ iCal descargado exitosamente")
            return cal
        except Exception as e:
            logger.error(f"❌ Error descargando iCal: {e}")
            return None
    
    def identify_setter_by_title_and_color(self, title: str, color: str) -> str:
        """
        Identifica el setter basado en título y color
        
        Lógica:
        - Negro (8) = Teresa
        - Verde (2) = Daniela  
        - Azul (9) = Matias O Robot
          - Si título empieza con "Asesoría Inmobiliaria" → Robot
          - Si título empieza con "Reunion" → Matias
        """
        # Normalizar título
        title_lower = title.lower().strip()
        
        # Verificar color directo (Negro o Verde)
        if color == "8":  # Negro
            return "Teresa"
        elif color == "2":  # Verde
            return "Daniela"
        elif color == "9":  # Azul (Matias o Robot)
            # Distinguir por título
            if title.startswith(self.robot_pattern):
                return "Robot"
            elif "reunion" in title_lower:
                return "Matias"
            else:
                # Default para azul sin patrón claro
                return "Matias"
        else:
            return "Desconocido"
    
    def is_completed(self, color: str) -> bool:
        """
        Determina si la reunión se realizó basándose en el color final
        
        Lógica:
        - Si el color es Naranjo (6) o Rojo (11) → NO se realizó
        - Si mantiene el color original del setter → SÍ se realizó
        """
        return color not in self.no_show_colors
    
    def extract_events(self, date: datetime) -> dict:
        """
        Extrae eventos de una fecha específica
        
        Returns:
            {
                'Daniela': {'agendadas': X, 'realizadas': Y, 'eventos': [...]},
                'Teresa': {...},
                'Matias': {...},
                'Robot': {...}
            }
        """
        cal = self.download_ical()
        if not cal:
            return {}
        
        # Definir rango de fechas (todo el día)
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        # Inicializar métricas
        metrics = {
            'Daniela': {'agendadas': 0, 'realizadas': 0, 'eventos': []},
            'Teresa': {'agendadas': 0, 'realizadas': 0, 'eventos': []},
            'Matias': {'agendadas': 0, 'realizadas': 0, 'eventos': []},
            'Robot': {'agendadas': 0, 'realizadas': 0, 'eventos': []}
        }
        
        logger.info(f"Extrayendo eventos para: {date.date()}")
        
        # Procesar eventos
        for component in cal.walk('VEVENT'):
            try:
                # Obtener fecha del evento
                dtstart = component.get('dtstart').dt
                
                # Si es datetime, convertir a timezone correcto
                if isinstance(dtstart, datetime):
                    if dtstart.tzinfo is None:
                        dtstart = self.timezone.localize(dtstart)
                    else:
                        dtstart = dtstart.astimezone(self.timezone)
                else:
                    # Si es date, convertir a datetime
                    dtstart = datetime.combine(dtstart, datetime.min.time())
                    dtstart = self.timezone.localize(dtstart)
                
                # Filtrar por fecha
                if not (start_of_day <= dtstart < end_of_day):
                    continue
                
                # Extraer datos del evento
                title = str(component.get('summary', 'Sin título'))
                color = str(component.get('color', ''))
                
                # Identificar setter
                setter = self.identify_setter_by_title_and_color(title, color)
                
                if setter == "Desconocido":
                    logger.warning(f"⚠️ Evento sin setter identificado: {title} (color: {color})")
                    continue
                
                # Determinar si se completó
                completed = self.is_completed(color)
                
                # Registrar evento
                event_data = {
                    'title': title,
                    'time': dtstart.strftime('%H:%M'),
                    'color': color,
                    'completed': completed
                }
                
                metrics[setter]['agendadas'] += 1
                if completed:
                    metrics[setter]['realizadas'] += 1
                
                metrics[setter]['eventos'].append(event_data)
                
                logger.debug(f"  {setter}: {title} - {'✅ Realizada' if completed else '❌ No realizada'}")
                
            except Exception as e:
                logger.error(f"Error procesando evento: {e}")
                continue
        
        # Log resumen
        logger.info("\n" + "="*60)
        logger.info("📊 RESUMEN DE REUNIONES:")
        logger.info("="*60)
        for setter, data in metrics.items():
            agendadas = data['agendadas']
            realizadas = data['realizadas']
            if agendadas > 0:
                show_up_rate = (realizadas / agendadas) * 100
                logger.info(f"{setter:10} | Agendadas: {agendadas:2} | Realizadas: {realizadas:2} | Show-up: {show_up_rate:.1f}%")
        logger.info("="*60)
        
        return metrics


def load_config(config_path: str = "config/config.yaml") -> dict:
    """Carga la configuración desde archivo YAML"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error cargando configuración: {e}")
        sys.exit(1)


def main():
    """Función principal"""
    logger.info("=" * 80)
    logger.info("🗓️  Iniciando extracción de Google Calendar")
    logger.info("=" * 80)
    
    # Cargar configuración
    config = load_config()
    
    # Inicializar extractor
    extractor = CalendarExtractor(config)
    
    # Fecha a extraer (ayer)
    yesterday = datetime.now(extractor.timezone) - timedelta(days=config['extraction']['days_back'])
    
    # Extraer eventos
    metrics = extractor.extract_events(yesterday)
    
    # Mostrar resultados
    print("\n" + "="*60)
    print("📊 MÉTRICAS EXTRAÍDAS:")
    print("="*60)
    for setter, data in metrics.items():
        if data['agendadas'] > 0:
            print(f"\n{setter}:")
            print(f"  Reuniones agendadas: {data['agendadas']}")
            print(f"  Reuniones realizadas: {data['realizadas']}")
            print(f"  Show-up rate: {(data['realizadas']/data['agendadas']*100):.1f}%")
            print(f"\n  Detalle:")
            for evento in data['eventos']:
                status = "✅" if evento['completed'] else "❌"
                print(f"    {status} {evento['time']} - {evento['title']}")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ Extracción de Calendar completada")
    logger.info("=" * 80)
    
    return metrics


if __name__ == "__main__":
    main()
