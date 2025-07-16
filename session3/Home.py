
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import utils.common as common
import utils.authenticate as authenticate

# Page configuration
st.set_page_config(
    page_title="AWS Developer Associate - Session 3",
    page_icon="🔄",
    layout="wide"
)

common.initialize_session_state()

with st.sidebar:
    common.render_sidebar()

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

    .database-card {
        background: #f0f8ff;
        border: 1px solid #4B9CD3;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #232F3E;
    }

    .monitoring-card {
        background: #f8f8f8;
        border: 1px solid #879196;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #FF9900;
    }

    .auth-card {
        background: #fef9e7;
        border: 1px solid #FF9900;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #52C41A;
    }

    .footer {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #232F3E 0%, #4B9CD3 100%);
        color: white;
        margin-top: 3rem;
        border-radius: 15px;
    }

    .event-flow {
        background: #f5f5f5;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-family: monospace;
    }
    </style>
    """, unsafe_allow_html=True)

def render_overview():
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>AWS Partner Certification Readiness</h1>
        <h2>Developer - Associate Session 3</h2>
        <h3>Application Integration & Development Services</h3>
        <p style="margin-top: 1rem; font-size: 1.1em;">Focus on serverless architectures, event-driven patterns, and monitoring</p>
    </div>
    """, unsafe_allow_html=True)

    # Progress indicator
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="training-progress">
            <h4>Session 3 of 6</h4>
            <div style="font-size: 2rem;">🔄</div>
            <p>Application Integration Focus</p>
        </div>
        """, unsafe_allow_html=True)

def render_learning_objectives():
    st.markdown("## 🎯 What You'll Learn Today")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        <div class="info-highlight">
            <h3>🚀 Core Learning Objectives</h3>
            <ul>
                <li><strong>Application Integration:</strong> Master SNS, SQS, and EventBridge patterns</li>
                <li><strong>Serverless Development:</strong> Build event-driven architectures</li>
                <li><strong>Database Caching:</strong> Implement ElastiCache strategies</li>
                <li><strong>Authentication:</strong> Secure applications with AWS Cognito</li>
                <li><strong>Monitoring & Observability:</strong> CloudWatch and CloudTrail integration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="event-flow">
            <strong>Event-Driven Flow:</strong><br>
            Producer → Topic/Queue → Consumer<br>
            ↓<br>
            Decoupled & Scalable<br>
            ↓<br>
            Reliable Processing
        </div>
        """, unsafe_allow_html=True)

def render_aws_services():
    st.markdown("## 🛠️ AWS Services We'll Cover")
    
    # Application Integration Services
    st.markdown("### 🔄 Application Integration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="service-card">
            <h4>🔔 Amazon Simple Notification Service (SNS)</h4>
            <p><strong>Pub/Sub Messaging Service</strong></p>
            <ul>
                <li>Fan-out message delivery patterns</li>
                <li>Message filtering and routing</li>
                <li>Multi-protocol support (SMS, Email, HTTP)</li>
                <li>Event-driven architectures</li>
            </ul>
            <div style="background: #e8f4fd; padding: 0.5rem; border-radius: 5px; margin-top: 1rem;">
                <strong>Key Pattern:</strong> One message → Multiple subscribers
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="service-card">
            <h4>🌐 AWS AppSync</h4>
            <p><strong>GraphQL & Pub/Sub API Service</strong></p>
            <ul>
                <li>Serverless GraphQL APIs</li>
                <li>Real-time subscriptions</li>
                <li>Mobile and web app support</li>
                <li>Automatic data synchronization</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="service-card">
            <h4>📤 Amazon Simple Queue Service (SQS)</h4>
            <p><strong>Message Queue Service</strong></p>
            <ul>
                <li>Standard and FIFO queues</li>
                <li>Dead letter queue patterns</li>
                <li>Visibility timeout configuration</li>
                <li>Lambda integration</li>
            </ul>
            <div style="background: #fff7e6; padding: 0.5rem; border-radius: 5px; margin-top: 1rem;">
                <strong>Key Pattern:</strong> Reliable message processing
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="service-card">
            <h4>⚡ Amazon EventBridge</h4>
            <p><strong>Event Bus Service</strong></p>
            <ul>
                <li>Event routing and filtering</li>
                <li>Custom and AWS service events</li>
                <li>Rule-based event processing</li>
                <li>Third-party integrations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Database Services
    st.markdown("### 🗄️ Database & Caching")
    
    st.markdown("""
    <div class="database-card">
        <h4>⚡ Amazon ElastiCache</h4>
        <p><strong>In-Memory Caching Service</strong></p>
        <div style="display: flex; gap: 2rem; margin-top: 1rem;">
            <div style="flex: 1;">
                <h5>Redis</h5>
                <ul>
                    <li>Advanced data structures</li>
                    <li>Persistence & replication</li>
                    <li>Pub/Sub messaging</li>
                    <li>Transactions support</li>
                </ul>
            </div>
            <div style="flex: 1;">
                <h5>Memcached</h5>
                <ul>
                    <li>Multi-threaded architecture</li>
                    <li>Simple key-value storage</li>
                    <li>Horizontal scaling</li>
                    <li>Sub-millisecond latency</li>
                </ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Authentication Services
    st.markdown("### 🔐 Authentication & Authorization")
    
    st.markdown("""
    <div class="auth-card">
        <h4>👤 AWS Cognito</h4>
        <p><strong>User Authentication & Management</strong></p>
        <div style="display: flex; gap: 2rem; margin-top: 1rem;">
            <div style="flex: 1;">
                <h5>User Pools</h5>
                <ul>
                    <li>User sign-up/sign-in</li>
                    <li>Identity verification</li>
                    <li>JWT token management</li>
                </ul>
            </div>
            <div style="flex: 1;">
                <h5>Identity Pools</h5>
                <ul>
                    <li>AWS credential exchange</li>
                    <li>Federated identities</li>
                    <li>Role-based access</li>
                </ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Monitoring Services
    st.markdown("### 📊 Management & Governance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="monitoring-card">
            <h4>📈 Amazon CloudWatch</h4>
            <p><strong>Monitoring & Observability</strong></p>
            <ul>
                <li>Metrics collection & analysis</li>
                <li>Log aggregation & search</li>
                <li>Alarms & notifications</li>
                <li>Dashboard visualization</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="monitoring-card">
            <h4>🔍 AWS CloudTrail</h4>
            <p><strong>API Auditing & Compliance</strong></p>
            <ul>
                <li>API call logging</li>
                <li>Security event tracking</li>
                <li>Compliance reporting</li>
                <li>CloudWatch integration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def render_training_curriculum():
    st.markdown("## 📚 Week 3 Digital Training Curriculum")
    
    st.markdown("""
    <div class="info-highlight">
        <h4>📅 Progress Check & Reminder</h4>
        <p>Do your best to complete this week's training content to stay on track for certification success!</p>
    </div>
    """, unsafe_allow_html=True)

    # Required Courses
    st.markdown("### 🎯 AWS Skill Builder Learning Plan Courses (Required)")
    
    required_courses = [
        {
            "name": "Introduction to Step Functions",
            "focus": "Serverless workflow orchestration",
            "duration": "45 min",
            "topics": ["State machines", "Error handling", "Parallel execution"]
        },
        {
            "name": "Amazon API Gateway for Serverless Applications", 
            "focus": "API management and integration",
            "duration": "60 min",
            "topics": ["REST APIs", "Authentication", "Rate limiting"]
        },
        {
            "name": "Designing Event-Driven Architectures",
            "focus": "Decoupled system design patterns",
            "duration": "90 min",
            "topics": ["Event sourcing", "CQRS", "Saga patterns"]
        },
        {
            "name": "Architecting Serverless Applications",
            "focus": "Best practices and patterns",
            "duration": "75 min", 
            "topics": ["Lambda patterns", "Cold starts", "Cost optimization"]
        },
        {
            "name": "Scaling Serverless Architectures",
            "focus": "Performance and scalability",
            "duration": "60 min",
            "topics": ["Concurrency", "Throttling", "Auto-scaling"]
        },
        {
            "name": "Getting Started with DevOps on AWS",
            "focus": "CI/CD and automation",
            "duration": "90 min",
            "topics": ["CodePipeline", "Infrastructure as Code", "Monitoring"]
        }
    ]

    col1, col2 = st.columns(2)
    
    for i, course in enumerate(required_courses):
        col = col1 if i % 2 == 0 else col2
        with col:
            st.markdown(f"""
            <div class="comparison-card">
                <h5>📖 {course['name']}</h5>
                <p><strong>Focus:</strong> {course['focus']}</p>
                <p><strong>Duration:</strong> {course['duration']}</p>
                <div style="margin-top: 0.5rem;">
                    <strong>Key Topics:</strong>
                    <ul style="margin: 0.5rem 0;">
                        {"".join([f"<li>{topic}</li>" for topic in course['topics']])}
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)

def render_optional_courses():
    st.markdown("### 🌟 Optional Courses")
    
    optional_courses = [
        {
            "name": "AWS Cloud Quest: Serverless Developer",
            "type": "Hands-on Practice",
            "description": "Interactive, gamified learning experience for serverless development",
            "benefit": "Practical application of serverless concepts"
        },
        {
            "name": "Lab: Launching and Managing a Web Application with AWS CloudFormation",
            "type": "Practical Lab",
            "description": "Infrastructure as Code hands-on experience",
            "benefit": "Learn deployment automation and infrastructure management"
        },
        {
            "name": "Exam Prep Enhanced Course: AWS Certified Developer Associate (DVA-C02)",
            "type": "Exam Preparation",
            "description": "Comprehensive exam preparation with practice questions",
            "benefit": "Direct certification preparation and assessment"
        }
    ]

    for course in optional_courses:
        st.markdown(f"""
        <div class="warning-box">
            <h5>⭐ {course['name']}</h5>
            <p><strong>Type:</strong> {course['type']}</p>
            <p><strong>Description:</strong> {course['description']}</p>
            <div style="background: rgba(255,255,255,0.7); padding: 0.5rem; border-radius: 5px; margin-top: 0.5rem;">
                <strong>💡 Benefit:</strong> {course['benefit']}
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_messaging_patterns():
    st.markdown("## 🔄 Key Messaging & Integration Patterns")
    
    # SNS Fan-out Pattern
    st.markdown("### 📡 SNS Fan-out Pattern")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="event-flow">
            <strong>Fan-out Architecture:</strong><br><br>
            📝 Order Placed → 📢 SNS Topic "Orders"<br>
            ├── 📤 SQS Queue (Processing)<br>
            ├── 📊 SQS Queue (Analytics)<br>
            ├── 📧 Email Notification<br>
            └── 📱 SMS Alert<br><br>
            <strong>Benefits:</strong> Parallel processing, decoupling, scalability
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #e8f5e8; padding: 1rem; border-radius: 8px;">
            <h5>🎯 Use Cases</h5>
            <ul>
                <li>Order processing</li>
                <li>Event notifications</li>
                <li>Data distribution</li>
                <li>Multi-system updates</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # SQS Best Practices
    st.markdown("### 📤 SQS Processing Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="comparison-card">
            <h5>✅ Best Practices</h5>
            <ul>
                <li><strong>Visibility Timeout:</strong> Match processing time</li>
                <li><strong>Dead Letter Queues:</strong> Handle failed messages</li>
                <li><strong>Batch Processing:</strong> Optimize throughput</li>
                <li><strong>Message Attributes:</strong> Enable filtering</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="warning-box">
            <h5>⚠️ Common Pitfalls</h5>
            <ul>
                <li>Incorrect visibility timeout settings</li>
                <li>Missing dead letter queue configuration</li>
                <li>Not handling duplicate messages</li>
                <li>Inadequate error handling</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def render_footer():
    st.markdown("""
    <div class="footer">
        <h3>🚀 Ready to Build Event-Driven Applications!</h3>
        <p>Session 3 focuses on the integration services that power modern serverless architectures</p>
        <div style="display: flex; justify-content: center; gap: 2rem; margin: 1rem 0;">
            <div>📡 Messaging</div>
            <div>⚡ Caching</div>
            <div>🔐 Authentication</div>
            <div>📊 Monitoring</div>
        </div>
        <p style="margin-top: 1rem; font-size: 0.9em;">
            <strong>Next:</strong> Apply these patterns in real-world scenarios and hands-on labs
        </p>
    </div>
    """, unsafe_allow_html=True)

# Main execution flow
if __name__ == "__main__":
    if 'localhost' in st.context.headers.get("host", ""):
        main()
        render_overview()
        render_learning_objectives()
        render_aws_services()
        render_training_curriculum()
        render_optional_courses()
        render_messaging_patterns()
        render_footer()
    else:
        # First check authentication
        is_authenticated = authenticate.login()
        
        # If authenticated, show the main app content
        if is_authenticated:
            main()
            render_overview()
            render_learning_objectives()
            render_aws_services()
            render_training_curriculum()
            render_optional_courses()
            render_messaging_patterns()
            render_footer()
