
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import utils.common as common
import utils.authenticate as authenticate

# Page configuration
st.set_page_config(
    page_title="AWS Developer Associate - Session 2",
    page_icon="⚡",
    layout="wide"
)

common.initialize_session_state()

def main():
    # Custom CSS for AWS styling
    st.markdown("""
    <style>
    /* AWS Color Scheme */
    :root {
        --aws-orange: #FF9900;
        --aws-blue: #232F3E;
        --aws-light-blue: #4B9CD3;
        --aws-gray: #879196;
        --aws-white: #FFFFFF;
    }

    .main-header {
        background: linear-gradient(135deg, #232F3E 0%, #4B9CD3 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }

    .service-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border-left: 6px solid #FF9900;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }

    .service-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }

    .info-highlight {
        background: linear-gradient(135deg, #E6F2FF 0%, #CCE7FF 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #00A1C9;
        margin: 1rem 0;
    }

    .training-progress {
        background: linear-gradient(135deg, #FF9900 0%, #FFB84D 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }

    .comparison-card {
        background: #e8f5e8;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }

    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #f39c12;
    }

    .footer {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #232F3E 0%, #4B9CD3 100%);
        color: white;
        margin-top: 3rem;
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

def render_overview():
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>AWS Partner Certification Readiness</h1>
        <h2>Developer - Associate Session 2</h2>
        <h3>Development with AWS Services</h3>
    </div>
    """, unsafe_allow_html=True)

    # Today's Focus
    st.markdown("## 🎯 Today's Focus: Development with AWS Services")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="info-highlight">
            <h3>🚀 What You'll Learn Today</h3>
            <p>In this session, we'll dive deep into AWS services that are essential for application development, 
            focusing on serverless architectures, database services, and application integration patterns.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="training-progress">
            <h4>Session 2 of 6</h4>
            <div style="font-size: 2rem;">⚡</div>
            <p>Development Focus</p>
        </div>
        """, unsafe_allow_html=True)

    # Service Categories
    st.markdown("### 🛠️ AWS Services We'll Cover")
    
    categories = [
        {
            "title": "Compute",
            "icon": "⚡",
            "services": ["AWS Lambda"],
            "color": "#FF9900"
        },
        {
            "title": "Database", 
            "icon": "🗄️",
            "services": ["Amazon DynamoDB", "Amazon RDS"],
            "color": "#4B9CD3"
        },
        {
            "title": "Networking",
            "icon": "🌐", 
            "services": ["Amazon API Gateway"],
            "color": "#52C41A"
        },
        {
            "title": "Integration",
            "icon": "🔄",
            "services": ["Amazon SNS", "Amazon SQS", "AWS Step Functions"],
            "color": "#722ED1"
        }
    ]
    
    cols = st.columns(4)
    for i, category in enumerate(categories):
        with cols[i]:
            st.markdown(f"""
            <div class="service-card" style="border-left-color: {category['color']}">
                <div style="text-align: center; font-size: 2rem;">{category['icon']}</div>
                <h4 style="text-align: center; margin: 1rem 0;">{category['title']}</h4>
                <ul>
                {"".join([f"<li>{service}</li>" for service in category['services']])}
                </ul>
            </div>
            """, unsafe_allow_html=True)

    # Week 2 Training Curriculum
    st.markdown("## 📚 Week 2 Digital Training Curriculum")
    
    training_modules = [
        {"name": "AWS Database Offerings", "type": "Core", "duration": "45 min"},
        {"name": "Amazon ElastiCache Getting Started", "type": "Core", "duration": "30 min"},
        {"name": "Getting into the Serverless Mindset", "type": "Core", "duration": "60 min"},
        {"name": "Amazon DynamoDB for Serverless Architectures", "type": "Core", "duration": "90 min"},
        {"name": "AWS Cloud Quest: Serverless Developer", "type": "Optional", "duration": "2 hours"},
        {"name": "Working with Amazon ECS Lab", "type": "Optional", "duration": "90 min"}
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Required Courses")
        for module in training_modules:
            if module["type"] == "Core":
                st.markdown(f"""
                <div class="comparison-card">
                    <strong>{module['name']}</strong><br>
                    <small>Duration: {module['duration']}</small>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Optional Courses")
        for module in training_modules:
            if module["type"] == "Optional":
                st.markdown(f"""
                <div class="warning-box">
                    <strong>{module['name']}</strong><br>
                    <small>Duration: {module['duration']}</small>
                </div>
                """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="footer">
        <h3>🚀 Welcome to Session 2!</h3>
        <p>Ready to dive deep into AWS development services and serverless architectures.</p>
        <p><strong>Focus:</strong> Building scalable applications with AWS managed services</p>
        <p style="margin-top: 1rem; font-size: 0.9em;">
            Let's build something amazing together! 🎯
        </p>
    </div>
    """, unsafe_allow_html=True)

# Main execution flow
if __name__ == "__main__":
    if 'localhost' in st.context.headers["host"]:
        main()
        render_overview()
    else:
        # First check authentication
        is_authenticated = authenticate.login()
        
        # If authenticated, show the main app content
        if is_authenticated:
            main()
            render_overview()
