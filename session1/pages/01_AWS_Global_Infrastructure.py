
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import utils.common as common
import utils.authenticate as authenticate

# Page configuration
st.set_page_config(
    page_title="AWS Global Infrastructure Hub",
    page_icon="🌍",
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
    'warning': '#FF6B35'
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
        
        .region-selector {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            border: 2px solid {AWS_COLORS['light_blue']};
            margin: 15px 0;
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
            - 🌍 AWS Regions - Global data center locations
            - 🏢 Availability Zones - Isolated data centers
            - 📍 Points of Presence - Edge locations worldwide
            - ⚡ Amazon CloudFront - Content delivery network
            - 🏪 Regional Edge Caches - Improved content caching
            
            **Learning Objectives:**
            - Understand AWS global infrastructure
            - Learn about high availability and disaster recovery
            - Explore content delivery optimization
            - Practice with interactive examples and visualizations
            """)

def create_region_architecture_mermaid():
    """Create mermaid diagram for AWS region architecture"""
    return """
    graph TB
        subgraph "AWS Region (us-east-1)"
            AZ1[Availability Zone 1a]
            AZ2[Availability Zone 1b]
            AZ3[Availability Zone 1c]
            
            subgraph AZ1
                DC1[Data Center 1]
                DC2[Data Center 2]
            end
            
            subgraph AZ2
                DC3[Data Center 3]
                DC4[Data Center 4]
            end
            
            subgraph AZ3
                DC5[Data Center 5]
                DC6[Data Center 6]
            end
        end
        
        AZ1 <--> AZ2
        AZ2 <--> AZ3
        AZ1 <--> AZ3
        
        style AZ1 fill:#FF9900,stroke:#232F3E,color:#fff
        style AZ2 fill:#FF9900,stroke:#232F3E,color:#fff
        style AZ3 fill:#FF9900,stroke:#232F3E,color:#fff
        style DC1 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style DC2 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style DC3 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style DC4 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style DC5 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style DC6 fill:#4B9EDB,stroke:#232F3E,color:#fff
    """

def create_global_infrastructure_mermaid():
    """Create mermaid diagram for global infrastructure"""
    return """
    graph TD
        A[AWS Global Infrastructure] --> B[34+ Regions]
        A --> C[108+ Availability Zones]
        A --> D[600+ Points of Presence]
        
        B --> E[US East N. Virginia]
        B --> F[US West Oregon]
        B --> G[EU Ireland]
        B --> H[Asia Pacific Singapore]
        
        C --> I[Multiple AZs per Region]
        C --> J[Isolated & Physically Separate]
        C --> K[High-bandwidth Low-latency]
        
        D --> L[Edge Locations]
        D --> M[Regional Edge Caches]
        D --> N[CloudFront Distribution]
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style B fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_cloudfront_architecture_mermaid():
    """Create mermaid diagram for CloudFront architecture"""
    return """
    graph LR
        A[👤 User Request] --> B[🌐 Route 53 DNS]
        B --> C[📍 Nearest Edge Location]
        C --> D{Content in Cache?}
        
        D -->|Yes| E[⚡ Serve from Cache]
        D -->|No| F[🏪 Regional Edge Cache]
        
        F --> G{Content in Regional Cache?}
        G -->|Yes| H[📦 Serve from Regional Cache]
        G -->|No| I[🗂️ Origin Server S3/ALB]
        
        I --> J[📤 Content to Regional Cache]
        J --> K[📤 Content to Edge Location]
        K --> L[📤 Content to User]
        
        H --> K
        E --> M[📱 User Receives Content]
        L --> M
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#FF9900,stroke:#232F3E,color:#fff
        style F fill:#3FB34F,stroke:#232F3E,color:#fff
        style I fill:#232F3E,stroke:#FF9900,color:#fff
        style M fill:#4B9EDB,stroke:#232F3E,color:#fff
    """

def create_regional_edge_cache_mermaid():
    """Create diagram for regional edge cache workflow"""
    return """
    graph TD
        A[User Request] --> B[Edge Location]
        B --> C{Content Cached?}
        C -->|Hit| D[Serve from Edge]
        C -->|Miss| E[Regional Edge Cache]
        
        E --> F{Content in Regional Cache?}
        F -->|Hit| G[Serve from Regional Cache]
        F -->|Miss| H[Origin Server]
        
        H --> I[Store in Regional Cache]
        I --> J[Store in Edge Location]
        J --> K[Serve to User]
        
        G --> J
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style B fill:#FF9900,stroke:#232F3E,color:#fff
        style E fill:#3FB34F,stroke:#232F3E,color:#fff
        style H fill:#232F3E,stroke:#FF9900,color:#fff
    """

def aws_regions_tab():
    """Content for AWS Regions tab"""
    st.markdown("## 🌍 AWS Regions")
    st.markdown("*Physical locations around the world where AWS clusters data centers*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    An **AWS Region** is a physical location around the world where AWS clusters data centers. 
    Each region consists of multiple, isolated, and physically separate Availability Zones within a geographic area.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Region Map
    st.markdown("### 🗺️ Global Region Distribution")
    regions_data_x = {
    'Region': [
        'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
        'ca-central-1', 'ca-west-1',
        'eu-north-1', 'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-central-1', 'eu-central-2', 'eu-south-1', 'eu-south-2',
        'ap-northeast-1', 'ap-northeast-2', 'ap-northeast-3', 'ap-southeast-1', 'ap-southeast-2', 'ap-southeast-3', 'ap-southeast-4', 'ap-south-1', 'ap-south-2', 'ap-east-1',
        'sa-east-1',
        'af-south-1',
        'me-south-1', 'me-central-1',
        'il-central-1'
    ],
    'Location': [
        'N. Virginia', 'Ohio', 'N. California', 'Oregon',
        'Central Canada', 'Calgary',
        'Stockholm', 'Ireland', 'London', 'Paris', 'Frankfurt', 'Zurich', 'Milan', 'Spain',
        'Tokyo', 'Seoul', 'Osaka', 'Singapore', 'Sydney', 'Jakarta', 'Melbourne', 'Mumbai', 'Hyderabad', 'Hong Kong',
        'São Paulo',
        'Cape Town',
        'Bahrain', 'UAE',
        'Tel Aviv'
    ],
    'Lat': [
        38.9, 39.9, 37.4, 45.5,
        43.7, 51.0,
        59.3, 53.3, 51.5, 48.9, 50.1, 47.4, 45.5, 40.4,
        35.7, 37.6, 34.7, 1.3, -33.9, -6.2, -37.8, 19.1, 17.4, 22.3,
        -23.5,
        -33.9,
        26.2, 24.5,
        32.1
    ],
    'Lon': [
        -77.0, -82.9, -122.1, -121.3,
        -79.4, -114.1,
        18.1, -6.2, -0.1, 2.3, 8.7, 8.5, 9.2, -3.7,
        139.7, 126.9, 135.5, 103.8, 151.2, 106.8, 144.9, 72.9, 78.5, 114.2,
        -46.6,
        18.4,
        50.6, 54.4,
        34.8
    ],
    'AZ_Count': [
        6, 3, 3, 4,
        3, 3,
        3, 3, 3, 3, 3, 3, 3, 3,
        4, 4, 3, 3, 3, 3, 3, 3, 3, 3,
        3,
        3,
        3, 3,
        3
    ]
}

    
    df_regions = pd.DataFrame(regions_data_x)
    
    fig = px.scatter_mapbox(df_regions, lat="Lat", lon="Lon", hover_name="Region",
                           hover_data=["Location", "AZ_Count"], size="AZ_Count",
                           color_discrete_sequence=[AWS_COLORS['primary']],
                           zoom=1, height=400)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)
    
    
    
    
    # Region statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 34+\n**AWS Regions**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 108+\n**Availability Zones**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 245+\n**Countries & Territories**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 99.99%\n**SLA Availability**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Region Selector
    st.markdown("### 🗺️ Interactive Region Explorer")
    
    # Sample region data
    regions_data = {
        'Region Name': ['US East (N. Virginia)', 'US West (Oregon)', 'EU (Ireland)', 
                       'Asia Pacific (Singapore)', 'Asia Pacific (Tokyo)', 'South America (São Paulo)'],
        'Region Code': ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1', 'ap-northeast-1', 'sa-east-1'],
        'Availability Zones': [6, 4, 3, 3, 4, 3],
        'Launch Year': [2006, 2011, 2007, 2010, 2011, 2011],
        'Services Available': ['200+', '190+', '200+', '180+', '190+', '150+']
    }
    
    df_regions = pd.DataFrame(regions_data)
    
    selected_region = st.selectbox("Select a Region to Explore:", df_regions['Region Name'])
    
    if selected_region:
        region_info = df_regions[df_regions['Region Name'] == selected_region].iloc[0]
        
        st.markdown('<div class="region-selector">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            **Region Details:**
            - **Name**: {region_info['Region Name']}
            - **Code**: `{region_info['Region Code']}`
            - **Availability Zones**: {region_info['Availability Zones']}
            - **Launch Year**: {region_info['Launch Year']}
            - **Services Available**: {region_info['Services Available']}
            """)
        
        with col2:
            if st.button(f"🚀 Deploy to {region_info['Region Code']}", use_container_width=True):
                st.success(f"✅ Successfully configured for {region_info['Region Name']}!")
                st.info(f"💡 Latency optimized for users in this geographic area")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Region Selection Factors
    st.markdown("### 🎯 Four Key Factors for Region Selection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚖️ Compliance
        - **Data residency** requirements
        - Legal and regulatory constraints
        - Industry-specific compliance needs
        - **Example**: GDPR requires EU data to stay in EU
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚡ Latency
        - **User experience** optimization
        - Network performance impact
        - Real-time application requirements
        - **Example**: Gaming servers need <50ms latency
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 💰 Cost
        - **Regional pricing differences**
        - Data transfer costs
        - Currency exchange considerations
        - **Example**: US regions often have lower costs
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛠️ Services & Features
        - **Service availability** varies
        - Newer features roll out gradually
        - Regional service limits
        - **Example**: Some AI services start in us-east-1
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Regional Pricing Comparison
    st.markdown("### 💰 Regional Pricing Comparison")
    
    pricing_data = {
        'Region': ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1'],
        'EC2 t3.micro': [0.0104, 0.0104, 0.0116, 0.0116],
        'S3 Standard': [0.023, 0.023, 0.025, 0.025],
        'Data Transfer': [0.09, 0.09, 0.09, 0.09]
    }
    
    df_pricing = pd.DataFrame(pricing_data)
    
    fig = px.bar(df_pricing, x='Region', y=['EC2 t3.micro', 'S3 Standard'], 
                 title='Regional Pricing Comparison (USD per hour/GB)',
                 color_discrete_sequence=[AWS_COLORS['primary'], AWS_COLORS['light_blue']])
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Region-aware Deployment")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Deploy resources across multiple regions for high availability
import boto3

def deploy_to_regions(regions, application_config):
    deployments = {}
    
    for region in regions:
        print(f"Deploying to {region}...")
        
        # Create clients for each region
        ec2 = boto3.client('ec2', region_name=region)
        s3 = boto3.client('s3', region_name=region)
        
        # Deploy EC2 instances
        try:
            response = ec2.run_instances(
                ImageId=get_ami_for_region(region),
                MinCount=2,
                MaxCount=2,
                InstanceType='t3.micro',
                UserData=application_config['user_data'],
                TagSpecifications=[{
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Region', 'Value': region},
                        {'Key': 'Application', 'Value': 'WebApp'},
                        {'Key': 'Environment', 'Value': 'Production'}
                    ]
                }]
            )
            
            deployments[region] = {
                'instances': [i['InstanceId'] for i in response['Instances']],
                'status': 'success'
            }
            
        except Exception as e:
            deployments[region] = {'status': 'failed', 'error': str(e)}
            
    return deployments

def get_ami_for_region(region):
    # AMI IDs vary by region
    ami_mappings = {
        'us-east-1': 'ami-0abcdef1234567890',
        'us-west-2': 'ami-0987654321fedcba0',
        'eu-west-1': 'ami-0123456789abcdef0',
        'ap-southeast-1': 'ami-0fedcba0987654321'
    }
    return ami_mappings.get(region)

# Multi-region deployment
regions = ['us-east-1', 'us-west-2', 'eu-west-1']
config = {
    'user_data': """#!/bin/bash
    yum update -y
    amazon-linux-extras install docker
    service docker start
    docker run -d -p 80:80 nginx
    """
}

results = deploy_to_regions(regions, config)
print("Deployment Results:", results)
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def availability_zones_tab():
    """Content for Availability Zones tab"""
    st.markdown("## 🏢 AWS Availability Zones")
    st.markdown("*One or more discrete data centers with redundant power, networking, and connectivity*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Availability Zones (AZs)** are isolated data center locations within a region. They enable you to operate 
    production applications and databases that are more highly available, fault tolerant, and scalable than would be possible from a single data center.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # AZ Architecture
    st.markdown("### 🏗️ Availability Zone Architecture")
    common.mermaid(create_region_architecture_mermaid(), height="auto")
    
    # Interactive AZ Explorer
    st.markdown("### 🔍 Interactive AZ Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_region = st.selectbox("Choose Region:", [
            "us-east-1 (N. Virginia)", "us-west-2 (Oregon)", "eu-west-1 (Ireland)"
        ])
        
        region_code = selected_region.split()[0]
        
        if region_code == "us-east-1":
            azs = ["us-east-1a", "us-east-1b", "us-east-1c", "us-east-1d", "us-east-1e", "us-east-1f"]
        elif region_code == "us-west-2":
            azs = ["us-west-2a", "us-west-2b", "us-west-2c", "us-west-2d"]
        else:
            azs = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
        
        selected_azs = st.multiselect("Select Availability Zones for Deployment:", azs, default=azs[:2])
    
    with col2:
        deployment_type = st.selectbox("Deployment Strategy:", [
            "High Availability (Multi-AZ)", 
            "Disaster Recovery (Cross-AZ)", 
            "Load Distribution (All AZs)"
        ])
        
        instance_count = st.slider("Instances per AZ:", 1, 5, 2)
    
    if st.button("🚀 Deploy Multi-AZ Architecture", use_container_width=True):
        total_instances = len(selected_azs) * instance_count
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ Multi-AZ Deployment Configured!
        
        **Deployment Details:**
        - **Region**: {selected_region}
        - **Availability Zones**: {', '.join(selected_azs)}
        - **Strategy**: {deployment_type}
        - **Total Instances**: {total_instances}
        - **Fault Tolerance**: Can survive {len(selected_azs)-1} AZ failure(s)
        
        🛡️ **High Availability**: 99.99% uptime guaranteed!
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # AZ Characteristics
    st.markdown("### 🔧 AZ Key Characteristics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔌 Power & Infrastructure
        - **Redundant power** supplies
        - Uninterruptible power sources
        - Backup generators
        - **99.99% availability** SLA
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🌐 Networking
        - **High-bandwidth** fiber connections
        - Low-latency networking (<1ms)
        - Fully redundant networking
        - **100 Gbps** connectivity between AZs
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛡️ Isolation
        - **Physically separate** locations
        - Several kilometers apart
        - Independent failure domains
        - **Natural disaster** protection
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Service Types by AZ
    st.markdown("### 🎯 Service Types by Availability Zone")
    
    service_types_data = {
        'Service Type': ['Zonal Services', 'Regional Services', 'Global Services'],
        'Description': [
            'Run in specific AZ - you choose',
            'Automatically distributed across AZs',  
            'Run across multiple regions globally'
        ],
        'Examples': [
            'EC2, EBS, RDS',
            'DynamoDB, S3, ALB',
            'IAM, Route 53, WAF'
        ],
        'Availability': ['Single AZ', 'Multi-AZ', 'Global']
    }
    
    df_services = pd.DataFrame(service_types_data)
    st.dataframe(df_services, use_container_width=True)
    
    # AZ Latency Simulation
    st.markdown("### ⚡ AZ Network Performance Simulation")
    
    # Simulate network latencies
    latency_data = {
        'Connection Type': ['Within same AZ', 'Between AZs (same region)', 'Between regions'],
        'Typical Latency': [0.1, 0.8, 45.0],
        'Max Latency': [0.2, 1.5, 120.0],
        'Bandwidth': ['25 Gbps', '100 Gbps', '10 Gbps']
    }
    
    df_latency = pd.DataFrame(latency_data)
    
    fig = px.bar(df_latency, x='Connection Type', y='Typical Latency',
                 title='Network Latency Comparison (milliseconds)',
                 color='Connection Type',
                 color_discrete_sequence=[AWS_COLORS['success'], AWS_COLORS['primary'], AWS_COLORS['warning']])
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Best Practices
    st.markdown("### 💡 Multi-AZ Best Practices")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Design Principles
    
    **Always design for failure:**
    - Deploy across **at least 2 AZs** for high availability
    - Use **Auto Scaling Groups** that span multiple AZs  
    - Implement **health checks** and automatic failover
    - Store data in **multiple AZs** using replication
    
    **Cost vs Availability trade-offs:**
    - More AZs = Higher availability but higher cost
    - Consider your **RTO/RPO** requirements
    - Use **reserved instances** for predictable workloads
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Multi-AZ High Availability Setup")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Create highly available infrastructure across multiple AZs
import boto3

def create_multi_az_infrastructure(region, azs):
    ec2 = boto3.client('ec2', region_name=region)
    elbv2 = boto3.client('elbv2', region_name=region)
    autoscaling = boto3.client('autoscaling', region_name=region)
    
    # Create VPC across multiple AZs
    vpc_response = ec2.create_vpc(CidrBlock='10.0.0.0/16')
    vpc_id = vpc_response['Vpc']['VpcId']
    
    subnet_ids = []
    
    # Create subnets in each AZ
    for i, az in enumerate(azs):
        subnet_response = ec2.create_subnet(
            VpcId=vpc_id,
            CidrBlock=f'10.0.{i+1}.0/24',
            AvailabilityZone=az
        )
        subnet_ids.append(subnet_response['Subnet']['SubnetId'])
        print(f"Created subnet in {az}: {subnet_response['Subnet']['SubnetId']}")
    
    # Create Application Load Balancer across AZs
    alb_response = elbv2.create_load_balancer(
        Name='multi-az-alb',
        Subnets=subnet_ids,
        SecurityGroups=['sg-12345678'],  # Assume security group exists
        Scheme='internet-facing',
        Tags=[
            {'Key': 'Name', 'Value': 'Multi-AZ-ALB'},
            {'Key': 'Environment', 'Value': 'Production'}
        ]
    )
    
    alb_arn = alb_response['LoadBalancers'][0]['LoadBalancerArn']
    
    # Create Launch Template
    launch_template = ec2.create_launch_template(
        LaunchTemplateName='multi-az-template',
        LaunchTemplateData={
            'ImageId': 'ami-0abcdef1234567890',
            'InstanceType': 't3.micro',
            'SecurityGroupIds': ['sg-12345678'],
            'UserData': """#!/bin/bash
            yum update -y
            yum install -y httpd
            systemctl start httpd
            systemctl enable httpd
            echo "<h1>Instance in $(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)</h1>" > /var/www/html/index.html
            """.encode('base64').decode()
        }
    )
    
    # Create Auto Scaling Group across multiple AZs
    autoscaling.create_auto_scaling_group(
        AutoScalingGroupName='multi-az-asg',
        LaunchTemplate={
            'LaunchTemplateId': launch_template['LaunchTemplate']['LaunchTemplateId'],
            'Version': '1'
        },
        MinSize=len(azs),  # At least one instance per AZ
        MaxSize=len(azs) * 3,  # Scale up to 3 instances per AZ
        DesiredCapacity=len(azs) * 2,  # Start with 2 instances per AZ
        VPCZoneIdentifier=','.join(subnet_ids),
        HealthCheckType='ELB',
        HealthCheckGracePeriod=300,
        Tags=[
            {
                'Key': 'Name',
                'Value': 'Multi-AZ-Instance',
                'PropagateAtLaunch': True,
                'ResourceId': 'multi-az-asg',
                'ResourceType': 'auto-scaling-group'
            }
        ]
    )
    
    return {
        'vpc_id': vpc_id,
        'subnet_ids': subnet_ids,
        'alb_arn': alb_arn,
        'message': f'Multi-AZ infrastructure created across {len(azs)} availability zones'
    }

# Deploy across multiple AZs in us-east-1
azs = ['us-east-1a', 'us-east-1b', 'us-east-1c']
result = create_multi_az_infrastructure('us-east-1', azs)
print(result['message'])
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def points_of_presence_tab():
    """Content for Points of Presence tab"""
    st.markdown("## 📍 Points of Presence (PoP)")
    st.markdown("*600+ Edge Locations and 13 regional mid-tier regional cache servers*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Points of Presence (PoPs)** are AWS infrastructure components that bring AWS services closer to end users. 
    They consist of Edge Locations and Regional Edge Caches that form the backbone of content delivery networks.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # PoP Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 600+\n**Edge Locations**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 13\n**Regional Edge Caches**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 90+\n**Countries/Cities**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### <10ms\n**Typical Latency**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Global Infrastructure Overview
    st.markdown("### 🌍 Global Infrastructure Overview")
    common.mermaid(create_global_infrastructure_mermaid(), height=350)
    
    # Interactive Edge Location Finder
    st.markdown("### 🔍 Interactive Edge Location Explorer")
    
    # Sample edge location data
    edge_locations = {
        'North America': {
            'locations': ['Ashburn, VA', 'Atlanta, GA', 'Chicago, IL', 'Dallas, TX', 'Los Angeles, CA', 'New York, NY'],
            'count': 50,
            'services': ['CloudFront', 'Route 53', 'WAF', 'Shield']
        },
        'Europe': {
            'locations': ['Amsterdam', 'Dublin', 'Frankfurt', 'London', 'Madrid', 'Paris'],
            'count': 35,
            'services': ['CloudFront', 'Route 53', 'WAF', 'Shield']
        },
        'Asia Pacific': {
            'locations': ['Hong Kong', 'Mumbai', 'Seoul', 'Singapore', 'Sydney', 'Tokyo'],
            'count': 30,
            'services': ['CloudFront', 'Route 53', 'WAF', 'Shield']
        },
        'South America': {
            'locations': ['São Paulo', 'Rio de Janeiro', 'Buenos Aires'],
            'count': 8,
            'services': ['CloudFront', 'Route 53', 'WAF']
        }
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_region = st.selectbox("Select Region:", list(edge_locations.keys()))
        user_location = st.text_input("Your Location (City, Country):", "San Francisco, USA")
    
    with col2:
        content_type = st.selectbox("Content Type:", [
            "Web Pages (HTML/CSS/JS)", "Images (JPEG/PNG)", "Videos (MP4/HLS)", 
            "API Responses (JSON)", "Software Downloads"
        ])
    
    if st.button("🔍 Find Nearest Edge Location", use_container_width=True):
        region_data = edge_locations[selected_region]
        nearest_location = np.random.choice(region_data['locations'])
        latency = np.random.uniform(5, 50)
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 🎯 Optimal Edge Location Found!
        
        **Location Details:**
        - **Nearest Edge**: {nearest_location}
        - **Estimated Latency**: {latency:.1f} ms
        - **Content**: {content_type}
        - **Cache Hit Ratio**: {np.random.uniform(80, 95):.1f}%
        - **Available Services**: {', '.join(region_data['services'])}
        
        ⚡ **Performance Boost**: {np.random.uniform(60, 85):.0f}% faster delivery!
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Edge Location vs Regional Cache
    st.markdown("### ⚖️ Edge Locations vs Regional Edge Caches")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📍 Edge Locations
        
        **Characteristics:**
        - **600+ locations** worldwide
        - Smaller cache capacity
        - Closest to end users
        - **Immediate response** for cached content
        
        **Best For:**
        - Popular, frequently accessed content
        - Real-time applications
        - Global user base
        - **Static assets** (images, CSS, JS)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🏪 Regional Edge Caches
        
        **Characteristics:**
        - **13 strategic locations**
        - Larger cache capacity
        - Between edge locations and origin
        - **Longer retention** of content
        
        **Best For:**
        - Less popular content
        - Large file distributions
        - Reducing origin server load
        - **Dynamic content** caching
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Services Using PoPs
    st.markdown("### 🛠️ AWS Services Using Points of Presence")
    
    services_data = {
        'Service': ['Amazon CloudFront', 'Amazon Route 53', 'AWS WAF', 'AWS Shield', 'AWS Global Accelerator'],
        'Function': ['Content Delivery', 'DNS Resolution', 'Web Application Firewall', 'DDoS Protection', 'Network Acceleration'],
        'Edge Locations': ['✅ Yes', '✅ Yes', '✅ Yes', '✅ Yes', '✅ Yes'],
        'Primary Use Case': [
            'Static/Dynamic content caching',
            'Fast DNS lookups worldwide', 
            'Filter malicious traffic',
            'Absorb DDoS attacks',
            'Optimize network paths'
        ]
    }
    
    df_services = pd.DataFrame(services_data)
    st.dataframe(df_services, use_container_width=True)
    
    # Performance Comparison
    st.markdown("### 📊 Performance Impact Visualization")
    
    # Simulate performance data
    scenarios = ['Without CDN', 'With Edge Locations Only', 'With Edge + Regional Cache']
    load_times = [2.5, 0.8, 0.3]
    cache_hit_rates = [0, 75, 90]
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Page Load Time (seconds)', 'Cache Hit Rate (%)'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    fig.add_trace(
        go.Bar(x=scenarios, y=load_times, name='Load Time', 
               marker_color=AWS_COLORS['primary']),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=scenarios, y=cache_hit_rates, name='Cache Hit Rate',
               marker_color=AWS_COLORS['light_blue']),
        row=1, col=2
    )
    
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Working with Edge Locations")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Monitor and manage content delivery across edge locations
import boto3
import json
from datetime import datetime, timedelta

def get_cloudfront_edge_performance():
    cloudfront = boto3.client('cloudfront')
    cloudwatch = boto3.client('cloudwatch')
    
    # List all CloudFront distributions
    distributions = cloudfront.list_distributions()
    
    for dist in distributions['DistributionList']['Items']:
        dist_id = dist['Id']
        domain_name = dist['DomainName']
        
        print(f"Distribution: {domain_name} ({dist_id})")
        
        # Get edge location statistics
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        
        # Cache hit rate across all edge locations
        cache_hits = cloudwatch.get_metric_statistics(
            Namespace='AWS/CloudFront',
            MetricName='CacheHitRate',
            Dimensions=[{'Name': 'DistributionId', 'Value': dist_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,  # 1 hour periods
            Statistics=['Average']
        )
        
        # Origin requests (cache misses)
        origin_requests = cloudwatch.get_metric_statistics(
            Namespace='AWS/CloudFront',
            MetricName='Requests',
            Dimensions=[{'Name': 'DistributionId', 'Value': dist_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=['Sum']
        )
        
        if cache_hits['Datapoints']:
            avg_hit_rate = sum([dp['Average'] for dp in cache_hits['Datapoints']]) / len(cache_hits['Datapoints'])
            print(f"  Average Cache Hit Rate: {avg_hit_rate:.2f}%")
        
        if origin_requests['Datapoints']:
            total_requests = sum([dp['Sum'] for dp in origin_requests['Datapoints']])
            print(f"  Total Requests (24h): {total_requests:,.0f}")
        
        # Get distribution config to see edge locations
        config = cloudfront.get_distribution_config(Id=dist_id)
        price_class = config['DistributionConfig'].get('PriceClass', 'PriceClass_All')
        
        edge_coverage = {
            'PriceClass_100': 'US, Canada, Europe',
            'PriceClass_200': 'US, Canada, Europe, Asia, Middle East, Africa', 
            'PriceClass_All': 'All Edge Locations Worldwide'
        }
        
        print(f"  Edge Location Coverage: {edge_coverage.get(price_class, 'Unknown')}")
        print("  " + "-" * 50)

def invalidate_edge_cache(distribution_id, paths):
    """Invalidate content across all edge locations"""
    cloudfront = boto3.client('cloudfront')
    
    try:
        response = cloudfront.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': len(paths),
                    'Items': paths
                },
                'CallerReference': str(datetime.utcnow().timestamp())
            }
        )
        
        invalidation_id = response['Invalidation']['Id']
        print(f"Cache invalidation started: {invalidation_id}")
        print(f"Paths invalidated: {', '.join(paths)}")
        print("Content will be refreshed at all edge locations within 10-15 minutes")
        
        return invalidation_id
        
    except Exception as e:
        print(f"Error creating invalidation: {e}")
        return None

# Monitor edge location performance
get_cloudfront_edge_performance()

# Invalidate cached content across all edge locations
invalidate_edge_cache('E1234567890ABC', ['/index.html', '/css/*', '/js/*'])
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def cloudfront_tab():
    """Content for Amazon CloudFront tab"""
    st.markdown("## ⚡ Amazon CloudFront")
    st.markdown("*Global content delivery network with low latency and high transfer speeds*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Amazon CloudFront** is a fast content delivery network (CDN) service that securely delivers data, videos, 
    applications, and APIs to customers globally with low latency, high transfer speeds, all within a developer-friendly environment.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # CloudFront Architecture Flow
    st.markdown("### 🔄 CloudFront Content Delivery Flow")
    common.mermaid(create_cloudfront_architecture_mermaid(), height=350)
    
    # Interactive CloudFront Distribution Builder
    st.markdown("### 🛠️ Interactive CloudFront Distribution Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🗂️ Origin Configuration")
        origin_type = st.selectbox("Origin Type:", [
            "Amazon S3 Bucket", "Application Load Balancer", "EC2 Instance", "Custom HTTP Server"
        ])
        
        if origin_type == "Amazon S3 Bucket":
            origin_domain = st.text_input("S3 Bucket Name:", "my-website-bucket.s3.amazonaws.com")
        else:
            origin_domain = st.text_input("Origin Domain:", "api.mycompany.com")
        
        price_class = st.selectbox("Price Class (Edge Location Coverage):", [
            "Use All Edge Locations (Best Performance)",
            "Use US, Canada, Europe (Balanced)",
            "Use US and Canada Only (Lowest Cost)"
        ])
    
    with col2:
        st.markdown("### ⚙️ Distribution Settings")
        cache_behavior = st.selectbox("Default Cache Behavior:", [
            "Cache Everything (Static Site)",
            "Cache Based on Headers (Dynamic)",
            "No Caching (Pass Through)",
            "Custom Caching Policy"
        ])
        
        ssl_certificate = st.selectbox("SSL Certificate:", [
            "Default CloudFront Certificate",
            "AWS Certificate Manager (ACM)",
            "Custom SSL Certificate"
        ])
        
        compression = st.checkbox("Enable Gzip Compression", value=True)
        logging = st.checkbox("Enable Access Logs", value=False)
    
    # Advanced Settings
    st.markdown("### 🔧 Advanced Configuration")
    col3, col4 = st.columns(2)
    
    with col3:
        custom_domain = st.text_input("Custom Domain (CNAME):", "cdn.mywebsite.com")
        default_root = st.text_input("Default Root Object:", "index.html")
    
    with col4:
        ttl_min = st.number_input("Minimum TTL (seconds):", 0, 86400, 0)
        ttl_max = st.number_input("Maximum TTL (seconds):", 1, 31536000, 31536000)
    
    if st.button("🚀 Create CloudFront Distribution", use_container_width=True):
        # Simulate distribution creation
        distribution_id = f"E{np.random.randint(100000000000, 999999999999)}"
        cloudfront_domain = f"{distribution_id.lower()}.cloudfront.net"
        
        # Calculate estimated cost
        if "All Edge Locations" in price_class:
            cost_multiplier = 1.0
            coverage = "600+ locations worldwide"
        elif "US, Canada, Europe" in price_class:
            cost_multiplier = 0.8
            coverage = "US, Canada, Europe"
        else:
            cost_multiplier = 0.6
            coverage = "US and Canada only"
        
        base_cost = 0.085 * cost_multiplier  # per GB
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ CloudFront Distribution Created!
        
        **Distribution Details:**
        - **Distribution ID**: {distribution_id}
        - **CloudFront Domain**: {cloudfront_domain}
        - **Custom Domain**: {custom_domain if custom_domain else 'None'}
        - **Origin**: {origin_domain}
        - **SSL Certificate**: {ssl_certificate}
        - **Edge Coverage**: {coverage}
        
        **Performance Features:**
        - **Compression**: {'✅ Enabled' if compression else '❌ Disabled'}
        - **Access Logs**: {'✅ Enabled' if logging else '❌ Disabled'}
        - **Cache TTL**: {ttl_min}s - {ttl_max}s
        
        💰 **Estimated Cost**: ${base_cost:.3f} per GB transferred
        ⏱️ **Deployment Time**: 15-20 minutes
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # CloudFront Benefits
    st.markdown("### ✨ CloudFront Benefits & Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚡ Performance
        - **Global edge network** (600+ locations)
        - Content cached close to users
        - Reduced latency and faster load times
        - **HTTP/2 and HTTP/3** support
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛡️ Security
        - **AWS WAF** integration
        - DDoS protection with AWS Shield
        - SSL/TLS encryption
        - **Origin Access Control** for S3
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 💰 Cost Optimization
        - **Pay-as-you-go** pricing
        - Reduced origin server load
        - Free tier: 1TB data transfer
        - **Regional pricing** options
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Use Cases
    st.markdown("### 🌟 Common CloudFront Use Cases")
    
    use_cases_data = {
        'Use Case': ['Static Website', 'API Acceleration', 'Video Streaming', 'Software Distribution', 'E-commerce'],
        'Content Type': ['HTML, CSS, JS, Images', 'JSON API Responses', 'Video Files, HLS', 'Software Packages', 'Product Images, CSS'],
        'Cache Strategy': ['Long TTL (1 day)', 'Short TTL (5 min)', 'Long TTL + Streaming', 'Very Long TTL (1 week)', 'Mixed TTL'],
        'Key Benefit': ['Fast Page Loads', 'Reduced API Latency', 'Global Video Delivery', 'Faster Downloads', 'Better User Experience']
    }
    
    df_use_cases = pd.DataFrame(use_cases_data)
    st.dataframe(df_use_cases, use_container_width=True)
    
    # Performance Simulation
    st.markdown("### 📊 Performance Impact Simulation")
    
    # Interactive performance calculator
    st.markdown("### 🧮 Performance Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        file_size = st.slider("Average File Size (MB):", 0.1, 100.0, 2.0)
        users_per_day = st.slider("Daily Users:", 1000, 1000000, 10000)
        origin_location = st.selectbox("Origin Server Location:", [
            "us-east-1 (Virginia)", "eu-west-1 (Ireland)", "ap-southeast-1 (Singapore)"
        ])
    
    with col2:
        user_location = st.selectbox("Primary User Base:", [
            "Global", "North America", "Europe", "Asia Pacific"
        ])
        
        cache_hit_rate = st.slider("Expected Cache Hit Rate (%):", 50, 95, 85)
    
    # Calculate performance metrics
    if st.button("📊 Calculate Performance Impact"):
        # Simulate latency improvements
        without_cdn_latency = np.random.uniform(800, 2000)  # ms
        with_cdn_latency = np.random.uniform(50, 200)  # ms
        
        # Calculate bandwidth savings
        total_requests = users_per_day * 10  # Assume 10 requests per user
        cached_requests = total_requests * (cache_hit_rate / 100)
        origin_requests = total_requests - cached_requests
        
        bandwidth_saved = (cached_requests * file_size) / 1024  # GB
        cost_savings = bandwidth_saved * 0.09  # Assume $0.09/GB origin cost
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Latency Reduction", 
                     f"{with_cdn_latency:.0f}ms", 
                     f"-{without_cdn_latency - with_cdn_latency:.0f}ms")
        
        with col2:
            st.metric("Speed Improvement", 
                     f"{(without_cdn_latency/with_cdn_latency):.1f}x", 
                     "Faster")
        
        with col3:
            st.metric("Bandwidth Saved", 
                     f"{bandwidth_saved:.1f} GB/day", 
                     f"{cache_hit_rate}% cache hit")
        
        with col4:
            st.metric("Cost Savings", 
                     f"${cost_savings:.2f}/day", 
                     "Origin bandwidth")
    
    # Code Example
    st.markdown("### 💻 Code Example: CloudFront Distribution Management")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Create and manage CloudFront distribution
import boto3
import json
from datetime import datetime

def create_cloudfront_distribution(origin_domain, custom_domain=None):
    cloudfront = boto3.client('cloudfront')
    
    # Distribution configuration
    distribution_config = {
        'CallerReference': str(datetime.utcnow().timestamp()),
        'Comment': 'My website CDN distribution',
        'DefaultCacheBehavior': {
            'TargetOriginId': 'myS3Origin',
            'ViewerProtocolPolicy': 'redirect-to-https',
            'MinTTL': 0,
            'ForwardedValues': {
                'QueryString': False,
                'Cookies': {'Forward': 'none'}
            },
            'Compress': True,  # Enable Gzip compression
            'LambdaFunctionAssociations': {
                'Quantity': 0,
                'Items': []
            }
        },
        'Origins': {
            'Quantity': 1,
            'Items': [
                {
                    'Id': 'myS3Origin',
                    'DomainName': origin_domain,
                    'S3OriginConfig': {
                        'OriginAccessIdentity': ''  # Use OAC instead for new distributions
                    }
                }
            ]
        },
        'Enabled': True,
        'PriceClass': 'PriceClass_All',  # Use all edge locations
        'DefaultRootObject': 'index.html'
    }
    
    # Add custom domain if provided
    if custom_domain:
        distribution_config['Aliases'] = {
            'Quantity': 1,
            'Items': [custom_domain]
        }
        distribution_config['ViewerCertificate'] = {
            'CertificateSource': 'acm',
            'SSLSupportMethod': 'sni-only',
            'MinimumProtocolVersion': 'TLSv1.2_2021'
        }
    else:
        distribution_config['ViewerCertificate'] = {
            'CloudFrontDefaultCertificate': True
        }
    
    try:
        response = cloudfront.create_distribution(
            DistributionConfig=distribution_config
        )
        
        distribution = response['Distribution']
        distribution_id = distribution['Id']
        domain_name = distribution['DomainName']
        
        print(f"✅ Distribution created successfully!")
        print(f"Distribution ID: {distribution_id}")
        print(f"CloudFront Domain: {domain_name}")
        print(f"Status: {distribution['Status']}")
        print("⏱️  Distribution will be deployed in 15-20 minutes")
        
        return distribution_id
        
    except Exception as e:
        print(f"❌ Error creating distribution: {e}")
        return None

def create_invalidation(distribution_id, paths):
    """Invalidate cached content"""
    cloudfront = boto3.client('cloudfront')
    
    try:
        response = cloudfront.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': len(paths),
                    'Items': paths
                },
                'CallerReference': str(datetime.utcnow().timestamp())
            }
        )
        
        print(f"🔄 Invalidation created: {response['Invalidation']['Id']}")
        print(f"Paths: {', '.join(paths)}")
        return response['Invalidation']['Id']
        
    except Exception as e:
        print(f"❌ Error creating invalidation: {e}")
        return None

def get_distribution_metrics(distribution_id, hours=24):
    """Get CloudFront performance metrics"""
    cloudwatch = boto3.client('cloudwatch')
    
    from datetime import timedelta
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    metrics = {}
    
    # Get requests count
    requests = cloudwatch.get_metric_statistics(
        Namespace='AWS/CloudFront',
        MetricName='Requests',
        Dimensions=[{'Name': 'DistributionId', 'Value': distribution_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=3600,
        Statistics=['Sum']
    )
    
    # Get bytes downloaded
    bytes_downloaded = cloudwatch.get_metric_statistics(
        Namespace='AWS/CloudFront',
        MetricName='BytesDownloaded',
        Dimensions=[{'Name': 'DistributionId', 'Value': distribution_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=3600,
        Statistics=['Sum']
    )
    
    # Get cache hit rate
    cache_hit_rate = cloudwatch.get_metric_statistics(
        Namespace='AWS/CloudFront',
        MetricName='CacheHitRate',
        Dimensions=[{'Name': 'DistributionId', 'Value': distribution_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=3600,
        Statistics=['Average']
    )
    
    if requests['Datapoints']:
        total_requests = sum([dp['Sum'] for dp in requests['Datapoints']])
        metrics['total_requests'] = total_requests
    
    if bytes_downloaded['Datapoints']:
        total_bytes = sum([dp['Sum'] for dp in bytes_downloaded['Datapoints']])
        metrics['total_gb'] = total_bytes / (1024**3)
    
    if cache_hit_rate['Datapoints']:
        avg_hit_rate = sum([dp['Average'] for dp in cache_hit_rate['Datapoints']]) / len(cache_hit_rate['Datapoints'])
        metrics['cache_hit_rate'] = avg_hit_rate
    
    return metrics

# Example usage
distribution_id = create_cloudfront_distribution(
    origin_domain='my-website-bucket.s3.amazonaws.com',
    custom_domain='cdn.mywebsite.com'
)

if distribution_id:
    # Create invalidation for updated content
    create_invalidation(distribution_id, ['/index.html', '/css/*', '/js/*'])
    
    # Get performance metrics
    metrics = get_distribution_metrics(distribution_id)
    if metrics:
        print(f"📊 Performance Metrics:")
        print(f"  Total Requests: {metrics.get('total_requests', 0):,}")
        print(f"  Data Transferred: {metrics.get('total_gb', 0):.2f} GB")
        print(f"  Cache Hit Rate: {metrics.get('cache_hit_rate', 0):.1f}%")
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def regional_edge_caches_tab():
    """Content for Regional Edge Caches tab"""
    st.markdown("## 🏪 Regional Edge Caches")
    st.markdown("*Regional edge caches for less popular content*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Regional Edge Caches** sit between CloudFront edge locations and your origin servers. They help improve 
    performance for content that isn't popular enough to stay cached at edge locations, providing a larger cache 
    with longer retention times.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Regional Edge Cache Architecture
    st.markdown("### 🏗️ Regional Edge Cache Architecture")
    common.mermaid(create_regional_edge_cache_mermaid(), height=1300)
    
    # Cache Hierarchy Explanation
    st.markdown("### 📚 Cache Hierarchy Explained")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 1️⃣ Edge Location Cache
        - **Capacity**: Small (limited storage)
        - **Content**: Most popular content
        - **Retention**: Hours to days
        - **Latency**: <10ms to users
        - **Count**: 600+ locations
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 2️⃣ Regional Edge Cache
        - **Capacity**: Large (extensive storage)
        - **Content**: Less popular content
        - **Retention**: Days to weeks
        - **Latency**: 20-50ms to edge locations
        - **Count**: 13 strategic locations
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 3️⃣ Origin Server
        - **Capacity**: Unlimited (source of truth)
        - **Content**: All content
        - **Retention**: Permanent
        - **Latency**: 100-500ms to regional caches
        - **Count**: Your servers/S3
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Cache Performance Simulator
    st.markdown("### 🎮 Interactive Cache Performance Simulator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Content Characteristics")
        content_type = st.selectbox("Content Type:", [
            "Popular Static Assets (CSS, JS, Images)",
            "User Generated Content (Photos, Videos)", 
            "E-commerce Product Images",
            "News Articles and Blog Posts",
            "Software Downloads",
            "API Responses"
        ])
        
        content_size = st.slider("Average Content Size (MB):", 0.1, 500.0, 5.0)
        popularity_score = st.slider("Content Popularity (1-10):", 1, 10, 5)
    
    with col2:
        st.markdown("### 🌍 Traffic Patterns")
        total_requests = st.slider("Daily Requests:", 1000, 1000000, 50000)
        geographic_spread = st.selectbox("Geographic Distribution:", [
            "Global (Worldwide)", "Regional (Continent)", "Local (Country/State)"
        ])
        
        time_pattern = st.selectbox("Access Pattern:", [
            "Consistent (24/7)", "Business Hours Peak", "Event-Driven Spikes"
        ])
    
    if st.button("🚀 Simulate Cache Performance", use_container_width=True):
        # Calculate cache efficiency based on inputs
        if popularity_score >= 8:
            edge_hit_rate = np.random.uniform(85, 95)
            regional_hit_rate = np.random.uniform(5, 10)
            origin_hit_rate = np.random.uniform(0, 5)
        elif popularity_score >= 5:
            edge_hit_rate = np.random.uniform(60, 80)
            regional_hit_rate = np.random.uniform(15, 25)
            origin_hit_rate = np.random.uniform(5, 15)
        else:
            edge_hit_rate = np.random.uniform(30, 50)
            regional_hit_rate = np.random.uniform(30, 50)
            origin_hit_rate = np.random.uniform(20, 40)
        
        # Calculate performance metrics
        avg_latency = (edge_hit_rate * 15 + regional_hit_rate * 45 + origin_hit_rate * 200) / 100
        bandwidth_saved = total_requests * content_size * (edge_hit_rate + regional_hit_rate) / 100 / 1024  # GB
        cost_savings = bandwidth_saved * 0.05  # Estimated origin bandwidth cost
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 📊 Cache Performance Results
        
        **Hit Rates:**
        - **Edge Location**: {edge_hit_rate:.1f}% (fastest response)
        - **Regional Cache**: {regional_hit_rate:.1f}% (fast response)
        - **Origin Server**: {origin_hit_rate:.1f}% (slowest response)
        
        **Performance Metrics:**
        - **Average Latency**: {avg_latency:.1f}ms
        - **Bandwidth Saved**: {bandwidth_saved:.1f} GB/day
        - **Estimated Savings**: ${cost_savings:.2f}/day
        - **User Experience**: {'Excellent' if avg_latency < 50 else 'Good' if avg_latency < 100 else 'Needs Improvement'}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Content Types and Caching Strategy
    st.markdown("### 📁 Content Types & Optimal Caching Strategies")
    
    caching_strategies = {
        'Content Type': [
            'Static Assets (CSS, JS)', 'Product Images', 'User Photos/Videos', 
            'News Articles', 'API Responses', 'Software Downloads'
        ],
        'Edge Cache TTL': ['7 days', '1 day', '6 hours', '2 hours', '5 minutes', '30 days'],
        'Regional Cache Benefit': ['Low', 'High', 'Very High', 'High', 'Medium', 'Very High'],
        'Primary Cache Tier': ['Edge', 'Regional', 'Regional', 'Regional', 'Edge', 'Regional'],
        'Use Case': [
            'Fast website loading',
            'E-commerce performance', 
            'Social media platforms',
            'News/blog websites',
            'API acceleration',
            'Software distribution'
        ]
    }
    
    df_strategies = pd.DataFrame(caching_strategies)
    st.dataframe(df_strategies, use_container_width=True)
    
    # Regional Edge Cache Benefits
    st.markdown("### ✨ Key Benefits of Regional Edge Caches")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 Performance Benefits
        - **Reduced origin load** by up to 60%
        - Faster delivery of less popular content
        - **Lower latency** for dynamic content
        - Improved user experience globally
        
        ### 💰 Cost Benefits
        - **Reduced data transfer** costs from origin
        - Lower origin server infrastructure needs
        - **Bandwidth optimization** across regions
        - Better resource utilization
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛡️ Reliability Benefits
        - **Origin protection** during traffic spikes
        - Fault tolerance and redundancy
        - **Graceful degradation** during outages
        - Improved overall system resilience
        
        ### 📈 Scalability Benefits
        - **Handle seasonal traffic** variations
        - Support for viral content distribution
        - **Global content distribution** efficiency
        - Automatic capacity scaling
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # When Regional Caches Help Most
    st.markdown("### 🎯 When Regional Edge Caches Help Most")
    
    scenarios_data = {
        'Scenario': [
            'User Generated Content',
            'E-commerce Catalogs', 
            'News & Media Sites',
            'Software Distribution',
            'Educational Content',
            'Enterprise Applications'
        ],
        'Why Regional Caches Help': [
            'Content not popular enough for edge cache',
            'Large product images need longer retention',
            'Articles become less popular over time', 
            'Large files need persistent caching',
            'Seasonal access patterns',
            'Internal content with varying popularity'
        ],
        'Expected Improvement': [
            '40-60% faster delivery',
            '50-70% origin load reduction',
            '30-50% improved cache hit rate',
            '60-80% bandwidth savings',
            '35-55% performance boost',
            '45-65% reduced latency'
        ]
    }
    
    df_scenarios = pd.DataFrame(scenarios_data)
    st.dataframe(df_scenarios, use_container_width=True)
    
    # Monitoring and Optimization
    st.markdown("### 📊 Monitoring Regional Edge Cache Performance")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🔍 Key Metrics to Monitor
    
    **Cache Performance:**
    - **Cache Hit Ratio** at each tier (Edge vs Regional vs Origin)
    - **Response Times** from each cache level
    - **Bandwidth Utilization** and data transfer patterns
    
    **Optimization Strategies:**
    - Adjust **TTL values** based on content popularity
    - Monitor **geographic access patterns**
    - Analyze **content request frequencies**
    - Implement **cache warming** for predictable content
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Monitoring Cache Performance")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Monitor Regional Edge Cache performance and optimize content delivery
import boto3
import pandas as pd
from datetime import datetime, timedelta

def analyze_cache_performance(distribution_id, days=7):
    """Analyze cache performance across all cache tiers"""
    cloudwatch = boto3.client('cloudwatch')
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    
    metrics = {}
    
    # Get detailed cache metrics
    cache_metrics = [
        'Requests', 'BytesDownloaded', 'CacheHitRate', 
        'OriginLatency', 'ErrorRate4xx', 'ErrorRate5xx'
    ]
    
    for metric_name in cache_metrics:
        try:
            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/CloudFront',
                MetricName=metric_name,
                Dimensions=[
                    {'Name': 'DistributionId', 'Value': distribution_id}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour intervals
                Statistics=['Average', 'Sum', 'Maximum']
            )
            
            metrics[metric_name] = response['Datapoints']
            
        except Exception as e:
            print(f"Error getting {metric_name}: {e}")
    
    return analyze_cache_efficiency(metrics)

def analyze_cache_efficiency(metrics_data):
    """Analyze cache efficiency and provide recommendations"""
    analysis = {}
    
    # Calculate cache hit rates
    if 'CacheHitRate' in metrics_data and metrics_data['CacheHitRate']:
        hit_rates = [dp['Average'] for dp in metrics_data['CacheHitRate']]
        avg_hit_rate = sum(hit_rates) / len(hit_rates)
        analysis['average_cache_hit_rate'] = avg_hit_rate
        
        # Determine cache effectiveness
        if avg_hit_rate > 85:
            analysis['cache_performance'] = 'Excellent'
            analysis['regional_cache_benefit'] = 'Low - most content served from edge'
        elif avg_hit_rate > 70:
            analysis['cache_performance'] = 'Good'
            analysis['regional_cache_benefit'] = 'Medium - regional cache helping'
        else:
            analysis['cache_performance'] = 'Needs Improvement'
            analysis['regional_cache_benefit'] = 'High - optimize TTL and caching strategies'
    
    # Calculate data transfer volumes
    if 'BytesDownloaded' in metrics_data and metrics_data['BytesDownloaded']:
        bytes_data = [dp['Sum'] for dp in metrics_data['BytesDownloaded']]
        total_gb = sum(bytes_data) / (1024**3)
        analysis['total_data_transferred'] = total_gb
        
        # Estimate regional cache contribution
        if 'average_cache_hit_rate' in analysis:
            # Estimate how much traffic went through regional caches
            edge_hit_estimate = min(analysis['average_cache_hit_rate'], 75)  # Edge typically handles up to 75%
            regional_hit_estimate = max(0, analysis['average_cache_hit_rate'] - edge_hit_estimate)
            
            analysis['estimated_regional_cache_gb'] = total_gb * (regional_hit_estimate / 100)
            analysis['estimated_cost_savings'] = analysis['estimated_regional_cache_gb'] * 0.05  # $0.05/GB savings
    
    # Origin latency analysis
    if 'OriginLatency' in metrics_data and metrics_data['OriginLatency']:
        latencies = [dp['Average'] for dp in metrics_data['OriginLatency']]
        avg_latency = sum(latencies) / len(latencies)
        analysis['average_origin_latency'] = avg_latency
        
        if avg_latency > 500:
            analysis['origin_recommendation'] = 'Consider multiple origin locations or faster origin servers'
        elif avg_latency > 200:
            analysis['origin_recommendation'] = 'Regional caches are providing significant benefit'
        else:
            analysis['origin_recommendation'] = 'Origin performance is good'
    
    return analysis

def optimize_cache_settings(distribution_id, content_analysis):
    """Recommend cache optimization based on content analysis"""
    cloudfront = boto3.client('cloudfront')
    
    try:
        # Get current distribution config
        response = cloudfront.get_distribution_config(Id=distribution_id)
        config = response['DistributionConfig']
        etag = response['ETag']
        
        recommendations = []
        
        # Analyze current cache behaviors
        default_behavior = config['DefaultCacheBehavior']
        current_ttl = default_behavior.get('DefaultTTL', 86400)
        
        # TTL recommendations based on cache hit rate
        if content_analysis.get('average_cache_hit_rate', 0) < 60:
            recommendations.append({
                'setting': 'Increase DefaultTTL',
                'current': f'{current_ttl} seconds',
                'recommended': f'{current_ttl * 2} seconds',
                'reason': 'Low cache hit rate - extend content retention'
            })
        
        # Compression recommendations
        if not default_behavior.get('Compress', False):
            recommendations.append({
                'setting': 'Enable Compression',
                'current': 'Disabled',
                'recommended': 'Enabled', 
                'reason': 'Reduce bandwidth and improve performance'
            })
        
        # Query string handling for better caching
        if default_behavior['ForwardedValues']['QueryString']:
            recommendations.append({
                'setting': 'Review Query String Forwarding',
                'current': 'All query strings forwarded',
                'recommended': 'Forward only necessary query strings',
                'reason': 'Improve cache hit rate by reducing cache key variations'
            })
        
        return recommendations
        
    except Exception as e:
        print(f"Error analyzing distribution config: {e}")
        return []

def generate_cache_report(distribution_id):
    """Generate comprehensive cache performance report"""
    print(f"🔍 Analyzing cache performance for distribution: {distribution_id}")
    print("=" * 60)
    
    # Get performance analysis
    analysis = analyze_cache_performance(distribution_id)
    
    print(f"📊 CACHE PERFORMANCE SUMMARY")
    print(f"Average Cache Hit Rate: {analysis.get('average_cache_hit_rate', 0):.1f}%")
    print(f"Cache Performance: {analysis.get('cache_performance', 'Unknown')}")
    print(f"Total Data Transferred: {analysis.get('total_data_transferred', 0):.2f} GB")
    print(f"Regional Cache Benefit: {analysis.get('regional_cache_benefit', 'Unknown')}")
    
    if 'estimated_cost_savings' in analysis:
        print(f"Estimated Cost Savings: ${analysis['estimated_cost_savings']:.2f}")
    
    if 'average_origin_latency' in analysis:
        print(f"Average Origin Latency: {analysis['average_origin_latency']:.0f}ms")
    
    print("\n🎯 OPTIMIZATION RECOMMENDATIONS")
    recommendations = optimize_cache_settings(distribution_id, analysis)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['setting']}")
        print(f"   Current: {rec['current']}")
        print(f"   Recommended: {rec['recommended']}")
        print(f"   Reason: {rec['reason']}")
        print()
    
    return analysis

# Example usage
distribution_id = "E1234567890ABC"
cache_analysis = generate_cache_report(distribution_id)
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
    # 🌍 AWS Global Infrastructure
    
    """)
    st.markdown("""<div class="info-box">
                Understand and implement AWS global infrastructure components including regions, availability zones, and content delivery networks to design highly available, low-latency applications with optimal performance and cost efficiency.
                </div>""", unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌍 AWS Regions", 
        "🏢 Availability Zones", 
        "📍 Points of Presence",
        "⚡ Amazon CloudFront",
        "🏪 Regional Edge Caches"
    ])
    
    with tab1:
        aws_regions_tab()
    
    with tab2:
        availability_zones_tab()
    
    with tab3:
        points_of_presence_tab()
    
    with tab4:
        cloudfront_tab()
        
    with tab5:
        regional_edge_caches_tab()
    
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
