
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import utils.common as common
import utils.authenticate as authenticate

# Page configuration
st.set_page_config(
    page_title="AWS IAM & Security Hub",
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
    'danger': '#D13212'
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
            background: linear-gradient(135deg, {AWS_COLORS['warning']} 0%, {AWS_COLORS['danger']} 100%);
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
        
        .policy-viewer {{
            background: white;
            border: 2px solid {AWS_COLORS['light_blue']};
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            font-family: 'Courier New', monospace;
        }}
        
        .permission-granted {{
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 10px;
            border-radius: 8px;
            margin: 5px 0;
        }}
        
        .permission-denied {{
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 10px;
            border-radius: 8px;
            margin: 5px 0;
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
            - 🔐 AWS Identity and Access Management - Core IAM concepts
            - 📜 IAM Policy Interpretation - Understanding JSON policies
            - 🛡️ Resource Policy Interpretation - Resource-based permissions
            - ⚙️ IAM Permissions Example - Real-world scenarios
            
            **Learning Objectives:**
            - Master IAM policies and permissions
            - Learn to interpret complex policy documents
            - Understand resource-based vs identity-based policies
            - Practice with interactive examples and troubleshooting
            """)

def create_iam_architecture_mermaid():
    """Create mermaid diagram for IAM architecture"""
    return """
    graph TB
        subgraph "AWS Account"
            subgraph "IAM Users"
                U1[👤 Developer]
                U2[👤 Admin]
                U3[👤 Auditor]
            end
            
            subgraph "IAM Groups"
                G1[👥 Developers]
                G2[👥 Administrators]
                G3[👥 Auditors]
            end
            
            subgraph "IAM Roles"
                R1[🎭 EC2-S3-Access]
                R2[🎭 Lambda-Execution]
                R3[🎭 Cross-Account]
            end
            
            subgraph "IAM Policies"
                P1[📜 S3-ReadWrite]
                P2[📜 EC2-FullAccess]
                P3[📜 ReadOnly-Access]
            end
            
            subgraph "AWS Resources"
                S3[🪣 S3 Buckets]
                EC2[💻 EC2 Instances]
                RDS[🗄️ RDS Databases]
            end
        end
        
        U1 --> G1
        U2 --> G2
        U3 --> G3
        
        G1 --> P1
        G2 --> P2
        G3 --> P3
        
        R1 --> P1
        R2 --> P1
        R3 --> P3
        
        P1 --> S3
        P2 --> EC2
        P3 --> RDS
        
        style U1 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style U2 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style U3 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style G1 fill:#FF9900,stroke:#232F3E,color:#fff
        style G2 fill:#FF9900,stroke:#232F3E,color:#fff
        style G3 fill:#FF9900,stroke:#232F3E,color:#fff
        style R1 fill:#3FB34F,stroke:#232F3E,color:#fff
        style R2 fill:#3FB34F,stroke:#232F3E,color:#fff
        style R3 fill:#3FB34F,stroke:#232F3E,color:#fff
        style P1 fill:#232F3E,stroke:#FF9900,color:#fff
        style P2 fill:#232F3E,stroke:#FF9900,color:#fff
        style P3 fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_policy_evaluation_mermaid():
    """Create mermaid diagram for policy evaluation"""
    return """
    graph TD
        A[🔍 Request Made] --> B{Identity-based<br/>Policy?}
        B -->|Yes| C[Check Allow]
        B -->|No| D[❌ Implicit Deny]
        
        C --> E{Explicit Deny?}
        E -->|Yes| F[❌ Explicit Deny]
        E -->|No| G{Resource-based<br/>Policy?}
        
        G -->|Yes| H[Check Resource Policy]
        G -->|No| I{Session Policy?}
        
        H --> J{Allow in<br/>Resource Policy?}
        J -->|Yes| K[✅ Allow]
        J -->|No| I
        
        I -->|Yes| L[Apply Session Limits]
        I -->|No| M{Permission<br/>Boundary?}
        
        L --> M
        M -->|Yes| N[Apply Boundary Limits]
        M -->|No| O[✅ Final Decision]
        
        N --> O
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style K fill:#3FB34F,stroke:#232F3E,color:#fff
        style O fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#D13212,stroke:#232F3E,color:#fff
        style F fill:#D13212,stroke:#232F3E,color:#fff
    """

def create_policy_types_mermaid():
    """Create mermaid diagram for policy types"""
    return """
    graph LR
        subgraph "Identity-based Policies"
            A[👤 User Policies]
            B[👥 Group Policies]
            C[🎭 Role Policies]
        end
        
        subgraph "Resource-based Policies"
            D[🪣 S3 Bucket Policies]
            E[🔑 KMS Key Policies]
            F[📊 CloudWatch Logs Policies]
        end
        
        subgraph "Permission Boundaries"
            G[🚧 Maximum Permissions]
            H[🔒 Guardrails]
        end
        
        subgraph "Session Policies"
            I[⏱️ Temporary Limits]
            J[🎫 STS Assume Role]
        end
        
        A --> K[AWS Resources]
        B --> K
        C --> K
        D --> K
        E --> K
        F --> K
        
        G --> L[Filter Permissions]
        H --> L
        I --> L
        J --> L
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style B fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#4B9EDB,stroke:#232F3E,color:#fff
        style D fill:#FF9900,stroke:#232F3E,color:#fff
        style E fill:#FF9900,stroke:#232F3E,color:#fff
        style F fill:#FF9900,stroke:#232F3E,color:#fff
        style K fill:#3FB34F,stroke:#232F3E,color:#fff
    """

def aws_iam_tab():
    """Content for AWS Identity and Access Management tab"""
    st.markdown("## 🔐 AWS Identity and Access Management")
    st.markdown("*Securely manage access to AWS services and resources*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **AWS Identity and Access Management (IAM)** enables you to manage access to AWS services and resources securely. 
    Using IAM, you can create and manage AWS users and groups, and use permissions to allow and deny their access to AWS resources.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # IAM Core Components
    st.markdown("### 🏗️ IAM Architecture Overview")
    common.mermaid(create_iam_architecture_mermaid(), height=600)
    
    # IAM Components Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 👤\n**Users**\nIndividual Identities")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 👥\n**Groups**\nCollection of Users")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🎭\n**Roles**\nAssumed Identities")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 📜\n**Policies**\nPermission Documents")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive IAM Component Builder
    st.markdown("### 🛠️ Interactive IAM Setup Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👤 User Configuration")
        user_name = st.text_input("IAM User Name:", "john-developer")
        user_type = st.selectbox("User Type:", [
            "Developer", "Administrator", "Read-Only User", "Service Account"
        ])
        
        access_type = st.multiselect("Access Type:", [
            "AWS Management Console", "Programmatic Access (CLI/SDK)", "Both"
        ], default=["AWS Management Console"])
        
        mfa_required = st.checkbox("Require MFA", value=True)
    
    with col2:
        st.markdown("### 👥 Group Assignment")
        available_groups = ["Developers", "Administrators", "Auditors", "PowerUsers"]
        selected_groups = st.multiselect("Assign to Groups:", available_groups, default=["Developers"])
        
        st.markdown("### 📜 Direct Policy Attachment")
        direct_policies = st.multiselect("Attach Policies Directly:", [
            "AmazonS3ReadOnlyAccess", "AmazonEC2ReadOnlyAccess", "PowerUserAccess"
        ])
    
    if st.button("🚀 Create IAM User", use_container_width=True):
        st.markdown('<div class="security-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ IAM User Created Successfully!
        
        **User Details:**
        - **Username**: {user_name}
        - **Type**: {user_type}
        - **Access**: {', '.join(access_type)}
        - **MFA Required**: {'✅ Yes' if mfa_required else '❌ No'}
        
        **Group Memberships:**
        {chr(10).join([f"- {group}" for group in selected_groups])}
        
        **Direct Policies:**
        {chr(10).join([f"- {policy}" for policy in direct_policies]) if direct_policies else "- None"}
        
        🔐 **Security Recommendation**: {'Strong security posture with MFA!' if mfa_required else 'Consider enabling MFA for better security.'}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # IAM Best Practices
    st.markdown("### 💡 IAM Best Practices")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛡️ Security Best Practices
        - **Enable MFA** for all users
        - **Use strong password policies**
        - **Rotate access keys regularly**
        - **Remove unused users and roles**
        - **Monitor with CloudTrail**
        - **Use IAM Access Analyzer**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 👥 User Management
        - **Create individual users** (no sharing)
        - **Use groups** for common permissions
        - **Apply least privilege principle**
        - **Use roles for applications**
        - **Implement permission boundaries**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔑 Access Management
        - **Use roles instead of users** for AWS services
        - **Implement cross-account roles** for access
        - **Use temporary credentials** when possible
        - **Regularly review permissions**
        - **Use AWS Organizations** for multiple accounts
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📊 Monitoring & Compliance
        - **Enable AWS CloudTrail**
        - **Use AWS Config** for compliance
        - **Monitor with CloudWatch**
        - **Regular access reviews**
        - **Automate compliance checks**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # IAM Policy Types Overview
    st.markdown("### 📋 IAM Policy Types")
    common.mermaid(create_policy_types_mermaid(), height=400)
    
    # Interactive Permission Calculator
    st.markdown("### 🧮 Permission Effectiveness Calculator")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Identity-based Policy**")
        identity_allow = st.selectbox("Identity Policy:", ["Allow", "Deny", "Not Specified"], key="identity")
        
    with col2:
        st.markdown("**Resource-based Policy**")
        resource_allow = st.selectbox("Resource Policy:", ["Allow", "Deny", "Not Specified"], key="resource")
        
    with col3:
        st.markdown("**Permission Boundary**")
        boundary_allow = st.selectbox("Permission Boundary:", ["Allow", "Deny", "Not Specified"], key="boundary")
    
    if st.button("🔍 Calculate Final Permission"):
        # IAM evaluation logic
        if identity_allow == "Deny" or resource_allow == "Deny" or boundary_allow == "Deny":
            result = "❌ DENIED"
            reason = "Explicit deny always wins"
            color_class = "permission-denied"
        elif identity_allow == "Allow" or resource_allow == "Allow":
            if boundary_allow == "Allow" or boundary_allow == "Not Specified":
                result = "✅ ALLOWED"
                reason = "Permission granted by policy"
                color_class = "permission-granted"
            else:
                result = "❌ DENIED"
                reason = "Permission boundary restricts access"
                color_class = "permission-denied"
        else:
            result = "❌ DENIED"
            reason = "No explicit allow (implicit deny)"
            color_class = "permission-denied"
        
        st.markdown(f'<div class="{color_class}">', unsafe_allow_html=True)
        st.markdown(f"""
        ### {result}
        **Reason**: {reason}
        
        **Evaluation Order**:
        1. Check for explicit deny → {identity_allow}, {resource_allow}, {boundary_allow}
        2. Check for explicit allow → {identity_allow}, {resource_allow}
        3. Apply permission boundaries → {boundary_allow}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: IAM User and Role Management")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Create and manage IAM users, groups, and roles
import boto3
import json

def create_developer_setup():
    """Create a complete developer IAM setup"""
    iam = boto3.client('iam')
    
    # 1. Create IAM Group for Developers
    try:
        group_response = iam.create_group(
            GroupName='Developers',
            Path='/teams/'
        )
        print("✅ Created group: Developers")
    except iam.exceptions.EntityAlreadyExistsException:
        print("ℹ️  Group 'Developers' already exists")
    
    # 2. Create and attach group policy
    developer_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject"
                ],
                "Resource": [
                    "arn:aws:s3:::dev-*/*",
                    "arn:aws:s3:::staging-*/*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "ec2:DescribeInstances",
                    "ec2:DescribeImages",
                    "ec2:DescribeKeyPairs"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Deny",
                "Action": [
                    "ec2:TerminateInstances",
                    "ec2:StopInstances"
                ],
                "Resource": "*",
                "Condition": {
                    "StringNotEquals": {
                        "ec2:ResourceTag/Environment": ["dev", "staging"]
                    }
                }
            }
        ]
    }
    
    try:
        iam.put_group_policy(
            GroupName='Developers',
            PolicyName='DeveloperAccess',
            PolicyDocument=json.dumps(developer_policy)
        )
        print("✅ Attached policy to Developers group")
    except Exception as e:
        print(f"❌ Error attaching policy: {e}")
    
    # 3. Create IAM User
    username = 'john-developer'
    try:
        user_response = iam.create_user(
            UserName=username,
            Path='/developers/',
            Tags=[
                {'Key': 'Department', 'Value': 'Engineering'},
                {'Key': 'Team', 'Value': 'Backend'},
                {'Key': 'Environment', 'Value': 'Development'}
            ]
        )
        print(f"✅ Created user: {username}")
    except iam.exceptions.EntityAlreadyExistsException:
        print(f"ℹ️  User '{username}' already exists")
    
    # 4. Add user to group
    try:
        iam.add_user_to_group(
            GroupName='Developers',
            UserName=username
        )
        print(f"✅ Added {username} to Developers group")
    except Exception as e:
        print(f"❌ Error adding user to group: {e}")
    
    # 5. Create access keys for programmatic access
    try:
        access_key_response = iam.create_access_key(UserName=username)
        access_key = access_key_response['AccessKey']
        
        print(f"🔑 Access Key Created:")
        print(f"   Access Key ID: {access_key['AccessKeyId']}")
        print(f"   Secret Access Key: {access_key['SecretAccessKey'][:8]}...")
        print("   ⚠️  Store these credentials securely!")
        
    except Exception as e:
        print(f"❌ Error creating access key: {e}")
    
    return username

def create_application_role():
    """Create IAM role for EC2 instances"""
    iam = boto3.client('iam')
    
    # Trust policy - who can assume this role
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "ec2.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # Permission policy - what the role can do
    permissions_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject"
                ],
                "Resource": "arn:aws:s3:::app-data-bucket/*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem"
                ],
                "Resource": "arn:aws:dynamodb:*:*:table/AppDataTable"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:*"
            }
        ]
    }
    
    role_name = 'EC2-App-Role'
    
    try:
        # Create the role
        role_response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for EC2 instances to access S3 and DynamoDB',
            Tags=[
                {'Key': 'Purpose', 'Value': 'Application'},
                {'Key': 'Environment', 'Value': 'Production'}
            ]
        )
        print(f"✅ Created role: {role_name}")
        
        # Attach the permissions policy
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName='AppPermissions',
            PolicyDocument=json.dumps(permissions_policy)
        )
        print(f"✅ Attached permissions policy to {role_name}")
        
        # Create instance profile
        iam.create_instance_profile(InstanceProfileName=role_name)
        iam.add_role_to_instance_profile(
            InstanceProfileName=role_name,
            RoleName=role_name
        )
        print(f"✅ Created instance profile for {role_name}")
        
    except Exception as e:
        print(f"❌ Error creating role: {e}")
    
    return role_name

def audit_iam_permissions(username):
    """Audit IAM user permissions"""
    iam = boto3.client('iam')
    
    print(f"🔍 Auditing permissions for user: {username}")
    print("=" * 50)
    
    try:
        # Get user details
        user = iam.get_user(UserName=username)
        print(f"User ARN: {user['User']['Arn']}")
        print(f"Created: {user['User']['CreateDate']}")
        
        # List user's groups
        groups = iam.get_groups_for_user(UserName=username)
        print(f"\n👥 Group Memberships:")
        for group in groups['Groups']:
            print(f"  - {group['GroupName']}")
            
            # Get group policies
            group_policies = iam.list_group_policies(GroupName=group['GroupName'])
            for policy_name in group_policies['PolicyNames']:
                print(f"    └── Policy: {policy_name}")
        
        # List attached managed policies
        attached_policies = iam.list_attached_user_policies(UserName=username)
        print(f"\n📜 Attached Managed Policies:")
        for policy in attached_policies['AttachedPolicies']:
            print(f"  - {policy['PolicyName']} ({policy['PolicyArn']})")
        
        # List inline policies
        inline_policies = iam.list_user_policies(UserName=username)
        print(f"\n📝 Inline Policies:")
        for policy_name in inline_policies['PolicyNames']:
            print(f"  - {policy_name}")
        
        # List access keys
        access_keys = iam.list_access_keys(UserName=username)
        print(f"\n🔑 Access Keys:")
        for key in access_keys['AccessKeyMetadata']:
            print(f"  - {key['AccessKeyId']} (Status: {key['Status']})")
            print(f"    Created: {key['CreateDate']}")
        
    except Exception as e:
        print(f"❌ Error auditing user: {e}")

# Example usage
print("🚀 Setting up IAM infrastructure...")

# Create developer setup
username = create_developer_setup()

# Create application role
role_name = create_application_role()

# Audit permissions
if username:
    audit_iam_permissions(username)
    
print("\n✅ IAM setup completed!")
print("🔐 Remember to:")
print("  - Enable MFA for all users")
print("  - Regularly rotate access keys")
print("  - Review permissions quarterly")
print("  - Monitor usage with CloudTrail")
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def iam_policy_interpretation_tab():
    """Content for IAM Policy Interpretation tab"""
    st.markdown("## 📜 IAM Policy Interpretation")
    st.markdown("*Understanding and analyzing IAM policy documents*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **IAM Policy Interpretation** is crucial for understanding how permissions are granted or denied in AWS. 
    Policies are JSON documents that define permissions using Effect, Action, Resource, and Condition elements.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Policy Evaluation Flow
    st.markdown("### 🔄 Policy Evaluation Process")
    common.mermaid(create_policy_evaluation_mermaid(), height=600)
    
    # Interactive Policy Builder and Analyzer
    st.markdown("### 🛠️ Interactive Policy Analyzer")
    
    # Sample policies for analysis
    sample_policies = {
        "S3 Developer Access": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject"
                    ],
                    "Resource": "arn:aws:s3:::dev-bucket/*"
                },
                {
                    "Effect": "Allow",
                    "Action": "s3:ListBucket",
                    "Resource": "arn:aws:s3:::dev-bucket"
                }
            ]
        },
        "EC2 Instance Management": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "ec2:RunInstances",
                        "ec2:TerminateInstances",
                        "ec2:StopInstances",
                        "ec2:StartInstances"
                    ],
                    "Resource": "*",
                    "Condition": {
                        "StringEquals": {
                            "ec2:InstanceType": ["t2.micro", "t3.micro"]
                        }
                    }
                }
            ]
        },
        "Database Read-Only": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:GetItem",
                        "dynamodb:BatchGetItem",
                        "dynamodb:Query",
                        "dynamodb:Scan"
                    ],
                    "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/UserData"
                },
                {
                    "Effect": "Deny",
                    "Action": [
                        "dynamodb:PutItem",
                        "dynamodb:UpdateItem",
                        "dynamodb:DeleteItem"
                    ],
                    "Resource": "*"
                }
            ]
        }
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown("### 📋 Policy Selection")
        selected_policy_name = st.selectbox("Choose Policy to Analyze:", list(sample_policies.keys()))
        
        # Policy analysis options
        st.markdown("### 🔍 Analysis Options")
        analyze_effects = st.checkbox("Analyze Effects", value=True)
        analyze_actions = st.checkbox("Analyze Actions", value=True)
        analyze_resources = st.checkbox("Analyze Resources", value=True)
        analyze_conditions = st.checkbox("Analyze Conditions", value=True)
        
        # Test scenario
        st.markdown("### 🧪 Test Scenario")
        test_action = st.text_input("Test Action:", "s3:GetObject")
        test_resource = st.text_input("Test Resource:", "arn:aws:s3:::dev-bucket/file.txt")
    
    with col1:
        st.markdown("### 📄 Policy Document")
        selected_policy = sample_policies[selected_policy_name]
        
        st.markdown('<div class="policy-viewer">', unsafe_allow_html=True)
        st.json(selected_policy)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Analyze button
    if st.button("🔍 Analyze Policy", use_container_width=True):
        analysis_results = analyze_policy(selected_policy, {
            'effects': analyze_effects,
            'actions': analyze_actions, 
            'resources': analyze_resources,
            'conditions': analyze_conditions
        }, test_action, test_resource)
        
        display_policy_analysis(analysis_results)
    
    # Policy Component Breakdown
    st.markdown("### 🧩 Policy Components Explained")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📋 Core Elements
        
        **Version**: Policy language version
        - Usually "2012-10-17"
        - Required field
        
        **Statement**: Array of permission statements
        - Can be single object or array
        - Each statement evaluated independently
        
        **Sid**: Statement identifier (optional)
        - Human-readable identifier
        - Useful for policy management
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚖️ Effect & Action
        
        **Effect**: Allow or Deny
        - "Allow" - grants permission
        - "Deny" - explicitly denies permission
        - Deny always overrides Allow
        
        **Action**: What operations are allowed/denied
        - Service prefix (e.g., s3:, ec2:)
        - Specific actions or wildcards
        - Can be single string or array
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 Resource & Principal
        
        **Resource**: What AWS resources are affected
        - ARN format required
        - Supports wildcards (*)
        - Can be single string or array
        
        **Principal**: Who the statement applies to
        - Used in resource-based policies
        - Can be AWS accounts, users, roles
        - Not used in identity-based policies
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔧 Condition
        
        **Condition**: When the statement applies
        - Optional but powerful
        - Uses condition operators
        - Can check various context keys
        
        **Common Operators**:
        - StringEquals, StringLike
        - NumericEquals, NumericLessThan
        - DateGreaterThan, IpAddress
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Common Policy Patterns
    st.markdown("### 🎨 Common Policy Patterns")
    
    patterns_data = {
        'Pattern': ['Read-Only Access', 'Time-Based Access', 'IP Restriction', 'MFA Required', 'Tag-Based Access'],
        'Use Case': [
            'Auditors, reporting users',
            'Business hours only',
            'Office network only', 
            'Administrative actions',
            'Environment-based access'
        ],
        'Key Condition': [
            'Only Get/List actions',
            'DateGreaterThan/LessThan',
            'IpAddress condition',
            'aws:MultiFactorAuthPresent',
            'aws:ResourceTag/Environment'
        ],
        'Security Level': ['Low', 'Medium', 'High', 'High', 'Medium']
    }
    
    df_patterns = pd.DataFrame(patterns_data)
    st.dataframe(df_patterns, use_container_width=True)
    
    # Policy Testing Simulator
    st.markdown("### 🧪 Policy Testing Simulator")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Test Parameters**")
        sim_user = st.text_input("User:", "arn:aws:iam::123456789012:user/developer")
        sim_action = st.text_input("Action:", "s3:GetObject") 
        sim_resource = st.text_input("Resource:", "arn:aws:s3:::my-bucket/file.txt")
    
    with col2:
        st.markdown("**Context**")
        sim_time = st.selectbox("Time:", ["Business Hours", "After Hours", "Weekend"])
        sim_ip = st.text_input("Source IP:", "192.168.1.100")
        sim_mfa = st.selectbox("MFA Status:", ["Present", "Not Present"])
    
    with col3:
        st.markdown("**Environment**")
        sim_region = st.selectbox("Region:", ["us-east-1", "us-west-2", "eu-west-1"])
        sim_instance_type = st.text_input("Instance Type:", "t3.micro")
        
    if st.button("🎯 Simulate Policy Evaluation"):
        # Simulate policy evaluation logic
        result = simulate_policy_evaluation(selected_policy, {
            'user': sim_user,
            'action': sim_action,
            'resource': sim_resource,
            'time': sim_time,
            'ip': sim_ip,
            'mfa': sim_mfa,
            'region': sim_region,
            'instance_type': sim_instance_type
        })
        
        display_simulation_result(result)
    
    # Code Example
    st.markdown("### 💻 Code Example: Policy Analysis and Testing")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Policy analysis and testing utilities
import json
import re
from datetime import datetime

def analyze_iam_policy(policy_document):
    """Comprehensive IAM policy analysis"""
    
    if isinstance(policy_document, str):
        policy = json.loads(policy_document)
    else:
        policy = policy_document
    
    analysis = {
        'version': policy.get('Version'),
        'statement_count': 0,
        'allow_statements': 0,
        'deny_statements': 0,
        'actions': set(),
        'resources': set(),
        'conditions': [],
        'security_issues': [],
        'recommendations': []
    }
    
    statements = policy.get('Statement', [])
    if not isinstance(statements, list):
        statements = [statements]
    
    analysis['statement_count'] = len(statements)
    
    for idx, statement in enumerate(statements):
        effect = statement.get('Effect', 'Allow')
        
        if effect == 'Allow':
            analysis['allow_statements'] += 1
        elif effect == 'Deny':
            analysis['deny_statements'] += 1
        
        # Analyze actions
        actions = statement.get('Action', [])
        if isinstance(actions, str):
            actions = [actions]
        
        for action in actions:
            analysis['actions'].add(action)
            
            # Check for overly permissive actions
            if action == '*':
                analysis['security_issues'].append(f"Statement {idx}: Wildcard action (*) grants all permissions")
            elif action.endswith(':*'):
                service = action.split(':')[0]
                analysis['security_issues'].append(f"Statement {idx}: Full service access ({service}:*)")
        
        # Analyze resources
        resources = statement.get('Resource', [])
        if isinstance(resources, str):
            resources = [resources]
            
        for resource in resources:
            analysis['resources'].add(resource)
            
            # Check for overly permissive resources
            if resource == '*':
                analysis['security_issues'].append(f"Statement {idx}: Wildcard resource (*) affects all resources")
        
        # Analyze conditions
        conditions = statement.get('Condition', {})
        if conditions:
            analysis['conditions'].append({
                'statement': idx,
                'conditions': conditions
            })
        else:
            if effect == 'Allow' and ('*' in str(actions) or '*' in str(resources)):
                analysis['security_issues'].append(f"Statement {idx}: No conditions on broad permissions")
    
    # Generate recommendations
    if analysis['allow_statements'] > 0 and analysis['deny_statements'] == 0:
        analysis['recommendations'].append("Consider adding explicit deny statements for security")
    
    if not analysis['conditions']:
        analysis['recommendations'].append("Add conditions to restrict when/where policies apply")
    
    if len(analysis['actions']) > 20:
        analysis['recommendations'].append("Policy grants many actions - consider splitting into multiple policies")
    
    return analysis

def test_policy_permission(policy, test_request):
    """Test if a policy would allow a specific request"""
    
    if isinstance(policy, str):
        policy = json.loads(policy)
    
    statements = policy.get('Statement', [])
    if not isinstance(statements, list):
        statements = [statements]
    
    # IAM evaluation logic: Explicit deny wins, then look for allow
    has_explicit_deny = False
    has_allow = False
    
    for statement in statements:
        effect = statement.get('Effect', 'Allow')
        
        # Check if statement applies to this request
        if statement_applies(statement, test_request):
            if effect == 'Deny':
                has_explicit_deny = True
                return {
                    'allowed': False,
                    'reason': 'Explicit deny in policy',
                    'statement': statement
                }
            elif effect == 'Allow':
                has_allow = True
    
    if has_allow:
        return {
            'allowed': True,
            'reason': 'Allowed by policy statement',
            'statement': None
        }
    else:
        return {
            'allowed': False,
            'reason': 'No matching allow statement (implicit deny)',
            'statement': None
        }

def statement_applies(statement, test_request):
    """Check if a policy statement applies to a test request"""
    
    # Check actions
    actions = statement.get('Action', [])
    if isinstance(actions, str):
        actions = [actions]
    
    action_matches = False
    for action in actions:
        if action == '*' or action == test_request['action']:
            action_matches = True
            break
        elif '*' in action:
            # Handle wildcard matching
            pattern = action.replace('*', '.*')
            if re.match(pattern, test_request['action']):
                action_matches = True
                break
    
    if not action_matches:
        return False
    
    # Check resources
    resources = statement.get('Resource', [])
    if isinstance(resources, str):
        resources = [resources]
    
    resource_matches = False
    for resource in resources:
        if resource == '*' or resource == test_request['resource']:
            resource_matches = True
            break
        elif '*' in resource:
            # Handle wildcard matching
            pattern = resource.replace('*', '.*')
            if re.match(pattern, test_request['resource']):
                resource_matches = True
                break
    
    if not resource_matches:
        return False
    
    # Check conditions (simplified)
    conditions = statement.get('Condition', {})
    if conditions:
        # This is a simplified condition check
        # Real AWS evaluation is much more complex
        for condition_type, condition_values in conditions.items():
            if not evaluate_condition(condition_type, condition_values, test_request):
                return False
    
    return True

def evaluate_condition(condition_type, condition_values, test_request):
    """Simplified condition evaluation"""
    
    context = test_request.get('context', {})
    
    if condition_type == 'StringEquals':
        for key, expected_values in condition_values.items():
            if isinstance(expected_values, str):
                expected_values = [expected_values]
            
            actual_value = context.get(key)
            if actual_value not in expected_values:
                return False
    
    elif condition_type == 'IpAddress':
        source_ip = context.get('aws:SourceIp')
        allowed_ips = condition_values.get('aws:SourceIp', [])
        
        if isinstance(allowed_ips, str):
            allowed_ips = [allowed_ips]
        
        # Simplified IP checking (in reality, would need CIDR matching)
        if source_ip not in allowed_ips:
            return False
    
    elif condition_type == 'Bool':
        for key, expected_value in condition_values.items():
            actual_value = context.get(key)
            if str(actual_value).lower() != str(expected_value).lower():
                return False
    
    return True

def generate_policy_report(policy_document):
    """Generate comprehensive policy analysis report"""
    
    print("🔍 IAM Policy Analysis Report")
    print("=" * 50)
    
    analysis = analyze_iam_policy(policy_document)
    
    print(f"Policy Version: {analysis['version']}")
    print(f"Total Statements: {analysis['statement_count']}")
    print(f"Allow Statements: {analysis['allow_statements']}")
    print(f"Deny Statements: {analysis['deny_statements']}")
    print(f"Unique Actions: {len(analysis['actions'])}")
    print(f"Unique Resources: {len(analysis['resources'])}")
    
    print(f"\n📋 Actions Granted:")
    for action in sorted(analysis['actions']):
        print(f"  - {action}")
    
    print(f"\n🎯 Resources Affected:")
    for resource in sorted(analysis['resources']):
        print(f"  - {resource}")
    
    if analysis['conditions']:
        print(f"\n🔧 Conditions Applied:")
        for condition in analysis['conditions']:
            print(f"  Statement {condition['statement']}: {condition['conditions']}")
    
    if analysis['security_issues']:
        print(f"\n⚠️  Security Issues Found:")
        for issue in analysis['security_issues']:
            print(f"  - {issue}")
    
    if analysis['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in analysis['recommendations']:
            print(f"  - {rec}")
    
    return analysis

# Example usage
sample_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::my-bucket/*",
            "Condition": {
                "IpAddress": {
                    "aws:SourceIp": "192.168.1.0/24"
                }
            }
        }
    ]
}

# Analyze the policy
analysis = generate_policy_report(sample_policy)

# Test a specific request
test_request = {
    'action': 's3:GetObject',
    'resource': 'arn:aws:s3:::my-bucket/file.txt',
    'context': {
        'aws:SourceIp': '192.168.1.100'
    }
}

result = test_policy_permission(sample_policy, test_request)
print(f"\n🧪 Permission Test Result:")
print(f"Allowed: {result['allowed']}")
print(f"Reason: {result['reason']}")
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def analyze_policy(policy, options, test_action, test_resource):
    """Analyze policy and return results"""
    analysis = {
        'summary': {},
        'statements': [],
        'test_result': None
    }
    
    statements = policy.get('Statement', [])
    if not isinstance(statements, list):
        statements = [statements]
    
    analysis['summary'] = {
        'total_statements': len(statements),
        'allow_statements': sum(1 for s in statements if s.get('Effect') == 'Allow'),
        'deny_statements': sum(1 for s in statements if s.get('Effect') == 'Deny'),
        'has_conditions': any('Condition' in s for s in statements)
    }
    
    # Analyze each statement
    for i, stmt in enumerate(statements):
        stmt_analysis = {
            'index': i,
            'effect': stmt.get('Effect', 'Allow'),
            'actions': stmt.get('Action', []),
            'resources': stmt.get('Resource', []),
            'conditions': stmt.get('Condition', {})
        }
        analysis['statements'].append(stmt_analysis)
    
    # Test the specific action/resource
    analysis['test_result'] = test_policy_against_request(policy, test_action, test_resource)
    
    return analysis

def test_policy_against_request(policy, action, resource):
    """Test if policy allows specific action on resource"""
    statements = policy.get('Statement', [])
    if not isinstance(statements, list):
        statements = [statements]
    
    has_allow = False
    has_deny = False
    
    for stmt in statements:
        effect = stmt.get('Effect', 'Allow')
        actions = stmt.get('Action', [])
        resources = stmt.get('Resource', [])
        
        if isinstance(actions, str):
            actions = [actions]
        if isinstance(resources, str):
            resources = [resources]
        
        # Check if action matches
        action_match = any(a == action or a == '*' or action.startswith(a.replace('*', '')) for a in actions)
        
        # Check if resource matches
        resource_match = any(r == resource or r == '*' or resource.startswith(r.replace('*', '')) for r in resources)
        
        if action_match and resource_match:
            if effect == 'Deny':
                has_deny = True
            elif effect == 'Allow':
                has_allow = True
    
    if has_deny:
        return {'allowed': False, 'reason': 'Explicit deny'}
    elif has_allow:
        return {'allowed': True, 'reason': 'Explicit allow'}
    else:
        return {'allowed': False, 'reason': 'Implicit deny (no matching allow)'}

def display_policy_analysis(analysis):
    """Display policy analysis results"""
    st.markdown("### 📊 Policy Analysis Results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Statements", analysis['summary']['total_statements'])
    with col2:
        st.metric("Allow Statements", analysis['summary']['allow_statements'])
    with col3:
        st.metric("Deny Statements", analysis['summary']['deny_statements'])
    with col4:
        st.metric("Has Conditions", "Yes" if analysis['summary']['has_conditions'] else "No")
    
    # Test result
    if analysis['test_result']:
        result = analysis['test_result']
        if result['allowed']:
            st.markdown('<div class="permission-granted">', unsafe_allow_html=True)
            st.markdown(f"### ✅ Permission Test: ALLOWED\n**Reason**: {result['reason']}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="permission-denied">', unsafe_allow_html=True)
            st.markdown(f"### ❌ Permission Test: DENIED\n**Reason**: {result['reason']}")
            st.markdown('</div>', unsafe_allow_html=True)

def simulate_policy_evaluation(policy, context):
    """Simulate policy evaluation with context"""
    # Simplified simulation logic
    statements = policy.get('Statement', [])
    if not isinstance(statements, list):
        statements = [statements]
    
    evaluation_steps = []
    final_result = {'allowed': False, 'reason': 'Implicit deny'}
    
    for i, stmt in enumerate(statements):
        effect = stmt.get('Effect', 'Allow')
        actions = stmt.get('Action', [])
        resources = stmt.get('Resource', [])
        conditions = stmt.get('Condition', {})
        
        step = {
            'statement': i + 1,
            'effect': effect,
            'matches': False,
            'reason': ''
        }
        
        # Check action match
        if isinstance(actions, str):
            actions = [actions]
        
        action_match = any(action == context['action'] or action == '*' for action in actions)
        
        # Check resource match  
        if isinstance(resources, str):
            resources = [resources]
            
        resource_match = any(res == context['resource'] or res == '*' for res in resources)
        
        if action_match and resource_match:
            step['matches'] = True
            if effect == 'Deny':
                step['reason'] = 'Explicit deny - evaluation stops'
                final_result = {'allowed': False, 'reason': f'Denied by statement {i+1}'}
                evaluation_steps.append(step)
                break
            elif effect == 'Allow':
                step['reason'] = 'Allow found - continue checking for denies'
                final_result = {'allowed': True, 'reason': f'Allowed by statement {i+1}'}
        else:
            step['reason'] = 'Action or resource does not match'
        
        evaluation_steps.append(step)
    
    return {
        'result': final_result,
        'steps': evaluation_steps,
        'context': context
    }

def display_simulation_result(simulation):
    """Display simulation results"""
    result = simulation['result']
    
    if result['allowed']:
        st.markdown('<div class="permission-granted">', unsafe_allow_html=True)
        st.markdown(f"### ✅ SIMULATION RESULT: ALLOWED\n**Final Reason**: {result['reason']}")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="permission-denied">', unsafe_allow_html=True)
        st.markdown(f"### ❌ SIMULATION RESULT: DENIED\n**Final Reason**: {result['reason']}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Show evaluation steps
    st.markdown("### 🔍 Evaluation Steps")
    for step in simulation['steps']:
        if step['matches']:
            icon = "✅" if step['effect'] == 'Allow' else "❌"
            st.markdown(f"{icon} **Statement {step['statement']}** ({step['effect']}): {step['reason']}")
        else:
            st.markdown(f"⏭️ **Statement {step['statement']}**: {step['reason']}")

def resource_policy_interpretation_tab():
    """Content for Resource Policy Interpretation tab"""
    st.markdown("## 🛡️ Resource Policy Interpretation")
    st.markdown("*Understanding resource-based policies and cross-account access*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Resource-based policies** are attached directly to AWS resources like S3 buckets, KMS keys, and SQS queues. 
    Unlike identity-based policies, they include a **Principal** element that specifies who can access the resource.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Identity-based vs Resource-based comparison
    st.markdown("### ⚖️ Identity-based vs Resource-based Policies")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 👤 Identity-based Policies
        
        **Attached to**: Users, Groups, Roles
        
        **Controls**: What the identity can do
        
        **Principal**: Implicit (the identity)
        
        **Use Cases**:
        - User permissions
        - Role permissions  
        - Service permissions
        
        **Example**: IAM user policy allowing S3 access
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛡️ Resource-based Policies
        
        **Attached to**: AWS Resources (S3, KMS, etc.)
        
        **Controls**: Who can access the resource
        
        **Principal**: Explicit (specified in policy)
        
        **Use Cases**:
        - Cross-account access
        - Service-to-service access
        - Public resource access
        
        **Example**: S3 bucket policy allowing external access
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Resource Policy Builder
    st.markdown("### 🛠️ Interactive Resource Policy Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏗️ Policy Configuration")
        resource_type = st.selectbox("Resource Type:", [
            "S3 Bucket", "KMS Key", "SQS Queue", "SNS Topic", "Lambda Function"
        ])
        
        policy_purpose = st.selectbox("Policy Purpose:", [
            "Cross-Account Access", "Public Read Access", "Service Integration", "Backup Account Access"
        ])
        
        principal_type = st.selectbox("Principal Type:", [
            "AWS Account", "IAM User", "IAM Role", "AWS Service", "Public (*)"
        ])
        
        if principal_type == "AWS Account":
            principal_value = st.text_input("Account ID:", "123456789012")
        elif principal_type == "IAM User":
            principal_value = st.text_input("User ARN:", "arn:aws:iam::123456789012:user/username")
        elif principal_type == "IAM Role":
            principal_value = st.text_input("Role ARN:", "arn:aws:iam::123456789012:role/rolename")
        elif principal_type == "AWS Service":
            principal_value = st.selectbox("Service:", ["lambda.amazonaws.com", "ec2.amazonaws.com", "s3.amazonaws.com"])
        else:
            principal_value = "*"
    
    with col2:
        st.markdown("### ⚙️ Permissions & Conditions")
        if resource_type == "S3 Bucket":
            allowed_actions = st.multiselect("Allowed Actions:", [
                "s3:GetObject", "s3:PutObject", "s3:DeleteObject", 
                "s3:ListBucket", "s3:GetBucketLocation"
            ], default=["s3:GetObject"])
        elif resource_type == "KMS Key":
            allowed_actions = st.multiselect("Allowed Actions:", [
                "kms:Encrypt", "kms:Decrypt", "kms:GenerateDataKey",
                "kms:ReEncrypt*", "kms:DescribeKey"
            ], default=["kms:Decrypt"])
        else:
            allowed_actions = st.multiselect("Allowed Actions:", [
                f"{resource_type.lower()}:*"
            ])
        
        # Conditions
        add_ip_condition = st.checkbox("Add IP Address Restriction")
        if add_ip_condition:
            ip_range = st.text_input("Allowed IP Range:", "192.168.1.0/24")
        
        add_time_condition = st.checkbox("Add Time-based Restriction")
        if add_time_condition:
            time_restriction = st.selectbox("Time Restriction:", [
                "Business Hours Only", "Weekdays Only", "Specific Date Range"
            ])
        
        add_ssl_condition = st.checkbox("Require SSL/HTTPS", value=True)
    
    if st.button("🚀 Generate Resource Policy", use_container_width=True):
        # Generate the resource policy
        policy = generate_resource_policy(
            resource_type, policy_purpose, principal_type, principal_value,
            allowed_actions, add_ip_condition, ip_range if add_ip_condition else None,
            add_ssl_condition
        )
        
        st.markdown("### 📄 Generated Resource Policy")
        st.markdown('<div class="policy-viewer">', unsafe_allow_html=True)
        st.json(policy)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Policy explanation
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 📋 Policy Summary
        
        **Resource**: {resource_type}
        **Purpose**: {policy_purpose}
        **Principal**: {principal_type} ({principal_value})
        **Actions**: {', '.join(allowed_actions)}
        **Conditions**: {'IP restriction, ' if add_ip_condition else ''}{'SSL required' if add_ssl_condition else ''}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Common Resource Policy Examples
    st.markdown("### 📚 Common Resource Policy Examples")
    
    # S3 Cross-Account Example
    st.markdown("#### 🪣 S3 Cross-Account Access Policy")
    s3_cross_account_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "CrossAccountAccess",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::123456789012:user/BackupUser"
                },
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject"
                ],
                "Resource": "arn:aws:s3:::my-backup-bucket/*"
            }
        ]
    }
    
    st.markdown('<div class="policy-viewer">', unsafe_allow_html=True)
    st.json(s3_cross_account_policy)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # KMS Key Policy Example
    st.markdown("#### 🔑 KMS Key Policy for Service Access")
    kms_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowServiceAccess",
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": [
                    "kms:Decrypt",
                    "kms:GenerateDataKey"
                ],
                "Resource": "*",
                "Condition": {
                    "StringEquals": {
                        "kms:ViaService": "s3.us-east-1.amazonaws.com"
                    }
                }
            }
        ]
    }
    
    st.markdown('<div class="policy-viewer">', unsafe_allow_html=True)
    st.json(kms_policy)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Policy Evaluation with Resource Policies
    st.markdown("### 🔍 Resource Policy Evaluation Logic")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Evaluation Rules
    
    **Cross-Account Access Requirements**:
    1. **Identity-based policy** must allow the action (in the calling account)
    2. **Resource-based policy** must allow the action (in the resource account)
    3. Both policies must align for access to be granted
    
    **Same-Account Access**:
    - Either identity-based OR resource-based policy can grant access
    - Explicit deny in either policy will block access
    
    **Service Principals**:
    - AWS services can be granted access via resource policies
    - Useful for services like Lambda, EC2, etc. to access resources
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Resource Policy Security Considerations
    st.markdown("### 🔒 Security Considerations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚠️ Common Security Issues
        
        **Overly Permissive Principals**:
        - Using "*" for public access
        - Granting access to entire AWS accounts
        
        **Missing Conditions**:
        - No IP restrictions
        - No SSL requirements
        - No MFA requirements
        
        **Broad Actions**:
        - Using wildcard actions (*)
        - More permissions than needed
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ✅ Security Best Practices
        
        **Principle of Least Privilege**:
        - Grant minimum required permissions
        - Use specific principals when possible
        
        **Add Protective Conditions**:
        - Require SSL for sensitive data
        - Restrict by IP range when appropriate
        - Add time-based restrictions
        
        **Regular Reviews**:
        - Audit resource policies regularly
        - Remove unused permissions
        - Monitor access patterns
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Resource Policy Management")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Resource policy management utilities
import boto3
import json
from datetime import datetime

def create_s3_cross_account_policy(bucket_name, external_account_id, actions=None):
    """Create S3 bucket policy for cross-account access"""
    
    s3 = boto3.client('s3')
    
    if actions is None:
        actions = ["s3:GetObject", "s3:PutObject"]
    
    # Create bucket policy
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "CrossAccountAccess",
                "Effect": "Allow",
                "Principal": {
                    "AWS": f"arn:aws:iam::{external_account_id}:root"
                },
                "Action": actions,
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*"
                ],
                "Condition": {
                    "Bool": {
                        "aws:SecureTransport": "true"
                    }
                }
            }
        ]
    }
    
    try:
        # Apply the bucket policy
        s3.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        
        print(f"✅ Successfully applied cross-account policy to bucket: {bucket_name}")
        print(f"   External Account: {external_account_id}")
        print(f"   Allowed Actions: {', '.join(actions)}")
        
        return bucket_policy
        
    except Exception as e:
        print(f"❌ Error applying bucket policy: {e}")
        return None

def create_kms_key_policy(key_description, admin_principals, user_principals):
    """Create KMS key with comprehensive key policy"""
    
    kms = boto3.client('kms')
    
    key_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "EnableIAMUserPermissions",
                "Effect": "Allow",
                "Principal": {
                    "AWS": f"arn:aws:iam::{boto3.Session().region_name}:root"
                },
                "Action": "kms:*",
                "Resource": "*"
            },
            {
                "Sid": "AllowKeyAdministration",
                "Effect": "Allow",
                "Principal": {
                    "AWS": admin_principals
                },
                "Action": [
                    "kms:Create*",
                    "kms:Describe*",
                    "kms:Enable*",
                    "kms:List*",
                    "kms:Put*",
                    "kms:Update*",
                    "kms:Revoke*",
                    "kms:Disable*",
                    "kms:Get*",
                    "kms:Delete*",
                    "kms:TagResource",
                    "kms:UntagResource",
                    "kms:ScheduleKeyDeletion",
                    "kms:CancelKeyDeletion"
                ],
                "Resource": "*"
            },
            {
                "Sid": "AllowKeyUsage",
                "Effect": "Allow",
                "Principal": {
                    "AWS": user_principals
                },
                "Action": [
                    "kms:Encrypt",
                    "kms:Decrypt",
                    "kms:ReEncrypt*",
                    "kms:GenerateDataKey*",
                    "kms:DescribeKey"
                ],
                "Resource": "*"
            }
        ]
    }
    
    try:
        # Create the KMS key
        response = kms.create_key(
            Policy=json.dumps(key_policy),
            Description=key_description,
            Usage='ENCRYPT_DECRYPT',
            KeySpec='SYMMETRIC_DEFAULT',
            Tags=[
                {'TagKey': 'Purpose', 'TagValue': 'ResourcePolicy'},
                {'TagKey': 'Created', 'TagValue': str(datetime.now())}
            ]
        )
        
        key_id = response['KeyMetadata']['KeyId']
        key_arn = response['KeyMetadata']['Arn']
        
        print(f"✅ Created KMS key: {key_id}")
        print(f"   ARN: {key_arn}")
        print(f"   Admins: {', '.join(admin_principals)}")
        print(f"   Users: {', '.join(user_principals)}")
        
        return {
            'key_id': key_id,
            'key_arn': key_arn,
            'policy': key_policy
        }
        
    except Exception as e:
        print(f"❌ Error creating KMS key: {e}")
        return None

def analyze_resource_policy(resource_arn, policy_document=None):
    """Analyze resource policy for security issues"""
    
    if policy_document is None:
        # Fetch policy based on resource type
        if ':s3:::' in resource_arn:
            policy_document = get_s3_bucket_policy(resource_arn.split(':')[-1])
        elif ':key/' in resource_arn:
            policy_document = get_kms_key_policy(resource_arn.split('/')[-1])
    
    if not policy_document:
        return {"error": "Could not retrieve policy"}
    
    if isinstance(policy_document, str):
        policy = json.loads(policy_document)
    else:
        policy = policy_document
    
    analysis = {
        'resource_arn': resource_arn,
        'policy_version': policy.get('Version'),
        'statements': len(policy.get('Statement', [])),
        'security_issues': [],
        'recommendations': [],
        'principals': set(),
        'actions': set(),
        'conditions': []
    }
    
    statements = policy.get('Statement', [])
    if not isinstance(statements, list):
        statements = [statements]
    
    for idx, statement in enumerate(statements):
        effect = statement.get('Effect', 'Allow')
        
        # Analyze principals
        principal = statement.get('Principal')
        if principal:
            if principal == '*':
                analysis['security_issues'].append(f"Statement {idx}: Public access (*) principal")
            elif isinstance(principal, dict):
                for key, values in principal.items():
                    if isinstance(values, list):
                        analysis['principals'].update(values)
                    else:
                        analysis['principals'].add(values)
            else:
                analysis['principals'].add(str(principal))
        
        # Analyze actions
        actions = statement.get('Action', [])
        if isinstance(actions, str):
            actions = [actions]
        
        for action in actions:
            analysis['actions'].add(action)
            if action == '*':
                analysis['security_issues'].append(f"Statement {idx}: Wildcard action (*)")
        
        # Analyze conditions
        conditions = statement.get('Condition', {})
        if conditions:
            analysis['conditions'].append({
                'statement': idx,
                'conditions': conditions
            })
        else:
            if effect == 'Allow' and (principal == '*' or '*' in str(actions)):
                analysis['security_issues'].append(f"Statement {idx}: No conditions on permissive statement")
    
    # Generate recommendations
    if not any('aws:SecureTransport' in str(cond) for cond in analysis['conditions']):
        analysis['recommendations'].append("Consider requiring SSL/TLS transport")
    
    if '*' in analysis['principals']:
        analysis['recommendations'].append("Review public access - ensure it's intentional")
    
    if len(analysis['actions']) > 10:
        analysis['recommendations'].append("Policy grants many actions - consider scope reduction")
    
    return analysis

def get_s3_bucket_policy(bucket_name):
    """Get S3 bucket policy"""
    s3 = boto3.client('s3')
    
    try:
        response = s3.get_bucket_policy(Bucket=bucket_name)
        return response['Policy']
    except s3.exceptions.NoSuchBucketPolicy:
        return None
    except Exception as e:
        print(f"Error getting bucket policy: {e}")
        return None

def get_kms_key_policy(key_id):
    """Get KMS key policy"""
    kms = boto3.client('kms')
    
    try:
        response = kms.get_key_policy(KeyId=key_id, PolicyName='default')
        return response['Policy']
    except Exception as e:
        print(f"Error getting key policy: {e}")
        return None

def audit_resource_policies():
    """Audit all resource policies in account"""
    print("🔍 Starting Resource Policy Audit")
    print("=" * 50)
    
    # Audit S3 bucket policies
    s3 = boto3.client('s3')
    try:
        buckets = s3.list_buckets()['Buckets']
        print(f"📋 Found {len(buckets)} S3 buckets")
        
        for bucket in buckets[:5]:  # Limit to first 5 for demo
            bucket_name = bucket['Name']
            policy = get_s3_bucket_policy(bucket_name)
            
            if policy:
                analysis = analyze_resource_policy(f"arn:aws:s3:::{bucket_name}", policy)
                print(f"\n🪣 Bucket: {bucket_name}")
                print(f"   Statements: {analysis['statements']}")
                print(f"   Principals: {len(analysis['principals'])}")
                
                if analysis['security_issues']:
                    print(f"   ⚠️  Issues: {len(analysis['security_issues'])}")
                    for issue in analysis['security_issues'][:2]:
                        print(f"      - {issue}")
            else:
                print(f"\n🪣 Bucket: {bucket_name} (No bucket policy)")
                
    except Exception as e:
        print(f"Error auditing S3 buckets: {e}")
    
    # Audit KMS key policies
    kms = boto3.client('kms')
    try:
        keys = kms.list_keys()['Keys']
        print(f"\n🔑 Found {len(keys)} KMS keys")
        
        for key in keys[:3]:  # Limit to first 3 for demo
            key_id = key['KeyId']
            try:
                policy = get_kms_key_policy(key_id)
                if policy:
                    analysis = analyze_resource_policy(key['KeyArn'], policy)
                    print(f"\n🔐 Key: {key_id}")
                    print(f"   Statements: {analysis['statements']}")
                    print(f"   Principals: {len(analysis['principals'])}")
                    
                    if analysis['security_issues']:
                        print(f"   ⚠️  Issues: {len(analysis['security_issues'])}")
                        
            except Exception:
                continue  # Skip keys we can't access
                
    except Exception as e:
        print(f"Error auditing KMS keys: {e}")

# Example usage
print("🚀 Resource Policy Management Examples")

# Create cross-account S3 access
bucket_policy = create_s3_cross_account_policy(
    bucket_name='my-shared-bucket',
    external_account_id='123456789012',
    actions=['s3:GetObject', 's3:ListBucket']
)

# Create KMS key with policy
kms_key = create_kms_key_policy(
    key_description='Shared encryption key',
    admin_principals=['arn:aws:iam::123456789012:user/admin'],
    user_principals=['arn:aws:iam::123456789012:role/app-role']
)

# Audit all resource policies
audit_resource_policies()
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def generate_resource_policy(resource_type, purpose, principal_type, principal_value, actions, add_ip, ip_range, add_ssl):
    """Generate a resource policy based on inputs"""
    
    # Base policy structure
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": purpose.replace(" ", ""),
                "Effect": "Allow",
                "Principal": {},
                "Action": actions,
                "Resource": "*"
            }
        ]
    }
    
    # Set principal
    if principal_type == "AWS Account":
        policy["Statement"][0]["Principal"] = {"AWS": f"arn:aws:iam::{principal_value}:root"}
    elif principal_type == "IAM User":
        policy["Statement"][0]["Principal"] = {"AWS": principal_value}
    elif principal_type == "IAM Role":
        policy["Statement"][0]["Principal"] = {"AWS": principal_value}
    elif principal_type == "AWS Service":
        policy["Statement"][0]["Principal"] = {"Service": principal_value}
    else:
        policy["Statement"][0]["Principal"] = "*"
    
    # Add conditions
    conditions = {}
    
    if add_ip and ip_range:
        conditions["IpAddress"] = {"aws:SourceIp": ip_range}
    
    if add_ssl:
        conditions["Bool"] = {"aws:SecureTransport": "true"}
    
    if conditions:
        policy["Statement"][0]["Condition"] = conditions
    
    # Set resource ARN based on type
    if resource_type == "S3 Bucket":
        policy["Statement"][0]["Resource"] = [
            "arn:aws:s3:::my-bucket",
            "arn:aws:s3:::my-bucket/*"
        ]
    elif resource_type == "KMS Key":
        policy["Statement"][0]["Resource"] = "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
    
    return policy

def iam_permissions_example_tab():
    """Content for IAM Permissions Example tab"""
    st.markdown("## ⚙️ IAM Permissions – Example")
    st.markdown("*Real-world IAM troubleshooting and permission scenarios*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Scenario from AWS Session
    **VPC Flow Logs Issue**: Flow log records are incomplete or no longer being published to CloudWatch Logs. 
    This is a common IAM permissions problem that requires understanding service roles and trust relationships.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # VPC Flow Logs Architecture
    st.markdown("### 🏗️ VPC Flow Logs Architecture")
    flow_logs_mermaid = """
    graph TB
        subgraph "VPC"
            A[🌐 Network Interface]
            B[📊 VPC Flow Logs]
        end
        
        subgraph "IAM"
            C[🎭 Flow Logs Role]
            D[📜 Trust Policy]
            E[📜 Permissions Policy]
        end
        
        subgraph "CloudWatch"
            F[📋 Log Group]
            G[📝 Log Stream]
            H[📊 Log Events]
        end
        
        A --> B
        B --> C
        C --> D
        C --> E
        D --> |trusts| I[vpc-flow-logs.amazonaws.com]
        E --> |allows| J[logs:CreateLogGroup<br/>logs:CreateLogStream<br/>logs:PutLogEvents]
        C --> F
        F --> G
        G --> H
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style B fill:#FF9900,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style F fill:#232F3E,stroke:#FF9900,color:#fff
    """
    
    common.mermaid(flow_logs_mermaid, height=400)
    
    # Problem Analysis Interface
    st.markdown("### 🔍 Interactive Problem Diagnosis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🚨 Observed Issues")
        issue_type = st.selectbox("Select Issue:", [
            "Flow log records are incomplete",
            "Flow logs stopped publishing", 
            "Access denied errors in CloudTrail",
            "Flow logs service unreachable"
        ])
        
        error_message = st.text_area("Error Message (if any):", 
                                    "AccessDenied: User is not authorized to perform logs:PutLogEvents")
        
        last_working = st.selectbox("When did it last work?", [
            "Never worked", "Stopped today", "Stopped this week", "Worked last month"
        ])
    
    with col2:
        st.markdown("### 🔧 Current Configuration")
        has_flow_logs_role = st.checkbox("Flow Logs IAM Role exists", value=True)
        
        if has_flow_logs_role:
            role_has_trust_policy = st.checkbox("Role has trust policy", value=False)
            role_has_permissions = st.checkbox("Role has CloudWatch permissions", value=False)
            trust_policy_correct = st.checkbox("Trust policy allows vpc-flow-logs service", value=False)
        
        cloudwatch_log_group_exists = st.checkbox("CloudWatch Log Group exists", value=True)
        vpc_flow_logs_enabled = st.checkbox("VPC Flow Logs enabled", value=True)
    
    if st.button("🔍 Diagnose Issue", use_container_width=True):
        diagnosis = diagnose_flow_logs_issue(
            issue_type, has_flow_logs_role, role_has_trust_policy, 
            role_has_permissions, trust_policy_correct, 
            cloudwatch_log_group_exists, vpc_flow_logs_enabled
        )
        
        display_diagnosis_results(diagnosis)
    
    # Step-by-Step Solution
    st.markdown("### 🛠️ Step-by-Step Solution")
    
    with st.expander("📋 Complete VPC Flow Logs Setup", expanded=False):
        st.markdown("""
        ### ✅ Complete Setup Checklist
        
        **1. Create IAM Role for VPC Flow Logs**
        ```json
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "vpc-flow-logs.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        ```
        
        **2. Attach Permissions Policy**
        ```json
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream", 
                        "logs:PutLogEvents",
                        "logs:DescribeLogGroups",
                        "logs:DescribeLogStreams"
                    ],
                    "Resource": "*"
                }
            ]
        }
        ```
        
        **3. Create CloudWatch Log Group**
        
        **4. Enable VPC Flow Logs with correct role ARN**
        """)
    
    # Interactive Permission Tester
    st.markdown("### 🧪 Permission Testing Simulator")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Trust Policy Check**")
        trust_service = st.selectbox("Service in Trust Policy:", [
            "vpc-flow-logs.amazonaws.com", "ec2.amazonaws.com", "lambda.amazonaws.com", "None"
        ])
        
    with col2:
        st.markdown("**Permissions Check**")
        permissions = st.multiselect("Granted Permissions:", [
            "logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents",
            "logs:DescribeLogGroups", "s3:PutObject"
        ])
    
    with col3:
        st.markdown("**Resource Access**")
        log_group_access = st.selectbox("Log Group Access:", ["Full Access (*)", "Specific ARN", "Denied"])
    
    if st.button("🎯 Test Permissions"):
        test_result = test_flow_logs_permissions(trust_service, permissions, log_group_access)
        display_permission_test_result(test_result)
    
    # Common IAM Issues and Solutions
    st.markdown("### 🚨 Common IAM Issues & Solutions")
    
    issues_data = {
        'Issue': [
            'AccessDenied for logs:PutLogEvents',
            'Role cannot be assumed',
            'Flow logs created but no data',
            'Partial log delivery',
            'Rate limiting errors'
        ],
        'Root Cause': [
            'Missing CloudWatch permissions',
            'Incorrect trust policy',
            'Wrong log group ARN',
            'Insufficient permissions',
            'Too many requests'
        ],
        'Solution': [
            'Add logs:* permissions to role',
            'Fix trust policy to allow vpc-flow-logs service',
            'Verify log group exists and ARN is correct',
            'Add DescribeLogGroups permission',
            'Implement exponential backoff'
        ],
        'Prevention': [
            'Use AWS managed policies when possible',
            'Always test trust relationships',
            'Validate resource ARNs',
            'Grant all required permissions',
            'Monitor CloudWatch metrics'
        ]
    }
    
    df_issues = pd.DataFrame(issues_data)
    st.dataframe(df_issues, use_container_width=True)
    
    # Real-world Troubleshooting Guide
    st.markdown("### 🔧 Real-world Troubleshooting Guide")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔍 Diagnostic Steps
        
        **1. Check CloudTrail Logs**
        - Look for AccessDenied errors
        - Identify which service/user is failing
        - Note the specific action being denied
        
        **2. Verify Trust Relationships**
        - Ensure service can assume the role
        - Check for typos in service names
        - Validate condition statements
        
        **3. Test Permissions Incrementally**
        - Start with basic permissions
        - Add permissions one by one
        - Test after each change
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛠️ Resolution Strategies
        
        **Use IAM Policy Simulator**
        - Test policies before deployment
        - Validate complex condition logic
        - Debug permission issues
        
        **Implement Monitoring**
        - Set up CloudWatch alarms
        - Monitor IAM events in CloudTrail
        - Use AWS Config for compliance
        
        **Follow Best Practices**
        - Use least privilege principle
        - Regular permission audits
        - Automated policy validation
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: VPC Flow Logs IAM Setup")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Complete VPC Flow Logs setup with proper IAM configuration
import boto3
import json
import time

def setup_vpc_flow_logs_with_iam(vpc_id, log_group_name):
    """Complete setup of VPC Flow Logs with proper IAM configuration"""
    
    iam = boto3.client('iam')
    logs = boto3.client('logs')
    ec2 = boto3.client('ec2')
    
    role_name = 'VPCFlowLogsRole'
    policy_name = 'VPCFlowLogsPolicy'
    
    print("🚀 Setting up VPC Flow Logs with IAM...")
    
    # Step 1: Create Trust Policy for VPC Flow Logs service
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "vpc-flow-logs.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # Step 2: Create IAM Role
    try:
        role_response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for VPC Flow Logs to write to CloudWatch',
            Tags=[
                {'Key': 'Purpose', 'Value': 'VPCFlowLogs'},
                {'Key': 'Service', 'Value': 'Networking'}
            ]
        )
        
        role_arn = role_response['Role']['Arn']
        print(f"✅ Created IAM role: {role_name}")
        print(f"   ARN: {role_arn}")
        
    except iam.exceptions.EntityAlreadyExistsException:
        # Role exists, get its ARN
        role_response = iam.get_role(RoleName=role_name)
        role_arn = role_response['Role']['Arn']
        print(f"ℹ️  Using existing IAM role: {role_name}")
    
    # Step 3: Create and attach permissions policy
    permissions_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogGroups",
                    "logs:DescribeLogStreams"
                ],
                "Resource": "*"
            }
        ]
    }
    
    try:
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(permissions_policy)
        )
        print(f"✅ Attached permissions policy: {policy_name}")
        
    except Exception as e:
        print(f"❌ Error attaching policy: {e}")
        return None
    
    # Step 4: Create CloudWatch Log Group
    try:
        logs.create_log_group(
            logGroupName=log_group_name,
            tags={
                'Purpose': 'VPCFlowLogs',
                'VPC': vpc_id
            }
        )
        print(f"✅ Created CloudWatch Log Group: {log_group_name}")
        
    except logs.exceptions.ResourceAlreadyExistsException:
        print(f"ℹ️  Using existing Log Group: {log_group_name}")
    
    # Step 5: Wait for role propagation (important!)
    print("⏳ Waiting for IAM role propagation...")
    time.sleep(10)
    
    # Step 6: Enable VPC Flow Logs
    try:
        flow_log_response = ec2.create_flow_logs(
            ResourceIds=[vpc_id],
            ResourceType='VPC',
            TrafficType='ALL',
            LogDestinationType='cloud-watch-logs',
            LogGroupName=log_group_name,
            DeliverLogsPermissionArn=role_arn,
            LogFormat='${version} ${account-id} ${interface-id} ${srcaddr} ${dstaddr} ${srcport} ${dstport} ${protocol} ${packets} ${bytes} ${windowstart} ${windowend} ${action} ${flowlogstatus}',
            Tags=[
                {'Key': 'Name', 'Value': f'FlowLogs-{vpc_id}'},
                {'Key': 'Purpose', 'Value': 'NetworkMonitoring'}
            ]
        )
        
        flow_log_ids = flow_log_response['FlowLogIds']
        unsuccessful = flow_log_response.get('Unsuccessful', [])
        
        if unsuccessful:
            print("❌ Flow Logs creation issues:")
            for issue in unsuccessful:
                print(f"   Resource: {issue['ResourceId']}")
                print(f"   Error: {issue['Error']['Message']}")
        else:
            print(f"✅ Created VPC Flow Logs: {', '.join(flow_log_ids)}")
        
        return {
            'role_arn': role_arn,
            'log_group': log_group_name,
            'flow_log_ids': flow_log_ids
        }
        
    except Exception as e:
        print(f"❌ Error creating flow logs: {e}")
        return None

def troubleshoot_flow_logs_permissions(flow_log_id):
    """Troubleshoot VPC Flow Logs permission issues"""
    
    ec2 = boto3.client('ec2')
    iam = boto3.client('iam')
    logs = boto3.client('logs')
    
    print(f"🔍 Troubleshooting Flow Logs: {flow_log_id}")
    print("=" * 50)
    
    try:
        # Get flow logs details
        response = ec2.describe_flow_logs(FlowLogIds=[flow_log_id])
        
        if not response['FlowLogs']:
            print("❌ Flow Log not found")
            return
        
        flow_log = response['FlowLogs'][0]
        status = flow_log['FlowLogStatus']
        role_arn = flow_log.get('DeliverLogsPermissionArn')
        log_group = flow_log.get('LogGroupName')
        
        print(f"📊 Flow Log Status: {status}")
        print(f"🎭 IAM Role: {role_arn}")
        print(f"📋 Log Group: {log_group}")
        
        # Check 1: Flow Log Status
        if status != 'ACTIVE':
            print(f"⚠️  Flow Log Status Issue: {status}")
            
            # Check if there are error messages
            if 'DeliverLogsErrorMessage' in flow_log:
                print(f"   Error: {flow_log['DeliverLogsErrorMessage']}")
        
        # Check 2: IAM Role exists and is accessible
        if role_arn:
            role_name = role_arn.split('/')[-1]
            try:
                role = iam.get_role(RoleName=role_name)
                print(f"✅ IAM Role exists: {role_name}")
                
                # Check trust policy
                trust_policy = json.loads(role['Role']['AssumeRolePolicyDocument'])
                vpc_flow_logs_trusted = False
                
                for statement in trust_policy.get('Statement', []):
                    principal = statement.get('Principal', {})
                    if isinstance(principal, dict):
                        services = principal.get('Service', [])
                        if isinstance(services, str):
                            services = [services]
                        if 'vpc-flow-logs.amazonaws.com' in services:
                            vpc_flow_logs_trusted = True
                            break
                
                if vpc_flow_logs_trusted:
                    print("✅ Trust policy allows vpc-flow-logs service")
                else:
                    print("❌ Trust policy does NOT allow vpc-flow-logs service")
                    print("   Fix: Update trust policy to include vpc-flow-logs.amazonaws.com")
                
                # Check permissions policy
                policies = iam.list_role_policies(RoleName=role_name)
                attached_policies = iam.list_attached_role_policies(RoleName=role_name)
                
                has_cloudwatch_permissions = False
                
                # Check inline policies
                for policy_name in policies['PolicyNames']:
                    policy = iam.get_role_policy(RoleName=role_name, PolicyName=policy_name)
                    policy_doc = json.loads(policy['PolicyDocument'])
                    
                    for statement in policy_doc.get('Statement', []):
                        actions = statement.get('Action', [])
                        if isinstance(actions, str):
                            actions = [actions]
                        
                        cloudwatch_actions = ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents']
                        if any(action in actions or 'logs:*' in actions or '*' in actions for action in cloudwatch_actions):
                            has_cloudwatch_permissions = True
                            break
                
                if has_cloudwatch_permissions:
                    print("✅ Role has CloudWatch Logs permissions")
                else:
                    print("❌ Role missing CloudWatch Logs permissions")
                    print("   Fix: Add logs:CreateLogGroup, logs:CreateLogStream, logs:PutLogEvents")
                
            except iam.exceptions.NoSuchEntityException:
                print(f"❌ IAM Role not found: {role_name}")
        
        # Check 3: CloudWatch Log Group exists
        if log_group:
            try:
                logs.describe_log_groups(logGroupNamePrefix=log_group)
                print(f"✅ CloudWatch Log Group exists: {log_group}")
            except Exception:
                print(f"❌ CloudWatch Log Group not found: {log_group}")
        
        # Check 4: Recent log events
        if log_group and status == 'ACTIVE':
            try:
                streams = logs.describe_log_streams(
                    logGroupName=log_group,
                    orderBy='LastEventTime',
                    descending=True,
                    limit=1
                )
                
                if streams['logStreams']:
                    last_event = streams['logStreams'][0].get('lastEventTime')
                    if last_event:
                        import datetime
                        last_event_time = datetime.datetime.fromtimestamp(last_event / 1000)
                        time_diff = datetime.datetime.now() - last_event_time
                        
                        if time_diff.total_seconds() < 3600:  # Less than 1 hour
                            print(f"✅ Recent log events found (last: {last_event_time})")
                        else:
                            print(f"⚠️  Last log event was {time_diff} ago")
                    else:
                        print("⚠️  No recent log events found")
                else:
                    print("⚠️  No log streams found")
                    
            except Exception as e:
                print(f"❌ Error checking log events: {e}")
    
    except Exception as e:
        print(f"❌ Error during troubleshooting: {e}")

def fix_common_flow_logs_issues(role_name, log_group_name):
    """Fix common VPC Flow Logs IAM issues"""
    
    iam = boto3.client('iam')
    logs = boto3.client('logs')
    
    print("🔧 Fixing common VPC Flow Logs issues...")
    
    try:
        # Fix 1: Update trust policy
        correct_trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "vpc-flow-logs.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        iam.update_assume_role_policy(
            RoleName=role_name,
            PolicyDocument=json.dumps(correct_trust_policy)
        )
        print("✅ Fixed trust policy")
        
        # Fix 2: Add comprehensive permissions
        comprehensive_permissions = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                        "logs:DescribeLogGroups",
                        "logs:DescribeLogStreams"
                    ],
                    "Resource": "*"
                }
            ]
        }
        
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName='VPCFlowLogsComprehensivePolicy',
            PolicyDocument=json.dumps(comprehensive_permissions)
        )
        print("✅ Updated permissions policy")
        
        # Fix 3: Ensure log group exists
        try:
            logs.create_log_group(logGroupName=log_group_name)
            print(f"✅ Created log group: {log_group_name}")
        except logs.exceptions.ResourceAlreadyExistsException:
            print(f"ℹ️  Log group already exists: {log_group_name}")
        
        print("🎉 Common issues fixed!")
        
    except Exception as e:
        print(f"❌ Error fixing issues: {e}")

# Example usage
vpc_id = 'vpc-12345678'
log_group_name = 'VPCFlowLogs'

# Complete setup
setup_result = setup_vpc_flow_logs_with_iam(vpc_id, log_group_name)

if setup_result and setup_result['flow_log_ids']:
    # Troubleshoot if needed
    flow_log_id = setup_result['flow_log_ids'][0]
    
    print(f"\n🔍 Running diagnostics on Flow Log: {flow_log_id}")
    troubleshoot_flow_logs_permissions(flow_log_id)
    
    # Fix common issues
    fix_common_flow_logs_issues('VPCFlowLogsRole', log_group_name)

print("\n✅ VPC Flow Logs setup and troubleshooting completed!")
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def diagnose_flow_logs_issue(issue_type, has_role, has_trust, has_permissions, trust_correct, log_group_exists, flow_logs_enabled):
    """Diagnose VPC Flow Logs issues"""
    
    diagnosis = {
        'primary_issue': issue_type,
        'root_causes': [],
        'solutions': [],
        'severity': 'Medium'
    }
    
    if not has_role:
        diagnosis['root_causes'].append("IAM Role for VPC Flow Logs does not exist")
        diagnosis['solutions'].append("Create IAM role with proper trust policy and permissions")
        diagnosis['severity'] = 'High'
    else:
        if not has_trust:
            diagnosis['root_causes'].append("IAM Role missing trust policy")
            diagnosis['solutions'].append("Add trust policy allowing vpc-flow-logs.amazonaws.com")
            diagnosis['severity'] = 'High'
        elif not trust_correct:
            diagnosis['root_causes'].append("Trust policy does not allow vpc-flow-logs service")
            diagnosis['solutions'].append("Update trust policy with correct service principal")
            diagnosis['severity'] = 'High'
        
        if not has_permissions:
            diagnosis['root_causes'].append("IAM Role missing CloudWatch permissions")
            diagnosis['solutions'].append("Add logs:CreateLogGroup, logs:CreateLogStream, logs:PutLogEvents permissions")
            diagnosis['severity'] = 'High'
    
    if not log_group_exists:
        diagnosis['root_causes'].append("CloudWatch Log Group does not exist")
        diagnosis['solutions'].append("Create CloudWatch Log Group for Flow Logs")
        diagnosis['severity'] = 'Medium'
    
    if not flow_logs_enabled:
        diagnosis['root_causes'].append("VPC Flow Logs not enabled")
        diagnosis['solutions'].append("Enable VPC Flow Logs with correct configuration")
        diagnosis['severity'] = 'High'
    
    if not diagnosis['root_causes']:
        diagnosis['root_causes'].append("Configuration appears correct - check for recent changes")
        diagnosis['solutions'].append("Review CloudTrail logs for recent permission changes")
        diagnosis['severity'] = 'Low'
    
    return diagnosis

def display_diagnosis_results(diagnosis):
    """Display diagnosis results"""
    
    severity_colors = {
        'High': 'danger',
        'Medium': 'warning', 
        'Low': 'success'
    }
    
    color = severity_colors.get(diagnosis['severity'], 'warning')
    
    if color == 'danger':
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    elif color == 'success':
        st.markdown('<div class="security-box">', unsafe_allow_html=True)
    else:
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
    
    st.markdown(f"""
    ### 🔍 Diagnosis Results - Severity: {diagnosis['severity']}
    
    **Primary Issue**: {diagnosis['primary_issue']}
    
    **Root Causes Identified**:
    {chr(10).join([f"• {cause}" for cause in diagnosis['root_causes']])}
    
    **Recommended Solutions**:
    {chr(10).join([f"• {solution}" for solution in diagnosis['solutions']])}
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)

def test_flow_logs_permissions(trust_service, permissions, log_group_access):
    """Test VPC Flow Logs permissions configuration"""
    
    result = {
        'overall_status': 'PASS',
        'trust_policy': 'PASS',
        'permissions_policy': 'PASS', 
        'resource_access': 'PASS',
        'issues': []
    }
    
    # Check trust policy
    if trust_service != "vpc-flow-logs.amazonaws.com":
        result['trust_policy'] = 'FAIL'
        result['overall_status'] = 'FAIL'
        result['issues'].append(f"Trust policy allows '{trust_service}' instead of 'vpc-flow-logs.amazonaws.com'")
    
    # Check permissions
    required_permissions = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
    missing_permissions = [perm for perm in required_permissions if perm not in permissions]
    
    if missing_permissions:
        result['permissions_policy'] = 'FAIL'
        result['overall_status'] = 'FAIL'
        result['issues'].append(f"Missing permissions: {', '.join(missing_permissions)}")
    
    # Check resource access
    if log_group_access == "Denied":
        result['resource_access'] = 'FAIL'
        result['overall_status'] = 'FAIL'
        result['issues'].append("CloudWatch Log Group access denied")
    
    return result

def display_permission_test_result(result):
    """Display permission test results"""
    
    if result['overall_status'] == 'PASS':
        st.markdown('<div class="permission-granted">', unsafe_allow_html=True)
        st.markdown("### ✅ Permission Test: PASSED\nAll required permissions are correctly configured!")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="permission-denied">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ❌ Permission Test: FAILED
        
        **Issues Found**:
        {chr(10).join([f"• {issue}" for issue in result['issues']])}
        
        **Component Status**:
        • Trust Policy: {result['trust_policy']}
        • Permissions Policy: {result['permissions_policy']}
        • Resource Access: {result['resource_access']}
        """)
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
    st.markdown("# 🔐 AWS IAM & Security Hub")
    
    st.markdown("""<div class="info-box">
                Master AWS Identity and Access Management concepts including policy interpretation, resource-based permissions, and real-world troubleshooting scenarios to design secure, compliant cloud architectures.
                </div>""", unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔐 AWS Identity and Access Management",
        "📜 IAM Policy Interpretation", 
        "🛡️ Resource Policy Interpretation",
        "⚙️ IAM Permissions – Example"
    ])
    
    with tab1:
        aws_iam_tab()
    
    with tab2:
        iam_policy_interpretation_tab()
    
    with tab3:
        resource_policy_interpretation_tab()
    
    with tab4:
        iam_permissions_example_tab()
    
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
