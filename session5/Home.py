
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import utils.common as common
import utils.authenticate as authenticate

# Page configuration
st.set_page_config(
    page_title="AWS Developer Associate - Session 5",
    page_icon="🔐",
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

    .security-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
        border-left: 4px solid #FF6B6B;
    }

    .monitoring-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
        border-left: 4px solid #f093fb;
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
        <h2>Developer - Associate Session 5</h2>
        <h3>Content Review - Security, Identity & Monitoring</h3>
    </div>
    """, unsafe_allow_html=True)

    # Today's Focus
    st.markdown("## 🎯 What You'll Learn Today")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="info-highlight">
            <h3>🔐 Advanced Security & Monitoring Mastery</h3>
            <p>In this penultimate session, we'll master AWS security services, identity management, 
            application monitoring, and advanced S3 features. You'll learn to secure applications, 
            monitor performance, and implement best practices for production workloads.</p>
            <ul>
                <li><strong>Security & Compliance:</strong> WAF, Secrets Manager, KMS, Certificate Manager</li>
                <li><strong>Identity Management:</strong> IAM policies, roles, and access patterns</li>
                <li><strong>Application Monitoring:</strong> X-Ray tracing and performance analysis</li>
                <li><strong>Storage Security:</strong> S3 advanced features and access control</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="training-progress">
            <h4>Session 5 of 6</h4>
            <div style="font-size: 2rem;">🔐</div>
            <p>Security & Monitoring Focus</p>
            <small>Final week preparation!</small>
        </div>
        """, unsafe_allow_html=True)

    # AWS Services We'll Cover
    st.markdown("### 🛠️ AWS Services We'll Cover")
    
    # Security Services
    st.markdown("#### 🔒 Security, Identity, and Compliance")
    security_cols = st.columns(3)
    
    security_services = [
        {
            "name": "AWS WAF",
            "icon": "🛡️",
            "description": "Web application firewall protecting against common attacks",
            "features": ["SQL injection protection", "XSS prevention", "IP filtering", "Rate limiting"]
        },
        {
            "name": "AWS Secrets Manager", 
            "icon": "🔐",
            "description": "Securely store and rotate secrets, API keys, and credentials",
            "features": ["Automatic rotation", "KMS encryption", "Fine-grained access", "Audit logging"]
        },
        {
            "name": "AWS KMS",
            "icon": "🔑", 
            "description": "Managed service for cryptographic keys and data encryption",
            "features": ["Customer managed keys", "AWS managed keys", "CloudTrail integration", "Cross-service encryption"]
        }
    ]
    
    for i, service in enumerate(security_services):
        with security_cols[i]:
            st.markdown(f"""
            <div class="security-card">
                <div style="text-align: center; font-size: 2rem;">{service['icon']}</div>
                <h4 style="text-align: center; margin: 1rem 0;">{service['name']}</h4>
                <p style="font-size: 0.9em; margin-bottom: 1rem;">{service['description']}</p>
                <ul style="font-size: 0.8em;">
                {"".join([f"<li>{feature}</li>" for feature in service['features']])}
                </ul>
            </div>
            """, unsafe_allow_html=True)

    # Additional Security Services
    security_cols2 = st.columns(2)
    
    with security_cols2[0]:
        st.markdown("""
        <div class="service-card">
            <h4>🌐 AWS PrivateLink & VPC Endpoints</h4>
            <p>Privately connect VPC to AWS services without internet gateway</p>
            <ul>
                <li>Enhanced security for service communication</li>
                <li>Reduced data transfer costs</li>
                <li>Improved network performance</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with security_cols2[1]:
        st.markdown("""
        <div class="service-card">
            <h4>📜 AWS Certificate Manager</h4>
            <p>Provision and manage SSL/TLS certificates</p>
            <ul>
                <li>Automated certificate renewal</li>
                <li>Integration with CloudFront, ALB</li>
                <li>Secure internal communication</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # IAM Deep Dive
    st.markdown("#### 👤 AWS Identity and Access Management")
    
    iam_col1, iam_col2 = st.columns(2)
    
    with iam_col1:
        st.markdown("""
        <div class="info-highlight">
            <h4>🔍 IAM Policy Interpretation</h4>
            <p>Master the art of reading and understanding IAM policies:</p>
            <ul>
                <li><strong>Resource Policies:</strong> Attached to resources (S3 buckets, etc.)</li>
                <li><strong>Identity Policies:</strong> Attached to users, groups, roles</li>
                <li><strong>Trust Policies:</strong> Control who can assume roles</li>
                <li><strong>Condition Elements:</strong> Add granular access control</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with iam_col2:
        st.markdown("""
        <div class="warning-box">
            <h4>⚠️ Policy Evaluation Logic</h4>
            <p><strong>Remember:</strong> IAM follows explicit deny > explicit allow > implicit deny</p>
            <ul>
                <li>Explicit DENY always wins</li>
                <li>Must have explicit ALLOW</li>
                <li>Default is implicit DENY</li>
                <li>Conditions must evaluate to TRUE</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Application Monitoring
    st.markdown("#### 📊 Application Monitoring")
    
    st.markdown("""
    <div class="monitoring-card">
        <h4 style="display: flex; align-items: center;">
            <span style="font-size: 2rem; margin-right: 1rem;">🔍</span>
            AWS X-Ray - Distributed Tracing
        </h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 1rem;">
            <div>
                <h5>Key Concepts:</h5>
                <ul>
                    <li><strong>Traces:</strong> End-to-end request journey</li>
                    <li><strong>Segments:</strong> Individual service calls</li>
                    <li><strong>Subsegments:</strong> Granular operation details</li>
                    <li><strong>Service Map:</strong> Visual service dependencies</li>
                </ul>
            </div>
            <div>
                <h5>Error Categories:</h5>
                <ul>
                    <li><strong>Error:</strong> Client errors (4xx)</li>
                    <li><strong>Fault:</strong> Server faults (5xx)</li>
                    <li><strong>Throttle:</strong> Rate limiting (429)</li>
                    <li><strong>Exceptions:</strong> Application errors with stack traces</li>
                </ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # S3 Advanced Features
    st.markdown("#### 📦 Amazon S3 - Advanced Features")
    
    s3_cols = st.columns(3)
    
    s3_features = [
        {
            "title": "Storage Classes",
            "icon": "🏗️",
            "items": ["S3 Standard", "S3 Standard-IA", "S3 One Zone-IA", "S3 Intelligent-Tiering", "S3 Glacier variants"]
        },
        {
            "title": "Security Features", 
            "icon": "🔒",
            "items": ["Presigned URLs", "CORS configuration", "CloudFront OAI", "Bucket policies", "Access control"]
        },
        {
            "title": "Lifecycle Management",
            "icon": "♻️", 
            "items": ["Transition actions", "Expiration actions", "Cost optimization", "Automated archiving"]
        }
    ]
    
    for i, feature in enumerate(s3_features):
        with s3_cols[i]:
            st.markdown(f"""
            <div class="service-card">
                <div style="text-align: center; font-size: 2rem;">{feature['icon']}</div>
                <h4 style="text-align: center; margin: 1rem 0;">{feature['title']}</h4>
                <ul>
                {"".join([f"<li>{item}</li>" for item in feature['items']])}
                </ul>
            </div>
            """, unsafe_allow_html=True)

    # Week 5 Digital Training Curriculum
    st.markdown("## 📚 Week 5 Digital Training Curriculum")
    st.markdown("### 🎯 Prepare yourselves for the final week of digital training!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📖 AWS Skill Builder Learning Plan Courses")
        
        core_courses = [
            {"name": "Amazon DynamoDB - Troubleshooting", "duration": "60 min", "focus": "Database debugging"},
            {"name": "Security and Observability for Serverless Applications", "duration": "90 min", "focus": "Serverless security"},
            {"name": "Securing and Protecting Your Data in Amazon S3", "duration": "75 min", "focus": "S3 security best practices"},
            {"name": "Exam Prep Standard Course: AWS Certified Developer - Associate (DVA-C02)", "duration": "4 hours", "focus": "Comprehensive review"},
            {"name": "Exam Prep Official Practice Question Set: AWS Certified Developer - Associate (DVA-C02)", "duration": "2 hours", "focus": "Practice questions"}
        ]
        
        for course in core_courses:
            st.markdown(f"""
            <div class="comparison-card">
                <strong>{course['name']}</strong><br>
                <small>⏱️ Duration: {course['duration']} | 🎯 Focus: {course['focus']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🌟 Optional Courses")
        
        optional_courses = [
            {
                "name": "Exam Prep Enhanced Course: AWS Certified Developer - Associate (DVA-C02)", 
                "duration": "6 hours",
                "type": "Subscription",
                "benefit": "In-depth exam preparation with detailed explanations"
            },
            {
                "name": "Exam Prep Official Practice Exam: AWS Certified Developer - Associate (DVA-C02)", 
                "duration": "2 hours", 
                "type": "Subscription",
                "benefit": "Full-length practice exam simulation"
            }
        ]
        
        for course in optional_courses:
            st.markdown(f"""
            <div class="warning-box">
                <strong>{course['name']}</strong><br>
                <small>⏱️ Duration: {course['duration']} | 📋 Type: {course['type']} Based</small><br>
                <em>💡 {course['benefit']}</em>
            </div>
            """, unsafe_allow_html=True)

    # Key Learning Objectives
    st.markdown("## 🎯 Key Learning Objectives for This Session")
    
    objectives_cols = st.columns(2)
    
    with objectives_cols[0]:
        st.markdown("""
        <div class="info-highlight">
            <h4>🔐 Security Mastery</h4>
            <ul>
                <li>Interpret and write IAM policies confidently</li>
                <li>Implement comprehensive application security</li>
                <li>Manage secrets and encryption keys properly</li>
                <li>Configure web application firewalls</li>
                <li>Set up secure network communication</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with objectives_cols[1]:
        st.markdown("""
        <div class="info-highlight">
            <h4>📊 Monitoring Excellence</h4>
            <ul>
                <li>Implement distributed tracing with X-Ray</li>
                <li>Analyze application performance bottlenecks</li>
                <li>Troubleshoot errors, faults, and exceptions</li>
                <li>Create effective monitoring strategies</li>
                <li>Optimize S3 storage and access patterns</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Exam Preparation Focus
    st.markdown("## 🏆 Exam Preparation Focus")
    
    st.markdown("""
    <div class="training-progress">
        <h3>🎯 Critical Success Factors</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem;">
            <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 8px;">
                <h4>📝 Policy Reading</h4>
                <p>Master IAM policy interpretation - this appears frequently on the exam</p>
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 8px;">
                <h4>🔍 X-Ray Tracing</h4>
                <p>Understand service maps, segments, and error categorization</p>
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 8px;">
                <h4>🔒 Security Services</h4>
                <p>Know when to use WAF, Secrets Manager, and KMS</p>
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 8px;">
                <h4>📦 S3 Advanced</h4>
                <p>Understand storage classes, lifecycle policies, and security features</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="footer">
        <h3>🚀 Almost There - Session 5 Complete!</h3>
        <p>You've mastered AWS security, identity management, and application monitoring!</p>
        <p><strong>Next Up:</strong> Final review and exam preparation in Session 6</p>
        <div style="margin-top: 1rem; font-size: 1.1em;">
            <span style="margin: 0 1rem;">🔐 Security ✓</span>
            <span style="margin: 0 1rem;">👤 IAM ✓</span>
            <span style="margin: 0 1rem;">📊 Monitoring ✓</span>
            <span style="margin: 0 1rem;">📦 S3 Advanced ✓</span>
        </div>
        <p style="margin-top: 1rem; font-size: 0.9em;">
            Ready for the final push! The AWS Certified Developer Associate certification is within reach! 🏆
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
