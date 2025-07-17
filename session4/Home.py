import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import utils.common as common
import utils.authenticate as authenticate

# Page configuration
st.set_page_config(
    page_title="AWS Developer Associate - Session 4",
    page_icon="🚀",
    layout="wide"
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

    .deployment-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
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

    .cicd-pipeline {
        background: #f0f8ff;
        border: 1px solid #4B9CD3;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #232F3E;
    }

    .comparison-table {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }

    .footer {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #232F3E 0%, #4B9CD3 100%);
        color: white;
        margin-top: 3rem;
        border-radius: 15px;
    }

    .pipeline-flow {
        background: #f5f5f5;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-family: monospace;
        border-left: 4px solid #FF9900;
    }

    .strategy-card {
        background: #e8f5e8;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

common.initialize_session_state()

with st.sidebar:
    common.render_sidebar()


def render_overview():
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>AWS Partner Certification Readiness</h1>
        <h2>Developer - Associate Session 4</h2>
        <h3>CI/CD & Deployment with AWS Services</h3>
        <p style="margin-top: 1rem; font-size: 1.1em;">Master continuous integration, continuous delivery, and advanced deployment strategies</p>
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
                <li><strong>CI/CD Pipeline Design:</strong> Build automated deployment workflows</li>
                <li><strong>AWS CodePipeline:</strong> Orchestrate multi-stage deployments</li>
                <li><strong>Infrastructure as Code:</strong> CloudFormation, CDK, and SAM</li>
                <li><strong>Deployment Strategies:</strong> Blue/Green, Canary, and Rolling deployments</li>
                <li><strong>Configuration Management:</strong> Parameter Store and Secrets Manager</li>
                <li><strong>Container Deployment:</strong> ECS, EKS, and ECR integration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="training-progress">
            <h4>Session 4 of 6</h4>
            <div style="font-size: 2rem;">🚀</div>
            <p>CI/CD & Deployment Focus</p>
            <div style="margin-top: 1rem; font-size: 0.9em;">
                <strong>Pipeline:</strong> Source → Build → Test → Deploy
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_aws_services():
    st.markdown("## 🛠️ AWS Services We'll Cover")
    
    # CI/CD Pipeline Services
    st.markdown("### 🔄 CI/CD Pipeline Services")
    
    st.markdown("""
    <div class="pipeline-flow">
        <strong>Complete CI/CD Pipeline Flow:</strong><br><br>
        📝 SOURCE → 🔨 BUILD → ✅ TEST → 🚀 DEPLOY → 📊 MONITOR<br><br>
        Git Repo → CodeBuild → CodeBuild → CodeDeploy → CloudWatch<br>
        (CodeArtifact) ↗️ Third Party ↗️ X-Ray<br><br>
        <strong>Orchestrated by:</strong> AWS CodePipeline
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="service-card">
            <h4>🔄 AWS CodePipeline</h4>
            <p><strong>Continuous Delivery Orchestration</strong></p>
            <ul>
                <li>Multi-stage pipeline automation</li>
                <li>6 action types: Source, Build, Test, Deploy, Approval, Invoke</li>
                <li>SNS integration for manual approvals</li>
                <li>Cross-region and cross-account deployments</li>
            </ul>
            <div style="background: #e8f4fd; padding: 0.5rem; border-radius: 5px; margin-top: 1rem;">
                <strong>Key Feature:</strong> Visual pipeline modeling and execution
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="service-card">
            <h4>🔨 AWS CodeBuild</h4>
            <p><strong>Managed Build Service</strong></p>
            <ul>
                <li>Fully managed build environments</li>
                <li>Support for multiple programming languages</li>
                <li>Custom build environments with Docker</li>
                <li>Integrated testing and artifact generation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="service-card">
            <h4>🚀 AWS CodeDeploy</h4>
            <p><strong>Application Deployment Service</strong></p>
            <ul>
                <li>EC2, ECS, Lambda, and Elastic Beanstalk deployments</li>
                <li>Blue/Green and Rolling deployment strategies</li>
                <li>Automatic rollback on failure</li>
                <li>Health monitoring during deployments</li>
            </ul>
            <div style="background: #fff7e6; padding: 0.5rem; border-radius: 5px; margin-top: 1rem;">
                <strong>Key Feature:</strong> Zero-downtime deployments
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="service-card">
            <h4>📦 AWS CodeArtifact</h4>
            <p><strong>Artifact Repository Service</strong></p>
            <ul>
                <li>Secure package management</li>
                <li>Support for npm, PyPI, Maven, NuGet</li>
                <li>Integration with existing tools</li>
                <li>Dependency management and caching</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Infrastructure as Code Services
    st.markdown("### 🏗️ Infrastructure as Code")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="cicd-pipeline">
            <h4>☁️ AWS CloudFormation</h4>
            <p><strong>Infrastructure Templates</strong></p>
            <ul>
                <li>JSON/YAML template format</li>
                <li>Dependency management</li>
                <li>Stack lifecycle management</li>
                <li>Change sets for preview</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="cicd-pipeline">
            <h4>⚡ AWS CDK</h4>
            <p><strong>Cloud Development Kit</strong></p>
            <ul>
                <li>Programming language support</li>
                <li>Higher-level constructs</li>
                <li>Type safety and IDE support</li>
                <li>Generates CloudFormation</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="cicd-pipeline">
            <h4>🚀 AWS SAM</h4>
            <p><strong>Serverless Application Model</strong></p>
            <ul>
                <li>Serverless-focused templates</li>
                <li>Local testing and debugging</li>
                <li>Built-in best practices</li>
                <li>Pipeline integration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Container & Deployment Platforms
    st.markdown("### 📦 Container & Deployment Platforms")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="deployment-card">
            <h4>🐳 Amazon ECS/EKS</h4>
            <p><strong>Container Orchestration</strong></p>
            <ul>
                <li><strong>ECS:</strong> AWS-native container service</li>
                <li><strong>EKS:</strong> Managed Kubernetes service</li>
                <li>Blue/Green deployments with CodeDeploy</li>
                <li>ECR integration for image storage</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="deployment-card">
            <h4>⚙️ Configuration Management</h4>
            <p><strong>AWS Systems Manager & Secrets Manager</strong></p>
            <ul>
                <li><strong>Parameter Store:</strong> Configuration values</li>
                <li><strong>Secrets Manager:</strong> Automatic rotation</li>
                <li>Environment-specific configurations</li>
                <li>Secure secret retrieval</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="deployment-card">
            <h4>🚀 AWS Elastic Beanstalk</h4>
            <p><strong>Platform as a Service</strong></p>
            <ul>
                <li>Quick application deployments</li>
                <li>Multiple deployment strategies</li>
                <li>Automatic capacity provisioning</li>
                <li>Health monitoring and scaling</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="deployment-card">
            <h4>🔍 Monitoring & Observability</h4>
            <p><strong>AWS X-Ray & CloudWatch</strong></p>
            <ul>
                <li><strong>X-Ray:</strong> Distributed tracing</li>
                <li><strong>CloudWatch:</strong> Metrics and logs</li>
                <li>Deployment health monitoring</li>
                <li>Performance insights</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def render_training_curriculum():
    st.markdown("## 📚 Week 4 Digital Training Curriculum")
    
    st.markdown("""
    <div class="info-highlight">
        <h4>📅 Progress Check & Reminder</h4>
        <p>Do your best to complete this week's training content to master CI/CD and deployment strategies!</p>
    </div>
    """, unsafe_allow_html=True)

    # Required Courses
    st.markdown("### 🎯 AWS Skill Builder Learning Plan Courses (Required)")
    
    required_courses = [
        {
            "name": "Getting Started with AWS CloudFormation",
            "focus": "Infrastructure as Code fundamentals",
            "duration": "60 min",
            "topics": ["Template structure", "Stacks management", "Change sets", "Best practices"]
        },
        {
            "name": "Deploying Serverless Applications", 
            "focus": "Serverless deployment patterns",
            "duration": "75 min",
            "topics": ["SAM templates", "Lambda deployments", "API Gateway", "Event-driven architecture"]
        },
        {
            "name": "Deep Dive with Security: AWS Identity and Access Management (IAM)",
            "focus": "Security in CI/CD pipelines",
            "duration": "90 min",
            "topics": ["Service roles", "Cross-account access", "Pipeline security", "Least privilege"]
        },
        {
            "name": "AWS Lambda - Troubleshooting",
            "focus": "Serverless debugging and monitoring",
            "duration": "45 min",
            "topics": ["Error handling", "Performance tuning", "CloudWatch integration", "X-Ray tracing"]
        },
        {
            "name": "Amazon CloudFront - Troubleshooting",
            "focus": "Content delivery optimization",
            "duration": "45 min",
            "topics": ["Cache behaviors", "Origin issues", "Performance monitoring", "Security headers"]
        }
    ]

    for i, course in enumerate(required_courses):
        st.markdown(f"""
        <div class="comparison-table">
            <h5>📖 {course['name']}</h5>
            <div style="display: flex; justify-content: space-between; margin: 1rem 0;">
                <div style="flex: 2;">
                    <p><strong>Focus:</strong> {course['focus']}</p>
                    <div style="margin-top: 0.5rem;">
                        <strong>Key Topics:</strong>
                        <ul style="margin: 0.5rem 0;">
                            {"".join([f"<li>{topic}</li>" for topic in course['topics']])}
                        </ul>
                    </div>
                </div>
                <div style="flex: 1; text-align: right;">
                    <div style="background: #FF9900; color: white; padding: 0.5rem; border-radius: 5px; font-weight: bold;">
                        ⏱️ {course['duration']}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_optional_courses():
    st.markdown("### 🌟 Companion Learning Plan Courses (Optional)")
    
    st.markdown("""
    <div class="warning-box">
        <h5>📚 Continue: Exam Prep Enhanced Course: AWS Certified Developer Associate (DVA-C02)</h5>
        <p><strong>Type:</strong> Comprehensive Exam Preparation</p>
        <p><strong>Description:</strong> In-depth exam preparation with practice questions, detailed explanations, and exam strategies specifically focused on the DVA-C02 certification exam.</p>
        <div style="background: rgba(255,255,255,0.7); padding: 0.5rem; border-radius: 5px; margin-top: 0.5rem;">
            <strong>💡 Benefit:</strong> Direct alignment with certification objectives and testing strategies
        </div>
        <div style="margin-top: 1rem;">
            <strong>🎯 Focus Areas for Session 4:</strong>
            <ul>
                <li>CI/CD pipeline implementation and troubleshooting</li>
                <li>Deployment strategy selection and configuration</li>
                <li>Infrastructure as Code best practices</li>
                <li>Container deployment and orchestration</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_deployment_strategies():
    st.markdown("## 🚀 AWS Deployment Strategies")
    
    st.markdown("""
    <div class="info-highlight">
        <h4>🎯 Deployment Strategy Overview</h4>
        <p>A deployment strategy determines how application changes are rolled out to minimize downtime and risk while ensuring reliable updates.</p>
        <ul>
            <li><strong>Deployment Types:</strong> In-Place vs. Rolling vs. Blue/Green</li>
            <li><strong>Deployment Configurations:</strong> All-at-Once vs. Linear vs. Canary</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Deployment Strategy Cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="strategy-card">
            <h4>🔄 All at Once</h4>
            <p><strong>Version A → Version B (Complete Switch)</strong></p>
            <ul>
                <li>✅ Fast deployment and rollback</li>
                <li>✅ No extra infrastructure needed</li>
                <li>❌ Service downtime during deployment</li>
                <li>❌ No production traffic testing</li>
            </ul>
            <div style="background: #fff; padding: 0.5rem; border-radius: 5px; margin-top: 1rem;">
                <strong>Best for:</strong> Non-critical applications, maintenance windows
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="strategy-card">
            <h4>🌊 Rolling Deployment</h4>
            <p><strong>Gradual replacement instance by instance</strong></p>
            <ul>
                <li>✅ No downtime</li>
                <li>✅ Controlled rollout pace</li>
                <li>❌ Slower deployment process</li>
                <li>❌ Complex rollback procedure</li>
            </ul>
            <div style="background: #fff; padding: 0.5rem; border-radius: 5px; margin-top: 1rem;">
                <strong>Best for:</strong> Large-scale applications requiring availability
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="strategy-card">
            <h4>🔵🟢 Blue/Green Deployment</h4>
            <p><strong>Two identical environments with traffic switch</strong></p>
            <ul>
                <li>✅ Zero downtime deployment</li>
                <li>✅ Instant rollback capability</li>
                <li>✅ Full production testing</li>
                <li>❌ Requires duplicate infrastructure</li>
            </ul>
            <div style="background: #fff; padding: 0.5rem; border-radius: 5px; margin-top: 1rem;">
                <strong>Best for:</strong> Mission-critical applications
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="strategy-card">
            <h4>🕊️ Canary Deployment</h4>
            <p><strong>Small subset testing before full rollout</strong></p>
            <ul>
                <li>✅ Real production traffic testing</li>
                <li>✅ Risk mitigation through gradual rollout</li>
                <li>✅ Easy monitoring and rollback</li>
                <li>❌ Complex orchestration required</li>
            </ul>
            <div style="background: #fff; padding: 0.5rem; border-radius: 5px; margin-top: 1rem;">
                <strong>Best for:</strong> High-risk changes, A/B testing
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Deployment Configuration Examples
    st.markdown("### ⚙️ AWS CodeDeploy Configuration Examples")
    
    deployment_configs = [
        {
            "strategy": "All at Once",
            "ecs_config": "CodeDeployDefault.ECSAllAtOnce",
            "lambda_config": "CodeDeployDefault.LambdaAllAtOnce",
            "description": "Shifts all traffic immediately"
        },
        {
            "strategy": "Linear",
            "ecs_config": "CodeDeployDefault.ECSLinear10PercentEvery1Minutes",
            "lambda_config": "CodeDeployDefault.LambdaLinear10PercentEvery3Minutes",
            "description": "Gradual traffic shift at regular intervals"
        },
        {
            "strategy": "Canary",
            "ecs_config": "CodeDeployDefault.ECSCanary10Percent15Minutes",
            "lambda_config": "CodeDeployDefault.LambdaCanary10Percent5Minutes",
            "description": "Small initial deployment, then full rollout"
        }
    ]

    config_df = pd.DataFrame(deployment_configs)
    
    st.markdown("""
    <div class="comparison-table">
        <h5>📊 Pre-configured Deployment Options</h5>
    </div>
    """, unsafe_allow_html=True)
    
    st.dataframe(
        config_df,
        column_config={
            "strategy": st.column_config.TextColumn("Strategy", help="Deployment pattern"),
            "ecs_config": st.column_config.TextColumn("ECS Configuration", help="CodeDeploy ECS config"),
            "lambda_config": st.column_config.TextColumn("Lambda Configuration", help="CodeDeploy Lambda config"),
            "description": st.column_config.TextColumn("Description", help="How traffic is shifted")
        },
        hide_index=True,
        use_container_width=True
    )

def render_sam_pipeline():
    st.markdown("## 🚀 AWS SAM Pipeline Integration")
    
    st.markdown("""
    <div class="pipeline-flow">
        <strong>Complete SAM Pipeline Architecture:</strong><br><br>
        👨‍💻 Developer → 📝 GitHub Repository → 🔄 AWS CodePipeline<br>
        ├── 🔨 AWS CodeBuild (Build Phase)<br>
        ├── 🧪 Deploy to DEV Environment<br>
        └── 🚀 Deploy to PROD Environment<br><br>
        <strong>Triggered by:</strong> Git push → Automated build and deployment
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        <div class="cicd-pipeline">
            <h4>🏗️ SAM Benefits</h4>
            <ul>
                <li><strong>Local Development:</strong> Build, test, and debug locally</li>
                <li><strong>Simplified Syntax:</strong> Serverless-focused CloudFormation extension</li>
                <li><strong>Built-in Best Practices:</strong> Security and performance defaults</li>
                <li><strong>CI/CD Integration:</strong> Native pipeline support</li>
                <li><strong>Step Functions Integration:</strong> Workflow orchestration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #f0f8ff; padding: 1rem; border-radius: 8px; border-left: 4px solid #4B9CD3;">
            <h5>🔧 SAM CLI Commands</h5>
            <div style="font-family: monospace; background: #ffffff; padding: 0.5rem; border-radius: 4px; margin: 0.5rem 0;">
                sam build<br>
                sam local start-api<br>
                sam deploy --guided<br>
                sam pipeline init
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_footer():
    st.markdown("""
    <div class="footer">
        <h3>🚀 Ready to Automate Your Deployments!</h3>
        <p>Session 4 equips you with the tools and strategies for reliable, automated software delivery</p>
        <div style="display: flex; justify-content: center; gap: 2rem; margin: 1rem 0;">
            <div>🔄 CI/CD Pipelines</div>
            <div>🏗️ Infrastructure as Code</div>
            <div>🚀 Deployment Strategies</div>
            <div>📦 Container Orchestration</div>
        </div>
        <p style="margin-top: 1rem; font-size: 0.9em;">
            <strong>Next:</strong> Implement these patterns in real-world deployment scenarios
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
        render_deployment_strategies()
        render_sam_pipeline()
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
            render_deployment_strategies()
            render_sam_pipeline()
            render_footer()