
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
    page_title="AWS Networking Essentials Hub",
    page_icon="🌐",
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
        
        .vpc-builder {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            border: 2px solid {AWS_COLORS['light_blue']};
            margin: 15px 0;
        }}
        
        .subnet-public {{
            background-color: #E8F5E8;
            border: 2px solid {AWS_COLORS['success']};
            padding: 10px;
            border-radius: 8px;
            margin: 5px;
        }}
        
        .subnet-private {{
            background-color: #FFE8E8;
            border: 2px solid {AWS_COLORS['warning']};
            padding: 10px;
            border-radius: 8px;
            margin: 5px;
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
            - 🌐 Amazon Virtual Private Cloud (VPC) - Isolated cloud networking
            - 🔗 AWS PrivateLink - Private connectivity to AWS services
            - 🌍 Amazon Route 53 - Scalable DNS and domain management
            
            **Learning Objectives:**
            - Design and implement VPC architectures
            - Configure private connectivity with PrivateLink
            - Set up DNS routing and domain management
            - Practice with interactive network builders and examples
            """)

def create_vpc_architecture_mermaid():
    """Create mermaid diagram for VPC architecture"""
    return """
    graph TB
        subgraph "AWS Cloud"
            subgraph "VPC 10.0.0.0/16"
                subgraph "Availability Zone A"
                    PubSubA[Public Subnet<br/>10.0.1.0/24]
                    PrivSubA[Private Subnet<br/>10.0.2.0/24]
                end
                
                subgraph "Availability Zone B"
                    PubSubB[Public Subnet<br/>10.0.3.0/24]
                    PrivSubB[Private Subnet<br/>10.0.4.0/24]
                end
                
                IGW[Internet Gateway]
                NAT[NAT Gateway]
                ALB[Application Load Balancer]
                
                PubSubA --> IGW
                PubSubB --> IGW
                PrivSubA --> NAT
                PrivSubB --> NAT
                NAT --> IGW
                
                ALB --> PubSubA
                ALB --> PubSubB
            end
        end
        
        Internet[🌐 Internet] --> IGW
        
        style PubSubA fill:#3FB34F,stroke:#232F3E,color:#fff
        style PubSubB fill:#3FB34F,stroke:#232F3E,color:#fff
        style PrivSubA fill:#FF6B35,stroke:#232F3E,color:#fff
        style PrivSubB fill:#FF6B35,stroke:#232F3E,color:#fff
        style IGW fill:#FF9900,stroke:#232F3E,color:#fff
        style NAT fill:#4B9EDB,stroke:#232F3E,color:#fff
        style ALB fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_privatelink_architecture_mermaid():
    """Create mermaid diagram for PrivateLink architecture"""
    return """
    graph TB
        subgraph "Customer VPC"
            EC2[EC2 Instance]
            VPCEndpoint[VPC Endpoint]
            EC2 --> VPCEndpoint
        end
        
        subgraph "AWS Service VPC"
            S3Service[Amazon S3]
            DynamoService[DynamoDB]
            ECSService[Amazon ECS]
        end
        
        VPCEndpoint -.->|Private Connection| S3Service
        VPCEndpoint -.->|No Internet Required| DynamoService
        VPCEndpoint -.->|Secure Access| ECSService
        
        Internet[🌐 Internet]
        EC2 -.->|❌ No Direct Access| Internet
        
        style EC2 fill:#FF9900,stroke:#232F3E,color:#fff
        style VPCEndpoint fill:#4B9EDB,stroke:#232F3E,color:#fff
        style S3Service fill:#3FB34F,stroke:#232F3E,color:#fff
        style DynamoService fill:#3FB34F,stroke:#232F3E,color:#fff
        style ECSService fill:#3FB34F,stroke:#232F3E,color:#fff
    """

def create_route53_dns_flow_mermaid():
    """Create mermaid diagram for Route 53 DNS flow"""
    return """
    graph LR
        User[👤 User] --> Browser[🌐 Browser]
        Browser --> Route53[Amazon Route 53]
        Route53 --> Policy{Routing Policy}
        
        Policy --> Simple[Simple Routing]
        Policy --> Weighted[Weighted Routing]
        Policy --> Latency[Latency-based]
        Policy --> Failover[Failover Routing]
        
        Simple --> Server1[🖥️ us-east-1]
        Weighted --> Server2[🖥️ us-west-2]
        Latency --> Server3[🖥️ eu-west-1]
        Failover --> Server4[🖥️ ap-southeast-1]
        
        Server1 --> Response[📄 Website Response]
        Server2 --> Response
        Server3 --> Response
        Server4 --> Response
        Response --> User
        
        style User fill:#4B9EDB,stroke:#232F3E,color:#fff
        style Route53 fill:#FF9900,stroke:#232F3E,color:#fff
        style Policy fill:#232F3E,stroke:#FF9900,color:#fff
        style Server1 fill:#3FB34F,stroke:#232F3E,color:#fff
        style Server2 fill:#3FB34F,stroke:#232F3E,color:#fff
        style Server3 fill:#3FB34F,stroke:#232F3E,color:#fff
        style Server4 fill:#3FB34F,stroke:#232F3E,color:#fff
    """

def vpc_tab():
    """Content for Amazon VPC tab"""
    st.markdown("## 🌐 Amazon Virtual Private Cloud (VPC)")
    st.markdown("*Provision a logically isolated section of the AWS Cloud*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Amazon VPC** enables you to launch AWS resources into a virtual network that you've defined. 
    This virtual network closely resembles a traditional network that you'd operate in your own data center, 
    with the benefits of using the scalable infrastructure of AWS.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # VPC Architecture Overview
    st.markdown("### 🏗️ VPC Architecture Overview")
    common.mermaid(create_vpc_architecture_mermaid(), height=500)
    
    # VPC Components
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 5\n**VPCs per Region**\n*Default Limit*")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 200\n**Subnets per VPC**\n*Maximum*")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 500\n**Security Groups**\n*per VPC*")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 200\n**Route Tables**\n*per VPC*")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive VPC Builder
    st.markdown("### 🛠️ Interactive VPC Builder")
    
    st.markdown('<div class="vpc-builder">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌐 VPC Configuration")
        vpc_name = st.text_input("VPC Name:", "MyApplication-VPC")
        vpc_cidr = st.selectbox("VPC CIDR Block:", [
            "10.0.0.0/16 (65,536 IPs)",
            "172.16.0.0/16 (65,536 IPs)", 
            "192.168.0.0/16 (65,536 IPs)",
            "10.0.0.0/24 (256 IPs)"
        ])
        
        enable_dns = st.checkbox("Enable DNS Hostnames", value=True)
        enable_dns_resolution = st.checkbox("Enable DNS Resolution", value=True)
    
    with col2:
        st.markdown("### 🏢 Availability Zones")
        selected_azs = st.multiselect("Select Availability Zones:", [
            "us-east-1a", "us-east-1b", "us-east-1c", "us-east-1d"
        ], default=["us-east-1a", "us-east-1b"])
        
        subnet_setup = st.selectbox("Subnet Setup Strategy:", [
            "Public + Private subnets in each AZ",
            "Public subnets only",
            "Private subnets only",
            "Custom configuration"
        ])
    
    # Advanced VPC Options
    st.markdown("### ⚙️ Advanced Options")
    col3, col4 = st.columns(2)
    
    with col3:
        internet_gateway = st.checkbox("Create Internet Gateway", value=True)
        nat_gateway = st.checkbox("Create NAT Gateway", value=True)
        vpn_gateway = st.checkbox("Create VPN Gateway", value=False)
    
    with col4:
        flow_logs = st.checkbox("Enable VPC Flow Logs", value=True)
        dedicated_tenancy = st.checkbox("Dedicated Tenancy", value=False)
        ipv6_support = st.checkbox("Enable IPv6 Support", value=False)
    
    if st.button("🚀 Create VPC Infrastructure", use_container_width=True):
        cidr_size = vpc_cidr.split('(')[0].strip()
        num_ips = int(vpc_cidr.split('(')[1].split()[0].replace(',', ''))
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ VPC Infrastructure Created Successfully!
        
        **VPC Details:**
        - **Name**: {vpc_name}
        - **CIDR Block**: {cidr_size}
        - **Available IP Addresses**: {num_ips:,}
        - **Availability Zones**: {len(selected_azs)}
        - **DNS Support**: {'✅ Enabled' if enable_dns else '❌ Disabled'}
        
        **Infrastructure Components:**
        - **Internet Gateway**: {'✅ Created' if internet_gateway else '❌ Not Created'}
        - **NAT Gateway**: {'✅ Created' if nat_gateway else '❌ Not Created'}
        - **VPN Gateway**: {'✅ Created' if vpn_gateway else '❌ Not Created'}
        - **Flow Logs**: {'✅ Enabled' if flow_logs else '❌ Disabled'}
        
        🛡️ **Security**: Default security group and NACLs configured
        📊 **Monitoring**: CloudWatch integration ready
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show subnet configuration
        st.markdown("### 📋 Subnet Configuration")
        subnets = []
        base_cidr_parts = cidr_size.split('/')[0].split('.')
        
        for i, az in enumerate(selected_azs):
            if "Public + Private" in subnet_setup:
                # Public subnet
                pub_cidr = f"{base_cidr_parts[0]}.{base_cidr_parts[1]}.{i*2+1}.0/24"
                subnets.append({
                    'Subnet Name': f'Public-{az}',
                    'CIDR': pub_cidr,
                    'AZ': az,
                    'Type': 'Public',
                    'Route Table': 'Public-RT (-> IGW)'
                })
                
                # Private subnet
                priv_cidr = f"{base_cidr_parts[0]}.{base_cidr_parts[1]}.{i*2+2}.0/24"
                subnets.append({
                    'Subnet Name': f'Private-{az}',
                    'CIDR': priv_cidr,
                    'AZ': az,
                    'Type': 'Private',
                    'Route Table': 'Private-RT (-> NAT)'
                })
        
        if subnets:
            df_subnets = pd.DataFrame(subnets)
            st.dataframe(df_subnets, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Security Groups vs NACLs
    st.markdown("### 🛡️ VPC Security: Security Groups vs Network ACLs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔒 Security Groups
        
        **Characteristics:**
        - **Stateful** firewall (return traffic automatically allowed)
        - **Instance level** protection
        - Only **allow rules** (implicit deny)
        - All rules are evaluated together
        
        **Use Cases:**
        - Application-specific access control
        - Database tier isolation
        - Web server protection
        - Microservices communication
        
        **Example Rules:**
        - Allow HTTP (80) from anywhere
        - Allow SSH (22) from specific IP
        - Allow MySQL (3306) from web tier SG
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🚧 Network ACLs (NACLs)
        
        **Characteristics:**
        - **Stateless** firewall (return traffic must be explicitly allowed)
        - **Subnet level** protection
        - Both **allow and deny** rules
        - Rules processed in numerical order
        
        **Use Cases:**
        - Subnet-level security
        - Compliance requirements
        - Defense in depth
        - Blocking specific IP ranges
        
        **Example Rules:**
        - DENY all from 192.168.1.0/24
        - ALLOW HTTP (80) inbound
        - ALLOW HTTP return traffic (32768-65535)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # VPC Connectivity Options
    st.markdown("### 🔗 VPC Connectivity Options")
    
    connectivity_options = {
        'Connection Type': [
            'Internet Gateway', 'NAT Gateway', 'VPC Peering', 
            'Transit Gateway', 'VPN Gateway', 'Direct Connect'
        ],
        'Purpose': [
            'Public internet access',
            'Outbound internet for private resources',
            'Connect two VPCs privately',
            'Hub for multiple VPC connections',
            'On-premises VPN connection',
            'Dedicated network connection'
        ],
        'Cost': ['Free', 'Hourly + Data', 'Free', 'Hourly + Data', 'Hourly', 'Monthly + Data'],
        'Bandwidth': ['Unlimited', '5-45 Gbps', 'Unlimited', 'Up to 50 Gbps', 'Up to 1.25 Gbps', 'Up to 100 Gbps']
    }
    
    df_connectivity = pd.DataFrame(connectivity_options)
    st.dataframe(df_connectivity, use_container_width=True)
    
    # Best Practices
    st.markdown("### 💡 VPC Design Best Practices")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Design Principles
    
    **Network Segmentation:**
    - Use **separate subnets** for different tiers (web, app, database)
    - Deploy across **multiple AZs** for high availability
    - Keep **private resources** in private subnets
    - Use **NAT Gateways** for outbound internet access from private subnets
    
    **Security Best Practices:**
    - Follow **principle of least privilege** for security groups
    - Use **NACLs for compliance** and additional protection
    - Enable **VPC Flow Logs** for monitoring and troubleshooting
    - Implement **defense in depth** with multiple security layers
    
    **IP Address Planning:**
    - Plan CIDR blocks to **avoid overlap** with on-premises networks
    - Leave room for **future growth** when sizing subnets
    - Use **RFC 1918** private address ranges
    - Reserve space for **peering connections**
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: VPC Creation and Configuration")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Create a complete VPC infrastructure with public and private subnets
import boto3
import time

def create_vpc_infrastructure(vpc_name, region, azs):
    """Create a complete VPC with public and private subnets across multiple AZs"""
    ec2 = boto3.client('ec2', region_name=region)
    
    try:
        # Create VPC
        vpc_response = ec2.create_vpc(
            CidrBlock='10.0.0.0/16',
            TagSpecifications=[
                {
                    'ResourceType': 'vpc',
                    'Tags': [
                        {'Key': 'Name', 'Value': vpc_name},
                        {'Key': 'Environment', 'Value': 'Production'},
                        {'Key': 'Application', 'Value': 'WebApp'}
                    ]
                }
            ]
        )
        
        vpc_id = vpc_response['Vpc']['VpcId']
        print(f"✅ VPC created: {vpc_id}")
        
        # Enable DNS hostnames and resolution
        ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={'Value': True})
        ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={'Value': True})
        print("✅ DNS settings configured")
        
        # Create Internet Gateway
        igw_response = ec2.create_internet_gateway(
            TagSpecifications=[
                {
                    'ResourceType': 'internet-gateway',
                    'Tags': [{'Key': 'Name', 'Value': f'{vpc_name}-IGW'}]
                }
            ]
        )
        igw_id = igw_response['InternetGateway']['InternetGatewayId']
        
        # Attach Internet Gateway to VPC
        ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
        print(f"✅ Internet Gateway created and attached: {igw_id}")
        
        # Create subnets
        subnets = {}
        nat_gateway_id = None
        
        for i, az in enumerate(azs):
            # Create public subnet
            public_subnet_response = ec2.create_subnet(
                VpcId=vpc_id,
                CidrBlock=f'10.0.{i*2+1}.0/24',
                AvailabilityZone=az,
                TagSpecifications=[
                    {
                        'ResourceType': 'subnet',
                        'Tags': [
                            {'Key': 'Name', 'Value': f'{vpc_name}-Public-{az}'},
                            {'Key': 'Type', 'Value': 'Public'}
                        ]
                    }
                ]
            )
            public_subnet_id = public_subnet_response['Subnet']['SubnetId']
            subnets[f'public_{az}'] = public_subnet_id
            
            # Enable auto-assign public IPs for public subnet
            ec2.modify_subnet_attribute(
                SubnetId=public_subnet_id,
                MapPublicIpOnLaunch={'Value': True}
            )
            
            # Create private subnet
            private_subnet_response = ec2.create_subnet(
                VpcId=vpc_id,
                CidrBlock=f'10.0.{i*2+2}.0/24',
                AvailabilityZone=az,
                TagSpecifications=[
                    {
                        'ResourceType': 'subnet',
                        'Tags': [
                            {'Key': 'Name', 'Value': f'{vpc_name}-Private-{az}'},
                            {'Key': 'Type', 'Value': 'Private'}
                        ]
                    }
                ]
            )
            private_subnet_id = private_subnet_response['Subnet']['SubnetId']
            subnets[f'private_{az}'] = private_subnet_id
            
            print(f"✅ Subnets created in {az}: {public_subnet_id}, {private_subnet_id}")
            
            # Create NAT Gateway in first public subnet only
            if i == 0:
                # Allocate Elastic IP for NAT Gateway
                eip_response = ec2.allocate_address(
                    Domain='vpc',
                    TagSpecifications=[
                        {
                            'ResourceType': 'elastic-ip',
                            'Tags': [{'Key': 'Name', 'Value': f'{vpc_name}-NAT-EIP'}]
                        }
                    ]
                )
                allocation_id = eip_response['AllocationId']
                
                # Create NAT Gateway
                nat_response = ec2.create_nat_gateway(
                    SubnetId=public_subnet_id,
                    AllocationId=allocation_id,
                    TagSpecifications=[
                        {
                            'ResourceType': 'nat-gateway',
                            'Tags': [{'Key': 'Name', 'Value': f'{vpc_name}-NAT'}]
                        }
                    ]
                )
                nat_gateway_id = nat_response['NatGateway']['NatGatewayId']
                print(f"✅ NAT Gateway created: {nat_gateway_id}")
        
        # Wait for NAT Gateway to be available
        if nat_gateway_id:
            print("⏳ Waiting for NAT Gateway to be available...")
            waiter = ec2.get_waiter('nat_gateway_available')
            waiter.wait(NatGatewayIds=[nat_gateway_id])
            print("✅ NAT Gateway is now available")
        
        # Create route tables
        # Public route table
        public_rt_response = ec2.create_route_table(
            VpcId=vpc_id,
            TagSpecifications=[
                {
                    'ResourceType': 'route-table',
                    'Tags': [{'Key': 'Name', 'Value': f'{vpc_name}-Public-RT'}]
                }
            ]
        )
        public_rt_id = public_rt_response['RouteTable']['RouteTableId']
        
        # Add route to Internet Gateway
        ec2.create_route(
            RouteTableId=public_rt_id,
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=igw_id
        )
        
        # Private route table
        private_rt_response = ec2.create_route_table(
            VpcId=vpc_id,
            TagSpecifications=[
                {
                    'ResourceType': 'route-table',
                    'Tags': [{'Key': 'Name', 'Value': f'{vpc_name}-Private-RT'}]
                }
            ]
        )
        private_rt_id = private_rt_response['RouteTable']['RouteTableId']
        
        # Add route to NAT Gateway
        if nat_gateway_id:
            ec2.create_route(
                RouteTableId=private_rt_id,
                DestinationCidrBlock='0.0.0.0/0',
                NatGatewayId=nat_gateway_id
            )
        
        # Associate subnets with route tables
        for az in azs:
            # Associate public subnet with public route table
            ec2.associate_route_table(
                RouteTableId=public_rt_id,
                SubnetId=subnets[f'public_{az}']
            )
            
            # Associate private subnet with private route table
            ec2.associate_route_table(
                RouteTableId=private_rt_id,
                SubnetId=subnets[f'private_{az}']
            )
        
        print("✅ Route tables created and associated")
        
        # Create security groups
        # Web tier security group
        web_sg_response = ec2.create_security_group(
            GroupName=f'{vpc_name}-Web-SG',
            Description='Security group for web servers',
            VpcId=vpc_id,
            TagSpecifications=[
                {
                    'ResourceType': 'security-group',
                    'Tags': [{'Key': 'Name', 'Value': f'{vpc_name}-Web-SG'}]
                }
            ]
        )
        web_sg_id = web_sg_response['GroupId']
        
        # Add rules to web security group
        ec2.authorize_security_group_ingress(
            GroupId=web_sg_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTP from anywhere'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 443,
                    'ToPort': 443,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'HTTPS from anywhere'}]
                }
            ]
        )
        
        # Database tier security group
        db_sg_response = ec2.create_security_group(
            GroupName=f'{vpc_name}-Database-SG',
            Description='Security group for database servers',
            VpcId=vpc_id,
            TagSpecifications=[
                {
                    'ResourceType': 'security-group',
                    'Tags': [{'Key': 'Name', 'Value': f'{vpc_name}-Database-SG'}]
                }
            ]
        )
        db_sg_id = db_sg_response['GroupId']
        
        # Add rules to database security group
        ec2.authorize_security_group_ingress(
            GroupId=db_sg_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 3306,
                    'ToPort': 3306,
                    'UserIdGroupPairs': [
                        {
                            'GroupId': web_sg_id,
                            'Description': 'MySQL access from web tier'
                        }
                    ]
                }
            ]
        )
        
        print("✅ Security groups created with appropriate rules")
        
        return {
            'vpc_id': vpc_id,
            'igw_id': igw_id,
            'nat_gateway_id': nat_gateway_id,
            'subnets': subnets,
            'route_tables': {
                'public': public_rt_id,
                'private': private_rt_id
            },
            'security_groups': {
                'web': web_sg_id,
                'database': db_sg_id
            }
        }
        
    except Exception as e:
        print(f"❌ Error creating VPC infrastructure: {e}")
        return None

# Create VPC infrastructure
vpc_config = create_vpc_infrastructure(
    vpc_name='MyApp-Production-VPC',
    region='us-east-1',
    azs=['us-east-1a', 'us-east-1b']
)

if vpc_config:
    print(f"🎉 VPC infrastructure created successfully!")
    print(f"VPC ID: {vpc_config['vpc_id']}")
    print(f"Public Subnets: {[v for k, v in vpc_config['subnets'].items() if 'public' in k]}")
    print(f"Private Subnets: {[v for k, v in vpc_config['subnets'].items() if 'private' in k]}")
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def privatelink_tab():
    """Content for AWS PrivateLink tab"""
    st.markdown("## 🔗 AWS PrivateLink")
    st.markdown("*Establish private connectivity between VPCs and AWS services*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **AWS PrivateLink** enables you to access AWS services privately from your VPC without requiring an internet gateway, 
    NAT device, VPN connection, or AWS Direct Connect connection. Traffic between your VPC and AWS services does not leave the Amazon network.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # PrivateLink Architecture
    st.markdown("### 🏗️ PrivateLink Architecture")
    common.mermaid(create_privatelink_architecture_mermaid(), height=500)
    
    # PrivateLink Benefits
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🛡️\n**Enhanced Security**\n*Private connections*")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### ⚡\n**Improved Performance**\n*Reduced latency*")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 💰\n**Cost Optimization**\n*No NAT charges*")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🌐\n**100+ Services**\n*Supported*")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive VPC Endpoint Builder
    st.markdown("### 🛠️ Interactive VPC Endpoint Configuration")
    
    st.markdown('<div class="vpc-builder">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Target Service")
        service_category = st.selectbox("Service Category:", [
            "Storage Services", "Database Services", "Compute Services", 
            "Analytics Services", "Security Services", "Management Tools"
        ])
        
        # Map services to categories
        service_mapping = {
            "Storage Services": ["Amazon S3", "Amazon EFS", "Amazon FSx"],
            "Database Services": ["Amazon DynamoDB", "Amazon RDS", "Amazon DocumentDB"],
            "Compute Services": ["Amazon ECS", "Amazon ECR", "AWS Lambda"],
            "Analytics Services": ["Amazon Kinesis", "Amazon Athena", "AWS Glue"],
            "Security Services": ["AWS Secrets Manager", "AWS Systems Manager", "AWS KMS"],
            "Management Tools": ["Amazon CloudWatch", "AWS CloudTrail", "AWS Config"]
        }
        
        target_service = st.selectbox("AWS Service:", service_mapping[service_category])
        endpoint_type = st.selectbox("Endpoint Type:", [
            "Gateway Endpoint (S3, DynamoDB)",
            "Interface Endpoint (Most Services)"
        ])
    
    with col2:
        st.markdown("### ⚙️ Configuration")
        vpc_selection = st.selectbox("Target VPC:", [
            "vpc-12345678 (Production-VPC)",
            "vpc-87654321 (Development-VPC)",
            "vpc-11111111 (Testing-VPC)"
        ])
        
        if "Interface" in endpoint_type:
            subnet_selection = st.multiselect("Subnets for Interface Endpoint:", [
                "subnet-11111111 (Private-1a)",
                "subnet-22222222 (Private-1b)", 
                "subnet-33333333 (Private-1c)"
            ], default=["subnet-11111111 (Private-1a)", "subnet-22222222 (Private-1b)"])
        else:
            route_table_selection = st.multiselect("Route Tables for Gateway Endpoint:", [
                "rtb-11111111 (Private-RT)", 
                "rtb-22222222 (Public-RT)"
            ], default=["rtb-11111111 (Private-RT)"])
    
    # Policy Configuration
    st.markdown("### 🔐 Access Policy Configuration")
    policy_type = st.selectbox("Access Policy:", [
        "Full Access (Default)",
        "Restricted Access (Custom)",
        "IP-based Restrictions",
        "Principal-based Restrictions"
    ])
    
    if policy_type != "Full Access (Default)":
        policy_details = st.text_area("Policy Details (JSON):", 
            """{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::my-private-bucket/*"
      ]
    }
  ]
}""", height=150)
    
    if st.button("🚀 Create VPC Endpoint", use_container_width=True):
        endpoint_id = f"vpce-{np.random.randint(100000000, 999999999):09d}"
        service_name = f"com.amazonaws.us-east-1.{target_service.lower().replace(' ', '').replace('amazon', '').replace('aws', '')}"
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ VPC Endpoint Created Successfully!
        
        **Endpoint Details:**
        - **Endpoint ID**: {endpoint_id}
        - **Service Name**: {service_name}
        - **Type**: {endpoint_type.split('(')[0].strip()}
        - **Target VPC**: {vpc_selection}
        - **Status**: Available
        
        **Configuration:**
        - **DNS Names**: Enabled
        - **Access Policy**: {policy_type}
        - **Route Table Updates**: {'✅ Applied' if 'Gateway' in endpoint_type else 'N/A'}
        - **Security Groups**: {'✅ Applied' if 'Interface' in endpoint_type else 'N/A'}
        
        🔒 **Security**: Traffic stays within AWS network
        💰 **Cost**: Hourly charges apply for Interface endpoints
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # VPC Endpoint Types Comparison
    st.markdown("### ⚖️ VPC Endpoint Types Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🚪 Gateway Endpoints
        
        **Supported Services:**
        - Amazon S3
        - Amazon DynamoDB
        
        **Characteristics:**
        - **Free of charge**
        - Route table-based routing
        - Highly available (horizontal scaling)
        - No security groups needed
        
        **Use Cases:**
        - S3 bucket access from private subnets
        - DynamoDB table operations
        - Cost-sensitive applications
        - High-throughput requirements
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔌 Interface Endpoints
        
        **Supported Services:**
        - 100+ AWS services
        - Third-party services (AWS Marketplace)
        
        **Characteristics:**
        - **Hourly charges** + data processing
        - ENI with private IP in subnet
        - DNS resolution support
        - Security groups apply
        
        **Use Cases:**
        - Most AWS services access
        - Fine-grained access control
        - DNS-based service discovery
        - Cross-service communication
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Supported Services
    st.markdown("### 🛠️ Popular Services Supporting PrivateLink")
    
    services_data = {
        'Service': [
            'Amazon S3', 'Amazon DynamoDB', 'Amazon ECS', 'Amazon ECR',
            'AWS Secrets Manager', 'Amazon CloudWatch', 'AWS Systems Manager', 'Amazon Kinesis'
        ],
        'Endpoint Type': [
            'Gateway', 'Gateway', 'Interface', 'Interface',
            'Interface', 'Interface', 'Interface', 'Interface'
        ],
        'Cost': [
            'Free', 'Free', 'Hourly + Data', 'Hourly + Data',
            'Hourly + Data', 'Hourly + Data', 'Hourly + Data', 'Hourly + Data'
        ],
        'Common Use Case': [
            'Private bucket access',
            'Database operations',
            'Container management',
            'Container image registry',
            'Secure credential access',
            'Private monitoring',
            'Instance management',
            'Stream processing'
        ]
    }
    
    df_services = pd.DataFrame(services_data)
    st.dataframe(df_services, use_container_width=True)
    
    # Security Benefits
    st.markdown("### 🛡️ Security Benefits & Use Cases")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🔒 Security Advantages
    
    **Network Isolation:**
    - Traffic **never leaves AWS network**
    - No exposure to public internet
    - **Reduced attack surface**
    - Compliance with strict security requirements
    
    **Access Control:**
    - **IAM policies** for service access
    - **VPC endpoint policies** for resource-level control
    - **Security groups** for interface endpoints
    - **Principal-based restrictions** available
    
    **Common Security Scenarios:**
    - **PCI DSS compliance** - keep payment data private
    - **HIPAA compliance** - protect health information
    - **Financial services** - regulatory data isolation
    - **Government workloads** - sensitive data protection
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Performance and Cost Analysis
    st.markdown("### 📊 Performance & Cost Comparison")
    
    # Cost comparison chart
    scenarios = ['Internet Gateway + NAT', 'PrivateLink Interface', 'PrivateLink Gateway']
    monthly_costs = [45.60, 21.90, 0.00]  # Example costs
    data_transfer_costs = [0.09, 0.01, 0.00]  # Per GB
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Monthly Base Cost ($)', 'Data Transfer Cost ($/GB)'),
    )
    
    fig.add_trace(
        go.Bar(x=scenarios, y=monthly_costs, name='Monthly Cost',
               marker_color=AWS_COLORS['primary']),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=scenarios, y=data_transfer_costs, name='Data Transfer',
               marker_color=AWS_COLORS['light_blue']),
        row=1, col=2
    )
    
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Creating and Managing VPC Endpoints")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Create and manage VPC endpoints for private service access
import boto3
import json

def create_s3_gateway_endpoint(vpc_id, route_table_ids, region='us-east-1'):
    """Create a gateway endpoint for Amazon S3"""
    ec2 = boto3.client('ec2', region_name=region)
    
    try:
        # Create S3 Gateway Endpoint
        response = ec2.create_vpc_endpoint(
            VpcId=vpc_id,
            ServiceName=f'com.amazonaws.{region}.s3',
            VpcEndpointType='Gateway',
            RouteTableIds=route_table_ids,
            PolicyDocument=json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": [
                            "s3:GetObject",
                            "s3:PutObject",
                            "s3:ListBucket"
                        ],
                        "Resource": [
                            "arn:aws:s3:::my-private-bucket",
                            "arn:aws:s3:::my-private-bucket/*"
                        ]
                    }
                ]
            })
        )
        
        endpoint_id = response['VpcEndpoint']['VpcEndpointId']
        print(f"✅ S3 Gateway Endpoint created: {endpoint_id}")
        return endpoint_id
        
    except Exception as e:
        print(f"❌ Error creating S3 endpoint: {e}")
        return None

def create_secrets_manager_interface_endpoint(vpc_id, subnet_ids, security_group_id, region='us-east-1'):
    """Create an interface endpoint for AWS Secrets Manager"""
    ec2 = boto3.client('ec2', region_name=region)
    
    try:
        # Create Secrets Manager Interface Endpoint
        response = ec2.create_vpc_endpoint(
            VpcId=vpc_id,
            ServiceName=f'com.amazonaws.{region}.secretsmanager',
            VpcEndpointType='Interface',
            SubnetIds=subnet_ids,
            SecurityGroupIds=[security_group_id],
            PrivateDnsEnabled=True,
            PolicyDocument=json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": [
                            "secretsmanager:GetSecretValue",
                            "secretsmanager:DescribeSecret"
                        ],
                        "Resource": "*",
                        "Condition": {
                            "StringEquals": {
                                "aws:PrincipalVpc": vpc_id
                            }
                        }
                    }
                ]
            })
        )
        
        endpoint_id = response['VpcEndpoint']['VpcEndpointId']
        print(f"✅ Secrets Manager Interface Endpoint created: {endpoint_id}")
        return endpoint_id
        
    except Exception as e:
        print(f"❌ Error creating Secrets Manager endpoint: {e}")
        return None

def create_endpoint_security_group(vpc_id, region='us-east-1'):
    """Create security group for interface endpoints"""
    ec2 = boto3.client('ec2', region_name=region)
    
    try:
        # Create security group
        response = ec2.create_security_group(
            GroupName='VPC-Endpoint-SG',
            Description='Security group for VPC Interface Endpoints',
            VpcId=vpc_id
        )
        
        sg_id = response['GroupId']
        
        # Add inbound rules for HTTPS traffic
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 443,
                    'ToPort': 443,
                    'IpRanges': [
                        {
                            'CidrIp': '10.0.0.0/16',
                            'Description': 'HTTPS from VPC'
                        }
                    ]
                }
            ]
        )
        
        print(f"✅ VPC Endpoint Security Group created: {sg_id}")
        return sg_id
        
    except Exception as e:
        print(f"❌ Error creating security group: {e}")
        return None

def monitor_vpc_endpoint_usage(endpoint_id, hours=24):
    """Monitor VPC endpoint usage and performance"""
    cloudwatch = boto3.client('cloudwatch')
    
    from datetime import datetime, timedelta
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    try:
        # Get packet count metrics
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/VPC',
            MetricName='PacketDropCount',
            Dimensions=[
                {
                    'Name': 'VpcId',
                    'Value': endpoint_id
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=['Sum']
        )
        
        if response['Datapoints']:
            total_packets = sum([dp['Sum'] for dp in response['Datapoints']])
            print(f"📊 VPC Endpoint Metrics ({hours}h):")
            print(f"  Total Packet Drops: {total_packets}")
            
            # Calculate hourly averages
            hourly_avg = total_packets / hours if hours > 0 else 0
            print(f"  Average Drops/Hour: {hourly_avg:.2f}")
            
            if total_packets == 0:
                print("✅ Excellent performance - no packet drops detected")
            elif total_packets < 100:
                print("✅ Good performance - minimal packet drops")
            else:
                print("⚠️  Consider investigating high packet drop rates")
        else:
            print("ℹ️  No metrics data available for this time period")
            
    except Exception as e:
        print(f"❌ Error retrieving metrics: {e}")

def test_private_connectivity(service_name, region='us-east-1'):
    """Test private connectivity to AWS service via VPC endpoint"""
    import requests
    import socket
    
    try:
        # Resolve service endpoint
        if service_name == 's3':
            endpoint_url = f"https://s3.{region}.amazonaws.com"
        elif service_name == 'secretsmanager':
            endpoint_url = f"https://secretsmanager.{region}.amazonaws.com"
        elif service_name == 'ec2':
            endpoint_url = f"https://ec2.{region}.amazonaws.com"
        else:
            endpoint_url = f"https://{service_name}.{region}.amazonaws.com"
        
        # Check DNS resolution
        hostname = endpoint_url.replace('https://', '').replace('http://', '')
        ip_address = socket.gethostbyname(hostname)
        print(f"🔍 DNS Resolution: {hostname} -> {ip_address}")
        
        # Check if IP is private (VPC endpoint) or public
        ip_parts = ip_address.split('.')
        if (ip_parts[0] == '10' or 
            (ip_parts[0] == '172' and 16 <= int(ip_parts[1]) <= 31) or
            (ip_parts[0] == '192' and ip_parts[1] == '168')):
            print("✅ Private IP detected - traffic using VPC endpoint")
        else:
            print("⚠️  Public IP detected - traffic may be using internet gateway")
        
        return ip_address
        
    except Exception as e:
        print(f"❌ Error testing connectivity: {e}")
        return None

# Example usage - Create complete VPC endpoint setup
def setup_private_aws_access():
    vpc_id = 'vpc-12345678'
    route_table_ids = ['rtb-11111111', 'rtb-22222222']
    subnet_ids = ['subnet-11111111', 'subnet-22222222']
    region = 'us-east-1'
    
    print("🚀 Setting up private AWS service access...")
    
    # Create security group for interface endpoints
    sg_id = create_endpoint_security_group(vpc_id, region)
    
    if sg_id:
        # Create S3 Gateway Endpoint (free)
        s3_endpoint = create_s3_gateway_endpoint(vpc_id, route_table_ids, region)
        
        # Create Secrets Manager Interface Endpoint
        secrets_endpoint = create_secrets_manager_interface_endpoint(
            vpc_id, subnet_ids, sg_id, region
        )
        
        if s3_endpoint and secrets_endpoint:
            print("✅ VPC endpoints created successfully!")
            
            # Test connectivity
            print("\n🧪 Testing private connectivity...")
            test_private_connectivity('s3', region)
            test_private_connectivity('secretsmanager', region)
            
            # Monitor usage
            print("\n📊 Monitoring endpoint usage...")
            monitor_vpc_endpoint_usage(s3_endpoint)
            
        return {
            's3_endpoint': s3_endpoint,
            'secrets_endpoint': secrets_endpoint,
            'security_group': sg_id
        }

# Run the setup
endpoints = setup_private_aws_access()
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def route53_tab():
    """Content for Amazon Route 53 tab"""
    st.markdown("## 🌍 Amazon Route 53")
    st.markdown("*Highly available and scalable cloud Domain Name System (DNS) web service*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Amazon Route 53** is a highly available and scalable cloud Domain Name System (DNS) web service. 
    It connects user requests to infrastructure running in AWS and can route users to infrastructure outside of AWS.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Route 53 DNS Flow
    st.markdown("### 🔄 Route 53 DNS Resolution Flow")
    common.mermaid(create_route53_dns_flow_mermaid(), height=450)
    
    # Route 53 Features
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 100%\n**SLA Uptime**\n*Availability*")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### <100ms\n**Query Response**\n*Typical latency*")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 300+\n**TLDs Supported**\n*Domain registration*")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 7\n**Routing Policies**\n*Advanced routing*")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive DNS Configuration
    st.markdown("### 🛠️ Interactive DNS Configuration Builder")
    
    st.markdown('<div class="vpc-builder">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌐 Domain Configuration")
        domain_name = st.text_input("Domain Name:", "mycompany.com")
        record_type = st.selectbox("DNS Record Type:", [
            "A - IPv4 Address", "AAAA - IPv6 Address", "CNAME - Canonical Name",
            "MX - Mail Exchange", "TXT - Text", "SRV - Service"
        ])
        
        if "A -" in record_type:
            record_value = st.text_input("IP Address:", "203.0.113.1")
        elif "CNAME" in record_type:
            record_value = st.text_input("Target Domain:", "www.example.com")
        else:
            record_value = st.text_input("Record Value:", "")
        
        ttl = st.selectbox("TTL (Time To Live):", [
            "300 seconds (5 minutes)",
            "3600 seconds (1 hour)",
            "86400 seconds (24 hours)",
            "Custom TTL"
        ])
    
    with col2:
        st.markdown("### 🎯 Routing Policy")
        routing_policy = st.selectbox("Routing Policy:", [
            "Simple - Single resource",
            "Weighted - Percentage-based",
            "Latency-based - Performance optimized",
            "Failover - Primary/Secondary",
            "Geolocation - Geographic routing",
            "Geoproximity - Distance + bias",
            "Multivalue - Multiple healthy resources"
        ])
        
        if "Weighted" in routing_policy:
            weight = st.slider("Weight (0-255):", 0, 255, 100)
        elif "Failover" in routing_policy:
            failover_type = st.selectbox("Failover Type:", ["Primary", "Secondary"])
        elif "Geolocation" in routing_policy:
            geo_location = st.selectbox("Location:", [
                "North America", "Europe", "Asia Pacific", "South America"
            ])
    
    # Health Check Configuration
    st.markdown("### 🏥 Health Check Configuration")
    col3, col4 = st.columns(2)
    
    with col3:
        enable_health_check = st.checkbox("Enable Health Checks", value=True)
        if enable_health_check:
            health_check_type = st.selectbox("Health Check Type:", [
                "HTTP", "HTTPS", "TCP", "Calculated"
            ])
            check_interval = st.selectbox("Check Interval:", [
                "30 seconds (Standard)", "10 seconds (Fast)"
            ])
    
    with col4:
        if enable_health_check:
            failure_threshold = st.slider("Failure Threshold:", 1, 10, 3)
            request_timeout = st.slider("Request Timeout (seconds):", 2, 60, 10)
            health_check_regions = st.slider("Health Check Regions:", 3, 18, 3)
    
    if st.button("🚀 Create DNS Record", use_container_width=True):
        record_id = f"Z{np.random.randint(100000000000, 999999999999):012d}"
        estimated_queries = np.random.randint(1000, 100000)
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ DNS Record Created Successfully!
        
        **Record Details:**
        - **Domain**: {domain_name}
        - **Record Type**: {record_type.split(' - ')[0]}
        - **Value**: {record_value if record_value else 'Not specified'}
        - **TTL**: {ttl.split(' ')[0]} seconds
        - **Hosted Zone ID**: {record_id}
        
        **Routing Configuration:**
        - **Policy**: {routing_policy.split(' - ')[0]}
        - **Health Checks**: {'✅ Enabled' if enable_health_check else '❌ Disabled'}
        - **Estimated Monthly Queries**: {estimated_queries:,}
        
        💰 **Estimated Cost**: ${(estimated_queries / 1000000) * 0.40:.2f}/month
        🌍 **Global Propagation**: 60 seconds or less
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Routing Policies Deep Dive
    st.markdown("### 🎯 Route 53 Routing Policies Explained")
    
    routing_policies_data = {
        'Policy': [
            'Simple', 'Weighted', 'Latency-based', 'Failover',
            'Geolocation', 'Geoproximity', 'Multivalue'
        ],
        'Use Case': [
            'Single web server',
            'A/B testing, gradual deployments',
            'Global applications with regional servers',
            'Active-passive disaster recovery',
            'Content localization, legal compliance',
            'Load balancing with geographic bias',
            'Load balancing with health checks'
        ],
        'Health Checks': [
            'Optional', 'Recommended', 'Recommended', 'Required',
            'Optional', 'Optional', 'Required'
        ],
        'Max Records': ['1', 'Multiple', 'Multiple', '2', 'Multiple', 'Multiple', '8']
    }
    
    df_policies = pd.DataFrame(routing_policies_data)
    st.dataframe(df_policies, use_container_width=True)
    
    # Routing Policy Examples
    st.markdown("### 📊 Routing Policy Performance Simulation")
    
    policy_selected = st.selectbox("Select Policy to Simulate:", [
        "Weighted Routing", "Latency-based Routing", "Failover Routing"
    ])
    
    if policy_selected == "Weighted Routing":
        st.markdown("### ⚖️ Weighted Routing Simulation")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            weight_us_east = st.slider("US-East-1 Weight:", 0, 100, 70)
        with col2:
            weight_us_west = st.slider("US-West-2 Weight:", 0, 100, 20)
        with col3:
            weight_eu_west = st.slider("EU-West-1 Weight:", 0, 100, 10)
        
        total_weight = weight_us_east + weight_us_west + weight_eu_west
        
        if total_weight > 0:
            # Calculate percentages
            pct_us_east = (weight_us_east / total_weight) * 100
            pct_us_west = (weight_us_west / total_weight) * 100
            pct_eu_west = (weight_eu_west / total_weight) * 100
            
            # Create pie chart
            fig = px.pie(
                values=[pct_us_east, pct_us_west, pct_eu_west],
                names=['US-East-1', 'US-West-2', 'EU-West-1'],
                title='Traffic Distribution by Weight',
                color_discrete_sequence=[AWS_COLORS['primary'], AWS_COLORS['light_blue'], AWS_COLORS['success']]
            )
            st.plotly_chart(fig, use_container_width=True)
    
    elif policy_selected == "Latency-based Routing":
        st.markdown("### ⚡ Latency-based Routing Simulation")
        
        # Sample latency data from different user locations
        locations = ['New York', 'London', 'Tokyo', 'Sydney', 'São Paulo']
        us_east_latency = [20, 80, 180, 200, 120]
        eu_west_latency = [90, 15, 250, 280, 150]
        ap_southeast_latency = [200, 280, 40, 60, 300]
        
        latency_data = pd.DataFrame({
            'User Location': locations,
            'US-East-1': us_east_latency,
            'EU-West-1': eu_west_latency,
            'AP-Southeast-1': ap_southeast_latency
        })
        
        # Determine optimal routing
        latency_data['Optimal Route'] = latency_data[['US-East-1', 'EU-West-1', 'AP-Southeast-1']].idxmin(axis=1)
        latency_data['Best Latency'] = latency_data[['US-East-1', 'EU-West-1', 'AP-Southeast-1']].min(axis=1)
        
        st.dataframe(latency_data, use_container_width=True)
        
        # Visualize latency comparison
        fig = px.bar(
            latency_data, 
            x='User Location', 
            y=['US-East-1', 'EU-West-1', 'AP-Southeast-1'],
            title='Latency Comparison by User Location (ms)',
            color_discrete_sequence=[AWS_COLORS['primary'], AWS_COLORS['light_blue'], AWS_COLORS['success']]
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Health Checks
    st.markdown("### 🏥 Route 53 Health Checks")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🩺 Health Check Types
        
        **HTTP/HTTPS Health Checks:**
        - Monitor web applications
        - Check specific URLs and response codes
        - Verify response content
        - Monitor SSL certificate validity
        
        **TCP Health Checks:**
        - Monitor non-HTTP services
        - Database connections
        - Custom application ports
        - Network connectivity verification
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📊 Health Check Features
        
        **Global Monitoring:**
        - Health checkers in 15+ AWS regions
        - Configurable check intervals (30s or 10s)
        - Failure threshold settings
        - SNS notifications on state changes
        
        **Calculated Health Checks:**
        - Combine multiple health checks
        - Boolean logic (AND, OR, NOT)
        - Complex application monitoring
        - Dependency-based routing
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Domain Registration
    st.markdown("### 🌐 Route 53 Domain Registration")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🏷️ Domain Registration Features
    
    **Supported TLDs:**
    - **Generic TLDs**: .com, .net, .org, .info, .biz
    - **Country Code TLDs**: .us, .uk, .de, .jp, .au
    - **New TLDs**: .app, .dev, .cloud, .tech, .online
    
    **Management Features:**
    - **Auto-renewal** with notification
    - **Domain privacy protection** included
    - **DNS management** integration
    - **Transfer lock** protection
    
    **Pricing Transparency:**
    - Clear upfront pricing
    - No hidden renewal fees
    - Volume discounts available
    - Competitive market rates
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Route 53 DNS Management")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Comprehensive Route 53 DNS management with health checks and routing policies
import boto3
import json
from datetime import datetime

def create_hosted_zone(domain_name, vpc_id=None):
    """Create a new hosted zone for domain management"""
    route53 = boto3.client('route53')
    
    try:
        # Create hosted zone configuration
        config = {
            'Name': domain_name,
            'CallerReference': str(datetime.utcnow().timestamp()),
            'HostedZoneConfig': {
                'Comment': f'Hosted zone for {domain_name}',
                'PrivateZone': vpc_id is not None
            }
        }
        
        # Add VPC association for private hosted zones
        if vpc_id:
            config['VPC'] = {
                'VPCRegion': 'us-east-1',
                'VPCId': vpc_id
            }
        
        response = route53.create_hosted_zone(**config)
        
        hosted_zone_id = response['HostedZone']['Id'].replace('/hostedzone/', '')
        name_servers = response['DelegationSet']['NameServers']
        
        print(f"✅ Hosted zone created: {hosted_zone_id}")
        print(f"Domain: {domain_name}")
        print(f"Name servers: {', '.join(name_servers)}")
        
        return hosted_zone_id, name_servers
        
    except Exception as e:
        print(f"❌ Error creating hosted zone: {e}")
        return None, None

def create_health_check(target_url, check_type='HTTPS'):
    """Create a health check for monitoring endpoint availability"""
    route53 = boto3.client('route53')
    
    try:
        # Parse URL components
        if '://' in target_url:
            protocol, rest = target_url.split('://', 1)
            if '/' in rest:
                fqdn, resource_path = rest.split('/', 1)
                resource_path = '/' + resource_path
            else:
                fqdn = rest
                resource_path = '/'
        else:
            fqdn = target_url
            resource_path = '/'
        
        # Default ports
        port = 443 if check_type == 'HTTPS' else 80 if check_type == 'HTTP' else 80
        
        health_check_config = {
            'Type': check_type,
            'ResourcePath': resource_path,
            'FullyQualifiedDomainName': fqdn,
            'Port': port,
            'RequestInterval': 30,  # Standard interval
            'FailureThreshold': 3,
            'MeasureLatency': True,
            'EnableSNI': True if check_type == 'HTTPS' else False
        }
        
        response = route53.create_health_check(
            CallerReference=str(datetime.utcnow().timestamp()),
            HealthCheckConfig=health_check_config,
            Tags=[
                {
                    'Key': 'Name',
                    'Value': f'Health check for {fqdn}'
                },
                {
                    'Key': 'Target', 
                    'Value': target_url
                }
            ]
        )
        
        health_check_id = response['HealthCheck']['Id']
        print(f"✅ Health check created: {health_check_id}")
        print(f"Target: {target_url}")
        print(f"Type: {check_type}, Interval: 30s, Threshold: 3")
        
        return health_check_id
        
    except Exception as e:
        print(f"❌ Error creating health check: {e}")
        return None

def create_weighted_routing_records(hosted_zone_id, domain, endpoints):
    """Create weighted routing records for load distribution"""
    route53 = boto3.client('route53')
    
    changes = []
    
    for endpoint in endpoints:
        record_name = endpoint['name']
        ip_address = endpoint['ip']
        weight = endpoint['weight']
        health_check_id = endpoint.get('health_check_id')
        
        change = {
            'Action': 'CREATE',
            'ResourceRecordSet': {
                'Name': domain,
                'Type': 'A',
                'SetIdentifier': record_name,
                'Weight': weight,
                'TTL': 300,
                'ResourceRecords': [{'Value': ip_address}]
            }
        }
        
        # Add health check if provided
        if health_check_id:
            change['ResourceRecordSet']['HealthCheckId'] = health_check_id
        
        changes.append(change)
    
    try:
        response = route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                'Comment': f'Weighted routing records for {domain}',
                'Changes': changes
            }
        )
        
        change_id = response['ChangeInfo']['Id']
        print(f"✅ Weighted routing records created")
        print(f"Change ID: {change_id}")
        print(f"Records: {len(changes)} weighted A records")
        
        return change_id
        
    except Exception as e:
        print(f"❌ Error creating weighted records: {e}")
        return None

def create_failover_routing(hosted_zone_id, domain, primary_ip, secondary_ip, 
                          primary_health_check, secondary_health_check):
    """Create failover routing with primary and secondary endpoints"""
    route53 = boto3.client('route53')
    
    changes = [
        # Primary record
        {
            'Action': 'CREATE',
            'ResourceRecordSet': {
                'Name': domain,
                'Type': 'A',
                'SetIdentifier': 'Primary',
                'Failover': 'PRIMARY',
                'TTL': 60,  # Short TTL for faster failover
                'ResourceRecords': [{'Value': primary_ip}],
                'HealthCheckId': primary_health_check
            }
        },
        # Secondary record
        {
            'Action': 'CREATE',
            'ResourceRecordSet': {
                'Name': domain,
                'Type': 'A',
                'SetIdentifier': 'Secondary',
                'Failover': 'SECONDARY',
                'TTL': 60,
                'ResourceRecords': [{'Value': secondary_ip}],
                'HealthCheckId': secondary_health_check
            }
        }
    ]
    
    try:
        response = route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                'Comment': f'Failover routing for {domain}',
                'Changes': changes
            }
        )
        
        change_id = response['ChangeInfo']['Id']
        print(f"✅ Failover routing configured")
        print(f"Primary: {primary_ip}")
        print(f"Secondary: {secondary_ip}")
        print(f"Change ID: {change_id}")
        
        return change_id
        
    except Exception as e:
        print(f"❌ Error creating failover routing: {e}")
        return None

def monitor_health_check_status(health_check_id):
    """Monitor health check status and get performance metrics"""
    route53 = boto3.client('route53')
    cloudwatch = boto3.client('cloudwatch')
    
    try:
        # Get health check status
        status_response = route53.get_health_check_status(
            HealthCheckId=health_check_id
        )
        
        print(f"🏥 Health Check Status: {health_check_id}")
        
        for checker in status_response['StatusOfHealthCheck'][:5]:  # Show first 5
            region = checker['Region']
            status = checker['Status']
            checked_time = checker['CheckedTime']
            
            print(f"  {region}: {status} (checked: {checked_time})")
        
        # Get CloudWatch metrics
        from datetime import timedelta
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        # Health check percentage healthy
        metrics_response = cloudwatch.get_metric_statistics(
            Namespace='AWS/Route53',
            MetricName='HealthCheckPercentHealthy',
            Dimensions=[
                {
                    'Name': 'HealthCheckId',
                    'Value': health_check_id
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,  # 5-minute periods
            Statistics=['Average']
        )
        
        if metrics_response['Datapoints']:
            latest_metric = sorted(metrics_response['Datapoints'], 
                                 key=lambda x: x['Timestamp'])[-1]
            health_percentage = latest_metric['Average']
            print(f"📊 Health Check Percentage: {health_percentage:.1f}%")
            
            if health_percentage >= 100:
                print("✅ Endpoint is healthy across all regions")
            elif health_percentage >= 80:
                print("⚠️  Endpoint experiencing some issues")
            else:
                print("❌ Endpoint is unhealthy - investigate immediately")
        
    except Exception as e:
        print(f"❌ Error monitoring health check: {e}")

# Example: Complete DNS setup with health checks and failover
def setup_production_dns():
    domain = 'myapp.com'
    
    print("🚀 Setting up production DNS configuration...")
    
    # Create hosted zone
    hosted_zone_id, name_servers = create_hosted_zone(domain)
    
    if hosted_zone_id:
        # Create health checks
        primary_health_check = create_health_check('https://primary.myapp.com/health')
        secondary_health_check = create_health_check('https://secondary.myapp.com/health')
        
        if primary_health_check and secondary_health_check:
            # Set up failover routing
            change_id = create_failover_routing(
                hosted_zone_id=hosted_zone_id,
                domain=domain,
                primary_ip='203.0.113.1',
                secondary_ip='203.0.113.2',
                primary_health_check=primary_health_check,
                secondary_health_check=secondary_health_check
            )
            
            if change_id:
                print("✅ Production DNS setup complete!")
                print(f"Update your domain registrar with these name servers:")
                for ns in name_servers:
                    print(f"  {ns}")
                
                # Monitor health checks
                print("\n🔍 Monitoring health check status...")
                monitor_health_check_status(primary_health_check)
                
                return {
                    'hosted_zone_id': hosted_zone_id,
                    'primary_health_check': primary_health_check,
                    'secondary_health_check': secondary_health_check,
                    'name_servers': name_servers
                }

# Run the production DNS setup
dns_config = setup_production_dns()
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
    st.markdown("# 🌐 AWS Networking Essentials")
    
    st.markdown("""<div class="info-box">
                Master AWS networking fundamentals including VPC design, private connectivity with PrivateLink, and DNS management with Route 53 to build secure, scalable, and high-performance cloud architectures.
                </div>""", unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "🌐 Amazon VPC", 
        "🔗 AWS PrivateLink", 
        "🌍 Amazon Route 53"
    ])
    
    with tab1:
        vpc_tab()
    
    with tab2:
        privatelink_tab()
    
    with tab3:
        route53_tab()
    
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
