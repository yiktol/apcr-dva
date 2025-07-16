
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
    page_title="AWS Cognito Authentication Hub",
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
        
        .auth-flow-container {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            border: 2px solid {AWS_COLORS['light_blue']};
            margin: 15px 0;
        }}
        
        .user-pool-card {{
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            padding: 20px;
            border-radius: 15px;
            color: white;
            margin: 10px 0;
        }}
        
        .identity-pool-card {{
            background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
            padding: 20px;
            border-radius: 15px;
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
            - 🔐 AWS Cognito - Authentication & Authorization service
            - 👥 User Pools - User directory and management
            - 🎫 Identity Pools - AWS credentials for authenticated users
            - 🔄 Authentication Flow - Sign-in, sign-up workflows
            - 🌐 Social Identity Providers - Facebook, Google, Amazon
            
            **Learning Objectives:**
            - Understand AWS Cognito authentication architecture
            - Learn to implement user pools and identity pools
            - Explore social identity provider integration
            - Practice with interactive examples and code samples
            - Master JWT token handling and validation
            """)

def create_cognito_architecture_mermaid():
    """Create mermaid diagram for AWS Cognito architecture"""
    return """
    graph TB
        subgraph "Client Application"
            WebApp[Web Application]
            MobileApp[Mobile Application]
        end
        
        subgraph "AWS Cognito"
            UserPool[User Pool<br/>Authentication]
            IdentityPool[Identity Pool<br/>Authorization]
        end
        
        subgraph "Identity Providers"
            CognitoIDP[Cognito User Pool]
            Facebook[Facebook]
            Google[Google]
            Amazon[Amazon]
            SAML[SAML]
        end
        
        subgraph "AWS Services"
            S3[Amazon S3]
            DynamoDB[DynamoDB]
            Lambda[AWS Lambda]
            APIGateway[API Gateway]
        end
        
        WebApp --> UserPool
        MobileApp --> UserPool
        
        UserPool --> IdentityPool
        
        CognitoIDP --> IdentityPool
        Facebook --> IdentityPool
        Google --> IdentityPool
        Amazon --> IdentityPool
        SAML --> IdentityPool
        
        IdentityPool --> S3
        IdentityPool --> DynamoDB
        IdentityPool --> Lambda
        IdentityPool --> APIGateway
        
        style UserPool fill:#4CAF50,stroke:#2E7D32,color:#fff
        style IdentityPool fill:#2196F3,stroke:#1565C0,color:#fff
        style WebApp fill:#FF9900,stroke:#E65100,color:#fff
        style MobileApp fill:#FF9900,stroke:#E65100,color:#fff
        style S3 fill:#FF6B35,stroke:#D84315,color:#fff
        style DynamoDB fill:#FF6B35,stroke:#D84315,color:#fff
        style Lambda fill:#FF6B35,stroke:#D84315,color:#fff
        style APIGateway fill:#FF6B35,stroke:#D84315,color:#fff
    """

def create_authentication_flow_mermaid():
    """Create mermaid diagram for authentication flow"""
    return """
    sequenceDiagram
        participant User
        participant App
        participant UserPool as User Pool
        participant IdentityPool as Identity Pool
        participant AWS as AWS Services
        
        User->>App: 1. Sign In Request
        App->>UserPool: 2. Authenticate User
        UserPool->>UserPool: 3. Validate Credentials
        UserPool->>App: 4. Return JWT Tokens
        
        Note over App: ID Token, Access Token, Refresh Token
        
        App->>IdentityPool: 5. Exchange Tokens
        IdentityPool->>IdentityPool: 6. Assume IAM Role
        IdentityPool->>App: 7. Return AWS Credentials
        
        App->>AWS: 8. Access AWS Services
        AWS->>App: 9. Return Data
        App->>User: 10. Display Results
    """

def create_user_pool_features_mermaid():
    """Create mermaid diagram for user pool features"""
    return """
    graph LR
        subgraph "User Pool Features"
            A[User Registration] --> B[Email Verification]
            A --> C[Phone Verification]
            B --> D[Password Policies]
            C --> D
            D --> E[MFA Support]
            E --> F[Custom Attributes]
            F --> G[Lambda Triggers]
            G --> H[UI Customization]
        end
        
        subgraph "Authentication Methods"
            I[Username/Password]
            J[Email/Password]
            K[Phone/OTP]
            L[Social Providers]
        end
        
        D --> I
        D --> J
        D --> K
        E --> L
        
        style A fill:#4CAF50,stroke:#2E7D32,color:#fff
        style E fill:#FF9900,stroke:#E65100,color:#fff
        style L fill:#2196F3,stroke:#1565C0,color:#fff
    """

def aws_cognito_tab():
    """Content for AWS Cognito tab"""
    st.markdown("## 🔐 AWS Cognito")
    st.markdown("*Authentication, authorization, and user management for web and mobile apps*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Amazon Cognito** provides authentication, authorization, and user management for your web and mobile apps. 
    Your users can sign in directly with a user name and password, or through a third party such as Facebook, 
    Amazon, Google or Apple.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Cognito Components
    st.markdown("### 🏗️ AWS Cognito Architecture")
    common.mermaid(create_cognito_architecture_mermaid(), height=610)
    
    # Core Components Overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="user-pool-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 👥 User Pools
        **User directory service for authentication**
        
        **Key Features:**
        - User registration and sign-in
        - Password policies and MFA
        - Email and phone verification
        - Social identity providers
        - Custom user attributes
        - Lambda triggers for customization
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="identity-pool-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎫 Identity Pools
        **AWS credentials for authenticated users**
        
        **Key Features:**
        - Temporary AWS credentials
        - Fine-grained IAM permissions
        - Support for multiple identity providers
        - Anonymous user access
        - Role-based access control
        - Cross-platform SDK support
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Cognito Configuration
    st.markdown("### 🛠️ Interactive Cognito Setup Wizard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📱 Application Settings")
        app_type = st.selectbox("Application Type:", [
            "Web Application", "Mobile App (iOS)", "Mobile App (Android)", 
            "Single Page Application (SPA)", "Server-side Application"
        ])
        
        user_base = st.slider("Expected Users:", 100, 1000000, 10000, step=1000)
        regions = st.multiselect("Deployment Regions:", [
            "us-east-1", "us-west-2", "eu-west-1", "eu-central-1", 
            "ap-southeast-1", "ap-northeast-1"
        ], default=["us-east-1"])
    
    with col2:
        st.markdown("### 🔐 Authentication Requirements")
        auth_methods = st.multiselect("Authentication Methods:", [
            "Username/Password", "Email/Password", "Phone/SMS", 
            "Social Login (Google)", "Social Login (Facebook)", "SAML/OIDC"
        ], default=["Email/Password"])
        
        security_features = st.multiselect("Security Features:", [
            "Multi-Factor Authentication", "Password Policies", 
            "Account Recovery", "Rate Limiting", "Advanced Security"
        ], default=["Multi-Factor Authentication", "Password Policies"])
    
    if st.button("🚀 Generate Cognito Configuration", use_container_width=True):
        # Generate configuration based on selections
        config = {
            "UserPool": {
                "PoolName": f"{app_type.replace(' ', '').lower()}-users",
                "UsernameAttributes": ["email"] if "Email/Password" in auth_methods else ["username"],
                "Policies": {
                    "PasswordPolicy": {
                        "MinimumLength": 8,
                        "RequireUppercase": True,
                        "RequireLowercase": True,
                        "RequireNumbers": True,
                        "RequireSymbols": "Password Policies" in security_features
                    }
                },
                "MfaConfiguration": "OPTIONAL" if "Multi-Factor Authentication" in security_features else "OFF",
                "EstimatedMonthlyCost": f"${(user_base * 0.0055):.2f}"
            },
            "IdentityPool": {
                "PoolName": f"{app_type.replace(' ', '').lower()}-identity",
                "AllowUnauthenticatedIdentities": False,
                "SupportedRegions": regions
            }
        }
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ Cognito Configuration Generated!
        
        **User Pool Settings:**
        - **Pool Name**: {config['UserPool']['PoolName']}
        - **Authentication**: {', '.join(auth_methods)}
        - **Security Features**: {', '.join(security_features)}
        - **Expected Users**: {user_base:,}
        - **Estimated Cost**: {config['UserPool']['EstimatedMonthlyCost']}/month
        
        **Identity Pool Settings:**
        - **Pool Name**: {config['IdentityPool']['PoolName']}
        - **Regions**: {', '.join(regions)}
        - **App Type**: {app_type}
        
        🔧 **Next Steps**: Implement user pool and identity pool with the generated configuration!
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show JSON configuration
        with st.expander("📋 View JSON Configuration"):
            st.json(config)
    
    # Use Cases and Benefits
    st.markdown("### 🌟 AWS Cognito Use Cases & Benefits")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🚀 Rapid Development
        - **Pre-built authentication** UI
        - SDK support for all platforms
        - **Social login** integration
        - Customizable workflows
        
        **Perfect for:**
        - Startups and MVPs
        - Time-sensitive projects
        - Cross-platform applications
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔒 Enterprise Security
        - **Industry standards** compliance
        - Advanced security features
        - **Audit logging** and monitoring
        - Fine-grained access control
        
        **Perfect for:**
        - Enterprise applications
        - Regulated industries
        - High-security requirements
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📈 Scalability
        - **Automatic scaling** to millions
        - Global deployment support
        - **High availability** SLA
        - Performance optimization
        
        **Perfect for:**
        - Growing applications
        - Global user base
        - Variable traffic patterns
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Authentication Flow
    st.markdown("### 🔄 Complete Authentication Flow")
    common.mermaid(create_authentication_flow_mermaid(), height=800)
    
    # Token Types Explanation
    st.markdown("### 🎫 JWT Token Types in Cognito")
    
    token_data = {
        'Token Type': ['ID Token', 'Access Token', 'Refresh Token'],
        'Purpose': [
            'Contains user identity information',
            'Grants access to protected resources',
            'Obtains new access and ID tokens'
        ],
        'Validity': ['1 hour (configurable)', '1 hour (configurable)', '30 days (configurable)'],
        'Contains': [
            'User attributes, claims',
            'Scopes, permissions',
            'Long-lived credential'
        ],
        'Usage': [
            'User profile, personalization',
            'API calls, resource access',
            'Token renewal, long sessions'
        ]
    }
    
    df_tokens = pd.DataFrame(token_data)
    st.dataframe(df_tokens, use_container_width=True)
    
    # Cost Calculator
    st.markdown("### 💰 Cognito Cost Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        monthly_active_users = st.slider("Monthly Active Users (MAUs):", 0, 100000, 5000, step=500)
        mfa_users = st.slider("Users with MFA (%):", 0, 100, 30)
        sms_mfa_messages = st.slider("SMS MFA messages per user/month:", 0, 20, 5)
    
    with col2:
        social_logins = st.slider("Social identity federation (%):", 0, 100, 20)
        saml_users = st.slider("SAML/OIDC users (%):", 0, 100, 0)
        advanced_security = st.checkbox("Advanced Security Features", value=False)
    
    if st.button("💵 Calculate Monthly Cost"):
        # Cost calculation based on AWS Cognito pricing
        base_cost = monthly_active_users * 0.0055  # $0.0055 per MAU
        
        # MFA SMS costs
        mfa_cost = (monthly_active_users * mfa_users / 100) * (sms_mfa_messages * 0.05)
        
        # Advanced security
        advanced_cost = monthly_active_users * 0.05 if advanced_security else 0
        
        total_cost = base_cost + mfa_cost + advanced_cost
        
        # Display cost breakdown
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Base Cost", f"${base_cost:.2f}", "User Pool MAUs")
        
        with col2:
            st.metric("MFA SMS Cost", f"${mfa_cost:.2f}", "SMS Messages")
        
        with col3:
            st.metric("Advanced Security", f"${advanced_cost:.2f}", "Optional Feature")
        
        with col4:
            st.metric("Total Monthly Cost", f"${total_cost:.2f}", f"for {monthly_active_users:,} MAUs")
        
        # Cost breakdown chart
        if total_cost > 0:
            cost_breakdown = pd.DataFrame({
                'Component': ['Base User Pool', 'MFA SMS', 'Advanced Security'],
                'Cost': [base_cost, mfa_cost, advanced_cost]
            })
            
            fig = px.pie(cost_breakdown, values='Cost', names='Component', 
                        title='Monthly Cost Breakdown',
                        color_discrete_sequence=[AWS_COLORS['primary'], AWS_COLORS['light_blue'], AWS_COLORS['warning']])
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Basic Cognito Setup")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Complete AWS Cognito setup with User Pool and Identity Pool
import boto3
import json
from botocore.exceptions import ClientError

def create_cognito_user_pool():
    """Create a Cognito User Pool with common settings"""
    cognito_idp = boto3.client('cognito-idp')
    
    try:
        # Create User Pool
        response = cognito_idp.create_user_pool(
            PoolName='MyAppUserPool',
            Policies={
                'PasswordPolicy': {
                    'MinimumLength': 8,
                    'RequireUppercase': True,
                    'RequireLowercase': True,
                    'RequireNumbers': True,
                    'RequireSymbols': True,
                    'TemporaryPasswordValidityDays': 7
                }
            },
            UsernameAttributes=['email'],
            AutoVerifiedAttributes=['email'],
            UsernameConfiguration={
                'CaseSensitive': False
            },
            EmailConfiguration={
                'EmailSendingAccount': 'COGNITO_DEFAULT'
            },
            AdminCreateUserConfig={
                'AllowAdminCreateUserOnly': False,
                'InviteMessageAction': 'EMAIL'  
            },
            MfaConfiguration='OPTIONAL',
            EnabledMfas=['SOFTWARE_TOKEN_MFA', 'SMS_MFA'],
            UserPoolTags={
                'Environment': 'Production',
                'Application': 'MyWebApp'
            }
        )
        
        user_pool_id = response['UserPool']['Id']
        print(f"✅ User Pool created: {user_pool_id}")
        
        # Create User Pool Client (App Client)
        client_response = cognito_idp.create_user_pool_client(
            UserPoolId=user_pool_id,
            ClientName='MyAppClient',
            GenerateSecret=False,  # Set to True for server-side apps
            RefreshTokenValidity=30,  # 30 days
            AccessTokenValidity=60,   # 60 minutes
            IdTokenValidity=60,       # 60 minutes
            TokenValidityUnits={
                'AccessToken': 'minutes',
                'IdToken': 'minutes', 
                'RefreshToken': 'days'
            },
            ExplicitAuthFlows=[
                'ALLOW_USER_SRP_AUTH',
                'ALLOW_REFRESH_TOKEN_AUTH'
            ],
            SupportedIdentityProviders=['COGNITO'],
            CallbackURLs=['https://myapp.example.com/callback'],
            LogoutURLs=['https://myapp.example.com/logout'],
            AllowedOAuthFlows=['code'],
            AllowedOAuthScopes=['email', 'openid', 'profile'],
            AllowedOAuthFlowsUserPoolClient=True
        )
        
        client_id = client_response['UserPoolClient']['ClientId']
        print(f"✅ User Pool Client created: {client_id}")
        
        return user_pool_id, client_id
        
    except ClientError as e:
        print(f"❌ Error creating User Pool: {e}")
        return None, None

def create_cognito_identity_pool(user_pool_id, client_id):
    """Create a Cognito Identity Pool"""
    cognito_identity = boto3.client('cognito-identity')
    
    try:
        response = cognito_identity.create_identity_pool(
            IdentityPoolName='MyAppIdentityPool',
            AllowUnauthenticatedIdentities=False,
            CognitoIdentityProviders=[
                {
                    'ProviderName': f'cognito-idp.us-east-1.amazonaws.com/{user_pool_id}',
                    'ClientId': client_id,
                    'ServerSideTokenCheck': True
                }
            ],
            IdentityPoolTags={
                'Environment': 'Production',
                'Application': 'MyWebApp'
            }
        )
        
        identity_pool_id = response['IdentityPoolId']
        print(f"✅ Identity Pool created: {identity_pool_id}")
        
        return identity_pool_id
        
    except ClientError as e:
        print(f"❌ Error creating Identity Pool: {e}")
        return None

def setup_identity_pool_roles(identity_pool_id):
    """Set up IAM roles for the Identity Pool"""
    iam = boto3.client('iam')
    cognito_identity = boto3.client('cognito-identity')
    
    # Authenticated user role trust policy
    authenticated_trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Federated": "cognito-identity.amazonaws.com"
                },
                "Action": "sts:AssumeRoleWithWebIdentity",
                "Condition": {
                    "StringEquals": {
                        "cognito-identity.amazonaws.com:aud": identity_pool_id
                    },
                    "ForAnyValue:StringLike": {
                        "cognito-identity.amazonaws.com:amr": "authenticated"
                    }
                }
            }
        ]
    }
    
    # Authenticated user permissions
    authenticated_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject"
                ],
                "Resource": "arn:aws:s3:::my-user-bucket/${cognito-identity.amazonaws.com:sub}/*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:Query"
                ],
                "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/UserData",
                "Condition": {
                    "ForAllValues:StringEquals": {
                        "dynamodb:LeadingKeys": ["${cognito-identity.amazonaws.com:sub}"]
                    }
                }
            }
        ]
    }
    
    try:
        # Create authenticated role
        auth_role_response = iam.create_role(
            RoleName='CognitoAuthenticatedRole',
            AssumeRolePolicyDocument=json.dumps(authenticated_trust_policy),
            Description='Role for authenticated Cognito users'
        )
        
        auth_role_arn = auth_role_response['Role']['Arn']
        
        # Attach policy to role
        iam.put_role_policy(
            RoleName='CognitoAuthenticatedRole',
            PolicyName='CognitoAuthenticatedPolicy',
            PolicyDocument=json.dumps(authenticated_policy)
        )
        
        # Set roles for identity pool
        cognito_identity.set_identity_pool_roles(
            IdentityPoolId=identity_pool_id,
            Roles={
                'authenticated': auth_role_arn
            }
        )
        
        print(f"✅ Identity Pool roles configured")
        return auth_role_arn
        
    except ClientError as e:
        print(f"❌ Error setting up roles: {e}")
        return None

def register_user(user_pool_id, client_id, email, password, name):
    """Register a new user in the User Pool"""
    cognito_idp = boto3.client('cognito-idp')
    
    try:
        response = cognito_idp.sign_up(
            ClientId=client_id,
            Username=email,
            Password=password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                },
                {
                    'Name': 'name', 
                    'Value': name
                }
            ]
        )
        
        print(f"✅ User registered: {email}")
        print(f"User Sub: {response['UserSub']}")
        print("📧 Check email for verification code")
        
        return response['UserSub']
        
    except ClientError as e:
        print(f"❌ Error registering user: {e}")
        return None

def authenticate_user(client_id, username, password):
    """Authenticate user and get tokens"""
    cognito_idp = boto3.client('cognito-idp')
    
    try:
        # Initiate authentication
        response = cognito_idp.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_SRP_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        
        # Get tokens from response
        tokens = response['AuthenticationResult']
        
        print("✅ Authentication successful!")
        print(f"Access Token: {tokens['AccessToken'][:50]}...")
        print(f"ID Token: {tokens['IdToken'][:50]}...")
        print(f"Refresh Token: {tokens['RefreshToken'][:50]}...")
        
        return tokens
        
    except ClientError as e:
        print(f"❌ Authentication failed: {e}")
        return None

# Complete setup workflow
def setup_cognito_infrastructure():
    """Set up complete Cognito infrastructure"""
    print("🚀 Setting up AWS Cognito infrastructure...")
    
    # Step 1: Create User Pool
    user_pool_id, client_id = create_cognito_user_pool()
    if not user_pool_id:
        return
    
    # Step 2: Create Identity Pool
    identity_pool_id = create_cognito_identity_pool(user_pool_id, client_id)
    if not identity_pool_id:
        return
    
    # Step 3: Set up IAM roles
    auth_role_arn = setup_identity_pool_roles(identity_pool_id)
    if not auth_role_arn:
        return
    
    print("🎉 Cognito setup completed successfully!")
    print(f"User Pool ID: {user_pool_id}")
    print(f"Client ID: {client_id}")
    print(f"Identity Pool ID: {identity_pool_id}")
    
    return {
        'user_pool_id': user_pool_id,
        'client_id': client_id,
        'identity_pool_id': identity_pool_id,
        'auth_role_arn': auth_role_arn
    }

# Example usage
if __name__ == "__main__":
    # Set up infrastructure
    config = setup_cognito_infrastructure()
    
    if config:
        # Register a test user
        user_sub = register_user(
            config['user_pool_id'],
            config['client_id'],
            'testuser@example.com',
            'TempPassword123!',
            'Test User'
        )
        
        # After email verification, authenticate
        # tokens = authenticate_user(
        #     config['client_id'],
        #     'testuser@example.com',
        #     'TempPassword123!'
        # )
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
    st.markdown("# 🔐 AWS Cognito Authentication")
    
    st.markdown("""<div class="info-box">
                Master AWS Cognito authentication and authorization services. Learn to implement user pools, identity pools, 
                and social identity providers to build secure, scalable authentication systems for web and mobile applications.
                </div>""", unsafe_allow_html=True)
    
    # Create tabs
    tab1, = st.tabs(["🔐 AWS Cognito"])
    
    with tab1:
        aws_cognito_tab()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>© 2025, Amazon Web Services, Inc. or its affiliates. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)

# Main execution flow
if __name__ == "__main__":
    if 'localhost' in st.context.headers.get("host", ""):
        main()
    else:
        # First check authentication
        is_authenticated = authenticate.login()
        
        # If authenticated, show the main app content
        if is_authenticated:
            main()
