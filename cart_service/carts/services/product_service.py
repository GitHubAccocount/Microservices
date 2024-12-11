import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ProductService:
    def __init__(self):
        self.base_url = settings.PRODUCT_SERVICE_URL
        
    def get_product(self, product_id):
        try:
            response = requests.get(f"{self.base_url}/api/products/{product_id}/")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching product {product_id}: {str(e)}")
            raise