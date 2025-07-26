"""Configuration settings for the SNS-SQS Streamlit application."""

import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class AWSConfig:
    """AWS configuration settings."""
    region: str
    topic_arn: str
    queue_urls: Dict[str, str]
    
    @classmethod
    def from_env(cls) -> 'AWSConfig':
        """Create configuration from environment variables."""
        return cls(
            region=os.getenv('AWS_REGION', 'ap-southeast-1'),
            topic_arn=os.getenv('SNS_TOPIC_ARN', 'arn:aws:sns:ap-southeast-1:875692608981:dev-message-topic'),
            queue_urls={
                'subscriber_1': os.getenv('SUBSCRIBER_1_QUEUE_URL', 'https://sqs.ap-southeast-1.amazonaws.com/875692608981/dev-subscriber-1-queue'),
                'subscriber_2': os.getenv('SUBSCRIBER_2_QUEUE_URL', 'https://sqs.ap-southeast-1.amazonaws.com/875692608981/dev-subscriber-2-queue'),
                'subscriber_3': os.getenv('SUBSCRIBER_3_QUEUE_URL', 'https://sqs.ap-southeast-1.amazonaws.com/875692608981/dev-subscriber-3-queue'),
            }
        )

@dataclass
class AppConfig:
    """Application configuration settings."""
    page_title: str = "SNS-SQS Publisher-Subscriber Demo"
    page_icon: str = "📨"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"
    
    # UI Configuration
    max_messages_display: int = 10
    message_retention_seconds: int = 300
    auto_refresh_interval: int = 5

# Sample message templates
SAMPLE_MESSAGES = [
    {
        "type": "notification",
        "title": "System Alert",
        "message": "Database backup completed successfully",
        "priority": "medium",
        "category": "system"
    },
    {
        "type": "user_action",
        "title": "New User Registration",
        "message": "User john.doe@example.com has registered for the platform",
        "priority": "low",
        "category": "user"
    },
    {
        "type": "error",
        "title": "Service Error",
        "message": "Payment service is experiencing high latency",
        "priority": "high",
        "category": "error"
    },
    {
        "type": "marketing",
        "title": "Campaign Launch",
        "message": "Summer sale campaign has been activated",
        "priority": "low",
        "category": "marketing"
    },
    {
        "type": "security",
        "title": "Security Alert",
        "message": "Multiple failed login attempts detected for admin user",
        "priority": "high",
        "category": "security"
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