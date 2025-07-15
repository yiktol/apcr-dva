
import streamlit as st
import pandas as pd
import utils.common as common
import utils.authenticate as authenticate


# Page configuration
st.set_page_config(
    page_title="AWS Certification Readiness - Developer Associate",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

    /* Main container styling */
    .main-header {
        background: linear-gradient(135deg, #232F3E 0%, #4B9CD3 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }

    .program-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border-left: 6px solid #FF9900;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }

    .program-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }

    .objective-item {
        background: linear-gradient(135deg, #f8f9fa 0%, #e3f2fd 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #4B9CD3;
        transition: all 0.3s ease;
    }

    .objective-item:hover {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        transform: translateX(10px);
    }

    .week-timeline {
        background: linear-gradient(135deg, #FF9900 0%, #FFB84D 100%);
        color: black;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 4px 15px rgba(255,153,0,0.3);
    }

    .training-module {
        background: #e8f5e8;
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 4px solid #4caf50;
        margin: 0.8rem 0;
        display: flex;
        align-items: center;
    }

    .icon-large {
        font-size: 2rem;
        margin-right: 1rem;
    }

    .stats-container {
        background: linear-gradient(135deg, #232F3E 0%, #4B9CD3 100%);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        margin: 0 0;
    }

    .footer {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #232F3E 0%, #4B9CD3 100%);
        color: white;
        margin-top: 3rem;
        border-radius: 15px;
    }
    .info-box {
        background-color: #E6F2FF;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 5px solid #00A1C9;
    }

    /* Adjust main content area */
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: none;
    }
    </style>
    """, unsafe_allow_html=True)

    common.initialize_session_state()

    with st.sidebar:
        common.render_sidebar()


    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>AWS Partner Certification Readiness</h1>
        <h2>Developer - Associate Certification Program</h2>
        <h3>Session 1: AWS Fundamentals & Core Services</h3>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
        <p style="font-size: 1.1em; margin-top: 1rem;">
            Master the fundamentals of AWS cloud computing and prepare for your Developer Associate certification
        </p>
    </div>
    """, unsafe_allow_html=True)


    # Program Overview Section
    st.markdown("## 🏠 Program Overview")

    # Program introduction
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        <div class="program-card">
            <h3>🎯 Welcome to AWS Developer Associate Certification Readiness</h3>
            <p style="font-size: 1.1em; line-height: 1.6;">
                This comprehensive 6-week program is designed to prepare you for the AWS Certified Developer - Associate exam. 
                Through a combination of live sessions, hands-on labs, and self-paced digital training, you'll master 
                the essential AWS services and development practices needed for cloud application development.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="stats-container">
            <h3>📊 Program Stats</h3>
            <div style="font-size: 2rem; margin: 1rem 0;">6</div>
            <div>Weeks Duration</div>
            <div style="font-size: 2rem; margin: 1rem 0;">12</div>
            <div>Live Sessions</div>
            <div style="font-size: 2rem; margin: 1rem 0;">600+</div>
            <div>Digital Courses Available</div>
        </div>
        """, unsafe_allow_html=True)

    # Current week focus
    st.markdown("""
    <div class="week-timeline">
        <h3>📚 Week 1 Focus: Foundation & Core Services</h3>
        <p>This week we're establishing your foundation in AWS fundamentals, covering essential services like EC2, VPC, IAM, and CloudFront</p>
    </div>
    """, unsafe_allow_html=True)

    # Learning Objectives Section
    st.markdown("## 📖 Learning Objectives")

    # Main objectives
    objectives = [
        {
            "title": "🌐 AWS Global Infrastructure",
            "description": "Understand AWS Regions, Availability Zones, and Edge Locations",
            "details": "Learn how AWS's global infrastructure provides high availability, fault tolerance, and low-latency access to services worldwide."
        },
        {
            "title": "☁️ Amazon CloudFront CDN",
            "description": "Master content delivery network concepts and implementation",
            "details": "Explore how CloudFront accelerates content delivery using edge locations and regional edge caches for optimal performance."
        },
        {
            "title": "💻 AWS Compute Services",
            "description": "Compare EC2, ECS, EKS, Lambda, and Fargate",
            "details": "Understand when to use different compute options based on your application requirements and scaling needs."
        },
        {
            "title": "🏗️ Amazon VPC Networking",
            "description": "Design secure and scalable network architectures",
            "details": "Learn to configure subnets, security groups, NACLs, and VPC endpoints for secure application deployment."
        },
        {
            "title": "🔒 AWS Identity and Access Management",
            "description": "Implement secure access controls and policies",
            "details": "Master IAM users, groups, roles, and policy interpretation for robust security implementations."
        },
        {
            "title": "🔄 DNS and Traffic Routing",
            "description": "Configure Route 53 for reliable application access",
            "details": "Implement DNS solutions with health checks, failover, and geographic routing capabilities."
        }
    ]

    for i, obj in enumerate(objectives):
        with st.expander(f"{obj['title']}", expanded=False):
            st.markdown(f"""
            <div class="objective-item">
                <h4>{obj['description']}</h4>
                <p style="margin-top: 1rem; line-height: 1.6;">{obj['details']}</p>
            </div>
            """, unsafe_allow_html=True)

    # Week 1 Training Modules
    st.markdown("### 📚 Week 1 Required Training Modules")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="training-module">
            <span class="icon-large">📘</span>
            <div>
                <strong>AWS Technical Essentials</strong><br>
                Foundation course covering core AWS concepts
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="training-module">
            <span class="icon-large">🖥️</span>
            <div>
                <strong>AWS Compute Services Overview</strong><br>
                Comprehensive guide to AWS compute options
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="training-module">
            <span class="icon-large">⚡</span>
            <div>
                <strong>Build with Amazon EC2</strong><br>
                Hands-on EC2 instance management and scaling
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="training-module">
            <span class="icon-large">🔬</span>
            <div>
                <strong>Optional: AWS CloudQuest Labs</strong><br>
                Interactive labs for DynamoDB and Lambda
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="footer">
        <h3>🚀 Ready to Begin Your AWS Journey?</h3>
        <p>Remember: This program is designed to get you certified, but your enthusiasm and engagement make the difference!</p>
        <p><strong>Next Session:</strong> Week 2 Content Review - Development & Deployment Tools</p>
        <p style="margin-top: 1rem; font-size: 0.9em;">
            © 2025 Amazon Web Services, Inc. or its affiliates. All rights reserved.
        </p>
    </div>
    """, unsafe_allow_html=True)


# Main execution flow
if __name__ == "__main__":
    if 'localhost' in st.context.headers["host"]:
        main()
    else:
        # First check authentication
        is_authenticated = authenticate.login()
        
        # If authenticated, show the main app content
        if is_authenticated:
            main()
        else:
            st.error("You are not authorized to view this page. Please login with the correct credentials.")