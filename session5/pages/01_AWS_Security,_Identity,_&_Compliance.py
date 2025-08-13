import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import utils.common as common
import utils.authenticate as authenticate
import json
import base64
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="AWS Security & Identity Hub",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# AWS Color Scheme
AWS_COLORS = {
    'primary': '#FF9900',
    'secondary': '#232F3E',
    'light_blue': '#4B9EDB',
    'dark_blue': '#1B2631',
    'light_gray': '#F2F3F3',
    'success': '#3FB34F',
    'warning': '#FF6B35',
    'danger': '#D73027'
}

def apply_custom_styles():
    """Apply custom CSS styling with AWS color scheme"""
    st.markdown(f"""
    <style>
        .main {{
            background-color: {AWS_COLORS['light_gray']};
        }}
        
        .stTabs [data-baseweb="tab-list"] {{
            gap: 20px;
            background-color: white;
            border-radius: 12px;
            padding: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            height: 65px;
            padding: 8px 20px;
            background-color: {AWS_COLORS['light_gray']};
            border-radius: 10px;
            color: {AWS_COLORS['secondary']};
            font-weight: 600;
            border: 2px solid transparent;
            font-size: 14px;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: {AWS_COLORS['primary']};
            color: white;
            border: 2px solid {AWS_COLORS['secondary']};
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, {AWS_COLORS['primary']} 0%, {AWS_COLORS['light_blue']} 100%);
            padding: 20px;
            border-radius: 15px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            margin: 10px 0;
        }}
        
        .concept-card {{
            background: white;
            padding: 15px;
            border-radius: 15px;
            border-left: 5px solid {AWS_COLORS['primary']};
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin: 5px 0;
        }}
        
        .highlight-box {{
            background: linear-gradient(135deg, {AWS_COLORS['light_blue']} 0%, {AWS_COLORS['primary']} 100%);
            padding: 20px;
            border-radius: 12px;
            color: white;
            margin: 15px 0;
        }}
        
        .warning-box {{
            background: linear-gradient(135deg, {AWS_COLORS['warning']} 0%, {AWS_COLORS['primary']} 100%);
            padding: 20px;
            border-radius: 12px;
            color: white;
            margin: 15px 0;
        }}
        
        .security-box {{
            background: linear-gradient(135deg, {AWS_COLORS['success']} 0%, {AWS_COLORS['light_blue']} 100%);
            padding: 20px;
            border-radius: 12px;
            color: white;
            margin: 15px 0;
        }}
        
        .info-box {{
            background-color: #E6F2FF;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            border-left: 5px solid #00A1C9;
        }}
        
        .footer {{
            margin-top: 10px;
            margin-bottom: 2px;
            padding: 5px;
            text-align: center;
            background-color: {AWS_COLORS['secondary']};
            color: white;
            border-radius: 10px;
        }}
        
        .code-container {{
            background-color: {AWS_COLORS['dark_blue']};
            color: white;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid {AWS_COLORS['primary']};
            margin: 15px 0;
        }}
        
        .threat-card {{
            background: linear-gradient(135deg, {AWS_COLORS['danger']} 0%, {AWS_COLORS['warning']} 100%);
            padding: 15px;
            border-radius: 12px;
            color: white;
            margin: 10px 0;
        }}
    </style>
    """, unsafe_allow_html=True)

def create_sidebar():
    """Create sidebar with app information and controls"""
    with st.sidebar:
        common.render_sidebar()
        
        # About section (collapsed by default)
        with st.expander("📖 About this App", expanded=False):
            st.markdown("""
            **Topics Covered:**
            - 🛡️ AWS WAF - Web Application Firewall protection
            - 🔐 AWS Secrets Manager - Secure credential management
            - 🔑 AWS KMS - Key Management Service for encryption
            - 🔗 AWS PrivateLink - Private connectivity between services
            - 📜 AWS Certificate Manager - SSL/TLS certificate management
            - 🗂️ Amazon S3 Security - Presigned URLs, CORS, and OAI
            
            **Learning Objectives:**
            - Understand AWS security and identity services
            - Learn to implement secure application architectures
            - Practice with interactive security configurations
            - Explore encryption and access control mechanisms
            """)

def create_waf_architecture_mermaid():
    """Create mermaid diagram for AWS WAF architecture"""
    return """
    graph TD
        A[👤 User Request] --> B[🌐 Internet]
        B --> C[🛡️ AWS WAF]
        C --> D{Security Rules Check}
        
        D -->|✅ Allow| E[📍 CloudFront/ALB/API Gateway]
        D -->|🚫 Block| F[🛑 Block Response]
        D -->|📊 Count| G[📈 CloudWatch Metrics]
        
        E --> H[🖥️ Origin Server]
        
        subgraph "WAF Rules"
            I[🌍 IP Allow/Block Lists]
            J[🔍 SQL Injection Protection]
            K[🕷️ XSS Protection]
            L[📊 Rate Limiting]
            M[🤖 Bot Detection]
        end
        
        D --> I
        D --> J
        D --> K
        D --> L
        D --> M
        
        style C fill:#FF9900,stroke:#232F3E,color:#fff
        style D fill:#4B9EDB,stroke:#232F3E,color:#fff
        style F fill:#D73027,stroke:#232F3E,color:#fff
        style E fill:#3FB34F,stroke:#232F3E,color:#fff
    """

def create_secrets_manager_mermaid():
    """Create mermaid diagram for Secrets Manager workflow"""
    return """
    graph TD
        A[🔐 Application] --> B[📞 AWS SDK Call]
        B --> C[🏛️ Secrets Manager]
        C --> D[🔑 KMS Encryption]
        
        C --> E{Secret Exists?}
        E -->|Yes| F[📤 Return Encrypted Secret]
        E -->|No| G[❌ Access Denied]
        
        F --> H[🔓 Application Decrypts]
        H --> I[🗄️ Connect to Database]
        
        subgraph "Automatic Rotation"
            J[⏱️ Rotation Schedule]
            K[🔄 Lambda Function]
            L[🗄️ Update Database]
            M[📝 Update Secret]
        end
        
        J --> K
        K --> L
        L --> M
        M --> C
        
        style C fill:#FF9900,stroke:#232F3E,color:#fff
        style D fill:#4B9EDB,stroke:#232F3E,color:#fff
        style I fill:#3FB34F,stroke:#232F3E,color:#fff
        style K fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_kms_encryption_mermaid():
    """Create mermaid diagram for KMS encryption process"""
    return """
    graph TD
        A[📄 Plain Text Data] --> B[🔐 KMS Encrypt API]
        B --> C[🔑 Customer Master Key]
        C --> D[🔢 Data Encryption Key]
        
        D --> E[🔒 Encrypt Data]
        E --> F[📦 Encrypted Data + Key]
        
        F --> G[🗄️ Store Encrypted Data]
        
        subgraph "Decryption Process"
            H[📦 Retrieve Encrypted Data]
            I[🔓 KMS Decrypt API]
            J[🔑 CMK Decrypts DEK]
            K[📄 Decrypted Data]
        end
        
        G --> H
        H --> I
        I --> J
        J --> K
        

        subgraph "Key Types"
            L[👤 Customer Managed Keys]
            M[🏛️ AWS Managed Keys]
            N[🔒 AWS Owned Keys]
        end
        

        style B fill:#FF9900,stroke:#232F3E,color:#fff
        style C fill:#4B9EDB,stroke:#232F3E,color:#fff
        style E fill:#3FB34F,stroke:#232F3E,color:#fff
        style I fill:#FF9900,stroke:#232F3E,color:#fff
    """

def create_privatelink_mermaid():
    """Create mermaid diagram for PrivateLink architecture"""
    return """
    graph TD
        A[🖥️ EC2 Instance] --> B[🔗 VPC Endpoint]
        B --> C[🌐 AWS PrivateLink]
        C --> D[🛠️ AWS Service]
        
        subgraph "Your VPC"
            A
            B
            E[📊 Private Subnet]
            F[🔒 Security Groups]
        end
        
        subgraph "AWS Service VPC"
            D
            G[⚖️ Load Balancer]
            H[🖥️ Service Instances]
        end
        
        B --> E
        B --> F
        D --> G
        G --> H
        
        I[🌍 Internet] -.->|No Internet| B
        
        style B fill:#FF9900,stroke:#232F3E,color:#fff
        style C fill:#4B9EDB,stroke:#232F3E,color:#fff
        style D fill:#3FB34F,stroke:#232F3E,color:#fff
        style I fill:#D73027,stroke:#232F3E,color:#fff
    """

def create_acm_certificate_mermaid():
    """Create mermaid diagram for ACM certificate workflow"""
    return """
    graph TD
        A[📝 Certificate Request] --> B[📜 AWS Certificate Manager]
        B --> C{Validation Method}
        
        C -->|DNS| D[🌐 DNS Validation]
        C -->|Email| E[📧 Email Validation]
        
        D --> F[✅ Domain Verified]
        E --> F
        
        F --> G[📜 Certificate Issued]
        G --> H[🔄 Auto-Renewal]
        
        subgraph "Certificate Usage"
            I[⚡ CloudFront]
            J[⚖️ Application Load Balancer]
            K[🌐 API Gateway]
            L[🏛️ Elastic Beanstalk]
        end
        
        G --> I
        G --> J
        G --> K
        G --> L
        
        H --> M[📅 Renewal Notification]
        M --> N[🔄 Automatic Renewal]
        
        style B fill:#FF9900,stroke:#232F3E,color:#fff
        style F fill:#3FB34F,stroke:#232F3E,color:#fff
        style G fill:#4B9EDB,stroke:#232F3E,color:#fff
        style H fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_s3_security_mermaid():
    """Create mermaid diagram for S3 security features"""
    return """
    graph TD
        A[👤 User Request] --> B{Request Type}
        
        B -->|Public| C[🌐 Public Access]
        B -->|Presigned URL| D[🔗 Presigned URL Access]
        B -->|OAI| E[🔐 Origin Access Identity]
        
        C --> F[🗂️ S3 Bucket]
        D --> F
        E --> F
        
        subgraph "S3 Security Features"
            G[🔒 Bucket Policies]
            H[🛡️ IAM Policies]
            I[🌐 CORS Configuration]
            J[🔐 Encryption at Rest]
            K[🚫 Block Public Access]
        end
        
        F --> G
        F --> H
        F --> I
        F --> J
        F --> K
        
        subgraph "CloudFront Integration"
            L[⚡ CloudFront Distribution]
            M[🔐 OAI Authentication]
            N[🌍 Global Edge Locations]
        end
        
        E --> L
        L --> M
        M --> N
        
        style F fill:#FF9900,stroke:#232F3E,color:#fff
        style D fill:#4B9EDB,stroke:#232F3E,color:#fff
        style E fill:#3FB34F,stroke:#232F3E,color:#fff
        style L fill:#232F3E,stroke:#FF9900,color:#fff
    """

def aws_waf_tab():
    """Content for AWS WAF tab"""
    st.markdown("## 🛡️ AWS WAF (Web Application Firewall)")
    st.markdown("*Protect web applications from common web exploits and attacks*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **AWS WAF** is a web application firewall that helps protect web applications from attacks by allowing you to configure rules 
    that allow, block, or monitor (count) web requests based on conditions that you define. These conditions include IP addresses, 
    HTTP headers, HTTP body, URI strings, SQL injection and cross-site scripting.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # WAF Architecture
    st.markdown("### 🏗️ AWS WAF Architecture")
    common.mermaid(create_waf_architecture_mermaid(), height=700, width="100%")
    
    # Protected Resources
    st.markdown("### 🎯 Resources Protected by AWS WAF")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### ⚡\n**CloudFront**\nDistributions")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        **Use Cases:**
        - Global content delivery protection
        - Edge-level filtering
        - DDoS mitigation
        - Geographic blocking
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### ⚖️\n**Application**\nLoad Balancer")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        **Use Cases:**
        - Regional application protection
        - Layer 7 filtering
        - Custom rule sets
        - Rate limiting per ALB
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🌐\n**API Gateway**\nREST APIs")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        **Use Cases:**
        - API endpoint protection
        - Request filtering
        - Authentication bypass protection
        - API abuse prevention
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive WAF Rule Builder
    st.markdown("### 🔧 Interactive WAF Rule Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🛠️ Rule Configuration")
        rule_name = st.text_input("Rule Name:", "BlockMaliciousIPs")
        rule_action = st.selectbox("Action:", ["Block", "Allow", "Count"])
        priority = st.number_input("Priority (lower = higher priority):", 1, 1000, 100)
        
        rule_type = st.selectbox("Rule Type:", [
            "IP Address Blocking",
            "SQL Injection Protection", 
            "XSS Protection",
            "Rate Limiting",
            "Geographic Blocking",
            "Bot Detection"
        ])
    
    with col2:
        st.markdown("### ⚙️ Rule Details")
        
        if rule_type == "IP Address Blocking":
            ip_addresses = st.text_area("IP Addresses (one per line):", "192.168.1.100\n10.0.0.0/24")
            scope = st.selectbox("Scope:", ["Specific IPs", "IP Ranges", "Country-based"])
            
        elif rule_type == "Rate Limiting":
            rate_limit = st.number_input("Requests per 5 minutes:", 100, 10000, 2000)
            scope = st.selectbox("Scope:", ["Per IP", "Per Session", "Global"])
            
        elif rule_type == "Geographic Blocking":
            countries = st.multiselect("Blocked Countries:", 
                                     ["China", "Russia", "North Korea", "Iran", "Syria"], 
                                     default=["North Korea"])
            
        else:
            sensitivity = st.selectbox("Detection Sensitivity:", ["Low", "Medium", "High"])
    
    if st.button("🚀 Create WAF Rule", use_container_width=True):
        # Generate rule configuration
        rule_config = {
            "Name": rule_name,
            "Action": rule_action,
            "Priority": priority,
            "Type": rule_type,
            "CreatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        st.markdown('<div class="security-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ WAF Rule Created Successfully!
        
        **Rule Configuration:**
        - **Name**: {rule_name}
        - **Action**: {rule_action}
        - **Priority**: {priority}
        - **Type**: {rule_type}
        - **Status**: Active
        
        🛡️ **Protection Level**: {np.random.choice(['High', 'Very High'])}
        📊 **Expected Block Rate**: {np.random.randint(15, 45)}% of malicious traffic
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Common Attack Types
    st.markdown("### 🎯 Common Web Application Attacks & WAF Protection")
    
    attack_data = {
        'Attack Type': ['SQL Injection', 'Cross-Site Scripting (XSS)', 'DDoS Attack', 'Bot Traffic', 'Geographic Attacks'],
        'Description': [
            'Malicious SQL code injection into database queries',
            'Malicious scripts injected into web pages',
            'Overwhelming traffic to disrupt service', 
            'Automated requests from bots',
            'Attacks from specific geographic regions'
        ],
        'WAF Protection': [
            'SQL injection rule sets',
            'XSS filtering and validation',
            'Rate limiting and IP blocking',
            'Bot detection and CAPTCHA',
            'Geographic IP blocking'
        ],
        'Effectiveness': ['99%', '95%', '90%', '85%', '100%']
    }
    
    df_attacks = pd.DataFrame(attack_data)
    st.dataframe(df_attacks, use_container_width=True)
    
    # WAF Metrics Simulation
    st.markdown("### 📊 WAF Protection Metrics Simulation")
    
    # Generate sample metrics
    dates = pd.date_range(start='2025-07-01', end='2025-07-14', freq='D')
    
    metrics_data = {
        'Date': dates,
        'Total Requests': np.random.randint(10000, 50000, len(dates)),
        'Blocked Requests': np.random.randint(500, 5000, len(dates)),
        'Allowed Requests': np.random.randint(8000, 45000, len(dates)),
        'SQL Injection Attempts': np.random.randint(50, 500, len(dates)),
        'XSS Attempts': np.random.randint(20, 200, len(dates))
    }
    
    df_metrics = pd.DataFrame(metrics_data)
    df_metrics['Block Rate %'] = (df_metrics['Blocked Requests'] / df_metrics['Total Requests'] * 100).round(2)
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Request Volume Over Time', 'Attack Types Blocked', 'Block Rate Percentage', 'Protection Effectiveness'),
        specs=[[{"secondary_y": False}, {"type": "pie"}],
               [{"secondary_y": False}, {"type": "bar"}]]
    )
    
    # Request volume
    fig.add_trace(
        go.Scatter(x=df_metrics['Date'], y=df_metrics['Total Requests'], 
                  name='Total Requests', line=dict(color=AWS_COLORS['primary'])),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df_metrics['Date'], y=df_metrics['Blocked Requests'], 
                  name='Blocked Requests', line=dict(color=AWS_COLORS['danger'])),
        row=1, col=1
    )
    
    # Attack types pie chart
    attack_totals = [df_metrics['SQL Injection Attempts'].sum(), 
                    df_metrics['XSS Attempts'].sum(),
                    np.random.randint(500, 1500)]
    fig.add_trace(
        go.Pie(labels=['SQL Injection', 'XSS', 'Other'], values=attack_totals,
               marker_colors=[AWS_COLORS['danger'], AWS_COLORS['warning'], AWS_COLORS['light_blue']]),
        row=1, col=2
    )
    
    # Block rate
    fig.add_trace(
        go.Scatter(x=df_metrics['Date'], y=df_metrics['Block Rate %'], 
                  name='Block Rate %', line=dict(color=AWS_COLORS['success'])),
        row=2, col=1
    )
    
    # Effectiveness
    effectiveness = ['SQL Injection', 'XSS', 'DDoS', 'Bot Traffic']
    effectiveness_rates = [99, 95, 90, 85]
    fig.add_trace(
        go.Bar(x=effectiveness, y=effectiveness_rates, name='Effectiveness %',
               marker_color=AWS_COLORS['success']),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # Best Practices
    st.markdown("### 💡 AWS WAF Best Practices")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚠️ Configuration Best Practices
        
        **Rule Ordering:**
        - Prioritize allow rules before block rules
        - Use specific rules before general ones
        - Test rules in **Count mode** first
        
        **Performance Optimization:**
        - Use **IP-based rules** for better performance
        - Limit regex complexity in string matching
        - Monitor rule evaluation costs
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="security-box">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛡️ Security Best Practices
        
        **Monitoring & Alerting:**
        - Enable **CloudWatch** metrics and alarms
        - Set up notifications for blocked requests
        - Regular review of WAF logs
        
        **Rule Management:**
        - Use **AWS Managed Rules** as baseline
        - Regular updates to threat intelligence
        - Document custom rule purposes
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: AWS WAF Configuration")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Configure AWS WAF with comprehensive protection rules
import boto3
import json

def create_waf_web_acl(name, scope='CLOUDFRONT'):
    """Create a comprehensive WAF Web ACL with multiple protection rules"""
    wafv2 = boto3.client('wafv2')
    
    # Define the Web ACL configuration
    web_acl_config = {
        'Name': name,
        'Scope': scope,  # CLOUDFRONT or REGIONAL
        'DefaultAction': {'Allow': {}},
        'Description': 'Comprehensive web application protection',
        'Rules': [
            # AWS Managed Rule - Core Rule Set
            {
                'Name': 'AWSManagedRulesCommonRuleSet',
                'Priority': 1,
                'OverrideAction': {'None': {}},
                'Statement': {
                    'ManagedRuleGroupStatement': {
                        'VendorName': 'AWS',
                        'Name': 'AWSManagedRulesCommonRuleSet'
                    }
                },
                'VisibilityConfig': {
                    'SampledRequestsEnabled': True,
                    'CloudWatchMetricsEnabled': True,
                    'MetricName': 'CommonRuleSetMetric'
                }
            },
            # AWS Managed Rule - SQL Injection Protection
            {
                'Name': 'AWSManagedRulesSQLiRuleSet',
                'Priority': 2,
                'OverrideAction': {'None': {}},
                'Statement': {
                    'ManagedRuleGroupStatement': {
                        'VendorName': 'AWS',
                        'Name': 'AWSManagedRulesSQLiRuleSet'
                    }
                },
                'VisibilityConfig': {
                    'SampledRequestsEnabled': True,
                    'CloudWatchMetricsEnabled': True,
                    'MetricName': 'SQLiRuleSetMetric'
                }
            },
            # Rate limiting rule
            {
                'Name': 'RateLimitRule',
                'Priority': 3,
                'Action': {'Block': {}},
                'Statement': {
                    'RateBasedStatement': {
                        'Limit': 2000,  # 2000 requests per 5 minutes
                        'AggregateKeyType': 'IP'
                    }
                },
                'VisibilityConfig': {
                    'SampledRequestsEnabled': True,
                    'CloudWatchMetricsEnabled': True,
                    'MetricName': 'RateLimitMetric'
                }
            },
            # IP blocking rule
            {
                'Name': 'IPBlockingRule',
                'Priority': 4,
                'Action': {'Block': {}},
                'Statement': {
                    'IPSetReferenceStatement': {
                        'ARN': 'arn:aws:wafv2:us-east-1:123456789012:global/ipset/BlockedIPs/12345678'
                    }
                },
                'VisibilityConfig': {
                    'SampledRequestsEnabled': True,
                    'CloudWatchMetricsEnabled': True,
                    'MetricName': 'IPBlockingMetric'
                }
            },
            # Geographic blocking rule
            {
                'Name': 'GeoBlockingRule',
                'Priority': 5,
                'Action': {'Block': {}},
                'Statement': {
                    'GeoMatchStatement': {
                        'CountryCodes': ['CN', 'RU', 'KP']  # Block China, Russia, North Korea
                    }
                },
                'VisibilityConfig': {
                    'SampledRequestsEnabled': True,
                    'CloudWatchMetricsEnabled': True,
                    'MetricName': 'GeoBlockingMetric'
                }
            }
        ]
    }
    
    try:
        response = wafv2.create_web_acl(**web_acl_config)
        web_acl_arn = response['Summary']['ARN']
        web_acl_id = response['Summary']['Id']
        
        print(f"✅ Web ACL created successfully!")
        print(f"Web ACL ARN: {web_acl_arn}")
        print(f"Web ACL ID: {web_acl_id}")
        
        return web_acl_id, web_acl_arn
        
    except Exception as e:
        print(f"❌ Error creating Web ACL: {e}")
        return None, None

def create_ip_set(name, scope, ip_addresses):
    """Create an IP set for blocking specific IP addresses"""
    wafv2 = boto3.client('wafv2')
    
    try:
        response = wafv2.create_ip_set(
            Name=name,
            Scope=scope,
            IPAddressVersion='IPV4',
            Addresses=ip_addresses,
            Description='Blocked IP addresses list'
        )
        
        ip_set_arn = response['Summary']['ARN']
        print(f"✅ IP Set created: {ip_set_arn}")
        return ip_set_arn
        
    except Exception as e:
        print(f"❌ Error creating IP Set: {e}")
        return None

def associate_waf_with_resource(web_acl_arn, resource_arn):
    """Associate WAF Web ACL with a resource (CloudFront, ALB, etc.)"""
    wafv2 = boto3.client('wafv2')
    
    try:
        response = wafv2.associate_web_acl(
            WebACLArn=web_acl_arn,
            ResourceArn=resource_arn
        )
        
        print(f"✅ WAF associated with resource: {resource_arn}")
        return True
        
    except Exception as e:
        print(f"❌ Error associating WAF: {e}")
        return False

def get_waf_metrics(web_acl_name, metric_name, start_time, end_time):
    """Get WAF metrics from CloudWatch"""
    cloudwatch = boto3.client('cloudwatch')
    
    try:
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/WAFV2',
            MetricName=metric_name,
            Dimensions=[
                {'Name': 'WebACL', 'Value': web_acl_name},
                {'Name': 'Region', 'Value': 'CloudFront'},
                {'Name': 'Rule', 'Value': 'ALL'}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,  # 1 hour
            Statistics=['Sum']
        )
        
        return response['Datapoints']
        
    except Exception as e:
        print(f"❌ Error getting metrics: {e}")
        return []

def monitor_waf_activity(web_acl_name):
    """Monitor WAF activity and generate alerts"""
    from datetime import datetime, timedelta
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
    
    # Get various metrics
    blocked_requests = get_waf_metrics(web_acl_name, 'BlockedRequests', start_time, end_time)
    allowed_requests = get_waf_metrics(web_acl_name, 'AllowedRequests', start_time, end_time)
    
    if blocked_requests and allowed_requests:
        total_blocked = sum([dp['Sum'] for dp in blocked_requests])
        total_allowed = sum([dp['Sum'] for dp in allowed_requests])
        total_requests = total_blocked + total_allowed
        
        block_rate = (total_blocked / total_requests * 100) if total_requests > 0 else 0
        
        print(f"📊 WAF Activity Summary (Last 24 Hours)")
        print(f"Total Requests: {total_requests:,.0f}")
        print(f"Blocked Requests: {total_blocked:,.0f}")
        print(f"Allowed Requests: {total_allowed:,.0f}")
        print(f"Block Rate: {block_rate:.2f}%")
        
        # Generate alerts for unusual activity
        if block_rate > 20:
            print(f"⚠️  HIGH ALERT: Block rate ({block_rate:.1f}%) is unusually high!")
            print("   Consider investigating potential attack patterns.")
        
        if total_blocked > 10000:
            print(f"⚠️  VOLUME ALERT: High number of blocked requests ({total_blocked:,.0f})")
            print("   Monitor for potential DDoS attack.")
    
    return {
        'total_requests': total_requests if 'total_requests' in locals() else 0,
        'blocked_requests': total_blocked if 'total_blocked' in locals() else 0,
        'block_rate': block_rate if 'block_rate' in locals() else 0
    }

# Example usage
if __name__ == "__main__":
    # Create IP set for blocking
    malicious_ips = ['192.168.1.100', '10.0.0.0/24', '172.16.0.1']
    ip_set_arn = create_ip_set('MaliciousIPs', 'CLOUDFRONT', malicious_ips)
    
    # Create comprehensive Web ACL
    web_acl_id, web_acl_arn = create_waf_web_acl('ComprehensiveProtection')
    
    if web_acl_arn:
        # Associate with CloudFront distribution
        cloudfront_arn = 'arn:aws:cloudfront::123456789012:distribution/E1234567890ABC'
        associate_waf_with_resource(web_acl_arn, cloudfront_arn)
        
        # Monitor activity
        activity = monitor_waf_activity('ComprehensiveProtection')
        print(f"🛡️ Protection Status: Active")
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def secrets_manager_tab():
    """Content for AWS Secrets Manager tab"""
    st.markdown("## 🔐 AWS Secrets Manager")
    st.markdown("*Manage, retrieve, and rotate database credentials, API keys, and other secrets throughout their lifecycles*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **AWS Secrets Manager** helps you manage, retrieve, and rotate database credentials, API keys, and other secrets throughout 
    their lifecycles. You can store and control access to secrets centrally by using the Secrets Manager console, CLI, or SDK.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Secrets Manager Architecture
    st.markdown("### 🏗️ Secrets Manager Workflow")
    common.mermaid(create_secrets_manager_mermaid(), height=1200)
    
    # Key Features
    st.markdown("### ✨ Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔄 Automatic Rotation
        - **Scheduled rotation** without user intervention
        - Lambda function integration
        - **Zero-downtime** credential updates
        - Custom rotation strategies
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔐 Strong Encryption
        - **AWS KMS encryption** at rest
        - TLS encryption in transit
        - **Customer-managed keys** support
        - Envelope encryption
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛡️ Security Best Practices
        - **No hard-coded credentials** in code
        - Centralized secret management
        - **Fine-grained access control**
        - Audit trail with CloudTrail
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Secret Creator
    st.markdown("### 🛠️ Interactive Secret Creator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📝 Secret Configuration")
        secret_name = st.text_input("Secret Name:", "prod/myapp/database")
        secret_type = st.selectbox("Secret Type:", [
            "Database Credentials",
            "API Keys", 
            "OAuth Tokens",
            "Custom Application Secrets",
            "Third-party Service Keys"
        ])
        
        # Dynamic fields based on secret type
        if secret_type == "Database Credentials":
            db_engine = st.selectbox("Database Engine:", ["MySQL", "PostgreSQL", "Oracle", "SQL Server"])
            username = st.text_input("Database Username:", "app_user")
            password = st.text_input("Database Password:", type="password")
            host = st.text_input("Database Host:", "prod-db.company.com")
            port = st.number_input("Port:", 1, 65535, 3306 if db_engine == "MySQL" else 5432)
        else:
            secret_value = st.text_area("Secret Value (JSON format):", 
                                      '{"api_key": "your-api-key", "secret_key": "your-secret-key"}')
    
    with col2:
        st.markdown("### ⚙️ Rotation Settings")
        enable_rotation = st.checkbox("Enable Automatic Rotation", value=True)
        
        if enable_rotation:
            rotation_interval = st.selectbox("Rotation Interval:", [
                "30 days", "60 days", "90 days", "Custom"
            ])
            
            if rotation_interval == "Custom":
                custom_days = st.number_input("Custom Interval (days):", 1, 365, 30)
            
            rotation_lambda = st.text_input("Rotation Lambda ARN:", 
                                          "arn:aws:lambda:us-east-1:123456789012:function:SecretsManagerRotation")
        
        kms_key = st.selectbox("KMS Key:", [
            "aws/secretsmanager (AWS Managed)",
            "Custom KMS Key",
            "Customer Managed Key"
        ])
        
        description = st.text_area("Description:", "Production database credentials for MyApp")
    
    if st.button("🔐 Create Secret", use_container_width=True):
        # Generate secret configuration
        if secret_type == "Database Credentials":
            secret_config = {
                "engine": db_engine.lower(),
                "username": username,
                "password": password,
                "host": host,
                "port": port,
                "dbname": "production"
            }
        else:
            try:
                secret_config = json.loads(secret_value)
            except:
                secret_config = {"raw_value": secret_value}
        
        secret_arn = f"arn:aws:secretsmanager:us-east-1:123456789012:secret:{secret_name}-{np.random.randint(100000, 999999)}"
        
        st.markdown('<div class="security-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ Secret Created Successfully!
        
        **Secret Details:**
        - **Name**: {secret_name}
        - **ARN**: {secret_arn}
        - **Type**: {secret_type}
        - **Encryption**: {kms_key}
        - **Rotation**: {'✅ Enabled' if enable_rotation else '❌ Disabled'}
        
        🔐 **Security Status**: Encrypted and Ready
        📅 **Next Rotation**: {(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Secret Types and Use Cases
    st.markdown("### 🎯 Secret Types and Use Cases")
    
    secret_types_data = {
        'Secret Type': ['Database Credentials', 'API Keys', 'OAuth Tokens', 'SSL Certificates', 'SSH Keys'],
        'Rotation Support': ['✅ Full', '⚠️ Manual', '✅ Full', '⚠️ Manual', '⚠️ Manual'],
        'Use Cases': [
            'RDS, Aurora, self-managed databases',
            'Third-party service integration',
            'Authentication with external services',
            'Web server certificates',
            'Server access credentials'
        ],
        'Recommended Rotation': ['30-90 days', '60-180 days', '24-48 hours', '1 year', '90-180 days']
    }
    
    df_secret_types = pd.DataFrame(secret_types_data)
    st.dataframe(df_secret_types, use_container_width=True)
    
    # Cost Analysis
    st.markdown("### 💰 Secrets Manager Cost Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Cost Calculator")
        num_secrets = st.slider("Number of Secrets:", 1, 1000, 50)
        api_calls_per_month = st.slider("API Calls per Month:", 1000, 1000000, 100000)
        
        # AWS Secrets Manager pricing (as of 2025)
        secret_cost = num_secrets * 0.40  # $0.40 per secret per month
        api_cost = (api_calls_per_month / 10000) * 0.05  # $0.05 per 10,000 API calls
        total_cost = secret_cost + api_cost
        
        col3, col4 = st.columns(2)
        with col3:
            st.metric("Secret Storage Cost", f"${secret_cost:.2f}/month")
            st.metric("API Call Cost", f"${api_cost:.2f}/month")
        with col4:
            st.metric("Total Monthly Cost", f"${total_cost:.2f}")
            st.metric("Cost per Secret", f"${total_cost/num_secrets:.3f}")
    
    with col2:
        # Cost comparison chart
        alternatives = ['Hard-coded Secrets', 'Environment Variables', 'Config Files', 'Secrets Manager']
        security_scores = [1, 3, 2, 10]
        operational_overhead = [1, 4, 6, 3]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Security Score', x=alternatives, y=security_scores,
                            marker_color=AWS_COLORS['success']))
        fig.add_trace(go.Bar(name='Operational Overhead', x=alternatives, y=operational_overhead,
                            marker_color=AWS_COLORS['warning']))
        
        fig.update_layout(title='Security vs Operational Overhead', barmode='group', height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Best Practices
    st.markdown("### 💡 Secrets Manager Best Practices")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚠️ Security Best Practices
        
        **Access Control:**
        - Use **IAM policies** for fine-grained access
        - Apply **least privilege** principle
        - Enable **VPC endpoints** for private access
        - Regularly audit access patterns
        
        **Secret Management:**
        - Use **descriptive names** with hierarchy
        - Enable **automatic rotation** where possible
        - Monitor rotation failures
        - **Version control** for secret updates
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="security-box">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛡️ Operational Best Practices
        
        **Application Integration:**
        - **Cache secrets** appropriately in applications
        - Handle rotation gracefully
        - Implement **retry logic** for API calls
        - Use SDK instead of direct API calls
        
        **Monitoring & Alerting:**
        - Set up **CloudWatch alarms** for failures
        - Monitor secret usage patterns
        - **Log rotation events**
        - Track unauthorized access attempts
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Secrets Manager Integration")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Complete Secrets Manager implementation with rotation and error handling
import boto3
import json
import pymysql
from botocore.exceptions import ClientError
import time

class SecretsManagerHelper:
    def __init__(self, region_name='us-east-1'):
        self.secrets_client = boto3.client('secretsmanager', region_name=region_name)
        self.secret_cache = {}
        self.cache_ttl = 300  # 5 minutes cache TTL
    
    def create_database_secret(self, secret_name, username, password, host, port, database):
        """Create a new database secret with automatic rotation"""
        secret_dict = {
            'engine': 'mysql',
            'username': username,
            'password': password,
            'host': host,
            'port': port,
            'dbname': database
        }
        
        try:
            response = self.secrets_client.create_secret(
                Name=secret_name,
                Description=f'Database credentials for {database}',
                SecretString=json.dumps(secret_dict),
                KmsKeyId='aws/secretsmanager'
            )
            
            print(f"✅ Secret created: {response['ARN']}")
            
            # Set up automatic rotation
            self.setup_rotation(secret_name, 30)  # 30-day rotation
            
            return response['ARN']
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceExistsException':
                print(f"⚠️  Secret {secret_name} already exists")
                return self.get_secret_arn(secret_name)
            else:
                print(f"❌ Error creating secret: {e}")
                return None
    
    def setup_rotation(self, secret_name, rotation_days):
        """Configure automatic rotation for a secret"""
        try:
            response = self.secrets_client.rotate_secret(
                SecretId=secret_name,
                RotationLambdaArn='arn:aws:lambda:us-east-1:123456789012:function:SecretsManagerMySQLRotationSingleUser',
                RotationRules={
                    'AutomaticallyAfterDays': rotation_days
                }
            )
            
            print(f"✅ Rotation configured for {secret_name}")
            return True
            
        except ClientError as e:
            print(f"❌ Error setting up rotation: {e}")
            return False
    
    def get_secret(self, secret_name, use_cache=True):
        """Retrieve a secret with caching support"""
        current_time = time.time()
        
        # Check cache first
        if use_cache and secret_name in self.secret_cache:
            cached_secret, cache_time = self.secret_cache[secret_name]
            if current_time - cache_time < self.cache_ttl:
                return cached_secret
        
        try:
            response = self.secrets_client.get_secret_value(SecretId=secret_name)
            secret_dict = json.loads(response['SecretString'])
            
            # Cache the secret
            if use_cache:
                self.secret_cache[secret_name] = (secret_dict, current_time)
            
            return secret_dict
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'DecryptionFailureException':
                print(f"❌ Cannot decrypt secret: {secret_name}")
            elif error_code == 'InternalServiceErrorException':
                print(f"❌ Internal service error retrieving: {secret_name}")
            elif error_code == 'InvalidParameterException':
                print(f"❌ Invalid parameter for secret: {secret_name}")
            elif error_code == 'InvalidRequestException':
                print(f"❌ Invalid request for secret: {secret_name}")
            elif error_code == 'ResourceNotFoundException':
                print(f"❌ Secret not found: {secret_name}")
            
            return None
    
    def get_database_connection(self, secret_name):
        """Get database connection using secrets from Secrets Manager"""
        secret = self.get_secret(secret_name)
        if not secret:
            return None
        
        try:
            connection = pymysql.connect(
                host=secret['host'],
                user=secret['username'],
                password=secret['password'],
                database=secret['dbname'],
                port=secret['port'],
                autocommit=True,
                charset='utf8mb4'
            )
            
            print(f"✅ Database connection established")
            return connection
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return None
    
    def update_secret(self, secret_name, new_secret_dict):
        """Update an existing secret"""
        try:
            response = self.secrets_client.update_secret(
                SecretId=secret_name,
                SecretString=json.dumps(new_secret_dict)
            )
            
            # Clear cache for this secret
            if secret_name in self.secret_cache:
                del self.secret_cache[secret_name]
            
            print(f"✅ Secret updated: {secret_name}")
            return response['ARN']
            
        except ClientError as e:
            print(f"❌ Error updating secret: {e}")
            return None
    
    def delete_secret(self, secret_name, force_delete=False):
        """Safely delete a secret"""
        try:
            if force_delete:
                response = self.secrets_client.delete_secret(
                    SecretId=secret_name,
                    ForceDeleteWithoutRecovery=True
                )
            else:
                response = self.secrets_client.delete_secret(
                    SecretId=secret_name,
                    RecoveryWindowInDays=30  # 30-day recovery window
                )
            
            print(f"✅ Secret scheduled for deletion: {secret_name}")
            return True
            
        except ClientError as e:
            print(f"❌ Error deleting secret: {e}")
            return False
    
    def list_secrets(self, name_filter=None):
        """List all secrets with optional name filtering"""
        try:
            kwargs = {}
            if name_filter:
                kwargs['Filters'] = [
                    {
                        'Key': 'name',
                        'Values': [name_filter]
                    }
                ]
            
            response = self.secrets_client.list_secrets(**kwargs)
            
            secrets_info = []
            for secret in response['SecretList']:
                info = {
                    'Name': secret['Name'],
                    'ARN': secret['ARN'],
                    'CreatedDate': secret.get('CreatedDate'),
                    'LastChangedDate': secret.get('LastChangedDate'),
                    'LastAccessedDate': secret.get('LastAccessedDate'),
                    'RotationEnabled': secret.get('RotationEnabled', False)
                }
                secrets_info.append(info)
            
            return secrets_info
            
        except ClientError as e:
            print(f"❌ Error listing secrets: {e}")
            return []

# Application example with database connection
class DatabaseApp:
    def __init__(self):
        self.secrets = SecretsManagerHelper()
        self.db_connection = None
    
    def initialize_database(self):
        """Initialize database connection using Secrets Manager"""
        self.db_connection = self.secrets.get_database_connection('prod/myapp/database')
        return self.db_connection is not None
    
    def execute_query(self, query, params=None):
        """Execute database query with automatic connection retry"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if not self.db_connection:
                    if not self.initialize_database():
                        raise Exception("Cannot establish database connection")
                
                cursor = self.db_connection.cursor()
                cursor.execute(query, params)
                
                if query.strip().upper().startswith('SELECT'):
                    results = cursor.fetchall()
                    cursor.close()
                    return results
                else:
                    cursor.close()
                    return True
                    
            except Exception as e:
                print(f"⚠️  Query execution failed (attempt {retry_count + 1}): {e}")
                
                # Clear connection and cache on failure
                self.db_connection = None
                retry_count += 1
                
                if retry_count < max_retries:
                    time.sleep(1)  # Brief pause before retry
                else:
                    print(f"❌ Query failed after {max_retries} attempts")
                    raise e
    
    def close_connection(self):
        """Safely close database connection"""
        if self.db_connection:
            self.db_connection.close()
            self.db_connection = None
            print("✅ Database connection closed")

# Example usage
if __name__ == "__main__":
    # Initialize Secrets Manager helper
    secrets = SecretsManagerHelper()
    
    # Create a database secret
    secret_arn = secrets.create_database_secret(
        secret_name='prod/myapp/database',
        username='app_user',
        password='secure_random_password_123!',
        host='prod-db.company.com',
        port=3306,
        database='production'
    )
    
    if secret_arn:
        print(f"Database secret created: {secret_arn}")
        
        # Use the secret in an application
        app = DatabaseApp()
        if app.initialize_database():
            # Execute some queries
            results = app.execute_query("SELECT COUNT(*) FROM users")
            print(f"Query results: {results}")
            
            app.close_connection()
    
    # List all secrets
    all_secrets = secrets.list_secrets()
    for secret in all_secrets:
        print(f"Secret: {secret['Name']}, Rotation: {secret['RotationEnabled']}")
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def kms_tab():
    """Content for AWS KMS tab"""
    st.markdown("## 🔑 AWS Key Management Service (KMS)")
    st.markdown("*Managed service to create and control cryptographic keys for data protection*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **AWS KMS** is a managed service that makes it easy for you to create and control the cryptographic keys that are used 
    to protect your data. All requests to use these keys are logged in AWS CloudTrail so that you can track who used which key, 
    how and when.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # KMS Architecture
    st.markdown("### 🏗️ KMS Encryption Process")
    common.mermaid(create_kms_encryption_mermaid(), height=1000)
    
    # Key Types
    st.markdown("### 🔐 AWS KMS Key Types")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 👤\n**Customer**\nManaged Keys")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        **Characteristics:**
        - **Full control** over key lifecycle
        - Custom key policies
        - **You manage** permissions
        - Can be disabled/deleted
        - **$1/month** per key + usage
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🏛️\n**AWS**\nManaged Keys")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        **Characteristics:**
        - **AWS manages** the key
        - Used by AWS services
        - **Automatic rotation** (yearly)
        - Cannot be disabled/deleted
        - **No additional charge**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🔒\n**AWS**\nOwned Keys")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        **Characteristics:**
        - **AWS owns and manages**
        - Used across multiple accounts
        - **Not visible** to customers
        - No customer control
        - **No charges** to customer
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive KMS Key Creator
    st.markdown("### 🛠️ Interactive KMS Key Creator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔑 Key Configuration")
        key_alias = st.text_input("Key Alias:", "alias/myapp-encryption-key")
        key_description = st.text_area("Key Description:", "Encryption key for MyApp production data")
        
        key_usage = st.selectbox("Key Usage:", [
            "ENCRYPT_DECRYPT (Symmetric)",
            "SIGN_VERIFY (Asymmetric)", 
            "GENERATE_VERIFY_MAC"
        ])
        
        key_spec = st.selectbox("Key Spec:", [
            "SYMMETRIC_DEFAULT",
            "RSA_2048",
            "RSA_3072", 
            "RSA_4096",
            "ECC_NIST_P256",
            "ECC_NIST_P384"
        ])
        
        origin = st.selectbox("Key Material Origin:", [
            "AWS_KMS (AWS Generated)",
            "EXTERNAL (Import Your Own)",
            "AWS_CLOUDHSM"
        ])
    
    with col2:
        st.markdown("### ⚙️ Key Policy & Usage")
        
        # Key policy configuration
        policy_type = st.selectbox("Policy Template:", [
            "Default Policy (Root user access)",
            "Service-Specific Policy",
            "Cross-Account Access Policy",
            "Custom Policy"
        ])
        
        enable_rotation = st.checkbox("Enable Automatic Key Rotation", value=True)
        
        if enable_rotation:
            rotation_period = st.selectbox("Rotation Period:", [
                "1 year (Recommended)",
                "2 years",
                "3 years"
            ])
        
        # Usage permissions
        key_admins = st.text_area("Key Administrators (ARNs):", 
                                 "arn:aws:iam::123456789012:root\narn:aws:iam::123456789012:user/admin")
        key_users = st.text_area("Key Users (ARNs):", 
                                "arn:aws:iam::123456789012:role/MyAppRole")
    
    if st.button("🔑 Create KMS Key", use_container_width=True):
        # Generate key configuration
        key_id = f"arn:aws:kms:us-east-1:123456789012:key/{np.random.randint(10000000, 99999999)}-" + \
                f"{np.random.randint(1000, 9999)}-{np.random.randint(1000, 9999)}-" + \
                f"{np.random.randint(1000, 9999)}-{np.random.randint(100000000000, 999999999999)}"
        
        # Calculate monthly cost
        base_cost = 1.00  # $1 per key per month
        estimated_requests = np.random.randint(10000, 100000)
        request_cost = (estimated_requests / 20000) * 0.03  # $0.03 per 20,000 requests
        total_cost = base_cost + request_cost
        
        st.markdown('<div class="security-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ KMS Key Created Successfully!
        
        **Key Details:**
        - **Key ID**: {key_id.split('/')[-1]}
        - **Alias**: {key_alias}
        - **Key ARN**: {key_id}
        - **Key Spec**: {key_spec}
        - **Usage**: {key_usage}
        - **Rotation**: {'✅ Enabled' if enable_rotation else '❌ Disabled'}
        
        💰 **Estimated Monthly Cost**: ${total_cost:.2f}
        📊 **Key State**: Enabled and Ready
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Encryption Methods Comparison
    st.markdown("### 🔐 KMS Encryption Methods")
    
    encryption_data = {
        'Method': ['Envelope Encryption', 'Direct Encryption', 'Client-Side Encryption'],
        'Data Limit': ['Unlimited', '4 KB', 'Unlimited'],
        'Performance': ['High', 'Low', 'Medium'],
        'Use Case': [
            'Large files, databases',
            'Small secrets, passwords',
            'Browser/mobile apps'
        ],
        'Network Calls': ['1 per operation', '1 per 4KB', 'Initial setup only'],
        'Best For': [
            'S3, RDS, EBS encryption',
            'Secrets Manager',
            'Client applications'
        ]
    }
    
    df_encryption = pd.DataFrame(encryption_data)
    st.dataframe(df_encryption, use_container_width=True)
    
    # KMS Integration with AWS Services
    st.markdown("### 🔗 KMS Integration with AWS Services")
    
    # Service integration chart
    services = ['Amazon S3', 'Amazon RDS', 'Amazon EBS', 'AWS Lambda', 'Amazon SQS', 'Amazon SNS']
    integration_scores = [10, 9, 10, 8, 7, 7]
    
    fig = px.bar(x=services, y=integration_scores, 
                 title='KMS Integration Score by AWS Service',
                 color=integration_scores,
                 color_continuous_scale=['#FF6B35', '#FF9900', '#3FB34F'])
    
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Cost Analysis
    st.markdown("### 💰 KMS Cost Analysis & Optimization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Cost Calculator")
        num_keys = st.slider("Number of Customer Keys:", 1, 100, 10)
        requests_per_month = st.slider("API Requests per Month:", 1000, 10000000, 100000)
        
        # KMS pricing calculation
        key_cost = num_keys * 1.00  # $1 per key per month
        request_cost = (requests_per_month / 20000) * 0.03  # $0.03 per 20,000 requests
        total_monthly_cost = key_cost + request_cost
        
        col3, col4 = st.columns(2)
        with col3:
            st.metric("Key Storage Cost", f"${key_cost:.2f}/month")
            st.metric("Request Cost", f"${request_cost:.2f}/month")
        with col4:
            st.metric("Total Monthly Cost", f"${total_monthly_cost:.2f}")
            st.metric("Cost per Key", f"${total_monthly_cost/num_keys:.2f}")
    
    with col2:
        # Cost optimization recommendations
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("""
        ### 💡 Cost Optimization Tips
        
        **Reduce API Calls:**
        - Use **data key caching**
        - Batch encrypt/decrypt operations
        - Use **envelope encryption** for large data
        
        **Key Management:**
        - **Consolidate** similar use case keys
        - Use **AWS managed keys** where appropriate
        - **Delete unused** customer managed keys
        - Implement **key rotation** policies
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Security Best Practices
    st.markdown("### 🛡️ KMS Security Best Practices")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔐 Key Management
        - Implement **least privilege** access
        - Use **separate keys** for different environments
        - Enable **key rotation** for long-lived keys
        - **Monitor key usage** with CloudTrail
        - Use **key policies** in addition to IAM policies
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛡️ Operational Security
        - **Never log** plaintext encryption keys
        - Use **VPC endpoints** for private access
        - Implement **cross-region** backup strategies
        - **Tag keys** for better organization
        - Set up **CloudWatch alarms** for anomalies
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: KMS Encryption Implementation")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Comprehensive KMS implementation with envelope encryption and best practices
import boto3
import base64
import json
from botocore.exceptions import ClientError
from cryptography.fernet import Fernet
import os

class KMSEncryptionHelper:
    def __init__(self, region_name='us-east-1'):
        self.kms_client = boto3.client('kms', region_name=region_name)
        self.data_key_cache = {}
        self.cache_max_age = 3600  # 1 hour cache for data keys
    
    def create_customer_key(self, key_alias, description, key_policy=None):
        """Create a customer managed KMS key"""
        try:
            # Create the key
            response = self.kms_client.create_key(
                Description=description,
                KeyUsage='ENCRYPT_DECRYPT',
                KeySpec='SYMMETRIC_DEFAULT',
                Origin='AWS_KMS'
            )
            
            key_id = response['KeyMetadata']['KeyId']
            key_arn = response['KeyMetadata']['Arn']
            
            # Create alias for the key
            self.kms_client.create_alias(
                AliasName=key_alias,
                TargetKeyId=key_id
            )
            
            # Set key policy if provided
            if key_policy:
                self.kms_client.put_key_policy(
                    KeyId=key_id,
                    PolicyName='default',
                    Policy=json.dumps(key_policy)
                )
            
            # Enable automatic key rotation
            self.kms_client.enable_key_rotation(KeyId=key_id)
            
            print(f"✅ KMS Key created successfully!")
            print(f"Key ID: {key_id}")
            print(f"Key ARN: {key_arn}")
            print(f"Alias: {key_alias}")
            
            return key_id, key_arn
            
        except ClientError as e:
            print(f"❌ Error creating KMS key: {e}")
            return None, None
    
    def generate_data_key(self, key_id, key_spec='AES_256'):
        """Generate a data encryption key for envelope encryption"""
        try:
            response = self.kms_client.generate_data_key(
                KeyId=key_id,
                KeySpec=key_spec
            )
            
            # Return both plaintext and encrypted data key
            return {
                'plaintext_key': response['Plaintext'],
                'encrypted_key': response['CiphertextBlob'],
                'key_id': response['KeyId']
            }
            
        except ClientError as e:
            print(f"❌ Error generating data key: {e}")
            return None
    
    def decrypt_data_key(self, encrypted_data_key):
        """Decrypt an encrypted data key"""
        try:
            response = self.kms_client.decrypt(CiphertextBlob=encrypted_data_key)
            return response['Plaintext']
            
        except ClientError as e:
            print(f"❌ Error decrypting data key: {e}")
            return None
    
    def envelope_encrypt(self, data, key_id):
        """Encrypt data using envelope encryption pattern"""
        try:
            # Generate a unique data key for this encryption operation
            data_key_response = self.generate_data_key(key_id)
            if not data_key_response:
                return None
            
            plaintext_key = data_key_response['plaintext_key']
            encrypted_key = data_key_response['encrypted_key']
            
            # Use the data key to encrypt the actual data
            fernet = Fernet(base64.urlsafe_b64encode(plaintext_key[:32]))
            encrypted_data = fernet.encrypt(data.encode() if isinstance(data, str) else data)
            
            # Return both encrypted data and encrypted data key
            return {
                'encrypted_data': base64.b64encode(encrypted_data).decode(),
                'encrypted_key': base64.b64encode(encrypted_key).decode(),
                'key_id': key_id
            }
            
        except Exception as e:
            print(f"❌ Error in envelope encryption: {e}")
            return None
        finally:
            # Clear plaintext key from memory
            if 'plaintext_key' in locals():
                plaintext_key = b'\\x00' * len(plaintext_key)
    
    def envelope_decrypt(self, encrypted_package):
        """Decrypt data using envelope encryption pattern"""
        try:
            encrypted_data = base64.b64decode(encrypted_package['encrypted_data'])
            encrypted_key = base64.b64decode(encrypted_package['encrypted_key'])
            
            # Decrypt the data key using KMS
            plaintext_key = self.decrypt_data_key(encrypted_key)
            if not plaintext_key:
                return None
            
            # Use the decrypted data key to decrypt the actual data
            fernet = Fernet(base64.urlsafe_b64encode(plaintext_key[:32]))
            decrypted_data = fernet.decrypt(encrypted_data)
            
            return decrypted_data.decode() if isinstance(decrypted_data, bytes) else decrypted_data
            
        except Exception as e:
            print(f"❌ Error in envelope decryption: {e}")
            return None
        finally:
            # Clear plaintext key from memory
            if 'plaintext_key' in locals():
                plaintext_key = b'\\x00' * len(plaintext_key)
    
    def direct_encrypt(self, data, key_id):
        """Direct encryption for small data (< 4KB)"""
        try:
            if len(data) > 4096:
                raise ValueError("Data too large for direct encryption. Use envelope encryption.")
            
            response = self.kms_client.encrypt(
                KeyId=key_id,
                Plaintext=data.encode() if isinstance(data, str) else data
            )
            
            return {
                'encrypted_data': base64.b64encode(response['CiphertextBlob']).decode(),
                'key_id': response['KeyId']
            }
            
        except ClientError as e:
            print(f"❌ Error in direct encryption: {e}")
            return None
    
    def direct_decrypt(self, encrypted_data_b64):
        """Direct decryption for small data"""
        try:
            encrypted_data = base64.b64decode(encrypted_data_b64)
            
            response = self.kms_client.decrypt(CiphertextBlob=encrypted_data)
            
            plaintext = response['Plaintext']
            return plaintext.decode() if isinstance(plaintext, bytes) else plaintext
            
        except ClientError as e:
            print(f"❌ Error in direct decryption: {e}")
            return None
    
    def encrypt_file(self, file_path, key_id, output_path=None):
        """Encrypt a file using envelope encryption"""
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            encrypted_package = self.envelope_encrypt(file_data, key_id)
            if not encrypted_package:
                return False
            
            # Save encrypted file
            if not output_path:
                output_path = file_path + '.encrypted'
            
            with open(output_path, 'w') as f:
                json.dump(encrypted_package, f)
            
            print(f"✅ File encrypted successfully: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error encrypting file: {e}")
            return False
    
    def decrypt_file(self, encrypted_file_path, output_path=None):
        """Decrypt a file that was encrypted with envelope encryption"""
        try:
            with open(encrypted_file_path, 'r') as f:
                encrypted_package = json.load(f)
            
            decrypted_data = self.envelope_decrypt(encrypted_package)
            if not decrypted_data:
                return False
            
            # Save decrypted file
            if not output_path:
                output_path = encrypted_file_path.replace('.encrypted', '.decrypted')
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data if isinstance(decrypted_data, bytes) else decrypted_data.encode())
            
            print(f"✅ File decrypted successfully: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error decrypting file: {e}")
            return False
    
    def get_key_info(self, key_id):
        """Get detailed information about a KMS key"""
        try:
            response = self.kms_client.describe_key(KeyId=key_id)
            key_metadata = response['KeyMetadata']
            
            # Check rotation status
            try:
                rotation_response = self.kms_client.get_key_rotation_status(KeyId=key_id)
                rotation_enabled = rotation_response['KeyRotationEnabled']
            except:
                rotation_enabled = False
            
            # Get key policy
            try:
                policy_response = self.kms_client.get_key_policy(KeyId=key_id, PolicyName='default')
                key_policy = json.loads(policy_response['Policy'])
            except:
                key_policy = None
            
            return {
                'key_id': key_metadata['KeyId'],
                'arn': key_metadata['Arn'],
                'description': key_metadata.get('Description', ''),
                'key_usage': key_metadata['KeyUsage'],
                'key_state': key_metadata['KeyState'],
                'creation_date': key_metadata['CreationDate'],
                'rotation_enabled': rotation_enabled,
                'key_policy': key_policy
            }
            
        except ClientError as e:
            print(f"❌ Error getting key info: {e}")
            return None
    
    def monitor_key_usage(self, key_id, days=7):
        """Monitor key usage using CloudTrail logs"""
        cloudtrail = boto3.client('cloudtrail')
        
        from datetime import datetime, timedelta
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        try:
            response = cloudtrail.lookup_events(
                LookupAttributes=[
                    {
                        'AttributeKey': 'ResourceName',
                        'AttributeValue': key_id
                    }
                ],
                StartTime=start_time,
                EndTime=end_time
            )
            
            events = response['Events']
            usage_summary = {
                'total_events': len(events),
                'encrypt_calls': 0,
                'decrypt_calls': 0,
                'generate_data_key_calls': 0,
                'unique_users': set()
            }
            
            for event in events:
                event_name = event['EventName']
                user_identity = event.get('Username', 'Unknown')
                
                usage_summary['unique_users'].add(user_identity)
                
                if event_name == 'Encrypt':
                    usage_summary['encrypt_calls'] += 1
                elif event_name == 'Decrypt':
                    usage_summary['decrypt_calls'] += 1
                elif event_name == 'GenerateDataKey':
                    usage_summary['generate_data_key_calls'] += 1
            
            usage_summary['unique_users'] = len(usage_summary['unique_users'])
            
            return usage_summary
            
        except Exception as e:
            print(f"❌ Error monitoring key usage: {e}")
            return None

# Example usage and testing
if __name__ == "__main__":
    # Initialize KMS helper
    kms = KMSEncryptionHelper()
    
    # Create a new customer managed key
    key_id, key_arn = kms.create_customer_key(
        key_alias='alias/myapp-encryption-key',
        description='MyApp production data encryption key'
    )
    
    if key_id:
        print(f"\\n📋 Key Information:")
        key_info = kms.get_key_info(key_id)
        if key_info:
            print(f"Key State: {key_info['key_state']}")
            print(f"Rotation Enabled: {key_info['rotation_enabled']}")
        
        # Test envelope encryption for large data
        large_data = "This is a large piece of data that needs to be encrypted securely. " * 100
        print(f"\\n🔐 Testing Envelope Encryption...")
        encrypted_package = kms.envelope_encrypt(large_data, key_id)
        
        if encrypted_package:
            print("✅ Envelope encryption successful")
            
            # Test decryption
            decrypted_data = kms.envelope_decrypt(encrypted_package)
            if decrypted_data == large_data:
                print("✅ Envelope decryption successful")
            else:
                print("❌ Envelope decryption failed")
        
        # Test direct encryption for small data
        small_data = "Small secret password"
        print(f"\\n🔐 Testing Direct Encryption...")
        encrypted_direct = kms.direct_encrypt(small_data, key_id)
        
        if encrypted_direct:
            print("✅ Direct encryption successful")
            
            # Test decryption
            decrypted_direct = kms.direct_decrypt(encrypted_direct['encrypted_data'])
            if decrypted_direct == small_data:
                print("✅ Direct decryption successful")
            else:
                print("❌ Direct decryption failed")
        
        # Monitor key usage
        print(f"\\n📊 Key Usage Monitoring...")
        usage = kms.monitor_key_usage(key_id)
        if usage:
            print(f"Total Events: {usage['total_events']}")
            print(f"Encrypt Calls: {usage['encrypt_calls']}")
            print(f"Decrypt Calls: {usage['decrypt_calls']}")
            print(f"Unique Users: {usage['unique_users']}")
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def privatelink_tab():
    """Content for AWS PrivateLink tab"""
    st.markdown("## 🔗 AWS PrivateLink")
    st.markdown("*Privately connect your VPC to services as if they were in your VPC*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **AWS PrivateLink** is a highly available, scalable technology that enables you to privately connect your VPC to services 
    as if they were in your VPC. Amazon VPC instances do not require public IP addresses to communicate with resources of the service. 
    Traffic between an Amazon VPC and a service does not leave the Amazon network.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # PrivateLink Architecture
    st.markdown("### 🏗️ AWS PrivateLink Architecture")
    common.mermaid(create_privatelink_mermaid(), height=800)
    
    # Key Benefits
    st.markdown("### ✨ Key Benefits of AWS PrivateLink")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🔒\n**Enhanced**\nSecurity")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🚫\n**No Internet**\nRequired")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### ⚡\n**Improved**\nPerformance")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 📏\n**Simplified**\nNetworking")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # VPC Endpoint Types
    st.markdown("### 🔍 VPC Endpoint Types")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🌐 Gateway Endpoints
        
        **Supported Services:**
        - Amazon S3
        - Amazon DynamoDB
        
        **Characteristics:**
        - **Route table entries** required
        - No additional charges
        - **Regional service** access
        - Policy-based access control
        
        **Use Cases:**
        - S3 bucket access from private subnets
        - DynamoDB table operations
        - Data pipeline applications
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔗 Interface Endpoints
        
        **Supported Services:**
        - 100+ AWS services
        - Your own services
        - Third-party services
        
        **Characteristics:**
        - **ENI with private IP** in subnet
        - Hourly + data processing charges
        - **DNS resolution** support
        - Security group controls
        
        **Use Cases:**
        - EC2, Lambda, ECS API calls
        - CloudWatch, SNS, SQS access
        - Custom application services
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive VPC Endpoint Creator
    st.markdown("### 🛠️ Interactive VPC Endpoint Creator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔧 Endpoint Configuration")
        endpoint_type = st.selectbox("Endpoint Type:", [
            "Interface Endpoint (com.amazonaws.region.service)",
            "Gateway Endpoint (S3/DynamoDB)"
        ])
        
        if "Interface" in endpoint_type:
            service_name = st.selectbox("AWS Service:", [
                "com.amazonaws.us-east-1.ec2",
                "com.amazonaws.us-east-1.s3",
                "com.amazonaws.us-east-1.lambda",
                "com.amazonaws.us-east-1.logs",
                "com.amazonaws.us-east-1.monitoring",
                "com.amazonaws.us-east-1.sns",
                "com.amazonaws.us-east-1.sqs",
                "com.amazonaws.us-east-1.secretsmanager"
            ])
            
            vpc_id = st.text_input("VPC ID:", "vpc-12345678")
            subnet_ids = st.text_area("Subnet IDs (one per line):", "subnet-12345678\nsubnet-87654321")
            security_group_ids = st.text_area("Security Group IDs:", "sg-12345678")
            
        else:
            service_name = st.selectbox("Service:", ["S3", "DynamoDB"])
            vpc_id = st.text_input("VPC ID:", "vpc-12345678")
            route_table_ids = st.text_area("Route Table IDs:", "rtb-12345678\nrtb-87654321")
    
    with col2:
        st.markdown("### ⚙️ Advanced Settings")
        
        enable_dns = st.checkbox("Enable DNS Resolution", value=True)
        enable_dns_hostnames = st.checkbox("Enable Private DNS Names", value=True)
        
        policy_type = st.selectbox("Endpoint Policy:", [
            "Full Access (Default)",
            "Custom Policy",
            "Restricted Access"
        ])
        
        if policy_type == "Custom Policy":
            custom_policy = st.text_area("Custom Policy JSON:", 
                                       '{"Version": "2012-10-17", "Statement": []}')
        
        tags = st.text_area("Tags (Key=Value, one per line):", "Environment=Production\nProject=MyApp")
    
    if st.button("🔗 Create VPC Endpoint", use_container_width=True):
        # Generate endpoint configuration
        endpoint_id = f"vpce-{np.random.randint(10000000, 99999999)}"
        
        # Calculate estimated cost for interface endpoints
        if "Interface" in endpoint_type:
            num_subnets = len(subnet_ids.strip().split('\n')) if subnet_ids.strip() else 1
            hourly_cost = num_subnets * 0.01  # $0.01 per hour per AZ
            data_processing_cost = 0.01  # $0.01 per GB processed
            monthly_cost = hourly_cost * 24 * 30
        else:
            monthly_cost = 0  # Gateway endpoints are free
        
        st.markdown('<div class="security-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ VPC Endpoint Created Successfully!
        
        **Endpoint Details:**
        - **Endpoint ID**: {endpoint_id}
        - **Service Name**: {service_name}
        - **Type**: {endpoint_type.split(' ')[0]}
        - **VPC**: {vpc_id}
        - **State**: Available
        
        💰 **Cost Information:**
        - **Monthly Base Cost**: ${monthly_cost:.2f}
        - **Data Processing**: $0.01 per GB (Interface only)
        - **Gateway Endpoints**: Free
        
        🔒 **Security**: Private connectivity established!
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # PrivateLink Use Cases
    st.markdown("### 🌟 Common PrivateLink Use Cases")
    
    use_cases_data = {
        'Use Case': ['Database Access', 'API Gateway', 'Microservices', 'Data Analytics', 'Compliance'],
        'Service Type': ['Interface Endpoint', 'Interface Endpoint', 'Custom Service', 'Gateway Endpoint', 'Interface Endpoint'],
        'Primary Benefit': ['Security', 'Performance', 'Isolation', 'Cost', 'Compliance'],
        'Example Services': [
            'RDS, Aurora via EC2 API',
            'API Gateway REST APIs',
            'Cross-VPC service calls',
            'S3, DynamoDB access',
            'CloudTrail, Config access'
        ],
        'Cost Impact': ['Medium', 'Low', 'High', 'None', 'Low']
    }
    
    df_use_cases = pd.DataFrame(use_cases_data)
    st.dataframe(df_use_cases, use_container_width=True)
    
    # Performance Comparison
    st.markdown("### 📊 PrivateLink vs Internet Gateway Performance")
    
    # Generate performance comparison data
    scenarios = ['Internet Gateway', 'NAT Gateway', 'VPC Endpoint (Interface)', 'VPC Endpoint (Gateway)']
    latency = [45, 35, 15, 12]
    security_score = [6, 7, 9, 9]
    cost_score = [8, 6, 5, 10]  # Higher is better (lower cost)
    
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('Latency (ms)', 'Security Score', 'Cost Efficiency'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]]
    )
    
    fig.add_trace(
        go.Bar(x=scenarios, y=latency, name='Latency', marker_color=AWS_COLORS['warning']),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=scenarios, y=security_score, name='Security', marker_color=AWS_COLORS['success']),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Bar(x=scenarios, y=cost_score, name='Cost Efficiency', marker_color=AWS_COLORS['primary']),
        row=1, col=3
    )
    
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Security Group Configuration
    st.markdown("### 🛡️ Security Group Configuration for VPC Endpoints")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🔒 Interface Endpoint Security Groups
    
    **Inbound Rules Required:**
    - **Port 443 (HTTPS)** from your application security groups
    - **Port 80 (HTTP)** if needed (not recommended)
    - **Source**: Security groups of resources that need access
    
    **Best Practices:**
    - Use **specific security groups** as sources, not CIDR blocks
    - **Minimum required ports** only
    - Regular **security group audits**
    - **Tag security groups** for better management
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Troubleshooting Guide
    st.markdown("### 🔧 PrivateLink Troubleshooting Guide")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ❌ Common Issues
        
        **DNS Resolution Problems:**
        - Enable DNS resolution on VPC endpoint
        - Check VPC DNS settings
        - Verify private DNS names
        
        **Connection Timeouts:**
        - Check security group rules
        - Verify subnet routing
        - Confirm endpoint policy
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ✅ Solutions
        
        **DNS Issues:**
        - Use endpoint-specific DNS names
        - Configure Route 53 private zones
        - Check DHCP option sets
        
        **Connectivity Issues:**
        - Test with AWS CLI/SDK
        - Use VPC Flow Logs
        - Check CloudTrail for API calls
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: PrivateLink Implementation")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Comprehensive AWS PrivateLink implementation and management
import boto3
import json
from botocore.exceptions import ClientError

class PrivateLinkManager:
    def __init__(self, region_name='us-east-1'):
        self.ec2_client = boto3.client('ec2', region_name=region_name)
        self.region = region_name
    
    def create_interface_endpoint(self, service_name, vpc_id, subnet_ids, security_group_ids, 
                                 enable_dns=True, policy=None):
        """Create a VPC Interface Endpoint"""
        try:
            endpoint_config = {
                'VpcId': vpc_id,
                'ServiceName': service_name,
                'VpcEndpointType': 'Interface',
                'SubnetIds': subnet_ids,
                'SecurityGroupIds': security_group_ids,
                'PrivateDnsEnabled': enable_dns
            }
            
            # Add custom policy if provided
            if policy:
                endpoint_config['PolicyDocument'] = json.dumps(policy)
            
            response = self.ec2_client.create_vpc_endpoint(**endpoint_config)
            
            endpoint_id = response['VpcEndpoint']['VpcEndpointId']
            print(f"✅ Interface endpoint created: {endpoint_id}")
            print(f"Service: {service_name}")
            print(f"DNS Names: {response['VpcEndpoint'].get('DnsEntries', [])}")
            
            return endpoint_id
            
        except ClientError as e:
            print(f"❌ Error creating interface endpoint: {e}")
            return None
    
    def create_gateway_endpoint(self, service_name, vpc_id, route_table_ids, policy=None):
        """Create a VPC Gateway Endpoint (S3 or DynamoDB)"""
        try:
            endpoint_config = {
                'VpcId': vpc_id,
                'ServiceName': f'com.amazonaws.{self.region}.{service_name.lower()}',
                'VpcEndpointType': 'Gateway',
                'RouteTableIds': route_table_ids
            }
            
            # Add custom policy if provided
            if policy:
                endpoint_config['PolicyDocument'] = json.dumps(policy)
            
            response = self.ec2_client.create_vpc_endpoint(**endpoint_config)
            
            endpoint_id = response['VpcEndpoint']['VpcEndpointId']
            print(f"✅ Gateway endpoint created: {endpoint_id}")
            print(f"Service: {service_name}")
            
            return endpoint_id
            
        except ClientError as e:
            print(f"❌ Error creating gateway endpoint: {e}")
            return None
    
    def get_available_services(self):
        """List all available VPC endpoint services"""
        try:
            response = self.ec2_client.describe_vpc_endpoint_services()
            
            aws_services = []
            custom_services = []
            
            for service in response['ServiceNames']:
                if service.startswith('com.amazonaws'):
                    aws_services.append(service)
                else:
                    custom_services.append(service)
            
            return {
                'aws_services': sorted(aws_services),
                'custom_services': sorted(custom_services),
                'total_count': len(response['ServiceNames'])
            }
            
        except ClientError as e:
            print(f"❌ Error listing services: {e}")
            return None
    
    def create_restrictive_endpoint_policy(self, allowed_actions, allowed_resources=None):
        """Create a restrictive endpoint policy"""
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": allowed_actions,
                    "Resource": allowed_resources or "*"
                }
            ]
        }
        
        return policy
    
    def monitor_endpoint_usage(self, endpoint_id):
        """Monitor VPC endpoint usage and performance"""
        cloudwatch = boto3.client('cloudwatch', region_name=self.region)
        
        from datetime import datetime, timedelta
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        
        try:
            # Get endpoint metrics if available
            metrics = []
            
            # Try to get network metrics
            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/VPC-Endpoint',
                MetricName='PacketsDropped',
                Dimensions=[
                    {'Name': 'VPC Endpoint Id', 'Value': endpoint_id}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            
            if response['Datapoints']:
                metrics.append({
                    'metric': 'PacketsDropped',
                    'datapoints': response['Datapoints']
                })
            
            return metrics
            
        except Exception as e:
            print(f"⚠️  Limited metrics available for endpoint {endpoint_id}: {e}")
            return []
    
    def test_endpoint_connectivity(self, endpoint_id, service_name):
        """Test connectivity to VPC endpoint"""
        try:
            # Get endpoint details
            response = self.ec2_client.describe_vpc_endpoints(
                VpcEndpointIds=[endpoint_id]
            )
            
            if not response['VpcEndpoints']:
                print(f"❌ Endpoint {endpoint_id} not found")
                return False
            
            endpoint = response['VpcEndpoints'][0]
            endpoint_state = endpoint['State']
            
            print(f"🔍 Endpoint Status: {endpoint_state}")
            
            if endpoint_state != 'Available':
                print(f"⚠️  Endpoint not in Available state")
                return False
            
            # For interface endpoints, test DNS resolution
            if endpoint['VpcEndpointType'] == 'Interface':
                dns_entries = endpoint.get('DnsEntries', [])
                print(f"🌐 DNS Entries: {len(dns_entries)}")
                for dns_entry in dns_entries:
                    print(f"   {dns_entry['DnsName']}")
            
            # Test basic connectivity by making an API call
            if 'ec2' in service_name:
                # Test EC2 API call through endpoint
                test_response = self.ec2_client.describe_regions()
                print(f"✅ API test successful: {len(test_response['Regions'])} regions")
                return True
            
            elif 's3' in service_name:
                # Test S3 API call
                s3_client = boto3.client('s3', region_name=self.region)
                test_response = s3_client.list_buckets()
                print(f"✅ S3 API test successful: {len(test_response['Buckets'])} buckets")
                return True
            
            print(f"✅ Endpoint connectivity appears healthy")
            return True
            
        except Exception as e:
            print(f"❌ Connectivity test failed: {e}")
            return False
    
    def create_security_group_for_endpoint(self, vpc_id, allowed_sg_ids, group_name):
        """Create security group specifically for VPC endpoints"""
        try:
            # Create security group
            response = self.ec2_client.create_security_group(
                VpcId=vpc_id,
                GroupName=group_name,
                Description='Security group for VPC endpoint access'
            )
            
            sg_id = response['GroupId']
            
            # Add inbound rules for HTTPS access from specified security groups
            for source_sg_id in allowed_sg_ids:
                self.ec2_client.authorize_security_group_ingress(
                    GroupId=sg_id,
                    IpPermissions=[
                        {
                            'IpProtocol': 'tcp',
                            'FromPort': 443,
                            'ToPort': 443,
                            'UserIdGroupPairs': [
                                {
                                    'GroupId': source_sg_id,
                                    'Description': f'HTTPS access from {source_sg_id}'
                                }
                            ]
                        }
                    ]
                )
            
            print(f"✅ Security group created: {sg_id}")
            return sg_id
            
        except ClientError as e:
            print(f"❌ Error creating security group: {e}")
            return None
    
    def cleanup_endpoint(self, endpoint_id):
        """Clean up VPC endpoint and associated resources"""
        try:
            # Delete VPC endpoint
            response = self.ec2_client.delete_vpc_endpoint(
                VpcEndpointIds=[endpoint_id]
            )
            
            print(f"✅ VPC endpoint {endpoint_id} deleted")
            return True
            
        except ClientError as e:
            print(f"❌ Error deleting endpoint: {e}")
            return False
    
    def get_endpoint_cost_estimate(self, endpoint_type, num_azs=2, gb_processed_monthly=100):
        """Estimate monthly cost for VPC endpoint"""
        if endpoint_type.lower() == 'gateway':
            return {
                'hourly_cost': 0,
                'data_processing_cost': 0,
                'monthly_total': 0,
                'note': 'Gateway endpoints (S3, DynamoDB) are free'
            }
        
        else:  # Interface endpoint
            hourly_rate = 0.01  # $0.01 per hour per AZ
            data_rate = 0.01    # $0.01 per GB processed
            
            monthly_hourly_cost = hourly_rate * num_azs * 24 * 30
            monthly_data_cost = gb_processed_monthly * data_rate
            
            return {
                'hourly_cost': monthly_hourly_cost,
                'data_processing_cost': monthly_data_cost,
                'monthly_total': monthly_hourly_cost + monthly_data_cost,
                'breakdown': {
                    'availability_zones': num_azs,
                    'hours_per_month': 24 * 30,
                    'gb_processed': gb_processed_monthly
                }
            }

# Example usage and comprehensive setup
if __name__ == "__main__":
    # Initialize PrivateLink manager
    pl_manager = PrivateLinkManager(region_name='us-east-1')
    
    # Get available services
    print("🔍 Available VPC Endpoint Services:")
    services = pl_manager.get_available_services()
    if services:
        print(f"AWS Services: {len(services['aws_services'])}")
        print(f"Custom Services: {len(services['custom_services'])}")
        
        # Show some popular services
        popular_services = [s for s in services['aws_services'] 
                          if any(service in s for service in ['ec2', 's3', 'lambda', 'logs'])]
        print("Popular Services:")
        for svc in popular_services[:5]:
            print(f"  - {svc}")
    
    # Create security group for endpoints
    sg_id = pl_manager.create_security_group_for_endpoint(
        vpc_id='vpc-12345678',
        allowed_sg_ids=['sg-app1', 'sg-app2'],
        group_name='VPCEndpoint-SecurityGroup'
    )
    
    if sg_id:
        # Create interface endpoint for EC2 API
        ec2_endpoint = pl_manager.create_interface_endpoint(
            service_name='com.amazonaws.us-east-1.ec2',
            vpc_id='vpc-12345678',
            subnet_ids=['subnet-12345678', 'subnet-87654321'],
            security_group_ids=[sg_id],
            enable_dns=True
        )
        
        if ec2_endpoint:
            # Test the endpoint
            print(f"\\n🧪 Testing endpoint connectivity...")
            success = pl_manager.test_endpoint_connectivity(
                ec2_endpoint, 
                'com.amazonaws.us-east-1.ec2'
            )
            
            if success:
                print("✅ Endpoint is working correctly")
            
            # Get cost estimate
            cost = pl_manager.get_endpoint_cost_estimate('interface', 2, 500)
            print(f"\\n💰 Monthly Cost Estimate: ${cost['monthly_total']:.2f}")
            print(f"   Hourly Costs: ${cost['hourly_cost']:.2f}")
            print(f"   Data Processing: ${cost['data_processing_cost']:.2f}")
    
    # Create gateway endpoint for S3
    s3_endpoint = pl_manager.create_gateway_endpoint(
        service_name='s3',
        vpc_id='vpc-12345678',
        route_table_ids=['rtb-12345678', 'rtb-87654321']
    )
    
    if s3_endpoint:
        print(f"\\n✅ S3 Gateway endpoint created successfully")
        cost = pl_manager.get_endpoint_cost_estimate('gateway')
        print(f"💰 S3 Gateway Cost: {cost['note']}")
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def certificate_manager_tab():
    """Content for AWS Certificate Manager tab"""
    st.markdown("## 📜 AWS Certificate Manager (ACM)")
    st.markdown("*Provision and manage SSL/TLS certificates with AWS services and connected resources*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **AWS Certificate Manager** is a service that lets you easily provision, manage, and deploy public and private Secure Sockets Layer/Transport Layer Security (SSL/TLS) certificates for use with AWS services and your internal connected resources.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ACM Architecture
    st.markdown("### 🏗️ ACM Certificate Workflow")
    common.mermaid(create_acm_certificate_mermaid(), height=1200)
    
    # Key Features
    st.markdown("### ✨ Key Features & Benefits")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔒 Secure Website Protection
        - **SSL/TLS certificates** for HTTPS
        - Stop traffic securely to your website
        - **Encryption in transit** protection
        - Industry-standard security protocols
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛡️ Internal Resource Protection
        - **Private network communication** security
        - Server-to-server encryption
        - **Mobile and IoT device** protection
        - Internal application security
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚡ Improved Uptime
        - **Automated certificate management**
        - Automatic renewal process
        - **No manual intervention** required
        - 60-day renewal window
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Certificate Request Tool
    st.markdown("### 🛠️ Interactive Certificate Request Tool")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📝 Certificate Configuration")
        
        cert_type = st.selectbox("Certificate Type:", [
            "Public Certificate (Free)",
            "Private Certificate (Private CA)"
        ])
        
        domain_name = st.text_input("Primary Domain Name:", "example.com")
        
        additional_domains = st.text_area("Additional Domain Names (one per line):", 
                                        "www.example.com\napi.example.com\n*.dev.example.com")
        
        validation_method = st.selectbox("Domain Validation Method:", [
            "DNS Validation (Recommended)",
            "Email Validation"
        ])
        
        if validation_method == "Email Validation":
            admin_emails = st.text_area("Administrator Email Addresses:", 
                                      "admin@example.com\nwebmaster@example.com")
    
    with col2:
        st.markdown("### ⚙️ Certificate Usage")
        
        intended_use = st.multiselect("Intended Use:", [
            "CloudFront Distribution",
            "Application Load Balancer", 
            "API Gateway",
            "Elastic Beanstalk",
            "CloudFormation Stack"
        ], default=["CloudFront Distribution"])
        
        key_algorithm = st.selectbox("Key Algorithm:", [
            "RSA-2048 (Default)",
            "RSA-1024 (Legacy)",
            "ECDSA P-256",
            "ECDSA P-384"
        ])
        
        tags = st.text_area("Tags (Key=Value format):", 
                          "Environment=Production\nProject=WebApp\nOwner=DevTeam")
    
    if st.button("📜 Request Certificate", use_container_width=True):
        # Generate certificate request details
        cert_arn = f"arn:aws:acm:us-east-1:123456789012:certificate/{np.random.randint(10000000, 99999999)}-" + \
                  f"{np.random.randint(1000, 9999)}-{np.random.randint(1000, 9999)}-" + \
                  f"{np.random.randint(1000, 9999)}-{np.random.randint(100000000000, 999999999999)}"
        
        all_domains = [domain_name]
        if additional_domains.strip():
            all_domains.extend([d.strip() for d in additional_domains.split('\n') if d.strip()])
        
        # Calculate estimated validation time
        if validation_method == "DNS Validation":
            validation_time = "5-10 minutes (automated)"
        else:
            validation_time = "24-72 hours (manual approval)"
        
        st.markdown('<div class="security-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ Certificate Request Submitted!
        
        **Certificate Details:**
        - **Certificate ARN**: {cert_arn}
        - **Primary Domain**: {domain_name}
        - **Total Domains**: {len(all_domains)}
        - **Validation Method**: {validation_method}
        - **Key Algorithm**: {key_algorithm}
        - **Status**: Pending Validation
        
        ⏱️ **Expected Validation Time**: {validation_time}
        🔄 **Auto-Renewal**: Enabled (60 days before expiration)
        💰 **Cost**: {'Free' if cert_type == 'Public Certificate (Free)' else '$400/month for Private CA'}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Certificate Usage by Service
    st.markdown("### 🔗 ACM Certificate Usage by AWS Service")
    
    service_usage_data = {
        'AWS Service': ['CloudFront', 'Application Load Balancer', 'API Gateway', 'Elastic Beanstalk', 'CloudFormation'],
        'Certificate Type': ['Public/Private', 'Public/Private', 'Public', 'Public', 'Public/Private'],
        'Automatic Deployment': ['✅ Yes', '✅ Yes', '✅ Yes', '✅ Yes', '⚠️ Template Required'],
        'Renewal Handling': ['Automatic', 'Automatic', 'Automatic', 'Automatic', 'Automatic'],
        'Regional Requirement': [
            'us-east-1 (Global)',
            'Same region as ALB',
            'us-east-1 (Edge)',
            'Same region as app',
            'Template specified'
        ]
    }
    
    df_service_usage = pd.DataFrame(service_usage_data)
    st.dataframe(df_service_usage, use_container_width=True)
    
    # Validation Methods Comparison
    st.markdown("### 🔍 Certificate Validation Methods")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🌐 DNS Validation (Recommended)
        
        **Process:**
        1. ACM provides DNS record (CNAME)
        2. Add record to your DNS zone
        3. **Automatic validation** within minutes
        4. **Supports wildcard** certificates
        
        **Advantages:**
        - Fast validation (5-10 minutes)
        - **Fully automated** renewal
        - Works with any DNS provider
        - **Best for production** environments
        
        **Requirements:**
        - Access to DNS management
        - Ability to create CNAME records
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📧 Email Validation
        
        **Process:**
        1. ACM sends validation emails
        2. **Manual approval** via email link
        3. Validation within 24-72 hours
        4. **No wildcard** support
        
        **Advantages:**
        - No DNS access required
        - Simple process
        - **Legacy compatibility**
        
        **Disadvantages:**
        - **Manual intervention** required
        - Slower validation process
        - **Renewal challenges**
        - Dependent on email delivery
        
        **Email Addresses Used:**
        - admin@domain.com, administrator@domain.com
        - hostmaster@domain.com, postmaster@domain.com
        - webmaster@domain.com
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Certificate Lifecycle Management
    st.markdown("### 🔄 Certificate Lifecycle Management")
    
    # Create lifecycle timeline with proper start and end dates
    current_date = datetime.now()
    lifecycle_data = {
        'Stage': ['Request', 'Validation', 'Issued', 'In Use', 'Renewal (60 days)', 'Renewed'],
        'Start': [
            current_date,
            current_date + timedelta(minutes=5),
            current_date + timedelta(hours=1),
            current_date + timedelta(hours=2),
            current_date + timedelta(days=305),  # 10 months later
            current_date + timedelta(days=365)   # 1 year later
        ],
        'End': [
            current_date + timedelta(minutes=5),
            current_date + timedelta(hours=1),
            current_date + timedelta(hours=2),
            current_date + timedelta(days=365),  # 1 year
            current_date + timedelta(days=365),  # Same as certificate expiry
            current_date + timedelta(days=730)   # 2 years total
        ],
        'Status': ['Pending', 'Validation', 'Success', 'Active', 'In Progress', 'Active'],
        'Action Required': ['None', 'DNS/Email', 'Deploy', 'Monitor', 'None', 'None']
    }
    
    df_lifecycle = pd.DataFrame(lifecycle_data)
    
    # Color-code the stages with proper start and end dates
    fig = px.timeline(df_lifecycle, x_start='Start', x_end='End', y='Stage', color='Status',
                      title="ACM Certificate Lifecycle")
    st.plotly_chart(fig, use_container_width=True)
    
    # Cost Analysis
    st.markdown("### 💰 ACM Cost Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Public Certificates")
        
        num_public_certs = st.slider("Number of Public Certificates:", 1, 100, 10)
        domains_per_cert = st.slider("Average Domains per Certificate:", 1, 25, 3)
        
        # Public certificates are free
        public_cert_cost = 0
        total_domains = num_public_certs * domains_per_cert
        
        col3, col4 = st.columns(2)
        with col3:
            st.metric("Certificate Cost", "$0.00", "Free!")
            st.metric("Total Domains", f"{total_domains}")
        with col4:
            st.metric("Annual Savings", f"${num_public_certs * 100:.2f}", 
                     help="Compared to commercial SSL certificates")
            st.metric("Renewal Cost", "$0.00", "Automatic & Free")
    
    with col2:
        st.markdown("### 📊 Private Certificates")
        
        num_private_cas = st.slider("Number of Private CAs:", 0, 10, 1)
        certs_per_ca = st.slider("Certificates per CA per month:", 0, 1000, 10)
        
        # Private CA pricing
        ca_cost = num_private_cas * 400  # $400/month per private CA
        cert_cost = num_private_cas * certs_per_ca * 0.75  # $0.75 per certificate
        total_private_cost = ca_cost + cert_cost
        
        col5, col6 = st.columns(2)
        with col5:
            st.metric("CA Monthly Cost", f"${ca_cost:.2f}")
            st.metric("Certificate Cost", f"${cert_cost:.2f}")
        with col6:
            st.metric("Total Monthly Cost", f"${total_private_cost:.2f}")
            st.metric("Annual Cost", f"${total_private_cost * 12:.2f}")
    
    # Best Practices
    st.markdown("### 💡 ACM Best Practices")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚠️ Security Best Practices
        
        **Certificate Management:**
        - Use **DNS validation** for automation
        - Implement **wildcard certificates** for subdomains
        - **Monitor certificate expiration** alerts
        - Use **separate certificates** for different environments
        
        **Domain Security:**
        - Validate **all domain ownership**
        - Use **CAA DNS records** for additional security
        - **Regular domain audits**
        - Monitor for **unauthorized certificates**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="security-box">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛡️ Operational Best Practices
        
        **Automation:**
        - **Infrastructure as Code** for certificate requests
        - **CloudFormation/Terraform** integration
        - Automated **deployment pipelines**
        - **CloudWatch monitoring** for certificate health
        
        **Organization:**
        - **Consistent naming** conventions
        - **Proper tagging** strategy
        - **Documentation** of certificate usage
        - **Regular access reviews**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: ACM Certificate Management")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Comprehensive AWS Certificate Manager implementation
import boto3
import json
import time
from botocore.exceptions import ClientError
from datetime import datetime, timedelta

class ACMCertificateManager:
    def __init__(self, region_name='us-east-1'):
        self.acm_client = boto3.client('acm', region_name=region_name)
        self.route53_client = boto3.client('route53')
        self.region = region_name
    
    def request_certificate(self, domain_name, subject_alternative_names=None, 
                          validation_method='DNS', certificate_authority_arn=None):
        """Request a new SSL/TLS certificate"""
        try:
            request_params = {
                'DomainName': domain_name,
                'ValidationMethod': validation_method,
                'Options': {
                    'CertificateTransparencyLoggingPreference': 'ENABLED'
                }
            }
            
            # Add additional domains if provided
            if subject_alternative_names:
                request_params['SubjectAlternativeNames'] = subject_alternative_names
            
            # For private certificates
            if certificate_authority_arn:
                request_params['CertificateAuthorityArn'] = certificate_authority_arn
            
            response = self.acm_client.request_certificate(**request_params)
            
            certificate_arn = response['CertificateArn']
            print(f"✅ Certificate requested successfully!")
            print(f"Certificate ARN: {certificate_arn}")
            print(f"Primary Domain: {domain_name}")
            print(f"Validation Method: {validation_method}")
            
            return certificate_arn
            
        except ClientError as e:
            print(f"❌ Error requesting certificate: {e}")
            return None
    
    def get_certificate_details(self, certificate_arn):
        """Get detailed information about a certificate"""
        try:
            response = self.acm_client.describe_certificate(
                CertificateArn=certificate_arn
            )
            
            certificate = response['Certificate']
            
            return {
                'arn': certificate['CertificateArn'],
                'domain_name': certificate['DomainName'],
                'subject_alternative_names': certificate.get('SubjectAlternativeNames', []),
                'status': certificate['Status'],
                'type': certificate['Type'],
                'key_algorithm': certificate['KeyAlgorithm'],
                'created_at': certificate.get('CreatedAt'),
                'issued_at': certificate.get('IssuedAt'),
                'not_before': certificate.get('NotBefore'),
                'not_after': certificate.get('NotAfter'),
                'domain_validation_options': certificate.get('DomainValidationOptions', []),
                'in_use_by': certificate.get('InUseBy', []),
                'renewal_eligibility': certificate.get('RenewalEligibility', 'INELIGIBLE')
            }
            
        except ClientError as e:
            print(f"❌ Error getting certificate details: {e}")
            return None
    
    def validate_certificate_dns(self, certificate_arn, hosted_zone_id=None):
        """Automatically validate certificate using DNS validation"""
        try:
            cert_details = self.get_certificate_details(certificate_arn)
            if not cert_details:
                return False
            
            if cert_details['status'] != 'PENDING_VALIDATION':
                print(f"Certificate is not pending validation: {cert_details['status']}")
                return True
            
            # Get DNS validation records
            validation_options = cert_details['domain_validation_options']
            
            for option in validation_options:
                domain = option['DomainName']
                resource_record = option.get('ResourceRecord')
                
                if not resource_record:
                    print(f"⚠️  DNS validation record not available for {domain}")
                    continue
                
                dns_name = resource_record['Name']
                dns_value = resource_record['Value']
                record_type = resource_record['Type']
                
                print(f"🌐 DNS Validation for {domain}:")
                print(f"   Record Type: {record_type}")
                print(f"   Name: {dns_name}")
                print(f"   Value: {dns_value}")
                
                # If hosted zone ID provided, automatically create DNS records
                if hosted_zone_id:
                    success = self.create_dns_validation_record(
                        hosted_zone_id, dns_name, dns_value, record_type
                    )
                    
                    if success:
                        print(f"✅ DNS record created for {domain}")
                    else:
                        print(f"❌ Failed to create DNS record for {domain}")
            
            # Wait for validation if DNS records were created
            if hosted_zone_id:
                print("⏳ Waiting for certificate validation...")
                return self.wait_for_certificate_validation(certificate_arn)
            
            return True
            
        except Exception as e:
            print(f"❌ Error in DNS validation: {e}")
            return False
    
    def create_dns_validation_record(self, hosted_zone_id, name, value, record_type):
        """Create DNS validation record in Route 53"""
        try:
            response = self.route53_client.change_resource_record_sets(
                HostedZoneId=hosted_zone_id,
                ChangeBatch={
                    'Changes': [
                        {
                            'Action': 'CREATE',
                            'ResourceRecordSet': {
                                'Name': name,
                                'Type': record_type,
                                'TTL': 300,
                                'ResourceRecords': [{'Value': value}]
                            }
                        }
                    ]
                }
            )
            
            change_id = response['ChangeInfo']['Id']
            print(f"DNS record change submitted: {change_id}")
            return True
            
        except ClientError as e:
            if 'RRSet already exists' in str(e):
                print("DNS record already exists")
                return True
            else:
                print(f"Error creating DNS record: {e}")
                return False
    
    def wait_for_certificate_validation(self, certificate_arn, max_wait_minutes=10):
        """Wait for certificate to be validated"""
        max_attempts = max_wait_minutes * 6  # Check every 10 seconds
        attempt = 0
        
        while attempt < max_attempts:
            cert_details = self.get_certificate_details(certificate_arn)
            
            if not cert_details:
                return False
            
            status = cert_details['status']
            
            if status == 'ISSUED':
                print(f"✅ Certificate validated and issued!")
                return True
            elif status in ['FAILED', 'EXPIRED', 'REVOKED']:
                print(f"❌ Certificate validation failed: {status}")
                return False
            
            attempt += 1
            if attempt % 6 == 0:  # Print status every minute
                print(f"⏳ Still waiting for validation... ({attempt // 6} min)")
            
            time.sleep(10)
        
        print(f"⏰ Certificate validation timeout after {max_wait_minutes} minutes")
        return False
    
    def list_certificates(self, certificate_statuses=None, includes=None):
        """List certificates with optional filtering"""
        try:
            params = {}
            
            if certificate_statuses:
                params['CertificateStatuses'] = certificate_statuses
            
            if includes:
                params['Includes'] = includes
            
            response = self.acm_client.list_certificates(**params)
            
            certificates = []
            for cert_summary in response['CertificateSummaryList']:
                cert_details = self.get_certificate_details(cert_summary['CertificateArn'])
                if cert_details:
                    certificates.append(cert_details)
            
            return certificates
            
        except ClientError as e:
            print(f"❌ Error listing certificates: {e}")
            return []
    
    def renew_certificate(self, certificate_arn):
        """Renew a certificate (ACM handles this automatically)"""
        try:
            cert_details = self.get_certificate_details(certificate_arn)
            
            if not cert_details:
                return False
            
            if cert_details['renewal_eligibility'] == 'ELIGIBLE':
                # ACM automatically renews eligible certificates
                print(f"✅ Certificate is eligible for automatic renewal")
                print(f"   ACM will automatically renew 60 days before expiration")
                return True
            else:
                print(f"⚠️  Certificate is not eligible for automatic renewal")
                print(f"   You may need to request a new certificate")
                return False
                
        except Exception as e:
            print(f"❌ Error checking renewal status: {e}")
            return False
    
    def export_certificate(self, certificate_arn, passphrase):
        """Export certificate for use outside of AWS"""
        try:
            response = self.acm_client.export_certificate(
                CertificateArn=certificate_arn,
                Passphrase=passphrase.encode('utf-8')
            )
            
            return {
                'certificate': response['Certificate'],
                'certificate_chain': response['CertificateChain'],
                'private_key': response['PrivateKey']
            }
            
        except ClientError as e:
            if 'InvalidParameterException' in str(e):
                print("❌ Certificate cannot be exported (likely using ACM private CA)")
            else:
                print(f"❌ Error exporting certificate: {e}")
            return None
    
    def monitor_certificate_expiration(self, days_before_expiry=60):
        """Monitor certificates for upcoming expiration"""
        certificates = self.list_certificates(['ISSUED'])
        
        expiring_soon = []
        now = datetime.now()
        
        for cert in certificates:
            if cert['not_after']:
                expiry_date = cert['not_after'].replace(tzinfo=None)
                days_until_expiry = (expiry_date - now).days
                
                if days_until_expiry <= days_before_expiry:
                    expiring_soon.append({
                        'domain': cert['domain_name'],
                        'arn': cert['arn'],
                        'expiry_date': expiry_date,
                        'days_until_expiry': days_until_expiry,
                        'renewal_eligible': cert['renewal_eligibility'] == 'ELIGIBLE'
                    })
        
        return expiring_soon
    
    def generate_certificate_report(self):
        """Generate comprehensive certificate report"""
        all_certificates = self.list_certificates()
        
        report = {
            'total_certificates': len(all_certificates),
            'by_status': {},
            'by_type': {},
            'expiring_soon': [],
            'in_use': 0,
            'unused': 0
        }
        
        for cert in all_certificates:
            # Count by status
            status = cert['status']
            report['by_status'][status] = report['by_status'].get(status, 0) + 1
            
            # Count by type
            cert_type = cert['type']
            report['by_type'][cert_type] = report['by_type'].get(cert_type, 0) + 1
            
            # Count usage
            if cert['in_use_by']:
                report['in_use'] += 1
            else:
                report['unused'] += 1
            
            # Check expiration
            if cert['not_after']:
                expiry_date = cert['not_after'].replace(tzinfo=None)
                days_until_expiry = (expiry_date - datetime.now()).days
                
                if days_until_expiry <= 60:
                    report['expiring_soon'].append({
                        'domain': cert['domain_name'],
                        'days': days_until_expiry
                    })
        
        return report

# Example usage and automated certificate management
if __name__ == "__main__":
    # Initialize ACM manager
    acm = ACMCertificateManager(region_name='us-east-1')
    
    # Request a certificate with DNS validation
    certificate_arn = acm.request_certificate(
        domain_name='example.com',
        subject_alternative_names=['www.example.com', '*.api.example.com'],
        validation_method='DNS'
    )
    
    if certificate_arn:
        print(f"\\n🔍 Certificate Details:")
        cert_details = acm.get_certificate_details(certificate_arn)
        
        if cert_details:
            print(f"Status: {cert_details['status']}")
            print(f"Domains: {cert_details['domain_name']}")
            print(f"Additional Names: {cert_details['subject_alternative_names']}")
            
            # Validate certificate (you would provide your Route 53 hosted zone ID)
            # acm.validate_certificate_dns(certificate_arn, 'Z1234567890ABC')
    
    # Generate certificate report
    print(f"\\n📊 Certificate Report:")
    report = acm.generate_certificate_report()
    print(f"Total Certificates: {report['total_certificates']}")
    print(f"In Use: {report['in_use']}")
    print(f"Unused: {report['unused']}")
    print(f"Expiring Soon: {len(report['expiring_soon'])}")
    
    for status, count in report['by_status'].items():
        print(f"  {status}: {count}")
    
    # Monitor expiring certificates
    expiring = acm.monitor_certificate_expiration(90)  # 90 days
    if expiring:
        print(f"\\n⚠️  Certificates expiring within 90 days:")
        for cert in expiring:
            print(f"  {cert['domain']}: {cert['days_until_expiry']} days")
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def s3_security_tab():
    """Content for Amazon S3 Security tab"""
    st.markdown("## 🗂️ Amazon S3 - Presigned URLs, CORS, & OAI")
    st.markdown("*Advanced S3 security features for secure and controlled access*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    Amazon S3 provides multiple security mechanisms including **Presigned URLs** for temporary access, **CORS** for cross-origin requests, 
    and **Origin Access Identity (OAI)** for CloudFront integration. These features enable secure, flexible access patterns while maintaining 
    strict security controls.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # S3 Security Architecture
    st.markdown("### 🏗️ S3 Security Architecture")
    common.mermaid(create_s3_security_mermaid(), height=850)
    
    # Security Features Overview
    st.markdown("### 🔐 S3 Security Features Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🔗\n**Presigned**\nURLs")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        **Use Cases:**
        - Temporary file access
        - Direct uploads from browsers
        - **Time-limited sharing**
        - Mobile app integrations
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🌐\n**CORS**\nConfiguration")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        **Use Cases:**
        - Web applications
        - **Cross-domain requests**
        - AJAX file uploads
        - Single-page applications
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🔐\n**Origin Access**\nIdentity")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        **Use Cases:**
        - CloudFront distributions
        - **Restricted bucket access**
        - CDN-only content delivery
        - Private content distribution
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Presigned URL Generator
    st.markdown("### 🔗 Interactive Presigned URL Generator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚙️ URL Configuration")
        
        bucket_name = st.text_input("S3 Bucket Name:", "my-secure-bucket")
        object_key = st.text_input("Object Key:", "documents/secure-file.pdf")
        
        operation = st.selectbox("Operation:", [
            "GetObject (Download)",
            "PutObject (Upload)", 
            "DeleteObject (Delete)",
            "GetObjectVersion (Version-specific)"
        ])
        
        expiration_time = st.selectbox("Expiration Time:", [
            "15 minutes", "1 hour", "4 hours", "12 hours", "1 day", "7 days", "Custom"
        ])
        
        if expiration_time == "Custom":
            custom_hours = st.number_input("Custom Hours:", 1, 168, 24)
    
    with col2:
        st.markdown("### 🔒 Security Options")
        
        content_type = st.text_input("Content-Type (for uploads):", "application/pdf")
        
        additional_conditions = st.multiselect("Additional Conditions:", [
            "Require SSL/TLS",
            "Limit file size",
            "Restrict IP address",
            "Require specific headers"
        ])
        
        if "Limit file size" in additional_conditions:
            max_file_size = st.slider("Max File Size (MB):", 1, 1000, 100)
        
        if "Restrict IP address" in additional_conditions:
            allowed_ip = st.text_input("Allowed IP Address:", "192.168.1.0/24")
    
    if st.button("🔗 Generate Presigned URL", use_container_width=True):
        # Generate simulated presigned URL
        import urllib.parse
        
        # Convert expiration to hours
        if expiration_time == "Custom":
            exp_hours = custom_hours
        else:
            exp_map = {"15 minutes": 0.25, "1 hour": 1, "4 hours": 4, 
                      "12 hours": 12, "1 day": 24, "7 days": 168}
            exp_hours = exp_map[expiration_time]
        
        # Generate mock presigned URL
        exp_timestamp = int((datetime.now() + timedelta(hours=exp_hours)).timestamp())
        
        base_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"
        signature = f"mock-signature-{np.random.randint(100000, 999999)}"
        
        presigned_url = f"{base_url}?AWSAccessKeyId=AKIAEXAMPLE&Expires={exp_timestamp}&Signature={signature}"
        
        st.markdown('<div class="security-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ Presigned URL Generated!
        
        **URL Details:**
        - **Bucket**: {bucket_name}
        - **Object**: {object_key}
        - **Operation**: {operation.split(' ')[0]}
        - **Expires**: {expiration_time} ({exp_hours} hours)
        - **Security**: {'Enhanced' if additional_conditions else 'Standard'}
        
        **Generated URL:**
        ```
        {presigned_url}
        ```
        
        ⚠️ **Security Note**: This URL provides temporary access without AWS credentials
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # CORS Configuration Tool
    st.markdown("### 🌐 CORS Configuration Tool")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔧 CORS Rule Configuration")
        
        allowed_origins = st.text_area("Allowed Origins (one per line):", 
                                     "https://mywebsite.com\nhttps://app.mywebsite.com\nhttp://localhost:3000")
        
        allowed_methods = st.multiselect("Allowed Methods:", [
            "GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"
        ], default=["GET", "POST"])
        
        allowed_headers = st.text_area("Allowed Headers:", "Content-Type\nAuthorization\nx-amz-*")
        
        expose_headers = st.text_area("Expose Headers (optional):", "ETag\nx-amz-request-id")
        
        max_age = st.number_input("Max Age (seconds):", 0, 86400, 3600)
    
    with col2:
        st.markdown("### 📝 Generated CORS Configuration")
        
        # Generate CORS configuration
        origins_list = [origin.strip() for origin in allowed_origins.split('\n') if origin.strip()]
        headers_list = [header.strip() for header in allowed_headers.split('\n') if header.strip()]
        expose_list = [header.strip() for header in expose_headers.split('\n') if header.strip()]
        
        cors_config = {
            "CORSRules": [
                {
                    "AllowedOrigins": origins_list,
                    "AllowedMethods": allowed_methods,
                    "AllowedHeaders": headers_list,
                    "ExposeHeaders": expose_list,
                    "MaxAgeSeconds": max_age
                }
            ]
        }
        
        st.code(json.dumps(cors_config, indent=2), language='json')
    
    # Origin Access Identity Configuration
    st.markdown("### 🔐 Origin Access Identity (OAI) Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 What is OAI?
        
        **Origin Access Identity** is a special CloudFront user that you can associate with your distribution 
        to secure your S3 content.
        
        **How it works:**
        1. Create OAI in CloudFront
        2. Associate with distribution
        3. Update S3 bucket policy
        4. **Block direct S3 access**
        
        **Benefits:**
        - Content only accessible via CloudFront
        - **Prevent direct S3 URLs**
        - Centralized access control
        - **Better security** and logging
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🛠️ OAI Setup Simulator")
        
        cloudfront_dist_id = st.text_input("CloudFront Distribution ID:", "E1234567890ABC")
        s3_bucket_for_oai = st.text_input("S3 Bucket Name:", "my-content-bucket")
        oai_comment = st.text_input("OAI Comment:", "OAI for my website content")
        
        block_public_access = st.checkbox("Block Public Access to S3", value=True)
        
        if st.button("🔐 Configure OAI", use_container_width=True):
            oai_id = f"E{np.random.randint(100000000000, 999999999999)}"
            
            # Generate bucket policy for OAI
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": f"arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity {oai_id}"
                        },
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{s3_bucket_for_oai}/*"
                    }
                ]
            }
            
            if block_public_access:
                bucket_policy["Statement"].append({
                    "Effect": "Deny",
                    "Principal": "*",
                    "Action": "s3:*",
                    "Resource": [
                        f"arn:aws:s3:::{s3_bucket_for_oai}",
                        f"arn:aws:s3:::{s3_bucket_for_oai}/*"
                    ],
                    "Condition": {
                        "StringNotEquals": {
                            "AWS:SourceAccount": "123456789012"
                        }
                    }
                })
            
            
            st.markdown('<div class="security-box">', unsafe_allow_html=True)
            st.markdown(f"""
            ### ✅ OAI Configuration Complete!
            
            **OAI Details:**
            - **OAI ID**: {oai_id}
            - **Distribution**: {cloudfront_dist_id}
            - **Bucket**: {s3_bucket_for_oai}
            - **Public Access**: {'Blocked' if block_public_access else 'Allowed'}
            
            **Required Bucket Policy:**
            ```json
            {bucket_policy}
            ```
            """)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Security Features Comparison
    st.markdown("### 🔍 S3 Security Features Comparison")
    
    security_comparison = {
        'Feature': ['Presigned URLs', 'CORS', 'OAI', 'Bucket Policies', 'IAM Policies'],
        'Access Control': ['Temporary', 'Browser-based', 'CloudFront-only', 'Resource-level', 'Identity-based'],
        'Use Case': [
            'File sharing, uploads',
            'Web app integration',
            'CDN content delivery',
            'Resource permissions',
            'User/role permissions'
        ],
        'Duration': ['Time-limited', 'Permanent', 'Permanent', 'Permanent', 'Permanent'],
        'Complexity': ['Low', 'Medium', 'Medium', 'High', 'High'],
        'Security Level': ['High', 'Medium', 'Very High', 'Very High', 'Very High']
    }
    
    df_security = pd.DataFrame(security_comparison)
    st.dataframe(df_security, use_container_width=True)
    
    # Best Practices
    st.markdown("### 💡 S3 Security Best Practices")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚠️ Security Best Practices
        
        **Presigned URLs:**
        - Use **shortest possible expiration** times
        - Implement **additional conditions** when possible
        - **Monitor usage** patterns for abuse
        - **Validate content types** for uploads
        - **Log all presigned URL** generation
        
        **CORS Configuration:**
        - **Specify exact origins**, avoid wildcards
        - **Minimum required methods** only
        - Regular **CORS policy audits**
        - **Test cross-origin** functionality thoroughly
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="security-box">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛡️ Advanced Security
        
        **Origin Access Identity:**
        - **Always use OAI** with CloudFront
        - **Block direct S3 access** when using CDN
        - **Regular OAI rotation** for high-security apps
        - **Monitor CloudFront logs** for access patterns
        
        **General S3 Security:**
        - Enable **S3 bucket logging**
        - Use **S3 Object Lock** for compliance
        - Implement **MFA delete** for critical buckets
        - **Encrypt sensitive data** at rest and in transit
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: S3 Security Implementation")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Comprehensive S3 security implementation with Presigned URLs, CORS, and OAI
import boto3
import json
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
import logging

class S3SecurityManager:
    def __init__(self, region_name='us-east-1'):
        self.s3_client = boto3.client('s3', region_name=region_name)
        self.cloudfront_client = boto3.client('cloudfront', region_name=region_name)
        self.logger = logging.getLogger(__name__)
    
    def generate_presigned_url(self, bucket_name, object_key, operation='get_object', 
                             expiration_hours=1, conditions=None):
        """Generate presigned URL with security conditions"""
        try:
            # Calculate expiration time
            expiration_seconds = expiration_hours * 3600
            
            # Base parameters for presigned URL
            params = {
                'Bucket': bucket_name,
                'Key': object_key
            }
            
            # Add conditions for enhanced security
            presigned_params = {
                'Params': params,
                'ExpiresIn': expiration_seconds
            }
            
            # Add security conditions
            if conditions:
                presigned_params['Conditions'] = conditions
            
            # Generate URL based on operation
            if operation == 'get_object':
                url = self.s3_client.generate_presigned_url(
                    'get_object', **presigned_params
                )
            elif operation == 'put_object':
                # Add content type condition for uploads
                if 'ContentType' not in params:
                    params['ContentType'] = 'application/octet-stream'
                url = self.s3_client.generate_presigned_url(
                    'put_object', **presigned_params
                )
            else:
                raise ValueError(f"Unsupported operation: {operation}")
            
            # Log URL generation for security monitoring
            self.logger.info(f"Presigned URL generated: {bucket_name}/{object_key}, "
                           f"operation: {operation}, expires in {expiration_hours}h")
            
            return {
                'url': url,
                'expires_at': datetime.now() + timedelta(hours=expiration_hours),
                'operation': operation,
                'bucket': bucket_name,
                'key': object_key
            }
            
        except ClientError as e:
            self.logger.error(f"Error generating presigned URL: {e}")
            return None
    
    def create_secure_upload_url(self, bucket_name, object_key, max_file_size_mb=10, 
                                allowed_content_types=None, expiration_hours=1):
        """Create secure presigned URL for file uploads with restrictions"""
        try:
            conditions = []
            
            # File size restriction
            if max_file_size_mb:
                max_size_bytes = max_file_size_mb * 1024 * 1024
                conditions.append(['content-length-range', 0, max_size_bytes])
            
            # Content type restriction
            if allowed_content_types:
                if len(allowed_content_types) == 1:
                    conditions.append(['eq', '$Content-Type', allowed_content_types[0]])
                else:
                    conditions.append(['starts-with', '$Content-Type', ''])
            
            # Require SSL
            conditions.append(['eq', '$x-amz-server-side-encryption', 'AES256'])
            
            # Generate presigned POST URL (more secure for uploads)
            response = self.s3_client.generate_presigned_post(
                Bucket=bucket_name,
                Key=object_key,
                Fields={
                    'x-amz-server-side-encryption': 'AES256'
                },
                Conditions=conditions,
                ExpiresIn=expiration_hours * 3600
            )
            
            self.logger.info(f"Secure upload URL generated: {bucket_name}/{object_key}")
            
            return {
                'url': response['url'],
                'fields': response['fields'],
                'expires_at': datetime.now() + timedelta(hours=expiration_hours),
                'max_file_size_mb': max_file_size_mb,
                'allowed_content_types': allowed_content_types
            }
            
        except ClientError as e:
            self.logger.error(f"Error generating secure upload URL: {e}")
            return None
    
    def configure_cors(self, bucket_name, cors_rules):
        """Configure CORS for S3 bucket"""
        try:
            cors_configuration = {
                'CORSRules': cors_rules
            }
            
            self.s3_client.put_bucket_cors(
                Bucket=bucket_name,
                CORSConfiguration=cors_configuration
            )
            
            self.logger.info(f"CORS configured for bucket: {bucket_name}")
            return True
            
        except ClientError as e:
            self.logger.error(f"Error configuring CORS: {e}")
            return False
    
    def create_web_app_cors_config(self, allowed_origins, development_mode=False):
        """Create CORS configuration optimized for web applications"""
        cors_rules = []
        
        # Production CORS rule
        production_rule = {
            'AllowedOrigins': allowed_origins,
            'AllowedMethods': ['GET', 'POST', 'PUT', 'DELETE', 'HEAD'],
            'AllowedHeaders': [
                'Content-Type',
                'Authorization',
                'x-amz-date',
                'x-amz-content-sha256',
                'x-amz-security-token'
            ],
            'ExposeHeaders': [
                'ETag',
                'x-amz-request-id'
            ],
            'MaxAgeSeconds': 3600
        }
        cors_rules.append(production_rule)
        
        # Development rule (if enabled)
        if development_mode:
            dev_rule = {
                'AllowedOrigins': ['http://localhost:*', 'http://127.0.0.1:*'],
                'AllowedMethods': ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'],
                'AllowedHeaders': ['*'],
                'ExposeHeaders': ['*'],
                'MaxAgeSeconds': 300  # Shorter cache for development
            }
            cors_rules.append(dev_rule)
        
        return cors_rules
    
    def create_origin_access_identity(self, comment):
        """Create CloudFront Origin Access Identity"""
        try:
            response = self.cloudfront_client.create_origin_access_identity(
                OriginAccessIdentityConfig={
                    'CallerReference': str(datetime.now().timestamp()),
                    'Comment': comment
                }
            )
            
            oai = response['OriginAccessIdentity']
            oai_id = oai['Id']
            canonical_user_id = oai['S3CanonicalUserId']
            
            self.logger.info(f"Origin Access Identity created: {oai_id}")
            
            return {
                'id': oai_id,
                'canonical_user_id': canonical_user_id,
                'domain_name': f"origin-access-identity.cloudfront.amazonaws.com/{oai_id}",
                'arn': f"arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity {oai_id}"
            }
            
        except ClientError as e:
            self.logger.error(f"Error creating OAI: {e}")
            return None
    
    def create_oai_bucket_policy(self, bucket_name, oai_arn, block_public_access=True):
        """Create S3 bucket policy for Origin Access Identity"""
        policy_statements = [
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": oai_arn
                },
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }
        ]
        
        # Block direct public access if requested
        if block_public_access:
            policy_statements.append({
                "Effect": "Deny",
                "Principal": "*",
                "Action": "s3:*",
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*"
                ],
                "Condition": {
                    "StringNotEquals": {
                        "aws:PrincipalServiceName": "cloudfront.amazonaws.com"
                    }
                }
            })
        
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": policy_statements
        }
        
        try:
            self.s3_client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(bucket_policy)
            )
            
            self.logger.info(f"OAI bucket policy applied to: {bucket_name}")
            return bucket_policy
            
        except ClientError as e:
            self.logger.error(f"Error applying bucket policy: {e}")
            return None
    
    def setup_cloudfront_s3_integration(self, bucket_name, distribution_comment):
        """Complete setup of S3 bucket with CloudFront integration"""
        try:
            # Create Origin Access Identity
            oai = self.create_origin_access_identity(
                f"OAI for {bucket_name} - {distribution_comment}"
            )
            
            if not oai:
                return None
            
            # Create bucket policy for OAI
            bucket_policy = self.create_oai_bucket_policy(
                bucket_name, oai['arn'], block_public_access=True
            )
            
            if not bucket_policy:
                return None
            
            # Block public access settings
            self.s3_client.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': False,  # Allow OAI policy
                    'RestrictPublicBuckets': False
                }
            )
            
            self.logger.info(f"CloudFront-S3 integration configured for: {bucket_name}")
            
            return {
                'bucket_name': bucket_name,
                'oai': oai,
                'bucket_policy': bucket_policy,
                'origin_domain_name': f"{bucket_name}.s3.amazonaws.com",
                'status': 'configured'
            }
            
        except Exception as e:
            self.logger.error(f"Error setting up CloudFront-S3 integration: {e}")
            return None
    
    def monitor_presigned_url_usage(self, bucket_name, hours_back=24):
        """Monitor presigned URL usage through CloudTrail logs"""
        cloudtrail = boto3.client('cloudtrail')
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours_back)
        
        try:
            # Look for presigned URL related events
            response = cloudtrail.lookup_events(
                LookupAttributes=[
                    {
                        'AttributeKey': 'ResourceName',
                        'AttributeValue': bucket_name
                    }
                ],
                StartTime=start_time,
                EndTime=end_time
            )
            
            presigned_events = []
            for event in response['Events']:
                if 'presigned' in event.get('EventName', '').lower():
                    presigned_events.append({
                        'timestamp': event['EventTime'],
                        'event_name': event['EventName'],
                        'user_identity': event.get('Username', 'Unknown'),
                        'source_ip': event.get('SourceIPAddress', 'Unknown'),
                        'resources': event.get('Resources', [])
                    })
            
            return {
                'total_events': len(presigned_events),
                'events': presigned_events,
                'monitoring_period_hours': hours_back
            }
            
        except Exception as e:
            self.logger.error(f"Error monitoring presigned URL usage: {e}")
            return None
    
    def validate_security_configuration(self, bucket_name):
        """Validate S3 bucket security configuration"""
        try:
            security_report = {
                'bucket_name': bucket_name,
                'timestamp': datetime.now(),
                'issues': [],
                'recommendations': [],
                'security_score': 0
            }
            
            # Check public access block
            try:
                response = self.s3_client.get_public_access_block(Bucket=bucket_name)
                pab = response['PublicAccessBlockConfiguration']
                
                if not all([pab['BlockPublicAcls'], pab['IgnorePublicAcls'], 
                           pab['BlockPublicPolicy'], pab['RestrictPublicBuckets']]):
                    security_report['issues'].append("Public access not fully blocked")
                else:
                    security_report['security_score'] += 25
                    
            except ClientError:
                security_report['issues'].append("Public access block not configured")
            
            # Check bucket encryption
            try:
                self.s3_client.get_bucket_encryption(Bucket=bucket_name)
                security_report['security_score'] += 25
            except ClientError:
                security_report['issues'].append("Bucket encryption not enabled")
                security_report['recommendations'].append("Enable default encryption")
            
            # Check bucket policy
            try:
                response = self.s3_client.get_bucket_policy(Bucket=bucket_name)
                policy = json.loads(response['Policy'])
                security_report['security_score'] += 25
                
                # Check for overly permissive policies
                for statement in policy.get('Statement', []):
                    if statement.get('Principal') == '*' and statement.get('Effect') == 'Allow':
                        security_report['issues'].append("Overly permissive bucket policy found")
                        
            except ClientError:
                security_report['recommendations'].append("Consider adding bucket policy for access control")
            
            # Check CORS configuration
            try:
                response = self.s3_client.get_bucket_cors(Bucket=bucket_name)
                cors_rules = response['CORSRules']
                security_report['security_score'] += 25
                
                # Check for overly permissive CORS
                for rule in cors_rules:
                    if '*' in rule.get('AllowedOrigins', []):
                        security_report['issues'].append("Overly permissive CORS configuration")
                        
            except ClientError:
                pass  # CORS not configured (might be intentional)
            
            # Generate overall security assessment
            if security_report['security_score'] >= 75:
                security_report['overall_status'] = 'Good'
            elif security_report['security_score'] >= 50:
                security_report['overall_status'] = 'Fair'
            else:
                security_report['overall_status'] = 'Needs Improvement'
            
            return security_report
            
        except Exception as e:
            self.logger.error(f"Error validating security configuration: {e}")
            return None

# Example usage and comprehensive S3 security setup
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize S3 security manager
    s3_security = S3SecurityManager()
    
    bucket_name = 'my-secure-content-bucket'
    
    # 1. Setup CloudFront integration with OAI
    print("🔐 Setting up CloudFront-S3 integration...")
    integration = s3_security.setup_cloudfront_s3_integration(
        bucket_name, 
        "My Website Content Distribution"
    )
    
    if integration:
        print(f"✅ Integration successful!")
        print(f"OAI ID: {integration['oai']['id']}")
        print(f"Origin Domain: {integration['origin_domain_name']}")
    
    # 2. Configure CORS for web applications
    print("\\n🌐 Configuring CORS...")
    cors_rules = s3_security.create_web_app_cors_config(
        allowed_origins=['https://mywebsite.com', 'https://app.mywebsite.com'],
        development_mode=True
    )
    
    success = s3_security.configure_cors(bucket_name, cors_rules)
    if success:
        print("✅ CORS configured successfully")
    
    # 3. Generate secure presigned URLs
    print("\\n🔗 Generating presigned URLs...")
    
    # Download URL
    download_url = s3_security.generate_presigned_url(
        bucket_name, 
        'documents/report.pdf',
        operation='get_object',
        expiration_hours=1
    )
    
    if download_url:
        print(f"Download URL: {download_url['url'][:100]}...")
        print(f"Expires: {download_url['expires_at']}")
    
    # Secure upload URL
    upload_url = s3_security.create_secure_upload_url(
        bucket_name,
        'uploads/user-document.pdf',
        max_file_size_mb=5,
        allowed_content_types=['application/pdf'],
        expiration_hours=0.5
    )
    
    if upload_url:
        print(f"Upload URL: {upload_url['url'][:100]}...")
        print(f"Max file size: {upload_url['max_file_size_mb']} MB")
    
    # 4. Validate security configuration  
    print("\\n🛡️ Validating security configuration...")
    security_report = s3_security.validate_security_configuration(bucket_name)
    
    if security_report:
        print(f"Security Score: {security_report['security_score']}/100")
        print(f"Overall Status: {security_report['overall_status']}")
        
        if security_report['issues']:
            print("Issues found:")
            for issue in security_report['issues']:
                print(f"  - {issue}")
        
        if security_report['recommendations']:
            print("Recommendations:")
            for rec in security_report['recommendations']:
                print(f"  - {rec}")
    
    print("\\n🎉 S3 security configuration complete!")
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application function"""
    # Apply styling
    apply_custom_styles()
    
    # Initialize session
    common.initialize_session_state()
    common.initialize_mermaid()
    
    # Create sidebar
    create_sidebar()
    
    # Main header
    st.markdown("""
    # 🔐 AWS Security & Identity Hub
    
    """)
    st.markdown("""<div class="info-box">
                Master AWS security and identity services to build secure, compliant applications with proper access controls, 
                encryption, and monitoring. Learn to implement defense-in-depth security strategies using AWS managed services.
                </div>""", unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🛡️ AWS WAF", 
        "🔐 Secrets Manager", 
        "🔑 AWS KMS",
        "🔗 AWS PrivateLink",
        "📜 Certificate Manager",
        "🗂️ S3 Security"
    ])
    
    with tab1:
        aws_waf_tab()
    
    with tab2:
        secrets_manager_tab()
    
    with tab3:
        kms_tab()
    
    with tab4:
        privatelink_tab()
        
    with tab5:
        certificate_manager_tab()
        
    with tab6:
        s3_security_tab()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>© 2025, Amazon Web Services, Inc. or its affiliates. All rights reserved.</p>
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
