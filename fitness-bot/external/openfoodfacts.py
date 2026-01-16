"""
Клиент для Open Food Facts API
https://world.openfoodfacts.org/
"""
import asyncio
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class OFFProduct:
    """Продукт из Open Food Facts"""
    barcode: str
    name: str
    brand: Optional[str]
    calories_100g: float
    protein_100g: float
    fat_100g: float
    carbs_100g: float
    fiber_100g: Optional[float]
    image_url: Optional[str]
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> Optional["OFFProduct"]:
        """Создать объект из ответа API"""
        try:
            product = data.get("product", {})
            
            # Извлекаем нутриенты
            nutrients = product.get("nutriments", {})
            
            # Калории могут быть в разных полях
            calories = (
                nutrients.get("energy-kcal_100g") or 
                nutrients.get("energy_100g", 0) / 4.184  # конвертация из кДж
            )
            
            name = (
                product.get("product_name_ru") or
                product.get("product_name") or
                product.get("generic_name") or
                "Неизвестный продукт"
            )
            
            return cls(
                barcode=product.get("code", ""),
                name=name[:200],  # Ограничиваем длину
                brand=product.get("brands", "")[:100] if product.get("brands") else None,
                calories_100g=round(float(calories or 0), 1),
                protein_100g=round(float(nutrients.get("proteins_100g", 0) or 0), 1),
                fat_100g=round(float(nutrients.get("fat_100g", 0) or 0), 1),
                carbs_100g=round(float(nutrients.get("carbohydrates_100g", 0) or 0), 1),
                fiber_100g=round(float(nutrients.get("fiber_100g", 0) or 0), 1) if nutrients.get("fiber_100g") else None,
                image_url=product.get("image_front_small_url")
            )
        except Exception as e:
            logger.error(f"Error parsing OFF product: {e}")
            return None


class OpenFoodFactsClient:
    """Клиент для работы с Open Food Facts API"""
    
    BASE_URL = "https://world.openfoodfacts.org/api/v2"
    SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"
    
    def __init__(self, timeout: int = 10):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Получить или создать сессию"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={
                    "User-Agent": "PersonalTrainerBot/1.0 (Telegram Bot)"
                }
            )
        return self._session
    
    async def close(self):
        """Закрыть сессию"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def get_product_by_barcode(self, barcode: str) -> Optional[OFFProduct]:
        """
        Получить продукт по штрих-коду
        
        Args:
            barcode: штрих-код продукта (EAN-13, EAN-8, UPC-A)
        
        Returns:
            OFFProduct или None если не найден
        """
        try:
            session = await self._get_session()
            url = f"{self.BASE_URL}/product/{barcode}"
            
            async with session.get(url, params={"fields": "product_name,product_name_ru,brands,nutriments,code,generic_name,image_front_small_url"}) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == 1:
                        return OFFProduct.from_api_response(data)
                elif response.status == 404:
                    logger.info(f"Product not found: {barcode}")
                else:
                    logger.warning(f"OFF API error: {response.status}")
        
        except asyncio.TimeoutError:
            logger.warning(f"Timeout getting product {barcode}")
        except Exception as e:
            logger.error(f"Error getting product {barcode}: {e}")
        
        return None
    
    async def search_products(
        self,
        query: str,
        limit: int = 10,
        country: str = "russia"
    ) -> List[OFFProduct]:
        """
        Поиск продуктов по названию
        
        Args:
            query: поисковый запрос
            limit: максимальное количество результатов
            country: страна для фильтрации (russia, ukraine, etc.)
        
        Returns:
            Список найденных продуктов
        """
        try:
            session = await self._get_session()
            
            params = {
                "search_terms": query,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page_size": limit,
                "fields": "product_name,product_name_ru,brands,nutriments,code,generic_name,image_front_small_url",
                "tagtype_0": "countries",
                "tag_contains_0": "contains",
                "tag_0": country
            }
            
            async with session.get(self.SEARCH_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    products = []
                    
                    for item in data.get("products", []):
                        product = OFFProduct.from_api_response({"product": item})
                        if product and product.calories_100g > 0:
                            products.append(product)
                    
                    return products[:limit]
        
        except asyncio.TimeoutError:
            logger.warning(f"Timeout searching products: {query}")
        except Exception as e:
            logger.error(f"Error searching products: {e}")
        
        return []
    
    async def search_products_global(
        self,
        query: str,
        limit: int = 10
    ) -> List[OFFProduct]:
        """
        Глобальный поиск продуктов (без фильтра по стране)
        
        Args:
            query: поисковый запрос
            limit: максимальное количество результатов
        
        Returns:
            Список найденных продуктов
        """
        try:
            session = await self._get_session()
            
            params = {
                "search_terms": query,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page_size": limit,
                "fields": "product_name,product_name_ru,brands,nutriments,code,generic_name,image_front_small_url"
            }
            
            async with session.get(self.SEARCH_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    products = []
                    
                    for item in data.get("products", []):
                        product = OFFProduct.from_api_response({"product": item})
                        if product and product.calories_100g > 0:
                            products.append(product)
                    
                    return products[:limit]
        
        except Exception as e:
            logger.error(f"Error in global search: {e}")
        
        return []


# Глобальный экземпляр клиента
off_client = OpenFoodFactsClient()
