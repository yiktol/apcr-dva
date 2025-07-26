import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class AWSConfig:
    """AWS Configuration settings"""
    region: str = "ap-southeast-1"
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    queue_url: Optional[str] = None
    dlq_url: Optional[str] = None

def load_aws_config() -> AWSConfig:
    """Load AWS configuration from environment variables"""
    return AWSConfig(
        region=os.getenv("AWS_REGION", "ap-southeast-1"),
        access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        queue_url=os.getenv("SQS_QUEUE_URL","https://sqs.ap-southeast-1.amazonaws.com/875692608981/dev-main-queue"),
        dlq_url=os.getenv("SQS_DLQ_URL","https://sqs.ap-southeast-1.amazonaws.com/875692608981/dev-dlq")
    )

# Sample message templates
SAMPLE_MESSAGES = [
    {
        "id": "order_001",
        "type": "order",
        "data": {
            "customer_id": "cust_12345",
            "items": [
                {"product": "laptop", "quantity": 1, "price": 999.99},
                {"product": "mouse", "quantity": 2, "price": 25.99}
            ],
            "total": 1051.97
        }
    },
    {
        "id": "user_002",
        "type": "user_registration",
        "data": {
            "username": "john_doe",
            "email": "john@example.com",
            "registration_date": "2025-01-01T10:30:00Z"
        }
    },
    {
        "id": "notification_003",
        "type": "notification",
        "data": {
            "recipient": "admin@company.com",
            "subject": "System Alert",
            "message": "High CPU usage detected on server-01",
            "priority": "high"
        }
    },
    {
        "id": "inventory_004",
        "type": "inventory_update",
        "data": {
            "product_id": "prod_5678",
            "current_stock": 150,
            "reorder_level": 50,
            "action": "restock_required"
        }
    }
]

# Styling configuration
CUSTOM_CSS = """
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #4ECDC4;
    }
    
    .message-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF6B6B;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .priority-high {
        border-left-color: #FF4757 !important;
    }
    
    .priority-medium {
        border-left-color: #FFA726 !important;
    }
    
    .priority-low {
        border-left-color: #66BB6A !important;
    }
    
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: #666;
        text-align: center;
        padding: 10px;
        font-size: 12px;
        z-index: 999;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4ECDC4;
        color: white;
    }
</style>
"""