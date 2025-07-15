import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import utils.common as common
import utils.authenticate as authenticate
import json

# Page configuration
st.set_page_config(
    page_title="AWS Identity and Access Management Hub",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)
common.initialize_mermaid()
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
        
        .policy-box {{
            background-color: {AWS_COLORS['dark_blue']};
            color: white;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid {AWS_COLORS['primary']};
            margin: 10px 0;
            font-family: 'Courier New', monospace;
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
        
        .trust-policy {{
            background-color: #E8F5E8;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid {AWS_COLORS['success']};
            margin: 10px 0;
        }}
        
        .permission-policy {{
            background-color: #FFF4E6;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid {AWS_COLORS['warning']};
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
            - 🔐 AWS Identity and Access Management - Core IAM concepts
            - 👤 IAM Roles - Temporary access permissions
            - 🎫 Security Token Service (STS) - Temporary credentials
            - 📜 Policy Interpretation - Understanding IAM policies
            - 🛡️ IAM Permissions - Managing access control
            
            **Learning Objectives:**
            - Understand AWS security and access management
            - Learn to create and manage IAM policies and roles
            - Master temporary credential mechanisms
            - Practice policy interpretation and troubleshooting
            - Implement secure access patterns
            """)

def create_iam_overview_mermaid():
    """Create mermaid diagram for IAM overview"""
    return """
    graph TB
        A[AWS Identity & Access Management] --> B[Users]
        A --> C[Groups]
        A --> D[Roles]
        A --> E[Policies]
        
        B --> F[Individual Access]
        B --> G[Long-term Credentials]
        
        C --> H[Collection of Users]
        C --> I[Shared Permissions]
        
        D --> J[Temporary Access]
        D --> K[Cross-service Access]
        
        E --> L[Permission Definitions]
        E --> M[JSON Documents]
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style B fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#4B9EDB,stroke:#232F3E,color:#fff
        style D fill:#3FB34F,stroke:#232F3E,color:#fff
        style E fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_role_assumption_mermaid():
    """Create mermaid diagram for role assumption process"""
    return """
    graph LR
        A[👤 Identity] --> B{Trust Policy Check}
        B -->|✅ Allowed| C[🎫 STS AssumeRole]
        B -->|❌ Denied| D[🚫 Access Denied]
        
        C --> E[📋 Temporary Credentials]
        E --> F[🔑 Access Key]
        E --> G[🔐 Secret Key]
        E --> H[⏰ Session Token]
        
        F --> I[🛠️ AWS API Calls]
        G --> I
        H --> I
        
        I --> J{Permission Policy Check}
        J -->|✅ Allowed| K[✅ Action Executed]
        J -->|❌ Denied| L[🚫 Action Denied]
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#FF9900,stroke:#232F3E,color:#fff
        style E fill:#3FB34F,stroke:#232F3E,color:#fff
        style K fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#FF6B35,stroke:#232F3E,color:#fff
        style L fill:#FF6B35,stroke:#232F3E,color:#fff
    """

def create_sts_flow_mermaid():
    """Create mermaid diagram for STS flow"""
    return """
    graph TD
        A[Client Application] --> B[AssumeRole Request]
        B --> C[AWS STS Service]
        
        C --> D{Validate Trust Policy}
        D -->|Valid| E[Generate Temporary Credentials]
        D -->|Invalid| F[Return Error]
        
        E --> G[Temporary Access Key]
        E --> H[Temporary Secret Key]
        E --> I[Session Token]
        E --> J[Expiration Time]
        
        G --> K[Make AWS API Calls]
        H --> K
        I --> K
        
        K --> L[AWS Service]
        L --> M{Check Permissions}
        M -->|Allowed| N[Execute Action]
        M -->|Denied| O[Return Error]
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#FF9900,stroke:#232F3E,color:#fff
        style E fill:#3FB34F,stroke:#232F3E,color:#fff
        style L fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_policy_evaluation_mermaid():
    """Create mermaid diagram for policy evaluation"""
    return """
    graph TD
        A[API Request] --> B[Identity-based Policies]
        B --> C[Resource-based Policies]
        C --> D[Permission Boundaries]
        D --> E[Service Control Policies]
        
        E --> F{Explicit Deny?}
        F -->|Yes| G[❌ DENY]
        F -->|No| H{Explicit Allow?}
        
        H -->|Yes| I[✅ ALLOW]
        H -->|No| J[❌ DENY by Default]
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style B fill:#FF9900,stroke:#232F3E,color:#fff
        style C fill:#FF9900,stroke:#232F3E,color:#fff
        style D fill:#FF9900,stroke:#232F3E,color:#fff
        style E fill:#FF9900,stroke:#232F3E,color:#fff
        style I fill:#3FB34F,stroke:#232F3E,color:#fff
        style G fill:#FF6B35,stroke:#232F3E,color:#fff
        style J fill:#FF6B35,stroke:#232F3E,color:#fff
    """

def aws_iam_tab():
    """Content for AWS Identity and Access Management tab"""
    st.markdown("## 🔐 AWS Identity and Access Management")
    st.markdown("*Policies and Technologies used to ensure the appropriate access to technology resources*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **AWS Identity and Access Management (IAM)** enables you to manage access to AWS services and resources securely. 
    Using IAM, you can create and manage AWS users and groups, and use permissions to allow and deny their access to AWS resources.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # IAM Overview Architecture
    st.markdown("### 🏗️ IAM Components Overview")
    common.mermaid(create_iam_overview_mermaid(), height=200)
    
    # IAM Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 👥\n**Users**")
        st.markdown("Individual Identities")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 📂\n**Groups**")
        st.markdown("Collection of Users")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🎭\n**Roles**")
        st.markdown("Temporary Access")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 📜\n**Policies**")
        st.markdown("Permission Documents")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive IAM Builder
    st.markdown("### 🛠️ Interactive IAM Setup Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👤 User Configuration")
        user_name = st.text_input("IAM User Name:", "john-developer")
        user_type = st.selectbox("User Type:", [
            "Developer", "Administrator", "Read-Only User", "Service Account"
        ])
        
        access_type = st.multiselect("Access Type:", [
            "AWS Management Console", "Programmatic Access", "CLI Access"
        ], default=["AWS Management Console"])
        
        mfa_enabled = st.checkbox("Enable Multi-Factor Authentication", value=True)
    
    with col2:
        st.markdown("### 📂 Group Assignment")
        available_groups = [
            "Developers", "Administrators", "ReadOnlyUsers", "PowerUsers", "BillingAdmins"
        ]
        selected_groups = st.multiselect("Assign to Groups:", available_groups)
        
        custom_policies = st.multiselect("Attach Custom Policies:", [
            "S3-ReadWrite", "EC2-Management", "Lambda-Execute", "DynamoDB-Access"
        ])
    
    if st.button("🚀 Create IAM Configuration", use_container_width=True):
        total_permissions = len(selected_groups) + len(custom_policies)
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ IAM User Configuration Created!
        
        **User Details:**
        - **Username**: {user_name}
        - **Type**: {user_type}
        - **Access Methods**: {', '.join(access_type)}
        - **MFA Enabled**: {'✅ Yes' if mfa_enabled else '❌ No'}
        
        **Permission Sources:**
        - **Group Memberships**: {len(selected_groups)} groups
        - **Custom Policies**: {len(custom_policies)} policies
        - **Total Permission Sources**: {total_permissions}
        
        🔐 **Security Score**: {85 + (10 if mfa_enabled else 0)}/100
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Users vs Groups vs Roles
    st.markdown("### ⚖️ Users vs Groups vs Roles")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 👤 IAM Users
        
        **Characteristics:**
        - **Individual identity** in AWS
        - Long-term credentials
        - Direct policy attachment
        - **Permanent access**
        
        **Best For:**
        - Human users
        - Individual developers
        - Service accounts (legacy)
        - **Direct AWS access**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📂 IAM Groups
        
        **Characteristics:**
        - **Collection of users**
        - Simplified permission management
        - Policy inheritance
        - **Organizational structure**
        
        **Best For:**
        - Team-based permissions
        - Role-based access
        - Permission standardization
        - **Scalable management**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎭 IAM Roles
        
        **Characteristics:**
        - **No permanent credentials**
        - Temporary access tokens
        - Assumable by entities
        - **Cross-service access**
        
        **Best For:**
        - Service-to-service access
        - Cross-account access
        - Temporary permissions
        - **Modern security practices**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # IAM Best Practices
    st.markdown("### 💡 IAM Security Best Practices")
    
    best_practices_data = {
        'Practice': [
            'Principle of Least Privilege',
            'Use IAM Roles for Applications', 
            'Enable Multi-Factor Authentication',
            'Rotate Credentials Regularly',
            'Use Groups for User Management',
            'Monitor and Audit Access'
        ],
        'Description': [
            'Grant only the permissions needed to perform tasks',
            'Avoid embedding long-term credentials in applications',
            'Add extra layer of security for sensitive operations',
            'Change access keys and passwords regularly',
            'Manage permissions at group level, not individual users',
            'Use CloudTrail and Access Analyzer for monitoring'
        ],
        'Security Impact': ['High', 'Very High', 'High', 'Medium', 'Medium', 'High'],
        'Implementation Difficulty': ['Medium', 'Low', 'Low', 'Medium', 'Low', 'Medium']
    }
    
    df_practices = pd.DataFrame(best_practices_data)
    st.dataframe(df_practices, use_container_width=True)
    
    # IAM Policy Types
    st.markdown("### 📜 IAM Policy Types")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 Identity-based Policies
        - Attached to **users, groups, or roles**
        - Define what the identity can do
        - Most common policy type
        - Can be AWS managed or customer managed
        
        **Examples:**
        - AmazonS3ReadOnlyAccess
        - PowerUserAccess
        - Custom developer policy
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🗂️ Resource-based Policies
        - Attached to **AWS resources**
        - Define who can access the resource
        - Specify permissions for the resource
        - Enable cross-account access
        
        **Examples:**
        - S3 bucket policies
        - KMS key policies
        - Lambda function policies
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: IAM User and Group Management")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Complete IAM user and group management with boto3
import boto3
import json
from datetime import datetime

def create_iam_user_with_groups(username, groups, policies=None):
    """Create IAM user and assign to groups with policies"""
    iam = boto3.client('iam')
    
    try:
        # Create IAM user
        user_response = iam.create_user(
            UserName=username,
            Tags=[
                {'Key': 'Created', 'Value': datetime.now().strftime('%Y-%m-%d')},
                {'Key': 'Purpose', 'Value': 'Developer Access'},
                {'Key': 'Environment', 'Value': 'Production'}
            ]
        )
        print(f"✅ Created user: {username}")
        
        # Create login profile for console access
        try:
            iam.create_login_profile(
                UserName=username,
                Password='TempPassword123!',
                PasswordResetRequired=True
            )
            print(f"🔑 Console access enabled for {username}")
        except Exception as e:
            print(f"⚠️ Console access setup failed: {e}")
        
        # Add user to groups
        for group_name in groups:
            try:
                iam.add_user_to_group(
                    GroupName=group_name,
                    UserName=username
                )
                print(f"📂 Added {username} to group: {group_name}")
            except Exception as e:
                print(f"❌ Failed to add to group {group_name}: {e}")
        
        # Attach additional policies if specified
        if policies:
            for policy_arn in policies:
                try:
                    iam.attach_user_policy(
                        UserName=username,
                        PolicyArn=policy_arn
                    )
                    print(f"📜 Attached policy: {policy_arn.split('/')[-1]}")
                except Exception as e:
                    print(f"❌ Failed to attach policy {policy_arn}: {e}")
        
        # Create access keys for programmatic access
        try:
            access_key_response = iam.create_access_key(UserName=username)
            access_key = access_key_response['AccessKey']
            
            print(f"🔐 Access Key Created:")
            print(f"   Access Key ID: {access_key['AccessKeyId']}")
            print(f"   Secret Access Key: {access_key['SecretAccessKey']}")
            print("   ⚠️ Store these credentials securely!")
            
        except Exception as e:
            print(f"❌ Failed to create access keys: {e}")
        
        return user_response['User']
        
    except Exception as e:
        print(f"❌ Failed to create user {username}: {e}")
        return None

def create_iam_group_with_policies(group_name, policy_arns, description=""):
    """Create IAM group and attach policies"""
    iam = boto3.client('iam')
    
    try:
        # Create group
        group_response = iam.create_group(
            GroupName=group_name,
            Path='/',
        )
        print(f"✅ Created group: {group_name}")
        
        # Attach policies to group
        for policy_arn in policy_arns:
            try:
                iam.attach_group_policy(
                    GroupName=group_name,
                    PolicyArn=policy_arn
                )
                print(f"📜 Attached policy to {group_name}: {policy_arn.split('/')[-1]}")
            except Exception as e:
                print(f"❌ Failed to attach policy {policy_arn}: {e}")
        
        return group_response['Group']
        
    except Exception as e:
        print(f"❌ Failed to create group {group_name}: {e}")
        return None

def create_custom_policy(policy_name, policy_document, description=""):
    """Create custom IAM policy"""
    iam = boto3.client('iam')
    
    # Example policy document for S3 read-write access
    if not policy_document:
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject"
                    ],
                    "Resource": "arn:aws:s3:::my-app-bucket/*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:ListBucket"
                    ],
                    "Resource": "arn:aws:s3:::my-app-bucket"
                }
            ]
        }
    
    try:
        policy_response = iam.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document),
            Description=description or f"Custom policy: {policy_name}"
        )
        
        policy_arn = policy_response['Policy']['Arn']
        print(f"✅ Created custom policy: {policy_name}")
        print(f"   Policy ARN: {policy_arn}")
        
        return policy_arn
        
    except Exception as e:
        print(f"❌ Failed to create policy {policy_name}: {e}")
        return None

def setup_developer_team():
    """Complete setup for a development team"""
    print("🚀 Setting up Developer Team IAM Configuration")
    print("=" * 50)
    
    # Create developer group with appropriate policies
    developer_policies = [
        'arn:aws:iam::aws:policy/PowerUserAccess',
        'arn:aws:iam::aws:policy/IAMReadOnlyAccess'
    ]
    
    group = create_iam_group_with_policies(
        group_name='Developers',
        policy_arns=developer_policies,
        description='Group for application developers'
    )
    
    # Create custom policy for S3 access
    s3_policy_arn = create_custom_policy(
        policy_name='DeveloperS3Access',
        policy_document=None,  # Uses default S3 read-write policy
        description='S3 access for development team'
    )
    
    # Create individual developer users
    developers = ['alice-dev', 'bob-dev', 'charlie-dev']
    
    for username in developers:
        user = create_iam_user_with_groups(
            username=username,
            groups=['Developers'],
            policies=[s3_policy_arn] if s3_policy_arn else []
        )
        
        if user:
            print(f"👤 Developer {username} setup complete")
    
    print("\n🎯 Team Setup Summary:")
    print(f"✅ Created group: Developers")
    print(f"✅ Created {len(developers)} developer users")
    print(f"✅ Applied PowerUser and custom S3 policies")
    print("⚠️ Remember to:")
    print("  - Enable MFA for all users")
    print("  - Distribute credentials securely")
    print("  - Set up credential rotation schedule")

def audit_iam_permissions(username):
    """Audit permissions for a specific user"""
    iam = boto3.client('iam')
    
    print(f"🔍 Auditing permissions for user: {username}")
    print("=" * 40)
    
    try:
        # Get user details
        user = iam.get_user(UserName=username)
        print(f"User: {user['User']['UserName']}")
        print(f"Created: {user['User']['CreateDate']}")
        
        # Get directly attached policies
        attached_policies = iam.list_attached_user_policies(UserName=username)
        print(f"\n📜 Directly Attached Policies: {len(attached_policies['AttachedPolicies'])}")
        for policy in attached_policies['AttachedPolicies']:
            print(f"  - {policy['PolicyName']} ({policy['PolicyArn']})")
        
        # Get inline policies
        inline_policies = iam.list_user_policies(UserName=username)
        print(f"\n📝 Inline Policies: {len(inline_policies['PolicyNames'])}")
        for policy_name in inline_policies['PolicyNames']:
            print(f"  - {policy_name}")
        
        # Get group memberships
        groups = iam.get_groups_for_user(UserName=username)
        print(f"\n📂 Group Memberships: {len(groups['Groups'])}")
        
        for group in groups['Groups']:
            print(f"  Group: {group['GroupName']}")
            
            # Get policies attached to each group
            group_policies = iam.list_attached_group_policies(GroupName=group['GroupName'])
            for policy in group_policies['AttachedPolicies']:
                print(f"    - {policy['PolicyName']}")
        
        # Get access keys
        access_keys = iam.list_access_keys(UserName=username)
        print(f"\n🔑 Access Keys: {len(access_keys['AccessKeyMetadata'])}")
        for key in access_keys['AccessKeyMetadata']:
            print(f"  - {key['AccessKeyId']} (Status: {key['Status']})")
        
    except Exception as e:
        print(f"❌ Error auditing user {username}: {e}")

# Example usage
if __name__ == "__main__":
    # Set up complete development team
    setup_developer_team()
    
    # Audit specific user permissions
    audit_iam_permissions('alice-dev')
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def iam_roles_tab():
    """Content for IAM Roles tab"""
    st.markdown("## 👤 IAM Roles")
    st.markdown("*Roles are a way for users to temporarily gain permissions*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **IAM Roles** are AWS identities with permission policies that determine what the identity can and cannot do in AWS. 
    However, instead of being uniquely associated with one person, a role is intended to be assumable by anyone who needs it.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Role Assumption Process
    st.markdown("### 🔄 Role Assumption Process")
    common.mermaid(create_role_assumption_mermaid(), height=200)
    
    # Role Types
    st.markdown("### 🎭 Types of IAM Roles")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🖥️ Service Roles
        - **AWS services** assume these roles
        - Grant services permission to act on your behalf
        - Common for **EC2, Lambda, ECS**
        
        **Examples:**
        - EC2 instance accessing S3
        - Lambda function writing to DynamoDB
        - ECS task reading from Parameter Store
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔄 Cross-Account Roles
        - Allow access **between AWS accounts**
        - Secure way to share resources
        - **Temporary access** only
        
        **Examples:**
        - External auditor access
        - Partner organization integration
        - Multi-account architecture
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 👥 Federated User Roles
        - For users from **external identity providers**
        - Single Sign-On (SSO) integration
        - **Google, Active Directory, SAML**
        
        **Examples:**
        - Corporate Active Directory users
        - Google Workspace integration
        - SAML federated access
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📱 Application Roles
        - For **applications and services**
        - Replace hardcoded credentials
        - **Dynamic permission assignment**
        
        **Examples:**
        - Web application accessing databases
        - Microservices communication
        - Container-based applications
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Role Builder
    st.markdown("### 🛠️ Interactive IAM Role Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Role Configuration")
        role_name = st.text_input("Role Name:", "MyApplicationRole")
        role_type = st.selectbox("Role Type:", [
            "AWS Service Role", "Cross-Account Role", "Web Identity Role", "SAML Role"
        ])
        
        if role_type == "AWS Service Role":
            trusted_service = st.selectbox("Trusted Service:", [
                "ec2.amazonaws.com", "lambda.amazonaws.com", "ecs-tasks.amazonaws.com",
                "apigateway.amazonaws.com", "glue.amazonaws.com"
            ])
        elif role_type == "Cross-Account Role":
            trusted_account = st.text_input("Trusted Account ID:", "123456789012")
        else:
            trusted_provider = st.text_input("Identity Provider ARN:", "arn:aws:iam::123456789012:saml-provider/ExampleProvider")
    
    with col2:
        st.markdown("### 🛡️ Permissions")
        permission_type = st.selectbox("Permission Strategy:", [
            "AWS Managed Policies", "Custom Policy", "Mixed Approach"
        ])
        
        if permission_type in ["AWS Managed Policies", "Mixed Approach"]:
            managed_policies = st.multiselect("AWS Managed Policies:", [
                "AmazonS3ReadOnlyAccess", "AmazonDynamoDBFullAccess", "AWSLambdaBasicExecutionRole",
                "AmazonEC2ReadOnlyAccess", "CloudWatchLogsFullAccess"
            ])
        
        max_session_duration = st.slider("Max Session Duration (hours):", 1, 12, 1)
    
    # Advanced Role Settings
    st.markdown("### ⚙️ Advanced Role Settings")
    col3, col4 = st.columns(2)
    
    with col3:
        require_mfa = st.checkbox("Require MFA for Role Assumption")
        external_id = st.text_input("External ID (for cross-account):", "")
        
    with col4:
        condition_key = st.selectbox("Additional Condition:", [
            "None", "Source IP", "Time-based", "Tag-based"
        ])
        
        if condition_key == "Time-based":
            allowed_hours = st.text_input("Allowed Hours (e.g., 09:00-17:00):", "09:00-17:00")
    
    if st.button("🚀 Create IAM Role", use_container_width=True):
        # Generate role configuration
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {},
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        if role_type == "AWS Service Role":
            trust_policy["Statement"][0]["Principal"]["Service"] = trusted_service
        elif role_type == "Cross-Account Role":
            trust_policy["Statement"][0]["Principal"]["AWS"] = f"arn:aws:iam::{trusted_account}:root"
        
        # Add conditions if specified
        conditions = {}
        if require_mfa:
            conditions["Bool"] = {"aws:MultiFactorAuthPresent": "true"}
        if external_id:
            conditions["StringEquals"] = {"sts:ExternalId": external_id}
        
        if conditions:
            trust_policy["Statement"][0]["Condition"] = conditions
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ IAM Role Configuration Generated!
        
        **Role Details:**
        - **Role Name**: {role_name}
        - **Type**: {role_type}
        - **Max Session Duration**: {max_session_duration} hours
        - **MFA Required**: {'✅ Yes' if require_mfa else '❌ No'}
        - **External ID**: {external_id if external_id else 'Not configured'}
        
        **Trust Policy Generated:**
        ```json
        {json.dumps(trust_policy, indent=2)}
        ```
        
        **Permissions**: {len(managed_policies) if 'managed_policies' in locals() else 0} policies attached
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Trust Policy vs Permission Policy
    st.markdown("### ⚖️ Trust Policy vs Permission Policy")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="trust-policy">', unsafe_allow_html=True)
        st.markdown("""
        ### 📋 Trust Policy
        - **WHO** can assume the role
        - Controls role assumption
        - Defines trusted entities
        - **Primary authentication**
        
        **Key Elements:**
        - Principal (who can assume)
        - Conditions (when/how)
        - External ID (additional security)
        - MFA requirements
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="permission-policy">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔑 Permission Policy
        - **WHAT** the role can do
        - Defines allowed actions
        - Specifies resources
        - **Authorization after assumption**
        
        **Key Elements:**
        - Actions (what can be done)
        - Resources (what can be accessed)
        - Effect (Allow/Deny)
        - Conditions (additional constraints)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Common Role Patterns
    st.markdown("### 🎯 Common IAM Role Patterns")
    
    role_patterns = {
        'Pattern': [
            'EC2 Instance Role',
            'Lambda Execution Role',
            'Cross-Account Access',
            'CI/CD Pipeline Role',
            'Data Processing Role',
            'Monitoring Role'
        ],
        'Trusted Entity': [
            'ec2.amazonaws.com',
            'lambda.amazonaws.com', 
            'External AWS Account',
            'CodeBuild/CodePipeline',
            'glue.amazonaws.com',
            'monitoring.amazonaws.com'
        ],
        'Common Permissions': [
            'S3 access, CloudWatch logs',
            'Basic execution, VPC access',
            'Specific resource access',
            'Deploy permissions, S3 artifacts',
            'Data lake access, ETL permissions',
            'CloudWatch metrics, SNS alerts'
        ],
        'Security Considerations': [
            'Least privilege, instance profile',
            'VPC security, resource-based policies',
            'External ID, MFA requirements',
            'Temporary credentials, audit logs',
            'Data encryption, access patterns',
            'Read-only where possible'
        ]
    }
    
    df_patterns = pd.DataFrame(role_patterns)
    st.dataframe(df_patterns, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: IAM Role Management")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Create and manage IAM roles with boto3
import boto3
import json
from datetime import datetime

def create_service_role(role_name, service_principal, policies, description=""):
    """Create an IAM role for AWS service"""
    iam = boto3.client('iam')
    
    # Define trust policy for the service
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": service_principal
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        # Create the role
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=description or f"Service role for {service_principal}",
            MaxSessionDuration=3600,  # 1 hour
            Tags=[
                {'Key': 'Purpose', 'Value': 'ServiceRole'},
                {'Key': 'CreatedBy', 'Value': 'IAMAutomation'},
                {'Key': 'Created', 'Value': datetime.now().strftime('%Y-%m-%d')}
            ]
        )
        
        role_arn = response['Role']['Arn']
        print(f"✅ Created role: {role_name}")
        print(f"   Role ARN: {role_arn}")
        
        # Attach policies to the role
        for policy_arn in policies:
            try:
                iam.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
                print(f"📜 Attached policy: {policy_arn.split('/')[-1]}")
            except Exception as e:
                print(f"❌ Failed to attach policy {policy_arn}: {e}")
        
        # For EC2 roles, create instance profile
        if service_principal == "ec2.amazonaws.com":
            try:
                iam.create_instance_profile(InstanceProfileName=role_name)
                iam.add_role_to_instance_profile(
                    InstanceProfileName=role_name,
                    RoleName=role_name
                )
                print(f"🖥️ Created instance profile: {role_name}")
            except Exception as e:
                print(f"⚠️ Instance profile creation failed: {e}")
        
        return role_arn
        
    except Exception as e:
        print(f"❌ Failed to create role {role_name}: {e}")
        return None

def create_cross_account_role(role_name, trusted_account_id, policies, external_id=None, require_mfa=False):
    """Create cross-account access role"""
    iam = boto3.client('iam')
    
    # Build trust policy for cross-account access
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": f"arn:aws:iam::{trusted_account_id}:root"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # Add conditions if specified
    conditions = {}
    if external_id:
        conditions["StringEquals"] = {"sts:ExternalId": external_id}
    if require_mfa:
        conditions["Bool"] = {"aws:MultiFactorAuthPresent": "true"}
    
    if conditions:
        trust_policy["Statement"][0]["Condition"] = conditions
    
    try:
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=f"Cross-account access role for account {trusted_account_id}",
            MaxSessionDuration=7200,  # 2 hours for cross-account
            Tags=[
                {'Key': 'Type', 'Value': 'CrossAccount'},
                {'Key': 'TrustedAccount', 'Value': trusted_account_id},
                {'Key': 'ExternalId', 'Value': external_id or 'None'},
                {'Key': 'MFARequired', 'Value': str(require_mfa)}
            ]
        )
        
        role_arn = response['Role']['Arn']
        print(f"✅ Created cross-account role: {role_name}")
        print(f"   Trusted Account: {trusted_account_id}")
        print(f"   External ID: {external_id or 'Not required'}")
        print(f"   MFA Required: {require_mfa}")
        
        # Attach policies
        for policy_arn in policies:
            iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
            print(f"📜 Attached policy: {policy_arn.split('/')[-1]}")
        
        return role_arn
        
    except Exception as e:
        print(f"❌ Failed to create cross-account role: {e}")
        return None

def assume_role_example(role_arn, session_name, external_id=None, mfa_serial=None, mfa_token=None):
    """Example of assuming an IAM role"""
    sts = boto3.client('sts')
    
    assume_role_params = {
        'RoleArn': role_arn,
        'RoleSessionName': session_name,
        'DurationSeconds': 3600  # 1 hour
    }
    
    # Add external ID if required
    if external_id:
        assume_role_params['ExternalId'] = external_id
    
    # Add MFA if required
    if mfa_serial and mfa_token:
        assume_role_params['SerialNumber'] = mfa_serial
        assume_role_params['TokenCode'] = mfa_token
    
    try:
        response = sts.assume_role(**assume_role_params)
        
        credentials = response['Credentials']
        
        print(f"✅ Successfully assumed role: {role_arn}")
        print(f"   Session Name: {session_name}")
        print(f"   Access Key ID: {credentials['AccessKeyId']}")
        print(f"   Expires: {credentials['Expiration']}")
        
        # Create a new boto3 session with temporary credentials
        session = boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )
        
        # Example: Use the session to access AWS services
        s3 = session.client('s3')
        buckets = s3.list_buckets()
        print(f"📁 Can access {len(buckets['Buckets'])} S3 buckets with assumed role")
        
        return session
        
    except Exception as e:
        print(f"❌ Failed to assume role: {e}")
        return None

def audit_role_usage(role_name, days=30):
    """Audit role usage using CloudTrail events"""
    import boto3
    from datetime import datetime, timedelta
    
    cloudtrail = boto3.client('cloudtrail')
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    
    print(f"🔍 Auditing role usage: {role_name}")
    print(f"   Time Range: {start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}")
    print("=" * 50)
    
    try:
        # Look for AssumeRole events
        events = cloudtrail.lookup_events(
            LookupAttributes=[
                {
                    'AttributeKey': 'EventName',
                    'AttributeValue': 'AssumeRole'
                }
            ],
            StartTime=start_time,
            EndTime=end_time
        )
        
        role_assumptions = []
        for event in events['Events']:
            # Check if this event is for our role
            if role_name in str(event.get('Resources', [])):
                role_assumptions.append({
                    'time': event['EventTime'],
                    'user': event['Username'],
                    'source_ip': event.get('SourceIPAddress', 'Unknown'),
                    'user_agent': event.get('UserAgent', 'Unknown')
                })
        
        print(f"📊 Found {len(role_assumptions)} role assumptions")
        
        if role_assumptions:
            print("\n🎯 Recent Role Assumptions:")
            for i, assumption in enumerate(role_assumptions[:10], 1):  # Show last 10
                print(f"{i}. {assumption['time']} - {assumption['user']} from {assumption['source_ip']}")
        else:
            print("ℹ️ No role assumptions found in the specified period")
        
        return role_assumptions
        
    except Exception as e:
        print(f"❌ Error auditing role usage: {e}")
        return []

# Example usage scenarios
def setup_example_roles():
    """Set up common role examples"""
    print("🚀 Setting up example IAM roles")
    print("=" * 40)
    
    # 1. Lambda execution role
    lambda_role = create_service_role(
        role_name='LambdaExecutionRole',
        service_principal='lambda.amazonaws.com',
        policies=[
            'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
            'arn:aws:iam::aws:policy/AmazonDynamoDBReadOnlyAccess'
        ],
        description='Role for Lambda function execution'
    )
    
    # 2. EC2 instance role
    ec2_role = create_service_role(
        role_name='EC2S3AccessRole',
        service_principal='ec2.amazonaws.com',
        policies=[
            'arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess',
            'arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy'
        ],
        description='Role for EC2 instances to access S3 and CloudWatch'
    )
    
    # 3. Cross-account role
    cross_account_role = create_cross_account_role(
        role_name='CrossAccountAuditorRole',
        trusted_account_id='123456789012',
        policies=[
            'arn:aws:iam::aws:policy/ReadOnlyAccess'
        ],
        external_id='unique-external-id-12345',
        require_mfa=True
    )
    
    print(f"\n✅ Role setup complete!")
    print(f"Lambda Role: {lambda_role}")
    print(f"EC2 Role: {ec2_role}")
    print(f"Cross-Account Role: {cross_account_role}")

if __name__ == "__main__":
    setup_example_roles()
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def security_token_service_tab():
    """Content for Security Token Service (STS) tab"""
    st.markdown("## 🎫 Security Token Service (STS)")
    st.markdown("*Request temporary, limited-privilege credentials for AWS IAM*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **AWS Security Token Service (STS)** is a web service that enables you to request temporary, limited-privilege 
    credentials for AWS Identity and Access Management (IAM) users or for users you authenticate (federated users).
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # STS Flow Diagram
    st.markdown("### 🔄 STS Token Generation Flow")
    common.mermaid(create_sts_flow_mermaid(), height=1000)
    
    # STS Operations
    st.markdown("### ⚙️ Key STS Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎭 AssumeRole
        - **Most common** STS operation
        - Assume an IAM role
        - Get temporary credentials
        - **Cross-account access**
        
        **Use Cases:**
        - Service-to-service access
        - Cross-account permissions
        - Temporary elevated privileges
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🌐 AssumeRoleWithWebIdentity
        - For **federated users**
        - Web identity providers
        - **Google, Facebook, Amazon**
        
        **Use Cases:**
        - Mobile applications
        - Web applications
        - Social login integration
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🏢 AssumeRoleWithSAML
        - For **enterprise federation**
        - SAML 2.0 identity providers
        - **Active Directory, ADFS**
        
        **Use Cases:**
        - Corporate SSO
        - Enterprise applications
        - Directory service integration
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔑 GetSessionToken
        - For **existing IAM users**
        - MFA-protected operations
        - **Temporary credentials**
        
        **Use Cases:**
        - MFA-enabled operations
        - Time-limited access
        - Enhanced security workflows
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive STS Token Simulator
    st.markdown("### 🎮 Interactive STS Token Simulator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔧 Token Request Configuration")
        operation_type = st.selectbox("STS Operation:", [
            "AssumeRole", "AssumeRoleWithWebIdentity", "AssumeRoleWithSAML", "GetSessionToken"
        ])
        
        if operation_type == "AssumeRole":
            role_arn = st.text_input("Role ARN:", "arn:aws:iam::123456789012:role/MyApplicationRole")
            session_name = st.text_input("Session Name:", "MyAppSession")
            external_id = st.text_input("External ID (optional):", "")
        elif operation_type == "AssumeRoleWithWebIdentity":
            role_arn = st.text_input("Role ARN:", "arn:aws:iam::123456789012:role/WebIdentityRole")
            web_identity_token = st.text_area("Web Identity Token:", "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...")
        elif operation_type == "GetSessionToken":
            duration = st.slider("Session Duration (seconds):", 900, 129600, 3600)
            
        session_duration = st.slider("Session Duration (hours):", 1, 12, 1)
    
    with col2:
        st.markdown("### 🔒 Security Settings")
        require_mfa = st.checkbox("Require MFA", value=False)
        
        if require_mfa:
            mfa_serial = st.text_input("MFA Device Serial:", "arn:aws:iam::123456789012:mfa/user")
            mfa_token = st.text_input("MFA Token:", "123456")
        
        source_ip_condition = st.checkbox("Restrict Source IP")
        if source_ip_condition:
            allowed_ip = st.text_input("Allowed IP/CIDR:", "203.0.113.0/24")
        
        time_condition = st.checkbox("Time-based Restriction")
        if time_condition:
            allowed_time_range = st.text_input("Allowed Hours (UTC):", "09:00-17:00")
    
    if st.button("🎫 Generate STS Token", use_container_width=True):
        # Simulate token generation
        import time
        access_key = f"ASIA{''.join(np.random.choice(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'), 16))}"
        secret_key = f"{''.join(np.random.choice(list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'), 40))}"
        session_token = f"{''.join(np.random.choice(list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'), 400))}"
        
        expiration_time = pd.Timestamp.now() + pd.Timedelta(hours=session_duration)
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ STS Token Generated Successfully!
        
        **Token Details:**
        - **Operation**: {operation_type}
        - **Access Key ID**: {access_key}
        - **Secret Access Key**: {secret_key[:10]}...
        - **Session Token**: {session_token[:50]}...
        - **Expiration**: {expiration_time.strftime('%Y-%m-%d %H:%M:%S UTC')}
        
        **Security Features:**
        - **MFA Protected**: {'✅ Yes' if require_mfa else '❌ No'}
        - **IP Restricted**: {'✅ Yes' if source_ip_condition else '❌ No'}
        - **Time Limited**: {session_duration} hours
        - **Token Size**: ~{len(session_token)} characters
        
        ⚠️ **Important**: Store these credentials securely and never commit to version control!
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Temporary Credentials Properties
    st.markdown("### 🔍 Temporary Credentials Properties")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⏰ Time-Limited
        - **Automatic expiration**
        - 15 minutes to 12 hours
        - Cannot be renewed
        - **Must be refreshed**
        
        **Benefits:**
        - Reduced security risk
        - Natural credential rotation
        - Limited blast radius
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 Least Privilege
        - **Limited permissions**
        - Based on role policies
        - Cannot exceed role limits
        - **Session policies** can restrict further
        
        **Benefits:**
        - Principle of least privilege
        - Granular access control
        - Risk mitigation
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔄 Dynamic
        - **Generated on demand**
        - Unique per session
        - Tracked independently
        - **Auditable**
        
        **Benefits:**
        - No hardcoded credentials
        - Better security posture
        - Detailed audit trails
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # STS Use Cases
    st.markdown("### 🎯 Common STS Use Cases")
    
    use_cases_data = {
        'Use Case': [
            'Cross-Account Access',
            'Service-to-Service Auth',
            'Mobile Applications', 
            'Web Federation',
            'Enterprise SSO',
            'CI/CD Pipelines'
        ],
        'STS Operation': [
            'AssumeRole',
            'AssumeRole',
            'AssumeRoleWithWebIdentity',
            'AssumeRoleWithWebIdentity', 
            'AssumeRoleWithSAML',
            'AssumeRole'
        ],
        'Duration': ['1-12 hours', '15 min-1 hour', '1-12 hours', '1-12 hours', '1-12 hours', '15 min-1 hour'],
        'Security Features': [
            'External ID, MFA',
            'Service principals',
            'App-specific tokens',
            'OAuth/OIDC integration',
            'SAML assertions',
            'Time-limited access'
        ]
    }
    
    df_use_cases = pd.DataFrame(use_cases_data)
    st.dataframe(df_use_cases, use_container_width=True)
    
    # Token Rotation and Best Practices
    st.markdown("### 💡 STS Best Practices")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🛡️ Security Best Practices
    
    **Token Management:**
    - **Minimize session duration** - use the shortest time needed
    - **Implement token refresh** before expiration
    - **Never store tokens** in persistent storage
    - **Use secure transmission** channels only
    
    **Access Control:**
    - **Apply session policies** to further restrict permissions
    - **Use condition keys** for additional security (IP, MFA, time)
    - **Monitor token usage** with CloudTrail
    - **Implement least privilege** principle consistently
    
    **Error Handling:**
    - **Handle token expiration** gracefully
    - **Implement retry logic** with exponential backoff
    - **Log security events** for audit purposes
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: STS Operations")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Complete STS operations with boto3
import boto3
import json
from datetime import datetime, timedelta
import time

class STSManager:
    """Manage STS operations and temporary credentials"""
    
    def __init__(self):
        self.sts = boto3.client('sts')
        self.credentials_cache = {}
    
    def assume_role(self, role_arn, session_name, duration_seconds=3600, 
                   external_id=None, mfa_serial=None, mfa_token=None, session_policy=None):
        """Assume an IAM role and get temporary credentials"""
        
        assume_role_params = {
            'RoleArn': role_arn,
            'RoleSessionName': session_name,
            'DurationSeconds': duration_seconds
        }
        
        # Add optional parameters
        if external_id:
            assume_role_params['ExternalId'] = external_id
        
        if mfa_serial and mfa_token:
            assume_role_params['SerialNumber'] = mfa_serial
            assume_role_params['TokenCode'] = mfa_token
        
        if session_policy:
            assume_role_params['Policy'] = json.dumps(session_policy)
        
        try:
            response = self.sts.assume_role(**assume_role_params)
            credentials = response['Credentials']
            
            # Cache credentials with expiration check
            cache_key = f"{role_arn}:{session_name}"
            self.credentials_cache[cache_key] = {
                'credentials': credentials,
                'expiration': credentials['Expiration'],
                'cached_at': datetime.now()
            }
            
            print(f"✅ Successfully assumed role: {role_arn}")
            print(f"   Session: {session_name}")
            print(f"   Expires: {credentials['Expiration']}")
            
            return credentials
            
        except Exception as e:
            print(f"❌ Failed to assume role: {e}")
            raise
    
    def assume_role_with_web_identity(self, role_arn, web_identity_token, 
                                    session_name, duration_seconds=3600):
        """Assume role using web identity (OAuth/OIDC)"""
        
        try:
            response = self.sts.assume_role_with_web_identity(
                RoleArn=role_arn,
                RoleSessionName=session_name,
                WebIdentityToken=web_identity_token,
                DurationSeconds=duration_seconds
            )
            
            credentials = response['Credentials']
            
            print(f"✅ Assumed role with web identity: {role_arn}")
            print(f"   Provider User ID: {response.get('SubjectFromWebIdentityToken', 'Unknown')}")
            
            return credentials
            
        except Exception as e:
            print(f"❌ Failed to assume role with web identity: {e}")
            raise
    
    def get_session_token(self, duration_seconds=3600, mfa_serial=None, mfa_token=None):
        """Get session token for existing IAM user (with optional MFA)"""
        
        params = {'DurationSeconds': duration_seconds}
        
        if mfa_serial and mfa_token:
            params['SerialNumber'] = mfa_serial
            params['TokenCode'] = mfa_token
        
        try:
            response = self.sts.get_session_token(**params)
            credentials = response['Credentials']
            
            print(f"✅ Generated session token")
            print(f"   Duration: {duration_seconds} seconds")
            print(f"   MFA Used: {bool(mfa_serial)}")
            
            return credentials
            
        except Exception as e:
            print(f"❌ Failed to get session token: {e}")
            raise
    
    def create_boto3_session(self, credentials):
        """Create boto3 session from temporary credentials"""
        
        return boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )
    
    def refresh_credentials_if_needed(self, cache_key, role_arn, session_name, buffer_minutes=5):
        """Refresh credentials if they're about to expire"""
        
        if cache_key not in self.credentials_cache:
            return None
        
        cached_creds = self.credentials_cache[cache_key]
        expiration = cached_creds['expiration']
        
        # Check if credentials expire within buffer time
        buffer_time = datetime.now(expiration.tzinfo) + timedelta(minutes=buffer_minutes)
        
        if expiration <= buffer_time:
            print(f"🔄 Refreshing credentials expiring at {expiration}")
            return self.assume_role(role_arn, session_name)
        
        print(f"✅ Using cached credentials (expires: {expiration})")
        return cached_creds['credentials']
    
    def get_caller_identity(self, session=None):
        """Get information about the current identity"""
        
        client = session.client('sts') if session else self.sts
        
        try:
            response = client.get_caller_identity()
            
            print(f"🆔 Caller Identity:")
            print(f"   User ID: {response['UserId']}")
            print(f"   Account: {response['Account']}")
            print(f"   ARN: {response['Arn']}")
            
            return response
            
        except Exception as e:
            print(f"❌ Failed to get caller identity: {e}")
            return None

def create_session_policy():
    """Create a session policy to further restrict permissions"""
    
    session_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::my-specific-bucket",
                    "arn:aws:s3:::my-specific-bucket/*"
                ]
            },
            {
                "Effect": "Deny",
                "Action": "*",
                "Resource": "*",
                "Condition": {
                    "DateGreaterThan": {
                        "aws:CurrentTime": "2024-12-31T23:59:59Z"
                    }
                }
            }
        ]
    }
    
    return session_policy

def demonstrate_cross_account_access():
    """Demonstrate cross-account role assumption"""
    
    sts_manager = STSManager()
    
    # Configuration for cross-account access
    cross_account_role = "arn:aws:iam::123456789012:role/CrossAccountRole"
    session_name = "CrossAccountSession"
    external_id = "unique-external-identifier-12345"
    
    try:
        # Assume cross-account role
        credentials = sts_manager.assume_role(
            role_arn=cross_account_role,
            session_name=session_name,
            external_id=external_id,
            duration_seconds=3600
        )
        
        # Create session with temporary credentials
        cross_account_session = sts_manager.create_boto3_session(credentials)
        
        # Verify identity in the other account
        sts_manager.get_caller_identity(cross_account_session)
        
        # Use the session to access resources
        s3 = cross_account_session.client('s3')
        
        try:
            buckets = s3.list_buckets()
            print(f"📁 Cross-account S3 access successful: {len(buckets['Buckets'])} buckets")
        except Exception as e:
            print(f"❌ S3 access failed: {e}")
        
        return cross_account_session
        
    except Exception as e:
        print(f"❌ Cross-account access failed: {e}")
        return None

def monitor_sts_usage():
    """Monitor STS token usage with CloudTrail"""
    
    cloudtrail = boto3.client('cloudtrail')
    
    try:
        # Look for STS events in the last 24 hours
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        
        sts_events = cloudtrail.lookup_events(
            LookupAttributes=[
                {
                    'AttributeKey': 'EventName',
                    'AttributeValue': 'AssumeRole'
                }
            ],
            StartTime=start_time,
            EndTime=end_time
        )
        
        print(f"🔍 STS Events in last 24 hours: {len(sts_events['Events'])}")
        
        for event in sts_events['Events'][:5]:  # Show first 5 events
            print(f"   {event['EventTime']} - {event['Username']} - {event.get('SourceIPAddress', 'Unknown IP')}")
        
        return sts_events['Events']
        
    except Exception as e:
        print(f"❌ Error monitoring STS usage: {e}")
        return []

# Example usage scenarios
def main_sts_examples():
    """Run comprehensive STS examples"""
    
    print("🚀 AWS STS Operations Examples")
    print("=" * 50)
    
    sts_manager = STSManager()
    
    # Example 1: Basic role assumption
    print("\n1️⃣ Basic Role Assumption")
    try:
        credentials = sts_manager.assume_role(
            role_arn="arn:aws:iam::123456789012:role/MyApplicationRole",
            session_name="MyAppSession",
            duration_seconds=3600
        )
        
        # Use credentials
        session = sts_manager.create_boto3_session(credentials)
        sts_manager.get_caller_identity(session)
        
    except Exception as e:
        print(f"Example 1 failed: {e}")
    
    # Example 2: Role assumption with session policy
    print("\n2️⃣ Role with Session Policy")
    try:
        session_policy = create_session_policy()
        
        credentials = sts_manager.assume_role(
            role_arn="arn:aws:iam::123456789012:role/RestrictedRole",
            session_name="RestrictedSession",
            session_policy=session_policy
        )
        
        print("✅ Session policy applied - permissions further restricted")
        
    except Exception as e:
        print(f"Example 2 failed: {e}")
    
    # Example 3: Cross-account access
    print("\n3️⃣ Cross-Account Access")
    cross_account_session = demonstrate_cross_account_access()
    
    # Example 4: Monitor usage
    print("\n4️⃣ Monitor STS Usage")
    events = monitor_sts_usage()
    
    print(f"\n✅ STS Examples completed - {len(events)} events found")

if __name__ == "__main__":
    main_sts_examples()
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def policy_interpretation_tab():
    """Content for Policy Interpretation tab"""
    st.markdown("## 📜 Policy Interpretation")
    st.markdown("*IAM policies are the bedrock of strong IAM security*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **IAM Policies** are JSON documents that define permissions in AWS. Understanding how to read and interpret 
    these policies is crucial for implementing proper security controls and troubleshooting access issues.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Policy Structure
    st.markdown("### 📋 IAM Policy Structure")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="policy-box">', unsafe_allow_html=True)
        st.markdown("""
        ```json
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::my-bucket/*",
                    "Principal": "arn:aws:iam::123456789012:user/alice",
                    "Condition": {
                        "StringEquals": {
                            "s3:ExistingObjectTag/Project": "DataAnalytics"
                        }
                    }
                }
            ]
        }
        ```
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔍 Policy Elements
        
        **Version**: Policy language version
        - `2012-10-17` (current)
        - Required element
        
        **Statement**: Core policy element
        - Array of individual statements
        - Each statement is evaluated
        
        **Effect**: Allow or Deny
        - `Allow` - grants permission
        - `Deny` - explicitly denies
        
        **Action**: What can be done
        - AWS service operations
        - Supports wildcards
        
        **Resource**: What it applies to
        - AWS resource ARNs
        - Can use wildcards
        
        **Principal**: Who (resource policies)
        - Users, roles, accounts
        - Not used in identity policies
        
        **Condition**: When it applies
        - Optional constraints
        - Context-based conditions
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Policy Builder
    st.markdown("### 🛠️ Interactive Policy Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚙️ Policy Configuration")
        effect = st.selectbox("Effect:", ["Allow", "Deny"])
        
        service = st.selectbox("AWS Service:", [
            "s3", "ec2", "lambda", "dynamodb", "iam", "cloudwatch", "sns", "sqs"
        ])
        
        action_type = st.selectbox("Action Scope:", [
            "Specific Action", "Service Wildcard", "Read Only", "Full Access"
        ])
        
        if action_type == "Specific Action":
            if service == "s3":
                action = st.selectbox("S3 Action:", ["GetObject", "PutObject", "DeleteObject", "ListBucket"])
            elif service == "ec2":
                action = st.selectbox("EC2 Action:", ["DescribeInstances", "RunInstances", "TerminateInstances", "StartInstances"])
            else:
                action = st.text_input("Custom Action:", f"{service}:DescribeInstances")
        else:
            action = f"{service}:*" if action_type == "Service Wildcard" else f"{service}:Describe*"
    
    with col2:
        st.markdown("### 🎯 Resource & Conditions")
        resource_type = st.selectbox("Resource Scope:", [
            "All Resources", "Specific ARN", "Wildcard Pattern"
        ])
        
        if resource_type == "Specific ARN":
            if service == "s3":
                resource = st.text_input("S3 Resource:", "arn:aws:s3:::my-bucket/*")
            else:
                resource = st.text_input("Resource ARN:", f"arn:aws:{service}:us-east-1:123456789012:*")
        elif resource_type == "Wildcard Pattern":
            resource = st.text_input("Resource Pattern:", f"arn:aws:{service}:*:*:*")
        else:
            resource = "*"
        
        add_condition = st.checkbox("Add Condition")
        if add_condition:
            condition_key = st.selectbox("Condition Key:", [
                "aws:CurrentTime", "aws:SourceIp", "s3:ExistingObjectTag/Project",
                "ec2:InstanceType", "aws:MultiFactorAuthPresent"
            ])
            condition_value = st.text_input("Condition Value:", "DataAnalytics")
    
    if st.button("🔨 Generate IAM Policy", use_container_width=True):
        # Build the policy
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": effect,
                    "Action": action if action_type == "Specific Action" else f"{service}:*",
                    "Resource": resource
                }
            ]
        }
        
        # Add condition if specified
        if add_condition:
            condition_operator = "StringEquals" if "Tag" in condition_key else "IpAddress" if "SourceIp" in condition_key else "StringEquals"
            policy["Statement"][0]["Condition"] = {
                condition_operator: {
                    condition_key: condition_value
                }
            }
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        
        md = f'''### ✅ IAM Policy Generated!
        
        **Policy Summary:**
        - **Effect**: {effect}
        - **Service**: {service.upper()}
        - **Action**: {action if action_type == "Specific Action" else f"{service}:*"}
        - **Resource**: {resource}
        - **Conditions**: {'Yes' if add_condition else 'None'}

        **Generated Policy:**
        ```json
        {json.dumps(policy, indent=2)}
        ```
        '''
        st.markdown(md)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Policy Evaluation Flow
    st.markdown("### 🔄 Policy Evaluation Process")
    common.mermaid(create_policy_evaluation_mermaid(), height=400)
    
    # Policy Practice Examples
    st.markdown("### 🧮 Policy Interpretation Practice")
    
    example_policies = {
        "S3 Resource Policy": {
            "policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::123456789012:user/developer"
                        },
                        "Action": "s3:GetObject",
                        "Resource": "arn:aws:s3:::company-data/*",
                        "Condition": {
                            "StringEquals": {
                                "s3:ExistingObjectTag/Department": "Engineering"
                            }
                        }
                    }
                ]
            },
            "explanation": "Allows the 'developer' user to read S3 objects only if they have the 'Department=Engineering' tag"
        },
        "EC2 Tag-Based Policy": {
            "policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": "ec2:*",
                        "Resource": "*",
                        "Condition": {
                            "StringEquals": {
                                "ec2:ResourceTag/Project": "DataAnalytics",
                                "aws:PrincipalTag/Department": "Data"
                            }
                        }
                    }
                ]
            },
            "explanation": "Allows EC2 actions only on instances tagged 'Project=DataAnalytics' by users tagged 'Department=Data'"
        },
        "Time-Based Policy": {
            "policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": "iam:*",
                        "Resource": "*",
                        "Condition": {
                            "DateGreaterThan": {
                                "aws:CurrentTime": "2024-01-01T00:00:00Z"
                            },
                            "DateLessThan": {
                                "aws:CurrentTime": "2024-12-31T23:59:59Z"
                            }
                        }
                    }
                ]
            },
            "explanation": "Allows IAM actions only during the year 2024"
        }
    }
    
    selected_example = st.selectbox("Select Policy Example:", list(example_policies.keys()))
    
    if selected_example:
        example = example_policies[selected_example]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="policy-box">', unsafe_allow_html=True)
            st.markdown(f"```json\n{json.dumps(example['policy'], indent=2)}\n```")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown(f"""
            ### 🔍 Policy Analysis
            
            **What this policy does:**
            {example['explanation']}
            
            **Key Elements:**
            - **Effect**: {example['policy']['Statement'][0]['Effect']}
            - **Actions**: {', '.join(example['policy']['Statement'][0]['Action']) if isinstance(example['policy']['Statement'][0]['Action'], list) else example['policy']['Statement'][0]['Action']}
            - **Resources**: {example['policy']['Statement'][0]['Resource']}
            - **Conditions**: {'Yes' if 'Condition' in example['policy']['Statement'][0] else 'None'}
            """)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Common Policy Patterns
    st.markdown("### 🎯 Common Policy Patterns")
    
    pattern_data = {
        'Pattern': [
            'Least Privilege',
            'Resource-Based Restriction',
            'Time-Based Access',
            'IP-Based Access',
            'MFA Requirement',
            'Tag-Based Access'
        ],
        'Use Case': [
            'Grant minimal required permissions',
            'Restrict access to specific resources',
            'Allow access only during business hours',
            'Restrict access from specific networks',
            'Require MFA for sensitive operations',
            'Control access based on resource tags'
        ],
        'Example Condition': [
            'No wildcards in actions',
            'Specific ARN in Resource',
            'aws:CurrentTime condition',
            'aws:SourceIp condition',
            'aws:MultiFactorAuthPresent',
            'ResourceTag conditions'
        ],
        'Security Benefit': [
            'Minimizes attack surface',
            'Prevents lateral movement',
            'Reduces off-hours risks',
            'Prevents external access',
            'Adds authentication layer',
            'Enables fine-grained control'
        ]
    }
    
    df_patterns = pd.DataFrame(pattern_data)
    st.dataframe(df_patterns, use_container_width=True)
    
    # Policy Troubleshoting
    st.markdown("### 🛠️ Policy Troubleshooting Guide")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ❌ Common Issues
        
        **Access Denied Errors:**
        - Missing Allow statement
        - Explicit Deny rule
        - Condition not met
        - Wrong resource ARN
        
        **Policy Syntax Errors:**
        - Invalid JSON format
        - Incorrect ARN format
        - Typos in action names
        - Missing required elements
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ✅ Troubleshooting Steps
        
        **Use AWS Tools:**
        - IAM Policy Simulator
        - CloudTrail for access logs
        - Access Analyzer
        - IAM Access Advisor
        
        **Manual Checks:**
        - Verify policy attachment
        - Check condition keys
        - Validate ARN formats
        - Test with minimal policy
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Policy Analysis and Validation")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Policy analysis and validation tools
import boto3
import json
from datetime import datetime, timedelta

class IAMPolicyAnalyzer:
    """Analyze and validate IAM policies"""
    
    def __init__(self):
        self.iam = boto3.client('iam')
        self.sts = boto3.client('sts')
    
    def validate_policy_syntax(self, policy_document):
        """Validate policy JSON syntax and structure"""
        
        try:
            # Parse JSON
            if isinstance(policy_document, str):
                policy = json.loads(policy_document)
            else:
                policy = policy_document
            
            validation_results = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'suggestions': []
            }
            
            # Check required fields
            if 'Version' not in policy:
                validation_results['errors'].append("Missing 'Version' field")
                validation_results['valid'] = False
            elif policy['Version'] != '2012-10-17':
                validation_results['warnings'].append("Consider using version '2012-10-17'")
            
            if 'Statement' not in policy:
                validation_results['errors'].append("Missing 'Statement' field")
                validation_results['valid'] = False
            else:
                # Validate each statement
                for i, statement in enumerate(policy['Statement']):
                    self._validate_statement(statement, i, validation_results)
            
            return validation_results
            
        except json.JSONDecodeError as e:
            return {
                'valid': False,
                'errors': [f"Invalid JSON: {str(e)}"],
                'warnings': [],
                'suggestions': []
            }
    
    def _validate_statement(self, statement, index, results):
        """Validate individual policy statement"""
        
        required_fields = ['Effect', 'Action']
        
        for field in required_fields:
            if field not in statement:
                results['errors'].append(f"Statement {index}: Missing '{field}' field")
                results['valid'] = False
        
        # Check Effect value
        if 'Effect' in statement and statement['Effect'] not in ['Allow', 'Deny']:
            results['errors'].append(f"Statement {index}: Effect must be 'Allow' or 'Deny'")
            results['valid'] = False
        
        # Validate Actions
        if 'Action' in statement:
            actions = statement['Action'] if isinstance(statement['Action'], list) else [statement['Action']]
            for action in actions:
                if ':' not in action and action != '*':
                    results['warnings'].append(f"Statement {index}: Action '{action}' may be invalid")
        
        # Check for overly permissive policies
        if statement.get('Effect') == 'Allow':
            if statement.get('Action') == '*' and statement.get('Resource') == '*':
                results['warnings'].append(f"Statement {index}: Very permissive policy - grants all actions on all resources")
            
            if statement.get('Resource') == '*':
                results['suggestions'].append(f"Statement {index}: Consider restricting resources for better security")
    
    def simulate_policy(self, policy_document, action, resource, context=None):
        """Simulate policy evaluation using IAM Policy Simulator"""
        
        try:
            # Get current user ARN for simulation
            caller_identity = self.sts.get_caller_identity()
            principal_arn = caller_identity['Arn']
            
            # Prepare simulation parameters
            simulation_params = {
                'PolicySourceArn': principal_arn,
                'ActionNames': [action],
                'ResourceArns': [resource] if isinstance(resource, str) else resource
            }
            
            # Add policy document if provided
            if policy_document:
                if isinstance(policy_document, dict):
                    policy_document = json.dumps(policy_document)
                simulation_params['PolicyInputList'] = [policy_document]
            
            # Add context keys if provided
            if context:
                context_entries = []
                for key, value in context.items():
                    context_entries.append({
                        'ContextKeyName': key,
                        'ContextKeyValues': [value] if isinstance(value, str) else value,
                        'ContextKeyType': 'string'
                    })
                simulation_params['ContextEntries'] = context_entries
            
            # Run simulation
            response = self.iam.simulate_principal_policy(**simulation_params)
            
            results = []
            for result in response['EvaluationResults']:
                results.append({
                    'action': result['EvalActionName'],
                    'resource': result['EvalResourceName'],
                    'decision': result['EvalDecision'],
                    'matched_statements': result.get('MatchedStatements', []),
                    'missing_context_values': result.get('MissingContextValues', [])
                })
            
            return results
            
        except Exception as e:
            print(f"❌ Policy simulation failed: {e}")
            return []
    
    def analyze_policy_permissions(self, policy_document):
        """Analyze what permissions a policy grants"""
        
        if isinstance(policy_document, str):
            policy = json.loads(policy_document)
        else:
            policy = policy_document
        
        analysis = {
            'services': set(),
            'actions': [],
            'resources': [],
            'conditions': [],
            'risk_level': 'Low'
        }
        
        for statement in policy['Statement']:
            if statement['Effect'] == 'Allow':
                # Extract actions
                actions = statement['Action'] if isinstance(statement['Action'], list) else [statement['Action']]
                analysis['actions'].extend(actions)
                
                # Extract services
                for action in actions:
                    if ':' in action:
                        service = action.split(':')[0]
                        analysis['services'].add(service)
                
                # Extract resources
                resources = statement.get('Resource', [])
                if isinstance(resources, str):
                    resources = [resources]
                analysis['resources'].extend(resources)
                
                # Extract conditions
                if 'Condition' in statement:
                    analysis['conditions'].append(statement['Condition'])
                
                # Assess risk level
                if '*' in actions and '*' in resources:
                    analysis['risk_level'] = 'High'
                elif '*' in actions or '*' in resources:
                    analysis['risk_level'] = 'Medium'
        
        analysis['services'] = list(analysis['services'])
        return analysis
    
    def compare_policies(self, policy1, policy2):
        """Compare two policies and highlight differences"""
        
        analysis1 = self.analyze_policy_permissions(policy1)
        analysis2 = self.analyze_policy_permissions(policy2)
        
        comparison = {
            'services_diff': {
                'only_in_policy1': set(analysis1['services']) - set(analysis2['services']),
                'only_in_policy2': set(analysis2['services']) - set(analysis1['services']),
                'common': set(analysis1['services']) & set(analysis2['services'])
            },
            'actions_diff': {
                'only_in_policy1': set(analysis1['actions']) - set(analysis2['actions']),
                'only_in_policy2': set(analysis2['actions']) - set(analysis1['actions']),
                'common': set(analysis1['actions']) & set(analysis2['actions'])
            },
            'risk_comparison': {
                'policy1_risk': analysis1['risk_level'],
                'policy2_risk': analysis2['risk_level']
            }
        }
        
        return comparison

def demonstrate_policy_analysis():
    """Demonstrate policy analysis capabilities"""
    
    analyzer = IAMPolicyAnalyzer()
    
    # Example policy with various patterns
    test_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject"
                ],
                "Resource": "arn:aws:s3:::my-app-bucket/*",
                "Condition": {
                    "StringEquals": {
                        "s3:ExistingObjectTag/Department": "Engineering"
                    }
                }
            },
            {
                "Effect": "Allow",
                "Action": "dynamodb:Query",
                "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/UserData"
            },
            {
                "Effect": "Deny",
                "Action": "*",
                "Resource": "*",
                "Condition": {
                    "Bool": {
                        "aws:MultiFactorAuthPresent": "false"
                    }
                }
            }
        ]
    }
    
    print("🔍 IAM Policy Analysis Results")
    print("=" * 50)
    
    # 1. Validate syntax
    print("\n1️⃣ Policy Syntax Validation")
    validation = analyzer.validate_policy_syntax(test_policy)
    
    if validation['valid']:
        print("✅ Policy syntax is valid")
    else:
        print("❌ Policy has syntax errors:")
        for error in validation['errors']:
            print(f"   - {error}")
    
    if validation['warnings']:
        print("⚠️ Warnings:")
        for warning in validation['warnings']:
            print(f"   - {warning}")
    
    if validation['suggestions']:
        print("💡 Suggestions:")
        for suggestion in validation['suggestions']:
            print(f"   - {suggestion}")
    
    # 2. Analyze permissions
    print("\n2️⃣ Permission Analysis")
    analysis = analyzer.analyze_policy_permissions(test_policy)
    
    print(f"Services: {', '.join(analysis['services'])}")
    print(f"Actions: {', '.join(analysis['actions'][:5])}{'...' if len(analysis['actions']) > 5 else ''}")
    print(f"Risk Level: {analysis['risk_level']}")
    print(f"Conditions: {len(analysis['conditions'])} conditional statements")
    
    # 3. Simulate specific access
    print("\n3️⃣ Policy Simulation")
    try:
        simulation_results = analyzer.simulate_policy(
            policy_document=test_policy,
            action='s3:GetObject',
            resource='arn:aws:s3:::my-app-bucket/document.pdf',
            context={
                's3:ExistingObjectTag/Department': 'Engineering',
                'aws:MultiFactorAuthPresent': 'true'
            }
        )
        
        for result in simulation_results:
            print(f"Action: {result['action']}")
            print(f"Resource: {result['resource']}")
            print(f"Decision: {result['decision']}")
            print(f"Matched Statements: {len(result['matched_statements'])}")
            
    except Exception as e:
        print(f"⚠️ Simulation requires AWS credentials and permissions: {e}")
    
    return analyzer

def create_policy_best_practices():
    """Generate policy following best practices"""
    
    best_practice_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowS3ReadAccess",
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:GetObjectVersion"
                ],
                "Resource": [
                    "arn:aws:s3:::company-data-bucket/*"
                ],
                "Condition": {
                    "StringEquals": {
                        "s3:ExistingObjectTag/Classification": "Public"
                    },
                    "IpAddress": {
                        "aws:SourceIp": ["203.0.113.0/24", "198.51.100.0/24"]
                    }
                }
            },
            {
                "Sid": "AllowCloudWatchLogging",
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:us-east-1:123456789012:log-group:/aws/lambda/my-function:*"
            },
            {
                "Sid": "DenyNonSSLRequests",
                "Effect": "Deny",
                "Action": "s3:*",
                "Resource": [
                    "arn:aws:s3:::company-data-bucket",
                    "arn:aws:s3:::company-data-bucket/*"
                ],
                "Condition": {
                    "Bool": {
                        "aws:SecureTransport": "false"
                    }
                }
            }
        ]
    }
    
    print("💡 Best Practice Policy Example:")
    print(json.dumps(best_practice_policy, indent=2))
    
    print("\n🎯 Best Practice Elements:")
    print("✅ Descriptive SIDs for each statement")
    print("✅ Specific actions instead of wildcards")
    print("✅ Specific resource ARNs")
    print("✅ Conditional access restrictions")
    print("✅ Explicit Deny for security requirements")
    print("✅ Proper JSON formatting and structure")
    
    return best_practice_policy

# Example usage
if __name__ == "__main__":
    # Run policy analysis demonstration
    analyzer = demonstrate_policy_analysis()
    
    # Show best practice example
    best_practice_policy = create_policy_best_practices()
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def iam_permissions_tab():
    """Content for IAM Permissions tab"""
    st.markdown("## 🛡️ IAM Permissions")
    st.markdown("*Managing access control and troubleshooting permission issues*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **IAM Permissions** determine what actions a user, group, or role can perform on AWS resources. 
    Effective permission management requires understanding policy types, evaluation logic, and common troubleshooting techniques.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Permission Sources
    st.markdown("### 📊 Sources of Permissions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 👤 Identity-Based
        - Attached to **users, groups, roles**
        - Define what identity can do
        - Most common permission source
        
        **Types:**
        - AWS Managed Policies
        - Customer Managed Policies
        - Inline Policies
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🗂️ Resource-Based
        - Attached to **AWS resources**
        - Define who can access resource
        - Enable cross-account access
        
        **Examples:**
        - S3 Bucket Policies
        - Lambda Function Policies
        - KMS Key Policies
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🏢 Organization-Based
        - **Service Control Policies** (SCPs)
        - Applied at organization level
        - Set maximum permissions
        
        **Purpose:**
        - Compliance guardrails
        - Prevent privilege escalation
        - Centralized governance
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Permission Troubleshooter
    st.markdown("### 🔧 Interactive Permission Troubleshooter")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Scenario Configuration")
        user_type = st.selectbox("Identity Type:", ["IAM User", "IAM Role", "Federated User"])
        service = st.selectbox("AWS Service:", ["S3", "EC2", "Lambda", "DynamoDB", "IAM"])
        action = st.text_input("Action Attempted:", f"{service.lower()}:ListBuckets" if service == "S3" else f"{service.lower()}:DescribeInstances")
        resource = st.text_input("Resource ARN:", f"arn:aws:{service.lower()}:us-east-1:123456789012:*")
        
        error_message = st.text_area("Error Message:", "User is not authorized to perform this action")
    
    with col2:
        st.markdown("### 🔍 Permission Audit")
        has_identity_policy = st.checkbox("Has Identity-based Policy", value=True)
        has_resource_policy = st.checkbox("Has Resource-based Policy", value=False)
        has_permission_boundary = st.checkbox("Has Permission Boundary", value=False)
        
        mfa_required = st.checkbox("MFA Required", value=False)
        source_ip_restricted = st.checkbox("Source IP Restricted", value=False)
        
        if mfa_required:
            mfa_enabled = st.checkbox("MFA Token Provided", value=False)
        
        if source_ip_restricted:
            current_ip = st.text_input("Current IP Address:", "203.0.113.50")
            allowed_ip = st.text_input("Allowed IP Range:", "203.0.113.0/24")
    
    if st.button("🔍 Analyze Permission Issue", use_container_width=True):
        # Simulate troubleshooting logic
        issues = []
        solutions = []
        
        # Check for common issues
        if not has_identity_policy:
            issues.append("❌ No identity-based policy attached")
            solutions.append("✅ Attach appropriate managed policy or create custom policy")
        
        if mfa_required and not mfa_enabled:
            issues.append("❌ MFA required but not provided")
            solutions.append("✅ Enable MFA device and include MFA token in request")
        
        if source_ip_restricted:
            if current_ip and allowed_ip:
                # Simple IP check (in real scenario, use proper CIDR validation)
                if not current_ip.startswith(allowed_ip.split('/')[0][:10]):
                    issues.append("❌ Source IP not in allowed range")
                    solutions.append("✅ Access from allowed IP range or update policy conditions")
        
        if has_permission_boundary:
            issues.append("⚠️ Permission boundary may be restricting access")
            solutions.append("✅ Review permission boundary policy for required permissions")
        
        # Generate diagnosis
        if not issues:
            issues = ["✅ No obvious permission issues detected"]
            solutions = ["🔍 Check CloudTrail logs for detailed access denial reasons"]
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 🔍 Permission Diagnosis Results
        
        **Scenario:**
        - **Identity**: {user_type}
        - **Action**: {action}
        - **Resource**: {resource}
        
        **Issues Found:**
        {chr(10).join([f"  {issue}" for issue in issues])}
        
        **Recommended Solutions:**
        {chr(10).join([f"  {solution}" for solution in solutions])}
        
        **Next Steps:**
        1. Review CloudTrail logs for detailed error context
        2. Use IAM Policy Simulator to test permissions
        3. Check all policy sources (identity, resource, SCPs)
        4. Verify condition key requirements (MFA, IP, tags)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Real-world Permission Scenario
    st.markdown("### 📚 Real-world Permission Scenario")
    
    st.markdown("""
    **Scenario: VPC Flow Logs Issue**
    
    Your flow log records are incomplete or no longer being published to CloudWatch Logs. 
    There might be a problem delivering the flow logs to the CloudWatch Logs log group.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔍 Possible Issues
        
        **Rate Limited Issues:**
        - **Throttling** if flow log records exceed limits
        - Too many network interfaces
        - High traffic volume
        
        **Access Errors:**
        - **IAM role lacks permissions** to publish logs
        - Missing trust relationship with VPC Flow Logs
        - Incorrect CloudWatch Logs permissions
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ✅ Solutions
        
        **Check IAM Role:**
        - Verify role has `logs:CreateLogGroup`
        - Ensure `logs:CreateLogStream` permission
        - Confirm `logs:PutLogEvents` access
        
        **Trust Relationship:**
        - Principal should be `vpc-flow-logs.amazonaws.com`
        - Include proper trust policy
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Permission Policy Examples
    st.markdown("### 📜 Required VPC Flow Logs Permissions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="trust-policy">', unsafe_allow_html=True)
        st.markdown("""
        **Trust Policy:**
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
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="permission-policy">', unsafe_allow_html=True)
        st.markdown("""
        **Permission Policy:**
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
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Permission Evaluation Matrix
    st.markdown("### 📊 Permission Evaluation Matrix")
    
    evaluation_data = {
        'Scenario': [
            'Identity Policy: Allow, Resource Policy: Allow',
            'Identity Policy: Allow, Resource Policy: Deny',
            'Identity Policy: Deny, Resource Policy: Allow',
            'Identity Policy: Allow, No Resource Policy',
            'No Identity Policy, Resource Policy: Allow',
            'Permission Boundary: Deny'
        ],
        'Result': ['✅ Allow', '❌ Deny', '❌ Deny', '✅ Allow', '✅ Allow', '❌ Deny'],
        'Explanation': [
            'Both policies allow the action',
            'Explicit deny in resource policy takes precedence',
            'Explicit deny in identity policy takes precedence',
            'Identity policy allows, no resource policy restrictions',
            'Resource policy allows cross-account/service access',
            'Permission boundary sets maximum permissions'
        ],
        'Common Use Case': [
            'Normal authorized access',
            'Resource protection override',
            'User restriction override',
            'Standard user permissions',
            'Cross-account resource sharing',
            'Developer environment restrictions'
        ]
    }
    
    df_evaluation = pd.DataFrame(evaluation_data)
    st.dataframe(df_evaluation, use_container_width=True)
    
    # Advanced Permission Concepts
    st.markdown("### 🎓 Advanced Permission Concepts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔒 Permission Boundaries
        - **Maximum permissions** for an entity
        - Cannot grant more than boundary allows
        - Used for **delegated administration**
        
        **Use Cases:**
        - Developer self-service
        - Contractor limitations
        - Department restrictions
        
        **Implementation:**
        - Attach to users or roles
        - Intersection with identity policies
        - Does not grant permissions itself
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🏢 Service Control Policies
        - **Organization-level guardrails**
        - Preventive controls only
        - Applied to **accounts or OUs**
        
        **Use Cases:**
        - Compliance requirements
        - Cost control
        - Regional restrictions
        
        **Capabilities:**
        - Deny specific actions
        - Restrict regions
        - Prevent privilege escalation
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Permission Monitoring
    st.markdown("### 📊 Permission Monitoring and Auditing")
    
    monitoring_tools = {
        'Tool': [
            'AWS CloudTrail',
            'IAM Access Advisor',
            'IAM Access Analyzer',
            'AWS Config',
            'IAM Policy Simulator',
            'AWS Well-Architected Tool'
        ],
        'Purpose': [
            'API call logging and auditing',
            'Service access analysis',
            'External access identification',
            'Compliance monitoring',
            'Permission testing',
            'Security best practices'
        ],
        'Key Features': [
            'Real-time logging, searchable events',
            'Last accessed timestamps, unused permissions',
            'External access paths, policy validation',
            'Configuration drift, compliance rules',
            'What-if scenarios, policy testing',
            'Security pillar recommendations'
        ],
        'Best For': [
            'Incident investigation, audit trails',
            'Permission cleanup, least privilege',
            'External access review, security',
            'Continuous compliance, governance',
            'Policy development, troubleshooting',
            'Overall security posture'
        ]
    }
    
    df_monitoring = pd.DataFrame(monitoring_tools)
    st.dataframe(df_monitoring, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Permission Management and Monitoring")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Comprehensive permission management and monitoring
import boto3
import json
from datetime import datetime, timedelta
from collections import defaultdict

class IAMPermissionManager:
    """Manage and monitor IAM permissions"""
    
    def __init__(self):
        self.iam = boto3.client('iam')
        self.organizations = boto3.client('organizations')
        self.cloudtrail = boto3.client('cloudtrail')
    
    def audit_user_permissions(self, username):
        """Comprehensive audit of user permissions"""
        
        print(f"🔍 Auditing permissions for user: {username}")
        print("=" * 50)
        
        try:
            # Get user details
            user = self.iam.get_user(UserName=username)
            user_arn = user['User']['Arn']
            
            print(f"User ARN: {user_arn}")
            print(f"Created: {user['User']['CreateDate']}")
            
            # Collect all permission sources
            permission_sources = {
                'attached_policies': [],
                'inline_policies': [],
                'group_policies': [],
                'permission_boundary': None
            }
            
            # 1. Directly attached managed policies
            attached_policies = self.iam.list_attached_user_policies(UserName=username)
            for policy in attached_policies['AttachedPolicies']:
                permission_sources['attached_policies'].append({
                    'name': policy['PolicyName'],
                    'arn': policy['PolicyArn'],
                    'type': 'managed'
                })
            
            # 2. Inline policies
            inline_policies = self.iam.list_user_policies(UserName=username)
            for policy_name in inline_policies['PolicyNames']:
                permission_sources['inline_policies'].append({
                    'name': policy_name,
                    'type': 'inline'
                })
            
            # 3. Group memberships and their policies
            groups = self.iam.get_groups_for_user(UserName=username)
            for group in groups['Groups']:
                group_name = group['GroupName']
                
                # Group attached policies
                group_attached = self.iam.list_attached_group_policies(GroupName=group_name)
                for policy in group_attached['AttachedPolicies']:
                    permission_sources['group_policies'].append({
                        'source': f"Group: {group_name}",
                        'name': policy['PolicyName'],
                        'arn': policy['PolicyArn'],
                        'type': 'managed'
                    })
                
                # Group inline policies
                group_inline = self.iam.list_group_policies(GroupName=group_name)
                for policy_name in group_inline['PolicyNames']:
                    permission_sources['group_policies'].append({
                        'source': f"Group: {group_name}",
                        'name': policy_name,
                        'type': 'inline'
                    })
            
            # 4. Permission boundary
            try:
                user_detail = self.iam.get_user(UserName=username)
                if 'PermissionsBoundary' in user_detail['User']:
                    permission_sources['permission_boundary'] = user_detail['User']['PermissionsBoundary']
            except:
                pass
            
            # Report findings
            self._report_permission_sources(permission_sources)
            
            # Analyze access patterns
            access_analysis = self.analyze_user_access_patterns(username)
            
            return {
                'permission_sources': permission_sources,
                'access_analysis': access_analysis
            }
            
        except Exception as e:
            print(f"❌ Error auditing user {username}: {e}")
            return None
    
    def _report_permission_sources(self, sources):
        """Report permission sources in a readable format"""
        
        print("\n📋 Permission Sources:")
        
        # Attached policies
        if sources['attached_policies']:
            print(f"\n📜 Directly Attached Policies ({len(sources['attached_policies'])}):")
            for policy in sources['attached_policies']:
                print(f"  - {policy['name']} ({policy['type']})")
        
        # Inline policies
        if sources['inline_policies']:
            print(f"\n📝 Inline Policies ({len(sources['inline_policies'])}):")
            for policy in sources['inline_policies']:
                print(f"  - {policy['name']}")
        
        # Group policies
        if sources['group_policies']:
            print(f"\n👥 Group-Based Policies ({len(sources['group_policies'])}):")
            for policy in sources['group_policies']:
                print(f"  - {policy['name']} (from {policy['source']})")
        
        # Permission boundary
        if sources['permission_boundary']:
            boundary = sources['permission_boundary']
            print(f"\n🔒 Permission Boundary:")
            print(f"  - {boundary['PermissionsBoundaryArn']}")
    
    def analyze_user_access_patterns(self, username, days=30):
        """Analyze user's API call patterns"""
        
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            # Get CloudTrail events for the user
            events = self.cloudtrail.lookup_events(
                LookupAttributes=[
                    {
                        'AttributeKey': 'Username',
                        'AttributeValue': username
                    }
                ],
                StartTime=start_time,
                EndTime=end_time
            )
            
            # Analyze patterns
            service_usage = defaultdict(int)
            action_usage = defaultdict(int)
            daily_activity = defaultdict(int)
            
            for event in events['Events']:
                event_name = event['EventName']
                event_time = event['EventTime'].date()
                
                # Extract service from event name
                if ':' in event_name:
                    service = event_name.split(':')[0]
                else:
                    service = event.get('EventSource', 'unknown').replace('.amazonaws.com', '')
                
                service_usage[service] += 1
                action_usage[event_name] += 1
                daily_activity[str(event_time)] += 1
            
            analysis = {
                'total_events': len(events['Events']),
                'unique_services': len(service_usage),
                'unique_actions': len(action_usage),
                'top_services': dict(sorted(service_usage.items(), key=lambda x: x[1], reverse=True)[:5]),
                'top_actions': dict(sorted(action_usage.items(), key=lambda x: x[1], reverse=True)[:10]),
                'daily_activity': dict(daily_activity)
            }
            
            print(f"\n📊 Access Pattern Analysis ({days} days):")
            print(f"  Total API Calls: {analysis['total_events']}")
            print(f"  Unique Services: {analysis['unique_services']}")
            print(f"  Unique Actions: {analysis['unique_actions']}")
            
            print(f"\n🔝 Top Services Used:")
            for service, count in analysis['top_services'].items():
                print(f"  - {service}: {count} calls")
            
            return analysis
            
        except Exception as e:
            print(f"⚠️ Access pattern analysis failed: {e}")
            return {}
    
    def check_unused_permissions(self, entity_arn, entity_type='user'):
        """Check for unused permissions using Access Advisor"""
        
        try:
            # Generate access advisor report
            response = self.iam.generate_service_last_accessed_details(Arn=entity_arn)
            job_id = response['JobId']
            
            # Wait for report completion (simplified - should implement proper polling)
            import time
            time.sleep(10)
            
            # Get report details
            report = self.iam.get_service_last_accessed_details(JobId=job_id)
            
            unused_services = []
            rarely_used_services = []
            
            for service in report['ServicesLastAccessed']:
                service_name = service['ServiceName']
                
                if 'LastAuthenticated' not in service:
                    unused_services.append(service_name)
                else:
                    last_used = service['LastAuthenticated']
                    days_since_use = (datetime.now(last_used.tzinfo) - last_used).days
                    
                    if days_since_use > 90:  # 90 days threshold
                        rarely_used_services.append({
                            'service': service_name,
                            'days_since_use': days_since_use
                        })
            
            print(f"\n🧹 Unused Permission Analysis:")
            print(f"  Never Used Services: {len(unused_services)}")
            print(f"  Rarely Used Services: {len(rarely_used_services)}")
            
            if unused_services:
                print(f"\n❌ Never Used Services:")
                for service in unused_services[:5]:  # Show first 5
                    print(f"  - {service}")
            
            if rarely_used_services:
                print(f"\n⚠️ Rarely Used Services (>90 days):")
                for item in rarely_used_services[:5]:
                    print(f"  - {item['service']}: {item['days_since_use']} days")
            
            return {
                'unused_services': unused_services,
                'rarely_used_services': rarely_used_services
            }
            
        except Exception as e:
            print(f"❌ Error checking unused permissions: {e}")
            return {}
    
    def create_least_privilege_policy(self, username, analysis_data):
        """Create a least privilege policy based on usage analysis"""
        
        if 'access_analysis' not in analysis_data:
            print("❌ Need access analysis data to create least privilege policy")
            return None
        
        access_analysis = analysis_data['access_analysis']
        
        # Build policy based on actual usage
        actions = []
        for action, count in access_analysis.get('top_actions', {}).items():
            if count > 1:  # Only include actions used more than once
                actions.append(action)
        
        # Create policy structure
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "LeastPrivilegeBasedOnUsage",
                    "Effect": "Allow",
                    "Action": actions[:20],  # Limit to top 20 actions
                    "Resource": "*",  # Should be refined based on resources actually accessed
                    "Condition": {
                        "DateGreaterThan": {
                            "aws:CurrentTime": datetime.now().strftime("%Y-%m-%dT00:00:00Z")
                        }
                    }
                }
            ]
        }
        
        print(f"\n📜 Generated Least Privilege Policy for {username}:")
        print(json.dumps(policy, indent=2))
        
        return policy
    
    def simulate_permission_changes(self, entity_arn, new_policy, test_actions):
        """Simulate the effect of policy changes"""
        
        print(f"\n🧪 Simulating Policy Changes:")
        print(f"Entity: {entity_arn}")
        
        try:
            # Test each action
            for action in test_actions:
                result = self.iam.simulate_principal_policy(
                    PolicySourceArn=entity_arn,
                    ActionNames=[action],
                    PolicyInputList=[json.dumps(new_policy)]
                )
                
                for evaluation in result['EvaluationResults']:
                    decision = evaluation['EvalDecision']
                    print(f"  {action}: {decision}")
                    
                    if decision == 'explicitDeny':
                        print(f"    Reason: Explicitly denied")
                    elif decision == 'implicitDeny':
                        print(f"    Reason: No matching allow statement")
            
        except Exception as e:
            print(f"❌ Simulation failed: {e}")

def demonstrate_permission_management():
    """Demonstrate comprehensive permission management"""
    
    manager = IAMPermissionManager()
    
    # Example: Audit a user's permissions
    username = "john-developer"
    
    print("🔐 IAM Permission Management Demonstration")
    print("=" * 60)
    
    # Comprehensive audit
    audit_results = manager.audit_user_permissions(username)
    
    if audit_results:
        # Check for unused permissions
        user_arn = f"arn:aws:iam::123456789012:user/{username}"
        unused_analysis = manager.check_unused_permissions(user_arn)
        
        # Create least privilege policy
        if audit_results.get('access_analysis'):
            least_privilege_policy = manager.create_least_privilege_policy(username, audit_results)
            
            # Simulate policy changes
            if least_privilege_policy:
                test_actions = ['s3:ListBuckets', 'ec2:DescribeInstances', 'iam:ListUsers']
                manager.simulate_permission_changes(user_arn, least_privilege_policy, test_actions)
    
    print(f"\n✅ Permission audit completed for {username}")

# Example usage
if __name__ == "__main__":
    demonstrate_permission_management()
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application function"""
    # Apply styling
    apply_custom_styles()
    
    # Initialize session
    common.initialize_session_state()
    
    # Create sidebar
    create_sidebar()
    
    # Main header
    st.markdown("""
    # 🔐 AWS Identity and Access Management
    
    """)
    st.markdown("""<div class="info-box">
                Master AWS security fundamentals including IAM users, roles, policies, and permissions. Learn to implement secure access patterns, troubleshoot permission issues, and apply security best practices for robust AWS environments.
                </div>""", unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔐 AWS Identity and Access Management", 
        "👤 IAM Roles", 
        "🎫 Security Token Service (STS)",
        "📜 Policy Interpretation",
        "🛡️ IAM Permissions"
    ])
    
    with tab1:
        aws_iam_tab()
    
    with tab2:
        iam_roles_tab()
    
    with tab3:
        security_token_service_tab()
    
    with tab4:
        policy_interpretation_tab()
        
    with tab5:
        iam_permissions_tab()
    
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
