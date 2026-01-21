#!/usr/bin/env python3
"""
Utilidades comunes para los scripts de extracción
Incluye retry logic, validaciones, y helpers

Autor: Felipe Barros - Vulpes Consulting
Fecha: Enero 2026
"""

import time
import logging
import functools
from typing import Callable, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


def create_session_with_retries(
    retries: int = 3,
    backoff_factor: float = 0.5,
    status_forcelist: tuple = (500, 502, 503, 504)
) -> requests.Session:
    """
    Crea una sesión de requests con retry automático

    Args:
        retries: Número de reintentos
        backoff_factor: Factor de espera exponencial (0.5 = 0.5s, 1s, 2s...)
        status_forcelist: Códigos HTTP que deben reintentar

    Returns:
        requests.Session configurada con retry logic
    """
    session = requests.Session()

    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def retry_on_exception(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorador para reintentar funciones que fallan

    Args:
        max_attempts: Número máximo de intentos
        delay: Delay inicial en segundos
        backoff: Multiplicador del delay en cada intento
        exceptions: Tupla de excepciones a capturar

    Example:
        @retry_on_exception(max_attempts=3, delay=1.0)
        def my_function():
            # código que puede fallar
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(f"❌ {func.__name__} falló después de {max_attempts} intentos")
                        raise

                    logger.warning(
                        f"⚠️ {func.__name__} falló (intento {attempt}/{max_attempts}). "
                        f"Reintentando en {current_delay:.1f}s... Error: {str(e)}"
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff

            # Este código nunca debería ejecutarse, pero por seguridad
            raise last_exception

        return wrapper
    return decorator


def validate_api_key(api_key: str, key_name: str = "API key") -> None:
    """
    Valida que una API key no esté vacía o sea un placeholder

    Args:
        api_key: La API key a validar
        key_name: Nombre de la key para el mensaje de error

    Raises:
        ValueError: Si la API key es inválida
    """
    if not api_key:
        raise ValueError(f"❌ {key_name} está vacía")

    placeholders = [
        "TU_API_KEY_AQUI",
        "YOUR_API_KEY_HERE",
        "REPLACE_ME",
        "XXX",
        "tu_api_key_aqui"
    ]

    if api_key in placeholders:
        raise ValueError(
            f"❌ {key_name} no está configurada. "
            f"Por favor configura la API key real en config/config.yaml"
        )

    logger.info(f"✅ {key_name} validada (termina en ...{api_key[-4:]})")


def validate_url(url: str, url_name: str = "URL") -> None:
    """
    Valida que una URL sea válida

    Args:
        url: La URL a validar
        url_name: Nombre de la URL para el mensaje de error

    Raises:
        ValueError: Si la URL es inválida
    """
    if not url:
        raise ValueError(f"❌ {url_name} está vacía")

    if not url.startswith(('http://', 'https://')):
        raise ValueError(f"❌ {url_name} debe empezar con http:// o https://")

    logger.debug(f"✅ {url_name} validada: {url}")


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    División segura que maneja división por cero

    Args:
        numerator: Numerador
        denominator: Denominador
        default: Valor a retornar si el denominador es 0

    Returns:
        Resultado de la división o default
    """
    if denominator == 0:
        return default
    return numerator / denominator


def calculate_show_up_rate(realizadas: int, agendadas: int) -> float:
    """
    Calcula el show-up rate como porcentaje

    Args:
        realizadas: Reuniones realizadas
        agendadas: Reuniones agendadas

    Returns:
        Show-up rate como porcentaje (0-100)
    """
    return safe_divide(realizadas, agendadas, default=0.0) * 100


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Formatea un porcentaje para display

    Args:
        value: Valor del porcentaje (0-100)
        decimals: Número de decimales

    Returns:
        String formateado (ej: "85.5%")
    """
    return f"{value:.{decimals}f}%"


def format_currency(value: float, currency: str = "CLP") -> str:
    """
    Formatea un valor monetario

    Args:
        value: Valor a formatear
        currency: Moneda (CLP, USD, etc)

    Returns:
        String formateado (ej: "$1,234,567 CLP")
    """
    if currency == "CLP":
        # Para pesos chilenos, sin decimales
        return f"${value:,.0f} {currency}"
    else:
        return f"${value:,.2f} {currency}"


class ProgressLogger:
    """Clase helper para logging de progreso"""

    def __init__(self, total: int, description: str = "Procesando"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()

    def update(self, increment: int = 1):
        """Actualiza el progreso"""
        self.current += increment
        percentage = (self.current / self.total) * 100
        elapsed = time.time() - self.start_time

        if self.current == self.total:
            logger.info(
                f"✅ {self.description} completado: "
                f"{self.current}/{self.total} ({percentage:.1f}%) "
                f"en {elapsed:.1f}s"
            )
        elif self.current % max(1, self.total // 10) == 0:
            # Log cada 10%
            logger.info(
                f"⏳ {self.description}: "
                f"{self.current}/{self.total} ({percentage:.1f}%)"
            )


def get_nested_value(dictionary: dict, keys: list, default: Any = None) -> Any:
    """
    Obtiene un valor anidado de un diccionario de forma segura

    Args:
        dictionary: Diccionario fuente
        keys: Lista de keys para navegar
        default: Valor por defecto si no existe

    Returns:
        El valor encontrado o default

    Example:
        >>> data = {'a': {'b': {'c': 123}}}
        >>> get_nested_value(data, ['a', 'b', 'c'])
        123
        >>> get_nested_value(data, ['a', 'x', 'y'], default=0)
        0
    """
    current = dictionary
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current
