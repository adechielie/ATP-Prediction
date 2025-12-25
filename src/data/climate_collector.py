"""
Collecteur de données climatiques depuis Open-Meteo API.
"""
print(">>> Climate collector loaded from THIS FILE")
from typing import Optional, Tuple, Dict, List
import time
from pathlib import Path

import pandas as pd
import requests
from loguru import logger
import openmeteo_requests
import requests_cache
from retry_requests import retry

from ..utils.config import config


class ClimateDataCollector:
    """Collecte les données climatiques pour les villes de tournois ATP."""
    
    def __init__(self):
        self.api_url = config.get('data.sources.climate.api_url')
        self.start_date = config.get('data.sources.climate.start_date')
        self.end_date = config.get('data.sources.climate.end_date')
        self.raw_path = config.data_paths['raw']
        self.raw_path.mkdir(parents=True, exist_ok=True)
        
        # Setup cache & retry
        cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.client = openmeteo_requests.Client(session=retry_session)
    
    def get_city_coordinates(
        self,
        city: str,
        timeout: int = 5
    ) -> Optional[Tuple[float, float]]:
        """
        Récupère les coordonnées GPS d'une ville via OpenStreetMap Nominatim.
        
        Args:
            city: Nom de la ville
            timeout: Timeout de la requête en secondes
        
        Returns:
            Tuple (latitude, longitude) ou None si erreur
        """
        headers = {"User-Agent": "ATP-Prediction/1.0 (adechielie@yahoo.fr)"}
        geocode_url = f"https://nominatim.openstreetmap.org/search?city={city}&format=json"
        
        try:
            response = requests.get(geocode_url, headers=headers, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            
            if data:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                logger.debug(f"✅ {city}: ({lat}, {lon})")
                return (lat, lon)
            else:
                logger.warning(f"⚠️  No coordinates found for {city}")
                return None
        
        except Exception as e:
            logger.error(f"❌ Error fetching coordinates for {city}: {e}")
            return None
    
    def get_all_city_coordinates(
        self,
        cities: List[str],
        rate_limit_delay: float = 1.0
    ) -> Dict[str, Tuple[float, float]]:
        """
        Récupère les coordonnées de toutes les villes.
        
        Args:
            cities: Liste des villes
            rate_limit_delay: Délai entre les requêtes (secondes)
        
        Returns:
            Dictionnaire {city: (lat, lon)}
        """
        coordinates = {}
        
        logger.info(f"Fetching coordinates for {len(cities)} cities...")
        
        for city in cities:
            coords = self.get_city_coordinates(city)
            if coords:
                coordinates[city] = coords
            
            # Respecter les limites de taux de l'API
            time.sleep(rate_limit_delay)
        
        logger.success(f"✅ Retrieved coordinates for {len(coordinates)} cities")
        
        return coordinates
    
    def fetch_climate_data(
        self,
        coordinates: Dict[str, Tuple[float, float]]
    ) -> pd.DataFrame:
        """
        Récupère les données climatiques pour toutes les villes.
        
        Args:
            coordinates: Dictionnaire {city: (lat, lon)}
        
        Returns:
            DataFrame avec les données climatiques
        """
        if not coordinates:
            raise ValueError("No coordinates provided!")
        
        # Préparer les listes de latitudes et longitudes
        cities = list(coordinates.keys())
        latitudes = [str(coords[0]) for coords in coordinates.values()]
        longitudes = [str(coords[1]) for coords in coordinates.values()]
        
        logger.info(f"Fetching climate data for {len(cities)} locations...")
        
        # Paramètres de l'API
        params = {
            "latitude": ",".join(latitudes),
            "longitude": ",".join(longitudes),
            "start_date": self.start_date,
            "end_date": self.end_date,
            "daily": "temperature_2m_max,wind_speed_10m_max",
            "timezone": "auto"
        }
        
        # Appel API
        responses = self.client.weather_api(self.api_url, params=params)
        
        # Traiter les réponses
        dataframes = []
        
        for city, response in zip(cities, responses):
            try:
                daily = response.Daily()
                
                if daily is None:
                    logger.warning(f"⚠️  No data for {city}")
                    continue
                
                # Extraire les variables
                temperature = daily.Variables(0).ValuesAsNumpy()
                wind_speed = daily.Variables(1).ValuesAsNumpy()
                
                # Créer le DataFrame
                df = pd.DataFrame({
                    "city": city,
                    "date": pd.date_range(
                        start=self.start_date,
                        end=self.end_date,
                        freq="D"
                    ),
                    "temperature_2m_max": temperature,
                    "wind_speed_10m_max": wind_speed
                })
                
                dataframes.append(df)
                logger.debug(f"✅ Processed {city}: {len(df)} days")
            
            except Exception as e:
                logger.error(f"❌ Error processing {city}: {e}")
                continue
        
        if not dataframes:
            raise ValueError("No climate data collected!")
        
        # Combiner tous les DataFrames
        climate_df = pd.concat(dataframes, ignore_index=True)
        
        logger.success(
            f"✅ Collected {len(climate_df):,} climate records for {len(dataframes)} cities"
        )
        
        return climate_df
    
    def collect_climate_data(
        self,
        cities: Optional[List[str]] = None,
        save_to_disk: bool = True
    ) -> pd.DataFrame:
        """
        Workflow complet de collecte des données climatiques.
        
        Args:
            cities: Liste des villes (utilise config par défaut si None)
            save_to_disk: Sauvegarder sur disque
        
        Returns:
            DataFrame des données climatiques
        """
        # Utiliser les villes des tournois si non spécifié
        if cities is None:
            location_mapping = config.location_mapping
            cities = list(set(location_mapping.values()))
        
        # Étape 1: Récupérer les coordonnées
        coordinates = self.get_all_city_coordinates(cities)
        
        # Étape 2: Récupérer les données climatiques
        climate_df = self.fetch_climate_data(coordinates)
        
        # Étape 3: Sauvegarder si demandé
        if save_to_disk:
            file_path = self.raw_path / "climate_data.csv"
            climate_df.to_csv(file_path, index=False)
            logger.info(f"💾 Saved climate data to {file_path}")
        
        return climate_df
    
    def load_from_disk(self) -> pd.DataFrame:
        """
        Charge les données climatiques depuis le disque.
        
        Returns:
            DataFrame des données climatiques
        """
        file_path = self.raw_path / "climate_data.csv"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Climate data not found: {file_path}")
        
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'])
        
        logger.info(f"Loaded {len(df):,} climate records from disk")
        
        return df
    
    def get_or_fetch_data(
        self,
        force_download: bool = False
    ) -> pd.DataFrame:
        """
        Récupère les données depuis le disque ou télécharge si nécessaire.
        
        Args:
            force_download: Forcer le téléchargement
        
        Returns:
            DataFrame des données climatiques
        """
        if force_download:
            return self.collect_climate_data()
        
        try:
            return self.load_from_disk()
        except FileNotFoundError:
            logger.info("No local climate data found, downloading...")
            return self.collect_climate_data()
