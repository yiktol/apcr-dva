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
    page_title="AWS Deployment Strategies Hub",
    page_icon="🚀",
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
        
        .deployment-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            border: 2px solid {AWS_COLORS['light_blue']};
            margin: 15px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .strategy-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
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
            - 🚀 Deployment Strategies - Overview and comparison
            - 🔵 Blue/Green - Zero-downtime deployments
            - 🔄 All at Once - Fast deployment strategy
            - 📈 Linear - Gradual traffic shifting
            - 🎯 Canary - Risk-mitigated deployments
            
            **Learning Objectives:**
            - Master AWS deployment strategies
            - Understand trade-offs between strategies
            - Learn best practices for production deployments
            - Practice with interactive deployment simulators
            """)

def create_deployment_overview_mermaid():
    """Create mermaid diagram for deployment strategy overview"""
    return """
    graph TB
        A[Application Deployment] --> B[Deployment Strategy]
        B --> C[All at Once]
        B --> D[Rolling/Linear]
        B --> E[Blue/Green]
        B --> F[Canary]
        
        C --> C1[Fast & Simple]
        C --> C2[Downtime Risk]
        
        D --> D1[No Downtime]
        D --> D2[Gradual Rollout]
        
        E --> E1[Zero Downtime]
        E --> E2[Fast Rollback]
        
        F --> F1[Risk Mitigation]
        F --> F2[Production Testing]
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style B fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#FF6B35,stroke:#232F3E,color:#fff
        style E fill:#232F3E,stroke:#FF9900,color:#fff
        style F fill:#1B2631,stroke:#FF9900,color:#fff
    """

def create_blue_green_mermaid():
    """Create mermaid diagram for blue/green deployment"""
    return """
    graph LR
        A[👥 Users] --> B[⚖️ Load Balancer]
        B --> C[🔵 Blue Environment<br/>Current Version]
        B -.-> D[🟢 Green Environment<br/>New Version]
        
        E[🚀 Deploy New Version] --> D
        F[🧪 Test Green Environment] --> D
        G[🔄 Switch Traffic] --> H[⚖️ Load Balancer]
        H --> D
        H -.-> C
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style B fill:#FF9900,stroke:#232F3E,color:#fff
        style C fill:#0066CC,stroke:#232F3E,color:#fff
        style D fill:#3FB34F,stroke:#232F3E,color:#fff
        style E fill:#FF6B35,stroke:#232F3E,color:#fff
        style F fill:#1B2631,stroke:#FF9900,color:#fff
        style G fill:#232F3E,stroke:#FF9900,color:#fff
        style H fill:#FF9900,stroke:#232F3E,color:#fff
    """

def create_linear_deployment_mermaid():
    """Create mermaid diagram for linear deployment"""
    return """
    graph TB
        A[Start Deployment] --> B[Deploy to 10% Instances]
        B --> C[Wait 3 Minutes]
        C --> D[Deploy to 20% Instances]
        D --> E[Wait 3 Minutes]
        E --> F[Deploy to 30% Instances]
        F --> G[Continue Linear Progression]
        G --> H[100% Deployment Complete]
        
        I[Health Checks] --> J{All Healthy?}
        J -->|Yes| K[Continue]
        J -->|No| L[Stop & Rollback]
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style B fill:#4B9EDB,stroke:#232F3E,color:#fff
        style H fill:#3FB34F,stroke:#232F3E,color:#fff
        style L fill:#FF6B35,stroke:#232F3E,color:#fff
    """

def create_canary_deployment_mermaid():
    """Create mermaid diagram for canary deployment"""
    return """
    graph TB
        A[Start Canary Deployment] --> B[Deploy to 10% Traffic]
        B --> C[Monitor Metrics]
        C --> D{Metrics Healthy?}
        D -->|Yes| E[Deploy to 90% Traffic]
        D -->|No| F[Rollback Canary]
        E --> G[Monitor Full Deployment]
        G --> H{Success?}
        H -->|Yes| I[Complete Deployment]
        H -->|No| J[Full Rollback]
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style B fill:#4B9EDB,stroke:#232F3E,color:#fff
        style E fill:#3FB34F,stroke:#232F3E,color:#fff
        style I fill:#3FB34F,stroke:#232F3E,color:#fff
        style F fill:#FF6B35,stroke:#232F3E,color:#fff
        style J fill:#FF6B35,stroke:#232F3E,color:#fff
    """

def deployment_strategies_tab():
    """Content for Deployment Strategies Overview tab"""
    st.markdown("## 🚀 AWS Deployment Strategies")
    st.markdown("*Overview and comparison of different deployment approaches*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Deployment strategies** determine how you change or upgrade applications. The goal is to minimize downtime 
    while ensuring reliability and providing fast rollback capabilities when issues occur.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Deployment Strategy Overview
    st.markdown("### 🗺️ Deployment Strategy Landscape")
    common.mermaid(create_deployment_overview_mermaid(), height=400)
    
    # Interactive Strategy Selector
    st.markdown("### 🎮 Interactive Strategy Selector")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Application Requirements")
        downtime_tolerance = st.selectbox("Downtime Tolerance:", [
            "Zero Downtime Required", "Minimal Downtime OK", "Some Downtime Acceptable"
        ])
        
        rollback_speed = st.selectbox("Rollback Speed Requirement:", [
            "Instant Rollback", "Fast Rollback (< 5 min)", "Standard Rollback (< 30 min)"
        ])
        
        risk_tolerance = st.selectbox("Risk Tolerance:", [
            "Very Low Risk", "Low Risk", "Medium Risk", "High Risk"
        ])
    
    with col2:
        st.markdown("### 🏗️ Infrastructure Constraints")
        infrastructure_cost = st.selectbox("Infrastructure Cost Sensitivity:", [
            "Cost is Primary Concern", "Balanced Cost/Performance", "Performance Over Cost"
        ])
        
        deployment_frequency = st.selectbox("Deployment Frequency:", [
            "Multiple times per day", "Daily", "Weekly", "Monthly or less"
        ])
        
        team_experience = st.selectbox("Team Experience with Deployments:", [
            "Expert", "Intermediate", "Beginner"
        ])
    
    if st.button("🎯 Get Strategy Recommendation", use_container_width=True):
        # Logic to recommend strategy based on inputs
        score_all_at_once = 0
        score_linear = 0
        score_blue_green = 0
        score_canary = 0
        
        # Downtime tolerance scoring
        if downtime_tolerance == "Zero Downtime Required":
            score_blue_green += 3
            score_canary += 3
            score_linear += 2
        elif downtime_tolerance == "Minimal Downtime OK":
            score_linear += 3
            score_canary += 2
            score_blue_green += 2
            score_all_at_once += 1
        else:
            score_all_at_once += 3
            score_linear += 1
        
        # Risk tolerance scoring
        if risk_tolerance == "Very Low Risk":
            score_canary += 3
            score_blue_green += 2
        elif risk_tolerance == "Low Risk":
            score_blue_green += 3
            score_canary += 2
            score_linear += 1
        elif risk_tolerance == "Medium Risk":
            score_linear += 3
            score_blue_green += 1
            score_all_at_once += 1
        else:
            score_all_at_once += 3
        
        # Cost sensitivity scoring
        if infrastructure_cost == "Cost is Primary Concern":
            score_all_at_once += 3
            score_linear += 2
        elif infrastructure_cost == "Balanced Cost/Performance":
            score_linear += 3
            score_canary += 2
        else:
            score_blue_green += 3
            score_canary += 2
        
        # Find best strategy
        strategies = {
            "All at Once": score_all_at_once,
            "Linear": score_linear,
            "Blue/Green": score_blue_green,
            "Canary": score_canary
        }
        
        recommended_strategy = max(strategies, key=strategies.get)
        confidence = max(strategies.values()) / sum(strategies.values()) * 100
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 🎯 Recommended Strategy: {recommended_strategy}
        **Confidence Level**: {confidence:.1f}%
        
        **Strategy Scores:**
        - All at Once: {score_all_at_once}/9
        - Linear: {score_linear}/9  
        - Blue/Green: {score_blue_green}/9
        - Canary: {score_canary}/9
        
        **Next Steps**: Explore the {recommended_strategy} tab for detailed implementation guidance!
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Comparison Table
    st.markdown("### 📊 Deployment Strategy Comparison")
    
    comparison_data = {
        'Strategy': ['All at Once', 'Linear', 'Blue/Green', 'Canary'],
        'Downtime': ['Yes', 'No', 'No', 'No'],
        'Rollback Speed': ['Slow', 'Fast', 'Instant', 'Fast'],
        'Infrastructure Cost': ['Low', 'Medium', 'High', 'Medium'],
        'Deployment Speed': ['Fast', 'Medium', 'Fast', 'Slow'],
        'Risk Level': ['High', 'Medium', 'Low', 'Very Low'],
        'Best For': [
            'Dev/Test environments',
            'Production with health checks',
            'Critical applications',
            'High-risk deployments'
        ]
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True)
    
    # AWS Services Supporting Each Strategy
    st.markdown("### 🛠️ AWS Services by Deployment Strategy")
    
    services_data = {
        'All at Once': ['AWS CodeDeploy', 'AWS Elastic Beanstalk', 'AWS CloudFormation'],
        'Linear': ['AWS CodeDeploy', 'AWS Elastic Beanstalk', 'Amazon ECS', 'Amazon EKS'],
        'Blue/Green': ['AWS CodeDeploy', 'AWS Elastic Beanstalk', 'Amazon ECS', 'Amazon API Gateway'],
        'Canary': ['AWS CodeDeploy', 'AWS Elastic Beanstalk', 'Amazon ECS', 'AWS Lambda', 'Amazon API Gateway']
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔄 All at Once
        **AWS Services:**
        - AWS CodeDeploy
        - AWS Elastic Beanstalk  
        - AWS CloudFormation
        
        **Use Case:** Development environments, low-risk applications
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔵 Blue/Green
        **AWS Services:**
        - AWS CodeDeploy
        - AWS Elastic Beanstalk
        - Amazon ECS
        - Amazon API Gateway
        
        **Use Case:** Critical production applications
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📈 Linear
        **AWS Services:**
        - AWS CodeDeploy
        - AWS Elastic Beanstalk
        - Amazon ECS
        - Amazon EKS
        
        **Use Case:** Standard production deployments
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 Canary
        **AWS Services:**
        - AWS CodeDeploy
        - AWS Elastic Beanstalk
        - Amazon ECS
        - AWS Lambda
        - Amazon API Gateway
        
        **Use Case:** High-risk, critical applications
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Performance Impact Visualization
    st.markdown("### 📊 Strategy Performance Comparison")
    
    # Create comparison metrics
    strategies = ['All at Once', 'Linear', 'Blue/Green', 'Canary']
    deployment_time = [2, 15, 5, 30]  # minutes
    risk_level = [9, 5, 3, 1]  # 1-10 scale
    infrastructure_cost = [1, 3, 8, 4]  # relative cost
    
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('Deployment Time (min)', 'Risk Level (1-10)', 'Infrastructure Cost (relative)'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]]
    )
    
    fig.add_trace(
        go.Bar(x=strategies, y=deployment_time, name='Deployment Time', 
               marker_color=AWS_COLORS['primary']),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=strategies, y=risk_level, name='Risk Level',
               marker_color=AWS_COLORS['warning']),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Bar(x=strategies, y=infrastructure_cost, name='Infrastructure Cost',
               marker_color=AWS_COLORS['light_blue']),
        row=1, col=3
    )
    
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Deployment Strategy Selection")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# AWS CodeDeploy deployment strategy configuration
import boto3
import json

def create_deployment_config(strategy_type, application_name):
    """Create deployment configuration based on strategy"""
    codedeploy = boto3.client('codedeploy')
    
    configs = {
        'all_at_once': {
            'deploymentConfigName': f'{application_name}-AllAtOnce',
            'trafficRoutingConfig': {
                'type': 'AllAtOnce'
            }
        },
        'linear': {
            'deploymentConfigName': f'{application_name}-Linear10Percent',
            'trafficRoutingConfig': {
                'type': 'TimeBasedLinear',
                'timeBasedLinear': {
                    'linearPercentage': 10,
                    'linearInterval': 3  # 3 minutes
                }
            }
        },
        'canary': {
            'deploymentConfigName': f'{application_name}-Canary10Percent',
            'trafficRoutingConfig': {
                'type': 'TimeBasedCanary',
                'timeBasedCanary': {
                    'canaryPercentage': 10,
                    'canaryInterval': 5  # 5 minutes
                }
            }
        }
    }
    
    if strategy_type not in configs:
        raise ValueError(f"Unknown strategy: {strategy_type}")
    
    config = configs[strategy_type]
    
    try:
        response = codedeploy.create_deployment_config(**config)
        print(f"✅ Created deployment config: {config['deploymentConfigName']}")
        return response['deploymentConfigId']
    except Exception as e:
        print(f"❌ Error creating deployment config: {e}")
        return None

def deploy_application(application_name, deployment_group, strategy, s3_bucket, s3_key):
    """Deploy application using specified strategy"""
    codedeploy = boto3.client('codedeploy')
    
    # Strategy to config mapping
    config_mapping = {
        'all_at_once': 'CodeDeployDefault.AllAtOnce',
        'linear': f'{application_name}-Linear10Percent',
        'blue_green': 'CodeDeployDefault.BlueGreen',
        'canary': f'{application_name}-Canary10Percent'
    }
    
    deployment_config = config_mapping.get(strategy, 'CodeDeployDefault.AllAtOnce')
    
    try:
        response = codedeploy.create_deployment(
            applicationName=application_name,
            deploymentGroupName=deployment_group,
            deploymentConfigName=deployment_config,
            revision={
                'revisionType': 'S3',
                's3Location': {
                    'bucket': s3_bucket,
                    'key': s3_key,
                    'bundleType': 'zip'
                }
            },
            description=f'Deployment using {strategy} strategy',
            ignoreApplicationStopFailures=False,
            autoRollbackConfiguration={
                'enabled': True,
                'events': ['DEPLOYMENT_FAILURE', 'DEPLOYMENT_STOP_ON_ALARM']
            }
        )
        
        deployment_id = response['deploymentId']
        print(f"🚀 Deployment started: {deployment_id}")
        print(f"Strategy: {strategy}")
        print(f"Config: {deployment_config}")
        
        return deployment_id
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return None

def monitor_deployment(deployment_id):
    """Monitor deployment progress"""
    codedeploy = boto3.client('codedeploy')
    
    try:
        response = codedeploy.get_deployment(deploymentId=deployment_id)
        deployment = response['deploymentInfo']
        
        status = deployment['status']
        progress = deployment.get('deploymentOverview', {})
        
        print(f"📊 Deployment Status: {status}")
        
        if progress:
            print(f"  ✅ Succeeded: {progress.get('Succeeded', 0)}")
            print(f"  🔄 In Progress: {progress.get('InProgress', 0)}")
            print(f"  ⏳ Pending: {progress.get('Pending', 0)}")
            print(f"  ❌ Failed: {progress.get('Failed', 0)}")
            print(f"  ⏭️  Skipped: {progress.get('Skipped', 0)}")
        
        return status
        
    except Exception as e:
        print(f"❌ Error monitoring deployment: {e}")
        return None

# Example usage
app_name = "my-web-application"
deployment_group = "production-group"

# Create deployment configurations
create_deployment_config('linear', app_name)
create_deployment_config('canary', app_name)

# Deploy using different strategies
strategies = ['all_at_once', 'linear', 'canary']

for strategy in strategies:
    print(f"\n🚀 Testing {strategy} deployment...")
    deployment_id = deploy_application(
        app_name, 
        deployment_group, 
        strategy,
        'my-deployment-bucket',
        'releases/v1.2.3.zip'
    )
    
    if deployment_id:
        status = monitor_deployment(deployment_id)
        print(f"Final status: {status}")
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def blue_green_tab():
    """Content for Blue/Green Deployment tab"""
    st.markdown("## 🔵 Blue/Green Deployment")
    st.markdown("*Zero-downtime deployment with instant rollback capability*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Blue/Green deployment** maintains two identical production environments. While one serves live traffic (Blue), 
    the other (Green) receives the new version. After testing, traffic switches instantly to Green, providing 
    zero-downtime deployment with fast rollback capability.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Blue/Green Flow Diagram
    st.markdown("### 🔄 Blue/Green Deployment Flow")
    common.mermaid(create_blue_green_mermaid(), height=450)
    
    # Interactive Blue/Green Simulator
    st.markdown("### 🎮 Interactive Blue/Green Deployment Simulator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔵 Blue Environment (Current)")
        blue_version = st.text_input("Current Version:", "v1.2.0")
        blue_instances = st.slider("Blue Instances:", 1, 10, 3)
        blue_health = st.selectbox("Blue Health Status:", ["Healthy", "Degraded", "Unhealthy"])
        blue_traffic = st.slider("Blue Traffic %:", 0, 100, 100)
    
    with col2:
        st.markdown("### 🟢 Green Environment (New)")
        green_version = st.text_input("New Version:", "v1.3.0")
        green_instances = st.slider("Green Instances:", 0, 10, 3)
        green_health = st.selectbox("Green Health Status:", ["Healthy", "Degraded", "Unhealthy", "Not Deployed"])
        green_traffic = st.slider("Green Traffic %:", 0, 100, 0)
    
    # Deployment Actions
    st.markdown("### 🎛️ Deployment Control Panel")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🚀 Deploy to Green", use_container_width=True):
            st.session_state.deployment_status = "Deploying to Green environment..."
            st.session_state.green_deployed = True
    
    with col2:
        if st.button("🧪 Test Green Environment", use_container_width=True):
            if st.session_state.get('green_deployed', False):
                st.session_state.deployment_status = "Testing Green environment..."
                st.session_state.green_tested = True
            else:
                st.session_state.deployment_status = "❌ Deploy to Green first!"
    
    with col3:
        if st.button("🔄 Switch Traffic to Green", use_container_width=True):
            if st.session_state.get('green_tested', False):
                st.session_state.deployment_status = "✅ Traffic switched to Green!"
                st.session_state.traffic_switched = True
            else:
                st.session_state.deployment_status = "❌ Test Green environment first!"
    
    with col4:
        if st.button("⏪ Rollback to Blue", use_container_width=True):
            st.session_state.deployment_status = "⏪ Rolled back to Blue environment"
            st.session_state.traffic_switched = False
    
    # Show deployment status
    if 'deployment_status' in st.session_state:
        if "✅" in st.session_state.deployment_status:
            st.success(st.session_state.deployment_status)
        elif "❌" in st.session_state.deployment_status:
            st.error(st.session_state.deployment_status)
        else:
            st.info(st.session_state.deployment_status)
    
    # Benefits and Challenges
    st.markdown("### ✨ Blue/Green Benefits & Challenges")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ✅ Benefits
        - **Zero Downtime**: Instant traffic switching
        - **Fast Rollback**: Immediate switch back to Blue
        - **Production Testing**: Test with real infrastructure
        - **Risk Reduction**: Full environment isolation
        - **Database Compatibility**: Can handle schema changes
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ❌ Challenges
        - **Infrastructure Cost**: Doubles resource requirements
        - **Database Complexity**: Schema sync challenges
        - **Environment Drift**: Keeping environments identical
        - **Stateful Applications**: Session management issues
        - **Testing Complexity**: Full end-to-end testing needed
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Use Cases
    st.markdown("### 🌟 Ideal Use Cases for Blue/Green")
    
    use_cases_data = {
        'Application Type': [
            'E-commerce Platforms',
            'Financial Services',
            'Healthcare Systems', 
            'Media Streaming',
            'SaaS Applications',
            'Mobile App Backends'
        ],
        'Why Blue/Green?': [
            'Zero tolerance for downtime during sales',
            'Regulatory compliance requirements',
            'Patient safety and data integrity',
            'Uninterrupted service for global users',
            'Customer retention and SLA requirements',
            'Mobile apps cannot handle service interruptions'
        ],
        'Key Benefit': [
            'Revenue protection',
            'Compliance assurance',
            'Safety guarantee',
            'User experience',
            'SLA compliance',
            'App store ratings'
        ]
    }
    
    df_use_cases = pd.DataFrame(use_cases_data)
    st.dataframe(df_use_cases, use_container_width=True)
    
    # AWS Services for Blue/Green
    st.markdown("### 🛠️ AWS Services Supporting Blue/Green")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🚀 AWS CodeDeploy
        - **EC2/On-premises**: Blue/Green with load balancers
        - **Lambda**: Version-based deployments
        - **ECS**: Service-level Blue/Green
        - **Built-in health checks** and rollback
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🌱 AWS Elastic Beanstalk
        - **Environment cloning** for Blue/Green
        - **URL swapping** for traffic switch
        - **Rollback capability** to previous version
        - **Integrated monitoring** and health checks
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📦 Amazon ECS
        - **Service updates** with Blue/Green
        - **Task definition** versioning
        - **Application Load Balancer** integration
        - **Container-level** deployment control
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Cost Analysis
    st.markdown("### 💰 Blue/Green Cost Analysis")
    
    # Interactive cost calculator
    st.markdown("### 🧮 Blue/Green Cost Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ec2_instances = st.slider("EC2 Instances per Environment:", 1, 20, 5)
        instance_type = st.selectbox("Instance Type:", [
            "t3.micro ($0.0104/hr)", "t3.small ($0.0208/hr)", 
            "t3.medium ($0.0416/hr)", "m5.large ($0.096/hr)"
        ])
        hours_per_deployment = st.slider("Hours per Deployment:", 1, 24, 4)
    
    with col2:
        deployments_per_month = st.slider("Deployments per Month:", 1, 100, 10)
        rds_cost = st.slider("RDS Instance Cost ($/hr):", 0.0, 5.0, 0.5)
        load_balancer_hours = st.slider("Load Balancer Hours:", 0, 744, 744)  # Full month
    
    if st.button("💰 Calculate Blue/Green Costs"):
        # Extract hourly cost from instance type
        hourly_cost = float(instance_type.split('$')[1].split('/')[0])
        
        # Calculate costs
        monthly_base_cost = ec2_instances * hourly_cost * 744  # One environment running full time
        deployment_cost = ec2_instances * hourly_cost * hours_per_deployment * deployments_per_month  # Second environment during deployments
        rds_additional_cost = rds_cost * hours_per_deployment * deployments_per_month  # Additional RDS if needed
        alb_cost = 0.0225 * load_balancer_hours  # ALB cost per hour
        
        total_monthly_cost = monthly_base_cost + deployment_cost + rds_additional_cost + alb_cost
        
        # Compare with single environment
        single_env_cost = ec2_instances * hourly_cost * 744 + rds_cost * 744 + alb_cost
        additional_cost = total_monthly_cost - single_env_cost
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Base Environment", f"${monthly_base_cost:.2f}/mo")
        with col2:
            st.metric("Deployment Overhead", f"${deployment_cost:.2f}/mo")
        with col3:
            st.metric("Total Blue/Green Cost", f"${total_monthly_cost:.2f}/mo")
        with col4:
            st.metric("Additional Cost", f"${additional_cost:.2f}/mo", 
                     f"{(additional_cost/single_env_cost*100):.1f}% more")
    
    # Code Example
    st.markdown("### 💻 Code Example: Blue/Green Deployment with AWS CodeDeploy")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Blue/Green deployment implementation with AWS CodeDeploy
import boto3
import time
import json

def create_blue_green_deployment(application_name, deployment_group_name, s3_bucket, s3_key):
    """Create Blue/Green deployment using AWS CodeDeploy"""
    codedeploy = boto3.client('codedeploy')
    
    try:
        response = codedeploy.create_deployment(
            applicationName=application_name,
            deploymentGroupName=deployment_group_name,
            deploymentConfigName='CodeDeployDefault.BlueGreen',
            revision={
                'revisionType': 'S3',
                's3Location': {
                    'bucket': s3_bucket,
                    'key': s3_key,
                    'bundleType': 'zip'
                }
            },
            description='Blue/Green deployment with zero downtime',
            ignoreApplicationStopFailures=False,
            autoRollbackConfiguration={
                'enabled': True,
                'events': [
                    'DEPLOYMENT_FAILURE',
                    'DEPLOYMENT_STOP_ON_ALARM',
                    'DEPLOYMENT_STOP_ON_INSTANCE_FAILURE'
                ]
            },
            blueGreenDeploymentConfiguration={
                'terminateBlueInstancesOnDeploymentSuccess': {
                    'action': 'TERMINATE',
                    'terminationWaitTimeInMinutes': 60
                },
                'deploymentReadyOption': {
                    'actionOnTimeout': 'CONTINUE_DEPLOYMENT_WITH_TIMEOUT',
                    'waitTimeInMinutes': 10
                },
                'greenFleetProvisioningOption': {
                    'action': 'COPY_AUTO_SCALING_GROUP'
                }
            }
        )
        
        deployment_id = response['deploymentId']
        print(f"🔵 Blue/Green deployment started: {deployment_id}")
        return deployment_id
        
    except Exception as e:
        print(f"❌ Blue/Green deployment failed: {e}")
        return None

def monitor_blue_green_deployment(deployment_id):
    """Monitor Blue/Green deployment progress with detailed status"""
    codedeploy = boto3.client('codedeploy')
    
    deployment_phases = [
        'Created', 'Queued', 'InProgress', 'Ready', 'Succeeded', 'Failed', 'Stopped'
    ]
    current_phase = 0
    
    while True:
        try:
            response = codedeploy.get_deployment(deploymentId=deployment_id)
            deployment = response['deploymentInfo']
            
            status = deployment['status']
            print(f"🔄 Deployment Status: {status}")
            
            # Blue/Green specific information
            if 'blueGreenDeploymentConfiguration' in deployment:
                bg_config = deployment['blueGreenDeploymentConfiguration']
                
                # Show target group info if available
                if 'targetGroupInfoList' in deployment:
                    for tg in deployment['targetGroupInfoList']:
                        print(f"  🎯 Target Group: {tg.get('name', 'Unknown')}")
                
                # Show load balancer info
                if 'loadBalancerInfoList' in deployment:
                    for lb in deployment['loadBalancerInfoList']:
                        if 'targetGroupInfoList' in lb:
                            for tg in lb['targetGroupInfoList']:
                                print(f"  ⚖️ Load Balancer Target: {tg.get('name', 'Unknown')}")
            
            # Deployment overview
            if 'deploymentOverview' in deployment:
                overview = deployment['deploymentOverview']
                print(f"  📊 Deployment Progress:")
                print(f"    ✅ Succeeded: {overview.get('Succeeded', 0)}")
                print(f"    🔄 In Progress: {overview.get('InProgress', 0)}")
                print(f"    ⏳ Pending: {overview.get('Pending', 0)}")
                print(f"    ❌ Failed: {overview.get('Failed', 0)}")
            
            if status in ['Succeeded', 'Failed', 'Stopped']:
                print(f"🏁 Final Status: {status}")
                break
                
            time.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            print(f"❌ Error monitoring deployment: {e}")
            break
    
    return status

def rollback_blue_green_deployment(deployment_id):
    """Rollback Blue/Green deployment"""
    codedeploy = boto3.client('codedeploy')
    
    try:
        response = codedeploy.stop_deployment(
            deploymentId=deployment_id,
            autoRollbackEnabled=True
        )
        
        print(f"⏪ Rollback initiated for deployment: {deployment_id}")
        return response
        
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        return None

def validate_green_environment(load_balancer_arn, target_group_arn):
    """Validate Green environment health before traffic switch"""
    elbv2 = boto3.client('elbv2')
    
    try:
        # Check target group health
        response = elbv2.describe_target_health(TargetGroupArn=target_group_arn)
        
        healthy_targets = 0
        total_targets = 0
        
        for target in response['TargetHealthDescriptions']:
            total_targets += 1
            if target['TargetHealth']['State'] == 'healthy':
                healthy_targets += 1
        
        health_percentage = (healthy_targets / total_targets) * 100 if total_targets > 0 else 0
        
        print(f"🟢 Green Environment Health Check:")
        print(f"  Healthy Targets: {healthy_targets}/{total_targets}")
        print(f"  Health Percentage: {health_percentage:.1f}%")
        
        # Validation criteria
        if health_percentage >= 100:
            print("✅ Green environment is ready for traffic")
            return True
        elif health_percentage >= 80:
            print("⚠️ Green environment partially healthy - proceed with caution")
            return False
        else:
            print("❌ Green environment not ready - deployment should be stopped")
            return False
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

# Example usage for Blue/Green deployment
def deploy_application_blue_green():
    """Complete Blue/Green deployment workflow"""
    
    # Configuration
    app_name = "my-web-application"
    deployment_group = "production-blue-green"
    s3_bucket = "my-deployment-artifacts"
    s3_key = "releases/v2.0.0.zip"
    
    print("🚀 Starting Blue/Green Deployment Process")
    print("=" * 50)
    
    # Step 1: Create deployment
    deployment_id = create_blue_green_deployment(
        app_name, deployment_group, s3_bucket, s3_key
    )
    
    if not deployment_id:
        print("❌ Failed to create deployment")
        return
    
    # Step 2: Monitor deployment
    final_status = monitor_blue_green_deployment(deployment_id)
    
    # Step 3: Handle results
    if final_status == 'Succeeded':
        print("🎉 Blue/Green deployment completed successfully!")
        print("✅ Traffic has been switched to the Green environment")
        print("🗑️ Blue environment will be terminated after cooldown period")
    elif final_status == 'Failed':
        print("❌ Blue/Green deployment failed")
        print("🔄 Automatic rollback should have occurred")
    else:
        print(f"⚠️ Deployment ended with status: {final_status}")

# Run the deployment
deploy_application_blue_green()
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def all_at_once_tab():
    """Content for All at Once Deployment tab"""
    st.markdown("## 🔄 All at Once Deployment")
    st.markdown("*Fast deployment strategy where all instances are updated simultaneously*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **All at Once deployment** terminates the current version and deploys the new version to all instances 
    simultaneously. This is the fastest deployment method but results in downtime and carries higher risk 
    since all instances are affected at once.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # All at Once Characteristics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### ⚡\n**Fastest**\nDeployment Speed")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 💰\n**Lowest**\nInfrastructure Cost")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### ⏰\n**Brief**\nDowntime Required")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🎯\n**Simple**\nImplementation")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive All at Once Simulator
    st.markdown("### 🎮 Interactive All at Once Deployment Simulator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚙️ Deployment Configuration")
        instance_count = st.slider("Number of Instances:", 1, 20, 6)
        deployment_time = st.slider("Deployment Time per Instance (seconds):", 30, 300, 90)
        failure_probability = st.slider("Failure Probability (%):", 0, 50, 5)
        rollback_time = st.slider("Rollback Time (seconds):", 60, 600, 180)
    
    with col2:
        st.markdown("### 📊 Current Status")
        current_version = st.text_input("Current Version:", "v1.4.2")
        new_version = st.text_input("New Version:", "v1.5.0")
        environment = st.selectbox("Environment:", ["Development", "Staging", "Production"])
    
    # Deployment simulation
    if st.button("🚀 Start All at Once Deployment", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simulate deployment
        total_time = deployment_time * instance_count
        
        for i in range(instance_count):
            # Simulate deployment to each instance
            progress = (i + 1) / instance_count
            progress_bar.progress(progress)
            status_text.text(f"Deploying to instance {i+1}/{instance_count}...")
            
            # Simulate failure
            if np.random.randint(0, 100) < failure_probability:
                st.error(f"❌ Deployment failed on instance {i+1}!")
                st.warning(f"⏪ Rolling back... (estimated {rollback_time} seconds)")
                time.sleep(1)  # Brief pause for effect
                st.info("🔄 All instances rolled back to previous version")
                st.session_state.deployment_failed = True
                break
            
            time.sleep(0.5)  # Brief pause for visual effect
        else:
            st.success("✅ All at Once deployment completed successfully!")
            st.info(f"🎉 All {instance_count} instances updated from {current_version} to {new_version}")
            st.session_state.deployment_failed = False
        
        progress_bar.empty()
        status_text.empty()
    
    # Deployment Analysis
    if st.session_state.get('deployment_failed'):
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚠️ Deployment Analysis: Failed
        
        **What Happened:**
        - Deployment failed on one or more instances
        - All instances were rolled back to prevent inconsistent state
        - Service experienced brief downtime during rollback
        
        **Mitigation Strategies:**
        - Use staging environment for thorough testing
        - Implement health checks before deployment
        - Consider blue/green or rolling deployment for production
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    elif 'deployment_failed' in st.session_state and not st.session_state.deployment_failed:
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown("""
        ### ✅ Deployment Analysis: Successful
        
        **What Happened:**
        - All instances successfully updated simultaneously
        - Minimal downtime during the deployment process
        - Fast completion due to parallel execution
        
        **Benefits Realized:**
        - Quick deployment completion
        - No additional infrastructure costs
        - Simple rollback if needed
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # When to Use All at Once
    st.markdown("### 🎯 When to Use All at Once Deployment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ✅ Good Use Cases
        - **Development environments** where downtime is acceptable
        - **Testing/staging** environments for quick iterations
        - **Single-instance applications** where rolling isn't possible
        - **Emergency patches** that need immediate deployment
        - **Cost-sensitive** deployments where infrastructure doubling isn't feasible
        - **Simple applications** with minimal deployment complexity
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ❌ Avoid for These Cases
        - **Production applications** with high availability requirements
        - **Customer-facing services** where downtime affects revenue
        - **Financial applications** where service interruption is costly
        - **Global applications** serving users across time zones
        - **Compliance-critical** systems with strict uptime requirements
        - **High-traffic applications** where even brief outages have major impact
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # AWS Service Configurations
    st.markdown("### 🛠️ AWS Service Configurations for All at Once")
    
    service_configs = {
        'AWS CodeDeploy': {
            'Config Name': 'CodeDeployDefault.AllAtOnce',
            'Description': 'Deploys to all instances simultaneously',
            'Use Case': 'EC2 instances and on-premises servers',
            'Rollback': 'Manual or automatic on failure'
        },
        'AWS Lambda': {
            'Config Name': 'CodeDeployDefault.LambdaAllAtOnce',
            'Description': 'Updates function code instantly',
            'Use Case': 'Serverless function deployments',
            'Rollback': 'Version-based rollback'
        },
        'Amazon ECS': {
            'Config Name': 'CodeDeployDefault.ECSAllAtOnce',
            'Description': 'Updates all tasks at once',
            'Use Case': 'Container service deployments',
            'Rollback': 'Task definition rollback'
        }
    }
    
    for service, config in service_configs.items():
        st.markdown('<div class="deployment-card">', unsafe_allow_html=True)
        st.markdown(f"""
        ### {service}
        **Configuration:** `{config['Config Name']}`
        
        **Description:** {config['Description']}
        
        **Use Case:** {config['Use Case']}
        
        **Rollback:** {config['Rollback']}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Downtime Analysis
    st.markdown("### ⏱️ Downtime Analysis")
    
    # Interactive downtime calculator
    st.markdown("### 🧮 Downtime Impact Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        avg_deployment_time = st.slider("Average Deployment Time (minutes):", 1, 30, 5)
        deployments_per_month = st.slider("Deployments per Month:", 1, 50, 8)
        revenue_per_minute = st.slider("Revenue per Minute ($):", 0, 10000, 100)
    
    with col2:
        users_affected = st.slider("Users Affected per Deployment:", 1, 1000000, 10000)
        customer_satisfaction_impact = st.slider("Customer Satisfaction Impact (1-10):", 1, 10, 3)
        rollback_success_rate = st.slider("Rollback Success Rate (%):", 50, 100, 90)
    
    if st.button("📊 Calculate Downtime Impact"):
        # Calculate monthly downtime
        monthly_downtime = avg_deployment_time * deployments_per_month
        annual_downtime = monthly_downtime * 12
        
        # Calculate business impact
        monthly_revenue_loss = monthly_downtime * revenue_per_minute
        annual_revenue_loss = monthly_revenue_loss * 12
        
        # User impact
        total_user_minutes_lost = users_affected * monthly_downtime
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Monthly Downtime", f"{monthly_downtime} min")
        with col2:
            st.metric("Annual Downtime", f"{annual_downtime} min", f"{annual_downtime/60:.1f} hours")
        with col3:
            st.metric("Monthly Revenue Impact", f"${monthly_revenue_loss:,.0f}")
        with col4:
            st.metric("User Minutes Lost/Month", f"{total_user_minutes_lost:,.0f}")
        
        # Recommendations based on impact
        if monthly_revenue_loss > 10000:
            st.error("💸 High revenue impact detected! Consider Blue/Green or Canary deployment.")
        elif monthly_revenue_loss > 1000:
            st.warning("⚠️ Moderate revenue impact. Consider Linear deployment for production.")
        else:
            st.success("✅ Low revenue impact. All at Once may be acceptable for your use case.")
    
    # Best Practices
    st.markdown("### 💡 All at Once Best Practices")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🛡️ Risk Mitigation Strategies
    
    **Pre-deployment:**
    - **Thorough testing** in staging environment identical to production
    - **Automated health checks** before and after deployment
    - **Database migration testing** with rollback procedures
    - **Communication plan** to notify stakeholders of downtime
    
    **During deployment:**
    - **Monitor deployment** progress and application health
    - **Have rollback plan** ready and tested
    - **Implement timeouts** to prevent stuck deployments
    - **Use deployment automation** to reduce human error
    
    **Post-deployment:**
    - **Immediate health verification** of all instances
    - **Performance monitoring** to detect regressions
    - **User feedback monitoring** for functional issues
    - **Rollback if any issues** detected quickly
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: All at Once Deployment")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# All at Once deployment implementation with comprehensive monitoring
import boto3
import time
import concurrent.futures
from datetime import datetime

def deploy_all_at_once(application_name, deployment_group, s3_bucket, s3_key):
    """Execute All at Once deployment with monitoring"""
    codedeploy = boto3.client('codedeploy')
    
    deployment_start = datetime.now()
    
    try:
        # Create deployment with All at Once configuration
        response = codedeploy.create_deployment(
            applicationName=application_name,
            deploymentGroupName=deployment_group,
            deploymentConfigName='CodeDeployDefault.AllAtOnce',
            revision={
                'revisionType': 'S3',
                's3Location': {
                    'bucket': s3_bucket,
                    'key': s3_key,
                    'bundleType': 'zip'
                }
            },
            description=f'All at Once deployment started at {deployment_start}',
            ignoreApplicationStopFailures=False,
            autoRollbackConfiguration={
                'enabled': True,
                'events': [
                    'DEPLOYMENT_FAILURE',
                    'DEPLOYMENT_STOP_ON_ALARM',
                    'DEPLOYMENT_STOP_ON_INSTANCE_FAILURE'
                ]
            }
        )
        
        deployment_id = response['deploymentId']
        print(f"🚀 All at Once deployment started: {deployment_id}")
        print(f"⏰ Start time: {deployment_start}")
        
        return deployment_id, deployment_start
        
    except Exception as e:
        print(f"❌ Failed to start deployment: {e}")
        return None, None

def monitor_all_at_once_deployment(deployment_id, start_time):
    """Monitor All at Once deployment with detailed progress tracking"""
    codedeploy = boto3.client('codedeploy')
    
    previous_status = None
    downtime_start = None
    
    while True:
        try:
            response = codedeploy.get_deployment(deploymentId=deployment_id)
            deployment = response['deploymentInfo']
            
            current_status = deployment['status']
            current_time = datetime.now()
            
            # Track status changes
            if current_status != previous_status:
                print(f"📊 Status changed: {previous_status} → {current_status}")
                print(f"⏰ Time: {current_time}")
                
                # Track downtime period
                if current_status == 'InProgress' and not downtime_start:
                    downtime_start = current_time
                    print("⏸️ Downtime started - application unavailable")
                elif current_status in ['Succeeded', 'Failed'] and downtime_start:
                    downtime_duration = (current_time - downtime_start).total_seconds()
                    print(f"⏱️ Downtime duration: {downtime_duration:.1f} seconds")
                
                previous_status = current_status
            
            # Show deployment progress
            if 'deploymentOverview' in deployment:
                overview = deployment['deploymentOverview']
                total_instances = sum([
                    overview.get('Succeeded', 0),
                    overview.get('InProgress', 0),
                    overview.get('Pending', 0),
                    overview.get('Failed', 0),
                    overview.get('Skipped', 0)
                ])
                
                if total_instances > 0:
                    success_rate = (overview.get('Succeeded', 0) / total_instances) * 100
                    print(f"  📈 Progress: {success_rate:.1f}% ({overview.get('Succeeded', 0)}/{total_instances})")
                    print(f"    ✅ Succeeded: {overview.get('Succeeded', 0)}")
                    print(f"    🔄 In Progress: {overview.get('InProgress', 0)}")
                    print(f"    ⏳ Pending: {overview.get('Pending', 0)}")
                    print(f"    ❌ Failed: {overview.get('Failed', 0)}")
            
            # Check for completion
            if current_status in ['Succeeded', 'Failed', 'Stopped']:
                total_duration = (current_time - start_time).total_seconds()
                print(f"🏁 Deployment completed with status: {current_status}")
                print(f"⏱️ Total deployment time: {total_duration:.1f} seconds")
                
                if downtime_start:
                    final_downtime = (current_time - downtime_start).total_seconds()
                    print(f"⏸️ Total downtime: {final_downtime:.1f} seconds")
                
                return current_status, total_duration
                
            time.sleep(10)  # Check every 10 seconds
            
        except Exception as e:
            print(f"❌ Error monitoring deployment: {e}")
            break
    
    return 'Unknown', 0

def validate_deployment_success(deployment_id, application_name):
    """Validate that deployment was successful and application is healthy"""
    codedeploy = boto3.client('codedeploy')
    
    try:
        # Get deployment details
        response = codedeploy.get_deployment(deploymentId=deployment_id)
        deployment = response['deploymentInfo']
        
        if deployment['status'] != 'Succeeded':
            print(f"❌ Deployment status is not successful: {deployment['status']}")
            return False
        
        # Get instance details
        instances_response = codedeploy.list_deployment_instances(deploymentId=deployment_id)
        instance_ids = instances_response['instancesList']
        
        healthy_instances = 0
        total_instances = len(instance_ids)
        
        for instance_id in instance_ids:
            try:
                instance_response = codedeploy.get_deployment_instance(
                    deploymentId=deployment_id,
                    instanceId=instance_id
                )
                
                instance_summary = instance_response['instanceSummary']
                if instance_summary['status'] == 'Succeeded':
                    healthy_instances += 1
                    
            except Exception as e:
                print(f"⚠️ Could not get status for instance {instance_id}: {e}")
        
        success_rate = (healthy_instances / total_instances) * 100 if total_instances > 0 else 0
        
        print(f"🏥 Health Check Results:")
        print(f"  Healthy instances: {healthy_instances}/{total_instances}")
        print(f"  Success rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("✅ All instances healthy - deployment successful!")
            return True
        elif success_rate >= 80:
            print("⚠️ Most instances healthy - monitoring recommended")
            return True
        else:
            print("❌ Too many unhealthy instances - consider rollback")
            return False
            
    except Exception as e:
        print(f"❌ Health validation failed: {e}")
        return False

def rollback_if_needed(deployment_id, health_check_passed):
    """Rollback deployment if health checks fail"""
    if health_check_passed:
        print("✅ Health checks passed - no rollback needed")
        return True
    
    codedeploy = boto3.client('codedeploy')
    
    try:
        print("⏪ Initiating rollback due to failed health checks...")
        
        response = codedeploy.stop_deployment(
            deploymentId=deployment_id,
            autoRollbackEnabled=True
        )
        
        print(f"🔄 Rollback initiated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        return False

def execute_all_at_once_deployment():
    """Complete All at Once deployment workflow with monitoring"""
    
    # Configuration
    app_name = "my-web-application"
    deployment_group = "production-all-at-once"
    s3_bucket = "my-deployment-bucket"
    s3_key = "releases/v1.6.0.zip"
    
    print("🚀 Starting All at Once Deployment")
    print("=" * 50)
    print("⚠️  WARNING: This will cause brief downtime!")
    print("=" * 50)
    
    # Step 1: Start deployment
    deployment_id, start_time = deploy_all_at_once(
        app_name, deployment_group, s3_bucket, s3_key
    )
    
    if not deployment_id:
        print("❌ Failed to start deployment")
        return False
    
    # Step 2: Monitor deployment
    final_status, duration = monitor_all_at_once_deployment(deployment_id, start_time)
    
    # Step 3: Validate success
    if final_status == 'Succeeded':
        health_check_passed = validate_deployment_success(deployment_id, app_name)
        
        # Step 4: Rollback if needed
        if not health_check_passed:
            rollback_success = rollback_if_needed(deployment_id, health_check_passed)
            if rollback_success:
                print("🔄 Rollback completed - application restored to previous version")
            else:
                print("❌ Rollback failed - manual intervention required!")
        else:
            print("🎉 All at Once deployment completed successfully!")
            print(f"⏱️ Total time: {duration:.1f} seconds")
    else:
        print(f"❌ Deployment failed with status: {final_status}")
        print("🔄 Automatic rollback should have been triggered")
    
    return final_status == 'Succeeded'

# Execute the deployment
success = execute_all_at_once_deployment()
print(f"\n🏁 Final Result: {'Success' if success else 'Failed'}")
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def linear_tab():
    """Content for Linear Deployment tab"""
    st.markdown("## 📈 Linear Deployment")
    st.markdown("*Gradual traffic shifting with equal increments over time*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Linear deployment** gradually shifts traffic to the new version using equal increments with equal time intervals 
    between each increment. For example, 10% of traffic every 3 minutes until 100% deployment is achieved. 
    This provides a balance between deployment speed and risk mitigation.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Linear Deployment Flow
    st.markdown("### 📊 Linear Deployment Flow")
    common.mermaid(create_linear_deployment_mermaid(), height=1000)
    
    # Interactive Linear Deployment Simulator
    st.markdown("### 🎮 Interactive Linear Deployment Simulator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚙️ Linear Configuration")
        linear_percentage = st.slider("Linear Percentage per Step:", 5, 50, 10)
        linear_interval = st.slider("Linear Interval (minutes):", 1, 10, 3)
        total_instances = st.slider("Total Instances:", 5, 50, 20)
        failure_threshold = st.slider("Failure Threshold (%):", 5, 30, 10)
    
    with col2:
        st.markdown("### 📊 Deployment Preview")
        steps = 100 // linear_percentage
        total_time = steps * linear_interval
        instances_per_step = max(1, (total_instances * linear_percentage) // 100)
        
        st.info(f"""
        **Deployment Plan:**
        - **Steps**: {steps} increments
        - **Instances per step**: {instances_per_step}
        - **Total time**: {total_time} minutes
        - **Risk window**: {linear_percentage}% at a time
        """)
    
    # Deployment execution simulator
    if st.button("🚀 Start Linear Deployment", use_container_width=True):
        st.markdown("### 📊 Live Deployment Progress")
        
        progress_bar = st.progress(0)
        metrics_container = st.container()
        status_container = st.container()
        
        deployment_successful = True
        current_step = 0
        
        for step in range(1, steps + 1):
            current_percentage = step * linear_percentage
            progress_bar.progress(current_percentage / 100)
            
            # Simulate deployment step
            with status_container:
                st.info(f"⏳ Step {step}/{steps}: Deploying to {current_percentage}% of instances...")
            
            # Simulate health checks
            time.sleep(1)  # Brief pause for visual effect
            
            # Random failure simulation
            if np.random.randint(0, 100) < (failure_threshold * step / steps):  # Increasing failure chance
                deployment_successful = False
                with status_container:
                    st.error(f"❌ Deployment failed at step {step} ({current_percentage}%)!")
                    st.warning("🔄 Initiating automatic rollback...")
                    st.info("⏪ Rolling back all deployed instances to previous version")
                break
            
            # Show metrics
            with metrics_container:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Current Step", f"{step}/{steps}")
                with col2:
                    st.metric("Traffic Shifted", f"{current_percentage}%")
                with col3:
                    st.metric("Instances Updated", f"{step * instances_per_step}")
                with col4:
                    st.metric("Time Elapsed", f"{step * linear_interval} min")
            
            current_step = step
        
        if deployment_successful:
            with status_container:
                st.success("✅ Linear deployment completed successfully!")
                st.balloons()
                
            st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
            st.markdown(f"""
            ### 🎉 Deployment Summary
            
            **Deployment Details:**
            - **Total Steps**: {steps}
            - **Final Traffic**: 100% on new version
            - **Total Time**: {total_time} minutes
            - **Instances Updated**: {total_instances}
            - **Risk Mitigation**: Gradual rollout minimized impact
            
            **Key Benefits Achieved:**
            - ✅ Zero downtime during deployment
            - ✅ Gradual risk exposure
            - ✅ Early detection capability
            - ✅ Controlled rollout pace
            """)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Linear Configuration Options
    st.markdown("### 🛠️ AWS Linear Configuration Options")
    
    linear_configs = {
        'CodeDeployDefault.ECSLinear10PercentEvery1Minutes': {
            'service': 'Amazon ECS',
            'increment': '10%',
            'interval': '1 minute',
            'total_time': '10 minutes',
            'use_case': 'Fast deployments with quick validation'
        },
        'CodeDeployDefault.ECSLinear10PercentEvery3Minutes': {
            'service': 'Amazon ECS',
            'increment': '10%',
            'interval': '3 minutes',
            'total_time': '30 minutes',
            'use_case': 'Standard production deployments'
        },
        'CodeDeployDefault.LambdaLinear10PercentEvery2Minutes': {
            'service': 'AWS Lambda',
            'increment': '10%',
            'interval': '2 minutes',
            'total_time': '20 minutes',
            'use_case': 'Serverless function updates'
        },
        'CodeDeployDefault.LambdaLinear10PercentEvery10Minutes': {
            'service': 'AWS Lambda',
            'increment': '10%',
            'interval': '10 minutes',
            'total_time': '100 minutes',
            'use_case': 'Critical functions requiring careful monitoring'
        }
    }
    
    selected_config = st.selectbox("Select Linear Configuration:", list(linear_configs.keys()))
    
    config_details = linear_configs[selected_config]
    
    st.markdown('<div class="deployment-card">', unsafe_allow_html=True)
    st.markdown(f"""
    ### Configuration Details: `{selected_config}`
    
    **AWS Service:** {config_details['service']}
    
    **Traffic Increment:** {config_details['increment']} every {config_details['interval']}
    
    **Total Deployment Time:** {config_details['total_time']}
    
    **Best Use Case:** {config_details['use_case']}
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Linear vs Other Strategies
    st.markdown("### ⚖️ Linear vs Other Deployment Strategies")
    
    comparison_metrics = {
        'Metric': ['Deployment Speed', 'Risk Level', 'Downtime', 'Rollback Speed', 'Infrastructure Cost', 'Complexity'],
        'All at Once': ['Fast', 'High', 'Yes', 'Slow', 'Low', 'Low'],  
        'Linear': ['Medium', 'Medium', 'No', 'Fast', 'Medium', 'Medium'],
        'Blue/Green': ['Fast', 'Low', 'No', 'Instant', 'High', 'Medium'],
        'Canary': ['Slow', 'Very Low', 'No', 'Fast', 'Medium', 'High']
    }
    
    df_comparison = pd.DataFrame(comparison_metrics)
    st.dataframe(df_comparison, use_container_width=True)
    
    # Linear Deployment Benefits
    st.markdown("### ✨ Linear Deployment Benefits")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ✅ Advantages
        - **No Downtime**: Gradual traffic shifting maintains availability
        - **Risk Mitigation**: Limited blast radius at each step
        - **Early Detection**: Problems caught before full deployment
        - **Predictable Timeline**: Fixed intervals provide timeline certainty
        - **Automated Rollback**: Failures trigger automatic recovery
        - **Cost Effective**: No duplicate infrastructure required
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚠️ Considerations
        - **Longer Deployment Time**: Takes more time than all-at-once
        - **Monitoring Overhead**: Requires watching multiple deployment steps
        - **Version Mixing**: Temporary state with mixed versions
        - **Complexity**: More complex than simple deployments
        - **Network Effects**: Load balancer configuration changes
        - **Resource Planning**: Need enough capacity during transition
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Monitoring Linear Deployments
    st.markdown("### 📊 Monitoring Linear Deployments")
    
    # Simulate deployment metrics
    if st.button("📈 Generate Linear Deployment Metrics", use_container_width=True):
        # Create sample data for linear deployment
        steps = np.arange(0, 11)
        traffic_percentage = steps * 10
        error_rate = np.random.uniform(0.5, 2.0, len(steps))
        response_time = np.random.uniform(150, 300, len(steps))
        cpu_utilization = np.random.uniform(40, 80, len(steps))
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Traffic Distribution', 'Error Rate', 'Response Time', 'CPU Utilization'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Traffic distribution
        fig.add_trace(
            go.Scatter(x=steps, y=traffic_percentage, mode='lines+markers',
                      name='New Version Traffic %', line=dict(color=AWS_COLORS['primary'])),
            row=1, col=1
        )
        
        # Error rate
        fig.add_trace(
            go.Scatter(x=steps, y=error_rate, mode='lines+markers',
                      name='Error Rate %', line=dict(color=AWS_COLORS['warning'])),
            row=1, col=2
        )
        
        # Response time
        fig.add_trace(
            go.Scatter(x=steps, y=response_time, mode='lines+markers',
                      name='Response Time (ms)', line=dict(color=AWS_COLORS['light_blue'])),
            row=2, col=1
        )
        
        # CPU utilization
        fig.add_trace(
            go.Scatter(x=steps, y=cpu_utilization, mode='lines+markers',
                      name='CPU %', line=dict(color=AWS_COLORS['success'])),
            row=2, col=2
        )
        
        fig.update_layout(height=500, showlegend=False, title_text="Linear Deployment Metrics Over Time")
        fig.update_xaxes(title_text="Deployment Step")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Analysis
        avg_error_rate = np.mean(error_rate)
        if avg_error_rate < 1.0:
            st.success("✅ Error rates remain within acceptable limits throughout deployment")
        elif avg_error_rate < 2.0:
            st.warning("⚠️ Moderate error rates detected - monitoring recommended")
        else:
            st.error("❌ High error rates - deployment should be halted")
    
    # Code Example
    st.markdown("### 💻 Code Example: Linear Deployment Implementation")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Linear deployment implementation with comprehensive monitoring
import boto3
import time
import json
from datetime import datetime, timedelta

def create_linear_deployment(application_name, deployment_group, s3_bucket, s3_key, 
                           linear_percentage=10, linear_interval=3):
    """Create linear deployment with custom configuration"""
    codedeploy = boto3.client('codedeploy')
    
    # Calculate deployment timeline
    total_steps = 100 // linear_percentage
    total_time = total_steps * linear_interval
    
    print(f"🚀 Starting Linear Deployment")
    print(f"📊 Configuration:")
    print(f"  - Linear Percentage: {linear_percentage}% per step")
    print(f"  - Linear Interval: {linear_interval} minutes")
    print(f"  - Total Steps: {total_steps}")
    print(f"  - Estimated Time: {total_time} minutes")
    
    try:
        response = codedeploy.create_deployment(
            applicationName=application_name,
            deploymentGroupName=deployment_group,
            deploymentConfigName=f'CodeDeployDefault.ECSLinear{linear_percentage}PercentEvery{linear_interval}Minutes',
            revision={
                'revisionType': 'S3',
                's3Location': {
                    'bucket': s3_bucket,
                    'key': s3_key,
                    'bundleType': 'zip'
                }
            },
            description=f'Linear deployment {linear_percentage}% every {linear_interval}min',
            ignoreApplicationStopFailures=False,
            autoRollbackConfiguration={
                'enabled': True,
                'events': [
                    'DEPLOYMENT_FAILURE',
                    'DEPLOYMENT_STOP_ON_ALARM'
                ]
            }
        )
        
        deployment_id = response['deploymentId']
        print(f"✅ Deployment created: {deployment_id}")
        return deployment_id
        
    except Exception as e:
        print(f"❌ Failed to create deployment: {e}")
        return None

def monitor_linear_deployment_progress(deployment_id, linear_percentage, linear_interval):
    """Monitor linear deployment with step-by-step progress tracking"""
    codedeploy = boto3.client('codedeploy')
    cloudwatch = boto3.client('cloudwatch')
    
    start_time = datetime.now()
    current_step = 0
    expected_steps = 100 // linear_percentage
    
    print(f"📊 Monitoring Linear Deployment Progress")
    print("-" * 50)
    
    while True:
        try:
            # Get deployment status
            response = codedeploy.get_deployment(deploymentId=deployment_id)
            deployment = response['deploymentInfo']
            
            current_status = deployment['status']
            current_time = datetime.now()
            elapsed_time = (current_time - start_time).total_seconds() / 60  # minutes
            
            print(f"⏰ Elapsed Time: {elapsed_time:.1f} minutes")
            print(f"📊 Status: {current_status}")
            
            # Estimate current step based on elapsed time
            if current_status == 'InProgress':
                estimated_step = min(int(elapsed_time / linear_interval) + 1, expected_steps)
                estimated_percentage = min(estimated_step * linear_percentage, 100)
                
                print(f"📈 Estimated Progress: Step {estimated_step}/{expected_steps} ({estimated_percentage}%)")
                
                # Get actual deployment overview
                if 'deploymentOverview' in deployment:
                    overview = deployment['deploymentOverview']
                    total_targets = sum([
                        overview.get('Succeeded', 0),
                        overview.get('InProgress', 0),
                        overview.get('Pending', 0),
                        overview.get('Failed', 0)
                    ])
                    
                    if total_targets > 0:
                        success_percentage = (overview.get('Succeeded', 0) / total_targets) * 100
                        print(f"🎯 Actual Progress: {success_percentage:.1f}% targets completed")
                        print(f"  ✅ Succeeded: {overview.get('Succeeded', 0)}")
                        print(f"  🔄 In Progress: {overview.get('InProgress', 0)}")
                        print(f"  ⏳ Pending: {overview.get('Pending', 0)}")
                        print(f"  ❌ Failed: {overview.get('Failed', 0)}")
                        
                        # Check for failures
                        if overview.get('Failed', 0) > 0:
                            print("⚠️ Failed targets detected - monitoring for automatic rollback")
            
            # Check for completion or failure
            if current_status in ['Succeeded', 'Failed', 'Stopped']:
                total_deployment_time = elapsed_time
                print(f"🏁 Deployment completed with status: {current_status}")
                print(f"⏱️ Total time: {total_deployment_time:.1f} minutes")
                
                if current_status == 'Succeeded':
                    print("🎉 Linear deployment successful!")
                elif current_status == 'Failed':
                    print("❌ Linear deployment failed - automatic rollback should have occurred")
                else:
                    print("⏹️ Linear deployment was stopped")
                
                return current_status, total_deployment_time
            
            print("-" * 30)
            time.sleep(60)  # Check every minute
            
        except Exception as e:
            print(f"❌ Error monitoring deployment: {e}")
            break
    
    return 'Unknown', 0

def get_deployment_metrics(deployment_id, application_name):
    """Get CloudWatch metrics for the linear deployment"""
    cloudwatch = boto3.client('cloudwatch')
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=2)  # Last 2 hours
    
    metrics_to_fetch = [
        ('ApplicationELB', 'TargetResponseTime'),
        ('ApplicationELB', 'HTTPCode_Target_4XX_Count'),
        ('ApplicationELB', 'HTTPCode_Target_5XX_Count'),
        ('ApplicationELB', 'RequestCount')
    ]
    
    deployment_metrics = {}
    
    for namespace, metric_name in metrics_to_fetch:
        try:
            response = cloudwatch.get_metric_statistics(
                Namespace=f'AWS/{namespace}',
                MetricName=metric_name,
                Dimensions=[
                    {'Name': 'LoadBalancer', 'Value': f'app/{application_name}-alb/*'}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,  # 5-minute intervals
                Statistics=['Average', 'Sum']
            )
            
            if response['Datapoints']:
                deployment_metrics[metric_name] = response['Datapoints']
                
        except Exception as e:
            print(f"⚠️ Could not fetch {metric_name}: {e}")
    
    return deployment_metrics

def analyze_linear_deployment_health(metrics):
    """Analyze deployment health based on metrics"""
    health_score = 100
    issues = []
    
    # Check response time
    if 'TargetResponseTime' in metrics:
        avg_response_time = sum([dp['Average'] for dp in metrics['TargetResponseTime']]) / len(metrics['TargetResponseTime'])
        if avg_response_time > 1.0:  # > 1 second
            health_score -= 20
            issues.append(f"High response time: {avg_response_time*1000:.0f}ms")
    
    # Check error rates
    if 'HTTPCode_Target_4XX_Count' in metrics and 'RequestCount' in metrics:
        total_4xx = sum([dp['Sum'] for dp in metrics['HTTPCode_Target_4XX_Count']])
        total_requests = sum([dp['Sum'] for dp in metrics['RequestCount']])
        
        if total_requests > 0:
            error_rate_4xx = (total_4xx / total_requests) * 100
            if error_rate_4xx > 5:  # > 5% 4xx errors
                health_score -= 15
                issues.append(f"High 4xx error rate: {error_rate_4xx:.1f}%")
    
    if 'HTTPCode_Target_5XX_Count' in metrics and 'RequestCount' in metrics:
        total_5xx = sum([dp['Sum'] for dp in metrics['HTTPCode_Target_5XX_Count']])
        total_requests = sum([dp['Sum'] for dp in metrics['RequestCount']])
        
        if total_requests > 0:
            error_rate_5xx = (total_5xx / total_requests) * 100
            if error_rate_5xx > 1:  # > 1% 5xx errors
                health_score -= 30
                issues.append(f"High 5xx error rate: {error_rate_5xx:.1f}%")
    
    # Determine health status
    if health_score >= 85:
        status = "Healthy"
    elif health_score >= 70:
        status = "Warning"
    else:
        status = "Critical"
    
    return {
        'health_score': health_score,
        'status': status,
        'issues': issues
    }

def execute_linear_deployment():
    """Complete linear deployment workflow"""
    
    # Configuration
    app_name = "my-web-application"
    deployment_group = "production-linear"
    s3_bucket = "my-deployment-bucket"
    s3_key = "releases/v1.7.0.zip"
    
    # Linear configuration
    linear_percentage = 10
    linear_interval = 3
    
    print("🚀 Starting Complete Linear Deployment Workflow")
    print("=" * 60)
    
    # Step 1: Create deployment
    deployment_id = create_linear_deployment(
        app_name, deployment_group, s3_bucket, s3_key,
        linear_percentage, linear_interval
    )
    
    if not deployment_id:
        return False
    
    # Step 2: Monitor deployment progress
    final_status, duration = monitor_linear_deployment_progress(
        deployment_id, linear_percentage, linear_interval
    )
    
    # Step 3: Get deployment metrics
    if final_status == 'Succeeded':
        print("\n📊 Fetching deployment metrics...")
        metrics = get_deployment_metrics(deployment_id, app_name)
        
        if metrics:
            health_analysis = analyze_linear_deployment_health(metrics)
            
            print(f"\n🏥 Health Analysis:")
            print(f"  Health Score: {health_analysis['health_score']}/100")
            print(f"  Status: {health_analysis['status']}")
            
            if health_analysis['issues']:
                print(f"  Issues Detected:")
                for issue in health_analysis['issues']:
                    print(f"    - {issue}")
            else:
                print(f"  ✅ No issues detected")
        
        print(f"\n🎉 Linear deployment completed successfully!")
        print(f"⏱️ Duration: {duration:.1f} minutes")
        return True
    else:
        print(f"\n❌ Linear deployment failed with status: {final_status}")
        return False

# Execute linear deployment
success = execute_linear_deployment()
print(f"\n🏁 Deployment Result: {'Success' if success else 'Failed'}")
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def canary_tab():
    """Content for Canary Deployment tab"""
    st.markdown("## 🎯 Canary Deployment")
    st.markdown("*Risk-mitigated deployments with small-scale production testing*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Canary deployment** releases new versions to a small subset of users first, monitors the performance and health metrics, 
    then proceeds with full deployment only if the canary shows no issues. This approach minimizes risk by testing 
    in production with real traffic while limiting the blast radius.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Canary Deployment Flow
    st.markdown("### 🔄 Canary Deployment Flow")
    common.mermaid(create_canary_deployment_mermaid(), height=1100)
    
    # Interactive Canary Simulator  
    st.markdown("### 🎮 Interactive Canary Deployment Simulator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🐦 Canary Configuration")
        canary_percentage = st.slider("Canary Traffic Percentage:", 1, 25, 10)
        canary_duration = st.slider("Canary Duration (minutes):", 5, 60, 15)
        success_threshold = st.slider("Success Threshold (%):", 90, 100, 95)
        max_error_rate = st.slider("Max Error Rate (%):", 0.1, 5.0, 1.0)
    
    with col2:
        st.markdown("### 📊 Monitoring Metrics")
        monitor_response_time = st.checkbox("Monitor Response Time", True)
        monitor_error_rate = st.checkbox("Monitor Error Rate", True)
        monitor_cpu_usage = st.checkbox("Monitor CPU Usage", True)
        monitor_memory_usage = st.checkbox("Monitor Memory Usage", True)
    
    # Canary deployment execution
    if st.button("🚀 Start Canary Deployment", use_container_width=True):
        st.markdown("### 📊 Canary Deployment Progress")
        
        # Phase 1: Canary deployment
        st.info(f"🐦 Phase 1: Deploying to {canary_percentage}% of traffic...")
        progress_bar = st.progress(0)
        
        canary_metrics = {
            'response_time': [],
            'error_rate': [],
            'cpu_usage': [],
            'memory_usage': []
        }
        
        # Simulate canary monitoring
        canary_healthy = True
        
        for minute in range(canary_duration):
            progress_bar.progress((minute + 1) / canary_duration)
            
            # Simulate metrics
            response_time = np.random.uniform(100, 200)  # ms
            error_rate = np.random.uniform(0.1, 2.0)  # %
            cpu_usage = np.random.uniform(30, 70)  # %
            memory_usage = np.random.uniform(40, 80)  # %
            
            canary_metrics['response_time'].append(response_time)
            canary_metrics['error_rate'].append(error_rate)
            canary_metrics['cpu_usage'].append(cpu_usage)
            canary_metrics['memory_usage'].append(memory_usage)
            
            # Check for failures
            if error_rate > max_error_rate:
                canary_healthy = False
                st.error(f"❌ Canary failed at minute {minute + 1}: Error rate {error_rate:.2f}% exceeds threshold {max_error_rate}%")
                break
            
            time.sleep(0.1)  # Brief pause for visual effect
        
        progress_bar.empty()
        
        # Show canary results
        if canary_healthy:
            avg_response_time = np.mean(canary_metrics['response_time'])
            avg_error_rate = np.mean(canary_metrics['error_rate'])
            
            st.success(f"✅ Canary deployment successful!")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Avg Response Time", f"{avg_response_time:.0f}ms")
            with col2:
                st.metric("Avg Error Rate", f"{avg_error_rate:.2f}%")
            with col3:
                st.metric("Canary Traffic", f"{canary_percentage}%")
            with col4:
                st.metric("Duration", f"{canary_duration} min")
            
            # Phase 2: Full deployment
            if st.button("🚀 Proceed with Full Deployment"):
                st.info("📈 Phase 2: Deploying to remaining 90% of traffic...")
                full_progress = st.progress(0)
                
                for i in range(10):
                    full_progress.progress((i + 1) / 10)
                    time.sleep(0.2)
                
                full_progress.empty()
                st.success("🎉 Full canary deployment completed successfully!")
                st.balloons()
                
                st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
                st.markdown(f"""
                ### 🎯 Canary Deployment Summary
                
                **Phase 1 - Canary:**
                - Traffic: {canary_percentage}%
                - Duration: {canary_duration} minutes
                - Result: ✅ Passed all health checks
                
                **Phase 2 - Full Deployment:**
                - Traffic: 100%
                - Result: ✅ Successfully completed
                
                **Risk Mitigation Achieved:**
                - Limited initial exposure to {canary_percentage}% of users
                - Real production testing with actual traffic
                - Automated health monitoring and failure detection
                """)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("⏪ Canary failed - initiating automatic rollback...")
            st.info("🔄 All canary traffic has been redirected back to stable version")
    
    # Canary Configuration Options
    st.markdown("### 🛠️ AWS Canary Configuration Options")
    
    canary_configs = {
        'CodeDeployDefault.LambdaCanary10Percent5Minutes': {
            'service': 'AWS Lambda',
            'canary_traffic': '10%',
            'canary_duration': '5 minutes',
            'total_time': '5 minutes + validation',
            'use_case': 'Quick serverless function validation'
        },
        'CodeDeployDefault.LambdaCanary10Percent30Minutes': {
            'service': 'AWS Lambda', 
            'canary_traffic': '10%',
            'canary_duration': '30 minutes',
            'total_time': '30 minutes + validation',
            'use_case': 'Thorough serverless function testing'
        },
        'CodeDeployDefault.ECSCanary10Percent5Minutes': {
            'service': 'Amazon ECS',
            'canary_traffic': '10%',
            'canary_duration': '5 minutes',
            'total_time': '5 minutes + validation',
            'use_case': 'Container application quick validation'
        },
        'CodeDeployDefault.ECSCanary10Percent15Minutes': {
            'service': 'Amazon ECS',
            'canary_traffic': '10%',
            'canary_duration': '15 minutes',
            'total_time': '15 minutes + validation',
            'use_case': 'Standard container application testing'
        }
    }
    
    selected_canary_config = st.selectbox("Select Canary Configuration:", list(canary_configs.keys()))
    
    config_details = canary_configs[selected_canary_config]
    
    st.markdown('<div class="deployment-card">', unsafe_allow_html=True)
    st.markdown(f"""
    ### Configuration: `{selected_canary_config}`
    
    **AWS Service:** {config_details['service']}
    
    **Canary Traffic:** {config_details['canary_traffic']} for {config_details['canary_duration']}
    
    **Total Time:** {config_details['total_time']}
    
    **Use Case:** {config_details['use_case']}
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Canary Metrics and Monitoring
    st.markdown("### 📊 Canary Monitoring Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔍 Application Metrics
        - **Response Time**: Latency compared to baseline
        - **Error Rate**: 4xx/5xx errors percentage
        - **Throughput**: Requests per second handling
        - **Success Rate**: Successful transaction percentage
        - **Custom Business Metrics**: Conversion, revenue, etc.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🖥️ Infrastructure Metrics
        - **CPU Utilization**: Processor usage patterns
        - **Memory Usage**: RAM consumption trends
        - **Network I/O**: Data transfer rates
        - **Disk I/O**: Storage performance metrics
        - **Container Health**: Pod/task status in orchestration
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Canary Success Criteria
    st.markdown("### ✅ Canary Success Criteria")
    
    success_criteria_data = {
        'Metric Category': ['Performance', 'Reliability', 'Business', 'Infrastructure', 'Security'],
        'Key Indicators': [
            'Response time within 10% of baseline',
            'Error rate < 1% for 4xx, < 0.1% for 5xx',
            'Conversion rate maintains baseline',
            'CPU/Memory usage within normal ranges',
            'No security alerts or anomalies'
        ],
        'Failure Actions': [
            'Immediate rollback if >20% slower',
            'Rollback if error threshold exceeded',
            'Alert stakeholders, consider rollback',
            'Scale resources or rollback',
            'Immediate security team notification'
        ],
        'Monitoring Duration': ['Continuous', 'Continuous', 'Full canary period', 'Continuous', 'Continuous']
    }
    
    df_success_criteria = pd.DataFrame(success_criteria_data)
    st.dataframe(df_success_criteria, use_container_width=True)
    
    # Canary vs A/B Testing
    st.markdown("### 🆚 Canary vs A/B Testing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 Canary Deployment
        **Purpose**: Risk mitigation and deployment validation
        
        **Focus**: 
        - Technical metrics (performance, errors)
        - Infrastructure stability
        - Deployment success validation
        
        **Decision**: Deploy or rollback based on technical health
        
        **Duration**: Minutes to hours
        
        **Traffic Split**: Small percentage (5-15%) then all
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🧪 A/B Testing
        **Purpose**: Feature effectiveness and user experience
        
        **Focus**:
        - Business metrics (conversion, engagement)
        - User behavior analysis
        - Feature performance comparison
        
        **Decision**: Keep best-performing variant
        
        **Duration**: Days to weeks
        
        **Traffic Split**: Usually 50/50 or other balanced splits
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Advanced Canary Strategies
    st.markdown("### 🚀 Advanced Canary Strategies")
    
    advanced_strategies = {
        'Strategy': [
            'Geographic Canary',
            'User Segment Canary', 
            'Feature Flag Canary',
            'Multi-Stage Canary',
            'Automated Canary'
        ],
        'Description': [
            'Deploy to specific regions first',
            'Target specific user groups (beta users, employees)',
            'Use feature flags to control canary exposure',
            'Multiple canary phases (1%, 5%, 25%, 100%)',
            'AI/ML-driven canary decisions based on metrics'
        ],
        'Best For': [
            'Global applications with regional variations',
            'B2B applications with diverse user types',
            'Complex features requiring granular control',
            'High-risk deployments requiring gradual validation',
            'High-frequency deployments with consistent patterns'
        ]
    }
    
    df_advanced = pd.DataFrame(advanced_strategies)
    st.dataframe(df_advanced, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Advanced Canary Deployment")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Advanced Canary deployment with comprehensive monitoring and automated decision making
import boto3
import time
import json
import statistics
from datetime import datetime, timedelta

class CanaryDeploymentManager:
    def __init__(self, application_name, deployment_group):
        self.application_name = application_name
        self.deployment_group = deployment_group
        self.codedeploy = boto3.client('codedeploy')
        self.cloudwatch = boto3.client('cloudwatch')
        self.deployment_id = None
        self.canary_start_time = None
        
    def create_canary_deployment(self, s3_bucket, s3_key, canary_percentage=10, canary_duration=15):
        """Create canary deployment with specified configuration"""
        
        config_name = f'CodeDeployDefault.ECSCanary{canary_percentage}Percent{canary_duration}Minutes'
        
        try:
            response = self.codedeploy.create_deployment(
                applicationName=self.application_name,
                deploymentGroupName=self.deployment_group,
                deploymentConfigName=config_name,
                revision={
                    'revisionType': 'S3',
                    's3Location': {
                        'bucket': s3_bucket,
                        'key': s3_key,
                        'bundleType': 'zip'
                    }
                },
                description=f'Canary deployment: {canary_percentage}% for {canary_duration} minutes',
                ignoreApplicationStopFailures=False,
                autoRollbackConfiguration={
                    'enabled': True,
                    'events': [
                        'DEPLOYMENT_FAILURE',
                        'DEPLOYMENT_STOP_ON_ALARM'
                    ]
                }
            )
            
            self.deployment_id = response['deploymentId']
            self.canary_start_time = datetime.now()
            
            print(f"🐦 Canary deployment created: {self.deployment_id}")
            print(f"📊 Configuration: {canary_percentage}% traffic for {canary_duration} minutes")
            
            return self.deployment_id
            
        except Exception as e:
            print(f"❌ Failed to create canary deployment: {e}")
            return None
    
    def monitor_canary_health(self, duration_minutes=15):
        """Monitor canary deployment health with comprehensive metrics"""
        
        print(f"🔍 Starting canary health monitoring for {duration_minutes} minutes...")
        
        end_time = self.canary_start_time + timedelta(minutes=duration_minutes)
        health_checks = []
        
        while datetime.now() < end_time:
            try:
                # Get deployment status
                deployment_response = self.codedeploy.get_deployment(deploymentId=self.deployment_id)
                deployment_status = deployment_response['deploymentInfo']['status']
                
                if deployment_status in ['Failed', 'Stopped']:
                    print(f"❌ Canary deployment failed with status: {deployment_status}")
                    return False, "Deployment failed"
                
                # Collect metrics
                metrics = self.collect_canary_metrics()
                health_score = self.calculate_health_score(metrics)
                health_checks.append(health_score)
                
                elapsed_minutes = (datetime.now() - self.canary_start_time).total_seconds() / 60
                print(f"⏰ Minute {elapsed_minutes:.1f}: Health Score {health_score}/100")
                
                # Early failure detection
                if health_score < 70:
                    print(f"🚨 Critical health score detected: {health_score}/100")
                    print("⏪ Initiating immediate rollback...")
                    return False, f"Health score too low: {health_score}/100"
                
                # If we have enough data points, check for trends
                if len(health_checks) >= 3:
                    recent_trend = statistics.mean(health_checks[-3:])
                    if recent_trend < 80:
                        print(f"📉 Declining health trend detected: {recent_trend:.1f}/100")
                        print("⚠️ Consider stopping canary deployment")
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"⚠️ Error during health monitoring: {e}")
                time.sleep(60)
                continue
        
        # Final health assessment
        if health_checks:
            avg_health = statistics.mean(health_checks)
            min_health = min(health_checks)
            
            print(f"📊 Canary Health Summary:")
            print(f"  Average Health: {avg_health:.1f}/100")
            print(f"  Minimum Health: {min_health}/100")
            print(f"  Total Checks: {len(health_checks)}")
            
            if avg_health >= 90 and min_health >= 80:
                print("✅ Canary health is excellent - proceed with full deployment")
                return True, "Excellent health"
            elif avg_health >= 80 and min_health >= 70:
                print("⚠️ Canary health is acceptable - proceed with caution")
                return True, "Acceptable health"
            else:
                print("❌ Canary health is poor - recommend rollback")
                return False, f"Poor health: avg={avg_health:.1f}, min={min_health}"
        
        return False, "No health data collected"
    
    def collect_canary_metrics(self):
        """Collect comprehensive metrics for canary analysis"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=5)  # Last 5 minutes
        
        metrics = {}
        
        # Application Load Balancer metrics
        alb_metrics = [
            ('TargetResponseTime', 'Average'),
            ('HTTPCode_Target_4XX_Count', 'Sum'),
            ('HTTPCode_Target_5XX_Count', 'Sum'),
            ('RequestCount', 'Sum'),
            ('HealthyHostCount', 'Average'),
            ('UnHealthyHostCount', 'Average')
        ]
        
        for metric_name, stat in alb_metrics:
            try:
                response = self.cloudwatch.get_metric_statistics(
                    Namespace='AWS/ApplicationELB',
                    MetricName=metric_name,
                    Dimensions=[
                        {'Name': 'LoadBalancer', 'Value': f'app/{self.application_name}-alb/*'}
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=300,  # 5-minute periods
                    Statistics=[stat]
                )
                
                if response['Datapoints']:
                    if stat == 'Average':
                        metrics[metric_name] = statistics.mean([dp['Average'] for dp in response['Datapoints']])
                    else:
                        metrics[metric_name] = sum([dp['Sum'] for dp in response['Datapoints']])
                        
            except Exception as e:
                print(f"⚠️ Could not fetch {metric_name}: {e}")
        
        # ECS metrics for container health
        ecs_metrics = ['CPUUtilization', 'MemoryUtilization']
        
        for metric_name in ecs_metrics:
            try:
                response = self.cloudwatch.get_metric_statistics(
                    Namespace='AWS/ECS',
                    MetricName=metric_name,
                    Dimensions=[
                        {'Name': 'ServiceName', 'Value': self.application_name},
                        {'Name': 'ClusterName', 'Value': f'{self.application_name}-cluster'}
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=300,
                    Statistics=['Average']
                )
                
                if response['Datapoints']:
                    metrics[metric_name] = statistics.mean([dp['Average'] for dp in response['Datapoints']])
                    
            except Exception as e:
                print(f"⚠️ Could not fetch ECS {metric_name}: {e}")
        
        return metrics
    
    def calculate_health_score(self, metrics):
        """Calculate overall health score based on collected metrics"""
        score = 100
        issues = []
        
        # Response time check (weight: 25%)
        if 'TargetResponseTime' in metrics:
            response_time = metrics['TargetResponseTime'] * 1000  # Convert to ms
            if response_time > 2000:  # > 2 seconds
                score -= 30
                issues.append(f"Very high response time: {response_time:.0f}ms")
            elif response_time > 1000:  # > 1 second
                score -= 15
                issues.append(f"High response time: {response_time:.0f}ms")
            elif response_time > 500:  # > 500ms
                score -= 5
                issues.append(f"Elevated response time: {response_time:.0f}ms")
        
        # Error rate check (weight: 35%)
        if all(key in metrics for key in ['HTTPCode_Target_4XX_Count', 'HTTPCode_Target_5XX_Count', 'RequestCount']):
            total_requests = metrics['RequestCount']
            if total_requests > 0:
                error_4xx_rate = (metrics['HTTPCode_Target_4XX_Count'] / total_requests) * 100
                error_5xx_rate = (metrics['HTTPCode_Target_5XX_Count'] / total_requests) * 100
                
                if error_5xx_rate > 1:  # > 1% server errors
                    score -= 40
                    issues.append(f"High 5xx error rate: {error_5xx_rate:.2f}%")
                elif error_5xx_rate > 0.5:  # > 0.5% server errors
                    score -= 20
                    issues.append(f"Elevated 5xx error rate: {error_5xx_rate:.2f}%")
                
                if error_4xx_rate > 10:  # > 10% client errors
                    score -= 15
                    issues.append(f"High 4xx error rate: {error_4xx_rate:.2f}%")
                elif error_4xx_rate > 5:  # > 5% client errors
                    score -= 8
                    issues.append(f"Elevated 4xx error rate: {error_4xx_rate:.2f}%")
        
        # Host health check (weight: 20%)
        if 'UnHealthyHostCount' in metrics and 'HealthyHostCount' in metrics:
            unhealthy_hosts = metrics['UnHealthyHostCount']
            healthy_hosts = metrics['HealthyHostCount']
            total_hosts = unhealthy_hosts + healthy_hosts
            
            if total_hosts > 0:
                unhealthy_percentage = (unhealthy_hosts / total_hosts) * 100
                if unhealthy_percentage > 20:  # > 20% unhealthy
                    score -= 25
                    issues.append(f"High unhealthy host percentage: {unhealthy_percentage:.1f}%")
                elif unhealthy_percentage > 10:  # > 10% unhealthy
                    score -= 10
                    issues.append(f"Some unhealthy hosts: {unhealthy_percentage:.1f}%")
        
        # Resource utilization check (weight: 20%)
        if 'CPUUtilization' in metrics:
            cpu_usage = metrics['CPUUtilization']
            if cpu_usage > 90:  # > 90% CPU
                score -= 15
                issues.append(f"Very high CPU usage: {cpu_usage:.1f}%")
            elif cpu_usage > 80:  # > 80% CPU
                score -= 8
                issues.append(f"High CPU usage: {cpu_usage:.1f}%")
        
        if 'MemoryUtilization' in metrics:
            memory_usage = metrics['MemoryUtilization']
            if memory_usage > 90:  # > 90% memory
                score -= 10
                issues.append(f"Very high memory usage: {memory_usage:.1f}%")
            elif memory_usage > 80:  # > 80% memory
                score -= 5
                issues.append(f"High memory usage: {memory_usage:.1f}%")
        
        # Ensure score doesn't go below 0
        score = max(0, score)
        
        if issues:
            print(f"  Issues detected: {', '.join(issues)}")
        
        return score
    
    def proceed_with_full_deployment(self):
        """Proceed with full deployment after successful canary"""
        try:
            # In a real implementation, this would trigger the next phase
            # For CodeDeploy canary, this happens automatically after canary duration
            print("🚀 Canary validation successful - proceeding with full deployment...")
            
            # Monitor the full deployment phase
            while True:
                response = self.codedeploy.get_deployment(deploymentId=self.deployment_id)
                status = response['deploymentInfo']['status']
                
                print(f"📊 Full deployment status: {status}")
                
                if status == 'Succeeded':
                    print("🎉 Full canary deployment completed successfully!")
                    return True
                elif status in ['Failed', 'Stopped']:
                    print(f"❌ Full deployment failed with status: {status}")
                    return False
                
                time.sleep(30)  # Check every 30 seconds
                
        except Exception as e:
            print(f"❌ Error during full deployment: {e}")
            return False
    
    def rollback_canary(self, reason):
        """Rollback canary deployment"""
        try:
            print(f"⏪ Rolling back canary deployment. Reason: {reason}")
            
            response = self.codedeploy.stop_deployment(
                deploymentId=self.deployment_id,
                autoRollbackEnabled=True
            )
            
            print("🔄 Rollback initiated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False

def execute_intelligent_canary_deployment():
    """Execute complete intelligent canary deployment workflow"""
    
    # Initialize canary manager
    canary_manager = CanaryDeploymentManager(
        application_name="my-critical-app",
        deployment_group="production-canary"
    )
    
    print("🎯 Starting Intelligent Canary Deployment")
    print("=" * 50)
    
    # Configuration
    s3_bucket = "my-deployment-bucket"
    s3_key = "releases/v2.1.0.zip"
    canary_percentage = 10
    canary_duration = 15  # minutes
    
    # Step 1: Create canary deployment
    deployment_id = canary_manager.create_canary_deployment(
        s3_bucket, s3_key, canary_percentage, canary_duration
    )
    
    if not deployment_id:
        print("❌ Failed to create canary deployment")
        return False
    
    # Step 2: Monitor canary health
    canary_healthy, health_reason = canary_manager.monitor_canary_health(canary_duration)
    
    # Step 3: Make deployment decision
    if canary_healthy:
        print(f"✅ Canary validation passed: {health_reason}")
        
        # Proceed with full deployment
        full_deployment_success = canary_manager.proceed_with_full_deployment()
        
        if full_deployment_success:
            print("🎉 Complete canary deployment workflow successful!")
            return True
        else:
            print("❌ Full deployment failed after successful canary")
            return False
    else:
        print(f"❌ Canary validation failed: {health_reason}")
        
        # Rollback canary
        rollback_success = canary_manager.rollback_canary(health_reason)
        
        if rollback_success:
            print("🔄 Canary rollback completed - system restored to stable state")
        else:
            print("❌ Canary rollback failed - manual intervention required!")
        
        return False

# Execute intelligent canary deployment
success = execute_intelligent_canary_deployment()
print(f"\n🏁 Canary Deployment Result: {'Success' if success else 'Failed'}")
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
    # 🚀 AWS Deployment Strategies
    
    """)
    st.markdown("""<div class="info-box">
                Master AWS deployment strategies and learn to implement zero-downtime deployments with automated rollback capabilities. Understand the trade-offs between speed, cost, and risk to choose the optimal deployment approach for your applications.
                </div>""", unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚀 Deployment Strategies", 
        "🔵 Blue/Green", 
        "🔄 All at Once",
        "📈 Linear",
        "🎯 Canary"
    ])
    
    with tab1:
        deployment_strategies_tab()
    
    with tab2:
        blue_green_tab()
    
    with tab3:
        all_at_once_tab()
    
    with tab4:
        linear_tab()
        
    with tab5:
        canary_tab()
    
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
