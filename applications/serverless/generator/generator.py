"""
Coffee Shop Sales Data Generator

This module generates synthetic coffee shop sales data and sends it to a specified endpoint.
It creates realistic sales records with customer names, coffee types, milk options, sizes, and quantities.
"""

import json
import logging
import random
import time
import uuid
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

import barnum
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('coffee_shop_generator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class CoffeeShopConfig:
    """Configuration class for the coffee shop data generator."""
    
    endpoint_url: str = 'https://coffeeshop.aws.yikyakyuk.com/cashier'
    sleep_interval: float = 0.01
    request_timeout: int = 30
    max_retries: int = 3
    
    # Coffee shop menu options
    coffee_types: tuple = (
        "Flat White", "Americano", "Macchiato", "Cappuccino", 
        "Latte", "Mocha", "Cold Brew"
    )
    milk_types: tuple = ("Full Cream", "Skinny", "Soy", "Almond", "Oat")
    sizes: tuple = ("Small", "Regular", "Large")
    quantity_weights: tuple = (1, 1, 2, 2, 3, 4)  # Weighted towards smaller quantities


class CoffeeShopDataGenerator:
    """
    A class to generate and send synthetic coffee shop sales data.
    
    This class creates realistic sales records and sends them to a specified endpoint
    with proper error handling, logging, and retry mechanisms.
    """
    
    def __init__(self, config: Optional[CoffeeShopConfig] = None):
        """
        Initialize the CoffeeShopDataGenerator.
        
        Args:
            config: Configuration object. If None, uses default configuration.
        """
        self.config = config or CoffeeShopConfig()
        self.session = self._create_session()
        logger.info("Coffee Shop Data Generator initialized")
    
    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry strategy and connection pooling.
        
        Returns:
            Configured requests session with retry strategy.
        """
        session = requests.Session()
        
        try:
            # Configure retry strategy - handle both old and new urllib3 versions
            retry_kwargs = {
                'total': self.config.max_retries,
                'status_forcelist': [429, 500, 502, 503, 504],
                'backoff_factor': 1
            }
            
            # Try new parameter name first, fallback to old one
            try:
                retry_strategy = Retry(
                    allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
                    **retry_kwargs
                )
            except TypeError:
                # Fallback for older urllib3 versions
                retry_strategy = Retry(
                    method_whitelist=["HEAD", "GET", "OPTIONS", "POST"],
                    **retry_kwargs
                )
            
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
        except Exception as e:
            logger.warning(f"Could not configure retry strategy: {e}. Using basic session.")
        
        # Set default headers
        session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'CoffeeShopDataGenerator/1.0'
        })
        
        return session
    
    def generate_sale_record(self) -> Dict[str, Any]:
        """
        Generate a synthetic sales record with realistic data.
        
        Returns:
            Dictionary containing sale record with customer info, products, and metadata.
            
        Example:
            {
                "customer": "John Doe",
                "saleid": "abc123def456",
                "timestamp": "2023-12-07 14:30:15",
                "coffee": "Latte",
                "milk": "Oat",
                "size": "Regular",
                "qty": 2
            }
        """
        try:
            # Generate customer name using barnum
            customer_name = barnum.create_name()
            customer = f"{customer_name[0]} {customer_name[1]}" if len(customer_name) > 1 else str(customer_name[0])
            
            # Generate unique sale ID (using last 12 characters for brevity)
            sale_id = str(uuid.uuid4()).replace('-', '')[-12:]
            
            # Generate current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Select random menu items
            record = {
                "customer": customer,
                "saleid": sale_id,
                "timestamp": timestamp,
                "coffee": random.choice(self.config.coffee_types),
                "milk": random.choice(self.config.milk_types),
                "size": random.choice(self.config.sizes),
                "qty": random.choice(self.config.quantity_weights)
            }
            
            logger.debug(
                f"Generated sale record - ID: {record['saleid']}, "
                f"Customer: {record['customer']}, "
                f"Order: {record['qty']}x {record['size']} {record['coffee']} with {record['milk']}"
            )
            
            return record
            
        except Exception as e:
            logger.error(f"Error generating sale record: {str(e)}")
            raise
    
    def send_sale_record(self, record: Dict[str, Any]) -> bool:
        """
        Send a sale record to the configured endpoint.
        
        Args:
            record: Dictionary containing the sale record to send.
            
        Returns:
            True if the record was sent successfully, False otherwise.
        """
        try:
            response = self.session.post(
                self.config.endpoint_url,
                data=json.dumps(record),
                timeout=self.config.request_timeout
            )
            
            response.raise_for_status()
            
            logger.info(
                f"Successfully sent sale record {record['saleid']} - "
                f"Status: {response.status_code}"
            )
            return True
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout sending record {record['saleid']} to {self.config.endpoint_url}")
            return False
            
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error sending record {record['saleid']} to {self.config.endpoint_url}")
            return False
            
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"HTTP error {e.response.status_code} sending record {record['saleid']}: "
                f"{e.response.text}"
            )
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error sending record {record['saleid']}: {str(e)}")
            return False
    
    def run_continuous_generation(self) -> None:
        """
        Run the data generator continuously, creating and sending sales records.
        
        This method runs indefinitely until interrupted (Ctrl+C).
        """
        logger.info(
            f"Starting continuous data generation - "
            f"Endpoint: {self.config.endpoint_url}, "
            f"Interval: {self.config.sleep_interval}s"
        )
        
        records_sent = 0
        records_failed = 0
        
        try:
            while True:
                # Generate and send record
                record = self.generate_sale_record()
                
                if self.send_sale_record(record):
                    records_sent += 1
                else:
                    records_failed += 1
                
                # Log periodic statistics
                if (records_sent + records_failed) % 100 == 0:
                    success_rate = (records_sent / (records_sent + records_failed)) * 100 if (records_sent + records_failed) > 0 else 0
                    logger.info(
                        f"Statistics - Sent: {records_sent}, "
                        f"Failed: {records_failed}, "
                        f"Success Rate: {success_rate:.1f}%"
                    )
                
                # Wait before next iteration
                time.sleep(self.config.sleep_interval)
                
        except KeyboardInterrupt:
            logger.info(
                f"Generator stopped by user - "
                f"Final stats - Sent: {records_sent}, Failed: {records_failed}"
            )
        except Exception as e:
            logger.error(f"Unexpected error in continuous generation: {str(e)}")
            raise
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources."""
        if hasattr(self, 'session'):
            self.session.close()


def main():
    """
    Main function to run the coffee shop data generator.
    
    Creates a generator instance and runs it continuously.
    """
    # You can customize configuration here
    config = CoffeeShopConfig(
        endpoint_url='https://coffeeshop.aws.yikyakyuk.com/cashier',
        sleep_interval=0.1,
        request_timeout=30,
        max_retries=3
    )
    
    # Use context manager for proper resource cleanup
    with CoffeeShopDataGenerator(config) as generator:
        generator.run_continuous_generation()


if __name__ == "__main__":
    main()
