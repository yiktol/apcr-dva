import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import utils.common as common
import utils.authenticate as authenticate
import json
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="AWS CI/CD",
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
        
        .pipeline-step {{
            background: white;
            padding: 15px;
            border-radius: 10px;
            border: 2px solid {AWS_COLORS['light_blue']};
            margin: 10px 0;
            text-align: center;
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
            - 🔄 Release process stages - Software delivery lifecycle
            - 🚀 CI/CD - Continuous integration and delivery
            - 🔗 AWS CodePipeline - Automated release pipelines
            - ⚙️ Application configuration - Managing app dependencies
            
            **Learning Objectives:**
            - Understand software release process stages
            - Learn CI/CD best practices and implementation
            - Master AWS CodePipeline for automated deployments
            - Configure applications using AWS Systems Manager and Secrets Manager
            """)

def create_release_process_mermaid():
    """Create mermaid diagram for release process stages"""
    return """
    graph LR
        A[📝 Source] --> B[🔨 Build]
        B --> C[🧪 Test]
        C --> D[🚀 Production]
        
        subgraph "Source Stage"
            A1[Check-in Code]
            A2[Peer Review]
            A3[Version Control]
        end
        
        subgraph "Build Stage"
            B1[Compile Code]
            B2[Unit Tests]
            B3[Style Checkers]
            B4[Create Artifacts]
        end
        
        subgraph "Test Stage"
            C1[Integration Tests]
            C2[Load Testing]
            C3[UI Tests]
            C4[Security Testing]
        end
        
        subgraph "Production Stage"
            D1[Deploy]
            D2[Monitor]
            D3[Error Detection]
        end
        
        A --> A1
        A --> A2
        A --> A3
        
        B --> B1
        B --> B2
        B --> B3
        B --> B4
        
        C --> C1
        C --> C2
        C --> C3
        C --> C4
        
        D --> D1
        D --> D2
        D --> D3
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style B fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_cicd_pipeline_mermaid():
    """Create mermaid diagram for CI/CD pipeline"""
    return """
    graph TD
        A[👨‍💻 Developer] --> B[📝 Git Commit]
        B --> C[🔔 Webhook Trigger]
        C --> D[🔗 AWS CodePipeline]
        
        D --> E[📦 Source Stage]
        E --> F[🔨 Build Stage]
        F --> G[🧪 Test Stage]
        G --> H[🚀 Deploy Stage]
        
        subgraph "Source"
            E1[📚 Git Repository]
            E2[🗂️ AWS CodeArtifact]
        end
        
        subgraph "Build"
            F1[⚙️ AWS CodeBuild]
            F2[🏗️ Third Party Tools]
        end
        
        subgraph "Test"
            G1[🧪 Automated Tests]
            G2[✅ Code Quality]
        end
        
        subgraph "Deploy"
            H1[🚀 AWS CodeDeploy]
            H2[📊 Monitor with X-Ray]
            H3[📈 CloudWatch Logs]
        end
        
        E --> E1
        E --> E2
        F --> F1
        F --> F2
        G --> G1
        G --> G2
        H --> H1
        H --> H2
        H --> H3
        
        style D fill:#FF9900,stroke:#232F3E,color:#fff
        style E fill:#4B9EDB,stroke:#232F3E,color:#fff
        style F fill:#3FB34F,stroke:#232F3E,color:#fff
        style G fill:#FF6B35,stroke:#232F3E,color:#fff
        style H fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_codepipeline_actions_mermaid():
    """Create mermaid diagram for CodePipeline actions"""
    return """
    graph TB
        A[🔗 AWS CodePipeline] --> B[Source Actions]
        A --> C[Build Actions]
        A --> D[Test Actions]
        A --> E[Deploy Actions]
        A --> F[Approval Actions]
        A --> G[Invoke Actions]
        
        B --> B1[📚 Git Repository]
        B --> B2[🗃️ S3 Bucket]
        
        C --> C1[⚙️ AWS CodeBuild]
        C --> C2[🔧 Third Party Build]
        
        D --> D1[🧪 CodeBuild Tests]
        D --> D2[🔍 Third Party Tests]
        
        E --> E1[🚀 AWS CodeDeploy]
        E --> E2[🐳 Amazon ECS]
        E --> E3[🌿 Elastic Beanstalk]
        
        F --> F1[👥 Manual Approval]
        F --> F2[📧 SNS Notification]
        
        G --> G1[⚡ AWS Lambda]
        G --> G2[🔧 Other Services]
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style B fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#FF6B35,stroke:#232F3E,color:#fff
        style E fill:#232F3E,stroke:#FF9900,color:#fff
        style F fill:#9D59D2,stroke:#232F3E,color:#fff
        style G fill:#1B2631,stroke:#FF9900,color:#fff
    """

def create_configuration_management_mermaid():
    """Create mermaid diagram for configuration management"""
    return """
    graph LR
        A[📱 Application] --> B{Configuration Source}
        
        B --> C[🏗️ Parameter Store]
        B --> D[🔐 Secrets Manager]
        
        C --> C1[📝 Plain Text Values]
        C --> C2[🔗 Database Strings]
        C --> C3[📄 License Codes]
        C --> C4[⚙️ Environment Variables]
        
        D --> D1[🔑 Passwords]
        D --> D2[🔐 API Keys]
        D --> D3[🗝️ Database Credentials]
        D --> D4[🔄 Auto Rotation]
        
        C1 --> E[📦 Application Runtime]
        C2 --> E
        C3 --> E
        C4 --> E
        D1 --> E
        D2 --> E
        D3 --> E
        D4 --> E
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style C fill:#4B9EDB,stroke:#232F3E,color:#fff
        style D fill:#3FB34F,stroke:#232F3E,color:#fff
        style E fill:#232F3E,stroke:#FF9900,color:#fff
    """

def release_process_stages_tab():
    """Content for Release Process Stages tab"""
    st.markdown("## 🔄 Release Process Stages")
    st.markdown("*Systematic approach to software delivery lifecycle*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Release Process Stages** represent the systematic approach to moving code from development to production.
    Each stage has specific goals, activities, and quality gates to ensure reliable software delivery.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Release Process Flow
    st.markdown("### 🔄 Release Process Flow")
    common.mermaid(create_release_process_mermaid(), height=1500)
    
    # Interactive Stage Explorer
    st.markdown("### 🔍 Interactive Stage Explorer")
    
    stages_data = {
        'Source': {
            'icon': '📝',
            'activities': ['Check-in source code (.java files)', 'Peer review new code', 'Version control management'],
            'tools': ['Git', 'GitHub', 'GitLab', 'AWS CodeCommit'],
            'duration': '1-2 hours',
            'success_criteria': ['Code review approved', 'No merge conflicts', 'Branch protection rules passed']
        },
        'Build': {
            'icon': '🔨',
            'activities': ['Compile code', 'Unit tests', 'Style checkers', 'Create build artifacts'],
            'tools': ['Maven', 'Gradle', 'AWS CodeBuild', 'Jenkins'],
            'duration': '5-15 minutes',
            'success_criteria': ['Compilation successful', 'Unit tests pass', 'Code quality checks pass']
        },
        'Test': {
            'icon': '🧪',
            'activities': ['Integration tests', 'Load testing', 'UI tests', 'Security testing'],
            'tools': ['Selenium', 'JMeter', 'SonarQube', 'OWASP ZAP'],
            'duration': '30-60 minutes',
            'success_criteria': ['All tests pass', 'Performance meets SLA', 'Security scan clean']
        },
        'Production': {
            'icon': '🚀',
            'activities': ['Deploy to production', 'Monitor in production', 'Quick error detection'],
            'tools': ['AWS CodeDeploy', 'CloudWatch', 'X-Ray', 'CloudFormation'],
            'duration': '5-30 minutes',
            'success_criteria': ['Deployment successful', 'Health checks pass', 'Metrics within range']
        }
    }
    
    selected_stage = st.selectbox("Select Stage to Explore:", list(stages_data.keys()))
    
    if selected_stage:
        stage_info = stages_data[selected_stage]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="pipeline-step">', unsafe_allow_html=True)
            st.markdown(f"""
            ## {stage_info['icon']} {selected_stage} Stage
            
            **Key Activities:**
            """)
            for activity in stage_info['activities']:
                st.markdown(f"• {activity}")
            
            st.markdown(f"""
            **Typical Duration:** {stage_info['duration']}
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="pipeline-step">', unsafe_allow_html=True)
            st.markdown(f"""
            **Common Tools:**
            """)
            for tool in stage_info['tools']:
                st.markdown(f"• {tool}")
            
            st.markdown(f"""
            **Success Criteria:**
            """)
            for criteria in stage_info['success_criteria']:
                st.markdown(f"✅ {criteria}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Stage Duration Analysis
    st.markdown("### ⏱️ Release Process Timeline Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        team_size = st.selectbox("Development Team Size:", ["Small (2-5)", "Medium (6-15)", "Large (15+)"])
        project_complexity = st.selectbox("Project Complexity:", ["Simple", "Moderate", "Complex"])
    
    with col2:
        automation_level = st.selectbox("Automation Level:", ["Manual", "Partially Automated", "Fully Automated"])
        testing_strategy = st.selectbox("Testing Strategy:", ["Basic", "Comprehensive", "Extensive"])
    
    if st.button("🔍 Analyze Release Timeline", use_container_width=True):
        # Calculate timeline based on inputs
        base_times = {
            'Source': 60,  # minutes
            'Build': 10,
            'Test': 45,
            'Production': 15
        }
        
        # Adjust based on complexity
        complexity_multiplier = {'Simple': 0.8, 'Moderate': 1.0, 'Complex': 1.5}[project_complexity]
        
        # Adjust based on automation
        automation_multiplier = {'Manual': 2.0, 'Partially Automated': 1.3, 'Fully Automated': 0.7}[automation_level]
        
        # Adjust based on testing
        testing_multiplier = {'Basic': 0.6, 'Comprehensive': 1.0, 'Extensive': 1.8}[testing_strategy]
        
        adjusted_times = {}
        for stage, base_time in base_times.items():
            if stage == 'Test':
                multiplier = complexity_multiplier * automation_multiplier * testing_multiplier
            else:
                multiplier = complexity_multiplier * automation_multiplier
            
            adjusted_times[stage] = base_time * multiplier
        
        total_time = sum(adjusted_times.values())
        
        # Create timeline visualization
        fig = px.bar(
            x=list(adjusted_times.keys()),
            y=list(adjusted_times.values()),
            title=f'Estimated Release Timeline: {total_time:.0f} minutes total',
            labels={'x': 'Release Stage', 'y': 'Duration (minutes)'},
            color=list(adjusted_times.values()),
            color_continuous_scale=['#3FB34F', '#FF9900', '#FF6B35']
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 📊 Release Timeline Analysis
        
        **Configuration:**
        - Team Size: {team_size}
        - Complexity: {project_complexity}
        - Automation: {automation_level}
        - Testing: {testing_strategy}
        
        **Estimated Times:**
        - Source: {adjusted_times['Source']:.0f} minutes
        - Build: {adjusted_times['Build']:.0f} minutes  
        - Test: {adjusted_times['Test']:.0f} minutes
        - Production: {adjusted_times['Production']:.0f} minutes
        
        **Total Release Time: {total_time:.0f} minutes ({total_time/60:.1f} hours)**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Best Practices
    st.markdown("### 💡 Release Process Best Practices")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔒 Quality Gates
        - **Mandatory code reviews** before merge
        - **Automated testing** at each stage
        - **Security scans** integrated
        - **Performance benchmarks** validated
        
        ### 🔄 Continuous Improvement
        - **Metrics collection** at each stage
        - **Feedback loops** implemented
        - **Process refinement** based on data
        - **Post-mortem analysis** for failures
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚡ Automation Focus
        - **Build automation** reduces errors
        - **Test automation** increases coverage
        - **Deployment automation** ensures consistency
        - **Monitoring automation** detects issues early
        
        ### 📊 Visibility & Tracking
        - **Pipeline dashboards** for status
        - **Notification systems** for failures
        - **Audit trails** for compliance
        - **Performance metrics** tracking
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Release Pipeline Configuration")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Example release pipeline configuration using AWS services
import boto3
import json
from datetime import datetime

class ReleasePipeline:
    def __init__(self, pipeline_name, region='us-east-1'):
        self.pipeline_name = pipeline_name
        self.region = region
        self.codepipeline = boto3.client('codepipeline', region_name=region)
        self.codebuild = boto3.client('codebuild', region_name=region)
    
    def create_source_stage(self, repo_name, branch='main'):
        """Configure source stage with Git repository"""
        return {
            'Name': 'Source',
            'Actions': [{
                'Name': 'SourceAction',
                'ActionTypeId': {
                    'Category': 'Source',
                    'Owner': 'AWS',
                    'Provider': 'CodeCommit',
                    'Version': '1'
                },
                'Configuration': {
                    'RepositoryName': repo_name,
                    'BranchName': branch,
                    'PollForSourceChanges': 'false'  # Use CloudWatch Events instead
                },
                'OutputArtifacts': [{'Name': 'SourceOutput'}]
            }]
        }
    
    def create_build_stage(self, project_name):
        """Configure build stage with CodeBuild"""
        # First create the CodeBuild project
        build_spec = {
            'version': '0.2',
            'phases': {
                'pre_build': {
                    'commands': [
                        'echo Logging in to Amazon ECR...',
                        'aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com'
                    ]
                },
                'build': {
                    'commands': [
                        'echo Build started on `date`',
                        'echo Compiling the Java application...',
                        'mvn clean compile',
                        'echo Running unit tests...',
                        'mvn test',
                        'echo Running style checks...',
                        'mvn checkstyle:check',
                        'echo Creating build artifacts...',
                        'mvn package'
                    ]
                },
                'post_build': {
                    'commands': [
                        'echo Build completed on `date`',
                        'echo Uploading artifacts...'
                    ]
                }
            },
            'artifacts': {
                'files': ['target/*.jar', 'appspec.yml', 'scripts/*']
            }
        }
        
        try:
            self.codebuild.create_project(
                name=project_name,
                source={
                    'type': 'CODEPIPELINE',
                    'buildspec': json.dumps(build_spec)
                },
                artifacts={'type': 'CODEPIPELINE'},
                environment={
                    'type': 'LINUX_CONTAINER',
                    'image': 'aws/codebuild/amazonlinux2-x86_64-standard:3.0',
                    'computeType': 'BUILD_GENERAL1_MEDIUM',
                    'privilegedMode': True
                },
                serviceRole=f'arn:aws:iam::{self.get_account_id()}:role/CodeBuildServiceRole'
            )
            print(f"✅ CodeBuild project '{project_name}' created")
        except Exception as e:
            print(f"Build project might already exist: {e}")
        
        return {
            'Name': 'Build',
            'Actions': [{
                'Name': 'BuildAction',
                'ActionTypeId': {
                    'Category': 'Build',
                    'Owner': 'AWS',
                    'Provider': 'CodeBuild',
                    'Version': '1'
                },
                'Configuration': {'ProjectName': project_name},
                'InputArtifacts': [{'Name': 'SourceOutput'}],
                'OutputArtifacts': [{'Name': 'BuildOutput'}]
            }]
        }
    
    def create_test_stage(self, test_project_name):
        """Configure test stage with automated testing"""
        test_build_spec = {
            'version': '0.2',
            'phases': {
                'pre_build': {
                    'commands': [
                        'echo Setting up test environment...',
                        'npm install -g newman',  # For API testing
                        'pip install selenium pytest'  # For UI testing
                    ]
                },
                'build': {
                    'commands': [
                        'echo Running integration tests...',
                        'mvn integration-test',
                        'echo Running API tests...',
                        'newman run api-tests.json',
                        'echo Running security scans...',
                        'sonar-scanner',
                        'echo Running load tests...',
                        'jmeter -n -t load-test.jmx -l results.jtl'
                    ]
                },
                'post_build': {
                    'commands': [
                        'echo Generating test reports...',
                        'mvn surefire-report:report'
                    ]
                }
            },
            'reports': {
                'test-results': {
                    'files': ['target/surefire-reports/*.xml'],
                    'file-format': 'JUNITXML'
                }
            }
        }
        
        try:
            self.codebuild.create_project(
                name=test_project_name,
                source={
                    'type': 'CODEPIPELINE',
                    'buildspec': json.dumps(test_build_spec)
                },
                artifacts={'type': 'CODEPIPELINE'},
                environment={
                    'type': 'LINUX_CONTAINER',
                    'image': 'aws/codebuild/amazonlinux2-x86_64-standard:3.0',
                    'computeType': 'BUILD_GENERAL1_LARGE'
                },
                serviceRole=f'arn:aws:iam::{self.get_account_id()}:role/CodeBuildServiceRole'
            )
        except Exception as e:
            print(f"Test project might already exist: {e}")
        
        return {
            'Name': 'Test',
            'Actions': [{
                'Name': 'TestAction',
                'ActionTypeId': {
                    'Category': 'Test',
                    'Owner': 'AWS',
                    'Provider': 'CodeBuild',
                    'Version': '1'
                },
                'Configuration': {'ProjectName': test_project_name},
                'InputArtifacts': [{'Name': 'BuildOutput'}],
                'OutputArtifacts': [{'Name': 'TestOutput'}]
            }]
        }
    
    def create_production_stage(self, application_name, deployment_group):
        """Configure production deployment stage"""
        return {
            'Name': 'Production',
            'Actions': [{
                'Name': 'DeployAction',
                'ActionTypeId': {
                    'Category': 'Deploy',
                    'Owner': 'AWS',
                    'Provider': 'CodeDeploy',
                    'Version': '1'
                },
                'Configuration': {
                    'ApplicationName': application_name,
                    'DeploymentGroupName': deployment_group
                },
                'InputArtifacts': [{'Name': 'TestOutput'}],
                'RunOrder': 1
            }]
        }
    
    def create_complete_pipeline(self, repo_name, build_project, test_project, 
                               app_name, deployment_group):
        """Create complete release pipeline"""
        
        pipeline_definition = {
            'name': self.pipeline_name,
            'roleArn': f'arn:aws:iam::{self.get_account_id()}:role/CodePipelineServiceRole',
            'artifactStore': {
                'type': 'S3',
                'location': f'{self.pipeline_name}-artifacts-{self.region}'
            },
            'stages': [
                self.create_source_stage(repo_name),
                self.create_build_stage(build_project),
                self.create_test_stage(test_project),
                self.create_production_stage(app_name, deployment_group)
            ]
        }
        
        try:
            response = self.codepipeline.create_pipeline(pipeline=pipeline_definition)
            print(f"✅ Pipeline '{self.pipeline_name}' created successfully!")
            print(f"Pipeline ARN: {response['pipeline']['metadata']['pipelineArn']}")
            return response
        except Exception as e:
            print(f"❌ Error creating pipeline: {e}")
            return None
    
    def get_account_id(self):
        """Get AWS account ID"""
        import boto3
        return boto3.client('sts').get_caller_identity()['Account']

# Example usage
pipeline = ReleasePipeline('my-app-release-pipeline')

# Create complete CI/CD pipeline
result = pipeline.create_complete_pipeline(
    repo_name='my-web-app',
    build_project='my-app-build',
    test_project='my-app-test',
    app_name='my-web-application',
    deployment_group='production-servers'
)

if result:
    print("🚀 Release pipeline ready for automated deployments!")
    print("Stages: Source → Build → Test → Production")
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def cicd_tab():
    """Content for CI/CD tab"""
    st.markdown("## 🚀 Continuous Integration and Continuous Delivery (CI/CD)")
    st.markdown("*Automated software delivery workflow for faster, reliable releases*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **CI/CD** is a method to frequently deliver apps to customers by introducing automation into the stages 
    of app development. The main concepts attributed to CI/CD are continuous integration, continuous delivery, 
    and continuous deployment. A pipeline helps automate steps in your software delivery process.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # CI/CD Pipeline Flow
    st.markdown("### 🔄 CI/CD Pipeline Architecture")
    common.mermaid(create_cicd_pipeline_mermaid(), height=700)
    
    # CI vs CD vs CD Comparison
    st.markdown("### ⚖️ CI vs CD vs CD - Understanding the Differences")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔄 Continuous Integration (CI)
        
        **Focus:** Code integration and testing
        
        **Key Activities:**
        - Frequent code commits
        - Automated builds
        - Automated unit testing
        - Early bug detection
        
        **Benefits:**
        - Reduce integration problems
        - Faster feedback to developers
        - Higher code quality
        - Smaller, manageable changes
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📦 Continuous Delivery (CD)
        
        **Focus:** Automated release preparation
        
        **Key Activities:**
        - Automated testing (all levels)
        - Automated deployments to staging
        - Manual approval for production
        - Release-ready at any time
        
        **Benefits:**
        - Reduced deployment risk
        - Faster time to market
        - Higher deployment frequency
        - Better quality assurance
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🚀 Continuous Deployment (CD)
        
        **Focus:** Fully automated releases
        
        **Key Activities:**
        - Automated production deployment
        - Automated testing in production
        - Zero manual intervention
        - Automatic rollback on failure
        
        **Benefits:**
        - Fastest time to market
        - Immediate user feedback
        - Maximum automation
        - Rapid iteration cycles
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive CI/CD Maturity Assessment
    st.markdown("### 📊 Interactive CI/CD Maturity Assessment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔧 Current Practices")
        version_control = st.selectbox("Version Control:", ["None", "Basic Git", "Git with branching strategy", "Advanced Git workflow"])
        build_automation = st.selectbox("Build Automation:", ["Manual builds", "Scripted builds", "CI server builds", "Full automation"])
        testing_automation = st.selectbox("Testing Automation:", ["Manual testing only", "Some unit tests", "Comprehensive test suite", "Full test automation"])
        deployment_process = st.selectbox("Deployment Process:", ["Manual deployment", "Scripted deployment", "Automated to staging", "Automated to production"])
    
    with col2:
        st.markdown("### 📈 Quality Practices")
        code_review = st.selectbox("Code Review Process:", ["None", "Informal reviews", "Required reviews", "Automated + manual reviews"])
        monitoring = st.selectbox("Monitoring & Alerting:", ["None", "Basic monitoring", "Comprehensive monitoring", "Proactive monitoring"])
        rollback_strategy = st.selectbox("Rollback Strategy:", ["None", "Manual rollback", "Automated rollback", "Blue-green deployment"])
        security_integration = st.selectbox("Security Integration:", ["None", "Manual security checks", "Automated security scans", "DevSecOps integrated"])
    
    if st.button("📊 Assess CI/CD Maturity", use_container_width=True):
        # Calculate maturity score
        practices_scores = {
            version_control: {"None": 0, "Basic Git": 1, "Git with branching strategy": 2, "Advanced Git workflow": 3},
            build_automation: {"Manual builds": 0, "Scripted builds": 1, "CI server builds": 2, "Full automation": 3},
            testing_automation: {"Manual testing only": 0, "Some unit tests": 1, "Comprehensive test suite": 2, "Full test automation": 3},
            deployment_process: {"Manual deployment": 0, "Scripted deployment": 1, "Automated to staging": 2, "Automated to production": 3},
            code_review: {"None": 0, "Informal reviews": 1, "Required reviews": 2, "Automated + manual reviews": 3},
            monitoring: {"None": 0, "Basic monitoring": 1, "Comprehensive monitoring": 2, "Proactive monitoring": 3},
            rollback_strategy: {"None": 0, "Manual rollback": 1, "Automated rollback": 2, "Blue-green deployment": 3},
            security_integration: {"None": 0, "Manual security checks": 1, "Automated security scans": 2, "DevSecOps integrated": 3}
        }
        
        total_score = 0
        for practice, score_map in practices_scores.items():
            total_score += score_map[practice]
        
        max_score = len(practices_scores) * 3
        maturity_percentage = (total_score / max_score) * 100
        
        # Determine maturity level
        if maturity_percentage >= 80:
            maturity_level = "Advanced"
            color = AWS_COLORS['success']
            recommendations = [
                "Consider implementing continuous deployment",
                "Explore advanced deployment strategies (canary, blue-green)",
                "Implement chaos engineering practices",
                "Focus on performance optimization"
            ]
        elif maturity_percentage >= 60:
            maturity_level = "Intermediate"
            color = AWS_COLORS['primary']
            recommendations = [
                "Enhance test automation coverage",
                "Implement automated deployment to production",
                "Add comprehensive monitoring and alerting",
                "Integrate security scanning into pipeline"
            ]
        elif maturity_percentage >= 40:
            maturity_level = "Basic"
            color = AWS_COLORS['light_blue']
            recommendations = [
                "Implement comprehensive build automation",
                "Add automated testing at multiple levels",
                "Establish proper code review processes",
                "Set up basic monitoring and alerting"
            ]
        else:
            maturity_level = "Initial"
            color = AWS_COLORS['warning']
            recommendations = [
                "Establish version control best practices",
                "Implement basic build automation",
                "Start with unit test automation",
                "Create deployment scripts"
            ]
        
        # Create maturity visualization
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = maturity_percentage,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "CI/CD Maturity Score"},
            delta = {'reference': 70},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 25], 'color': AWS_COLORS['warning']},
                    {'range': [25, 50], 'color': AWS_COLORS['light_blue']},
                    {'range': [50, 75], 'color': AWS_COLORS['primary']},
                    {'range': [75, 100], 'color': AWS_COLORS['success']}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 📊 CI/CD Maturity Assessment Results
        
        **Overall Score:** {total_score}/{max_score} ({maturity_percentage:.0f}%)
        **Maturity Level:** {maturity_level}
        
        **Key Recommendations:**
        """)
        for rec in recommendations:
            st.markdown(f"• {rec}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Benefits Comparison
    st.markdown("### ✨ CI/CD Benefits Analysis")
    
    benefits_data = {
        'Metric': ['Deployment Frequency', 'Lead Time', 'Change Failure Rate', 'Recovery Time', 'Developer Productivity'],
        'Without CI/CD': ['Monthly', '2-4 weeks', '20-30%', '2-7 days', 'Low'],
        'With CI/CD': ['Daily/Weekly', '1-3 days', '5-15%', '1-4 hours', 'High'],
        'Improvement': ['10-30x faster', '5-10x faster', '2-3x lower', '10-50x faster', '2-3x higher']
    }
    
    df_benefits = pd.DataFrame(benefits_data)
    st.dataframe(df_benefits, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Complete CI/CD Pipeline Setup")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Complete CI/CD pipeline implementation with AWS services
import boto3
import json
import yaml
from datetime import datetime

class CompleteCICDPipeline:
    def __init__(self, project_name, region='us-east-1'):
        self.project_name = project_name
        self.region = region
        
        # Initialize AWS clients
        self.codepipeline = boto3.client('codepipeline', region_name=region)
        self.codebuild = boto3.client('codebuild', region_name=region)
        self.codecommit = boto3.client('codecommit', region_name=region)
        self.codedeploy = boto3.client('codedeploy', region_name=region)
        self.cloudformation = boto3.client('cloudformation', region_name=region)
        
    def setup_source_repository(self):
        """Create CodeCommit repository for source code"""
        try:
            response = self.codecommit.create_repository(
                repositoryName=f'{self.project_name}-repo',
                repositoryDescription=f'Source repository for {self.project_name}',
                tags={
                    'Project': self.project_name,
                    'Environment': 'CICD'
                }
            )
            
            clone_url = response['repositoryMetadata']['cloneUrlHttp']
            print(f"✅ Repository created: {clone_url}")
            return response['repositoryMetadata']['repositoryName']
            
        except Exception as e:
            print(f"Repository might already exist: {e}")
            return f'{self.project_name}-repo'
    
    def create_build_project(self):
        """Create comprehensive CodeBuild project"""
        
        # Advanced buildspec with multiple stages
        buildspec = {
            'version': '0.2',
            'env': {
                'variables': {
                    'AWS_DEFAULT_REGION': self.region,
                    'AWS_ACCOUNT_ID': '${AWS_ACCOUNT_ID}',
                    'IMAGE_REPO_NAME': f'{self.project_name}-app',
                    'IMAGE_TAG': 'latest'
                }
            },
            'phases': {
                'install': {
                    'runtime-versions': {
                        'java': 'corretto11',
                        'nodejs': '14',
                        'python': '3.8'
                    },
                    'commands': [
                        'echo Installing dependencies...',
                        'pip install --upgrade pip',
                        'npm install -g @angular/cli',
                        'curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh | bash'
                    ]
                },
                'pre_build': {
                    'commands': [
                        'echo Pre-build phase started on `date`',
                        'echo Logging in to Amazon ECR...',
                        'aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com',
                        'REPOSITORY_URI=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME',
                        'COMMIT_HASH=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c 1-7)',
                        'IMAGE_TAG=${COMMIT_HASH:=latest}'
                    ]
                },
                'build': {
                    'commands': [
                        'echo Build phase started on `date`',
                        'echo Compiling application...',
                        'mvn clean compile',
                        
                        'echo Running unit tests...',
                        'mvn test',
                        
                        'echo Running integration tests...',
                        'mvn integration-test',
                        
                        'echo Running code quality checks...',
                        'mvn sonar:sonar -Dsonar.projectKey=$PROJECT_NAME',
                        
                        'echo Running security scans...',
                        'mvn org.owasp:dependency-check-maven:check',
                        
                        'echo Building Docker image...',
                        'docker build -t $IMAGE_REPO_NAME:$IMAGE_TAG .',
                        'docker tag $IMAGE_REPO_NAME:$IMAGE_TAG $REPOSITORY_URI:$IMAGE_TAG',
                        
                        'echo Creating deployment package...',
                        'mvn package -DskipTests'
                    ]
                },
                'post_build': {
                    'commands': [
                        'echo Post-build phase started on `date`',
                        'echo Pushing Docker image...',
                        'docker push $REPOSITORY_URI:$IMAGE_TAG',
                        
                        'echo Generating deployment artifacts...',
                        'printf \'[{"name":"web-app","imageUri":"%s"}]\' $REPOSITORY_URI:$IMAGE_TAG > imagedefinitions.json',
                        
                        'echo Build completed on `date`'
                    ]
                }
            },
            'reports': {
                'unit-test-results': {
                    'files': ['target/surefire-reports/*.xml'],
                    'file-format': 'JUNITXML'
                },
                'integration-test-results': {
                    'files': ['target/failsafe-reports/*.xml'],
                    'file-format': 'JUNITXML'
                },
                'code-coverage': {
                    'files': ['target/site/jacoco/jacoco.xml'],
                    'file-format': 'JACOCOXMLPATH'
                }
            },
            'artifacts': {
                'files': [
                    'target/*.jar',
                    'imagedefinitions.json',
                    'appspec.yml',
                    'scripts/*',
                    'cloudformation/*'
                ]
            },
            'cache': {
                'paths': [
                    '/root/.m2/**/*',
                    'node_modules/**/*'
                ]
            }
        }
        
        try:
            response = self.codebuild.create_project(
                name=f'{self.project_name}-build',
                description=f'Build project for {self.project_name}',
                source={
                    'type': 'CODEPIPELINE',
                    'buildspec': yaml.dump(buildspec)
                },
                artifacts={'type': 'CODEPIPELINE'},
                environment={
                    'type': 'LINUX_CONTAINER',
                    'image': 'aws/codebuild/amazonlinux2-x86_64-standard:3.0',
                    'computeType': 'BUILD_GENERAL1_MEDIUM',
                    'privilegedMode': True,
                    'environmentVariables': [
                        {
                            'name': 'AWS_ACCOUNT_ID',
                            'value': boto3.client('sts').get_caller_identity()['Account']
                        },
                        {
                            'name': 'PROJECT_NAME',
                            'value': self.project_name
                        }
                    ]
                },
                serviceRole=f'arn:aws:iam::{boto3.client("sts").get_caller_identity()["Account"]}:role/CodeBuildServiceRole',
                timeoutInMinutes=60,
                queuedTimeoutInMinutes=30,
                cache={
                    'type': 'S3',
                    'location': f'{self.project_name}-build-cache'
                }
            )
            
            print(f"✅ Build project created: {response['project']['name']}")
            return response['project']['name']
            
        except Exception as e:
            print(f"Build project creation error: {e}")
            return f'{self.project_name}-build'
    
    def create_deployment_application(self):
        """Create CodeDeploy application and deployment group"""
        try:
            # Create CodeDeploy application
            app_response = self.codedeploy.create_application(
                applicationName=f'{self.project_name}-app',
                computePlatform='Server'  # or 'ECS' for container deployments
            )
            
            # Create deployment group
            deployment_group_response = self.codedeploy.create_deployment_group(
                applicationName=f'{self.project_name}-app',
                deploymentGroupName=f'{self.project_name}-prod-deployment-group',
                serviceRoleArn=f'arn:aws:iam::{boto3.client("sts").get_caller_identity()["Account"]}:role/CodeDeployServiceRole',
                deploymentConfigName='CodeDeployDefault.AllAtOnceInPlace',
                ec2TagFilters=[
                    {
                        'Type': 'KEY_AND_VALUE',
                        'Key': 'Environment',
                        'Value': 'Production'
                    }
                ],
                autoRollbackConfiguration={
                    'enabled': True,
                    'events': ['DEPLOYMENT_FAILURE', 'DEPLOYMENT_STOP_ON_ALARM']
                },
                alarmConfiguration={
                    'enabled': True,
                    'alarms': [
                        {
                            'name': f'{self.project_name}-high-error-rate'
                        }
                    ]
                }
            )
            
            print(f"✅ Deployment application created: {app_response['applicationId']}")
            return f'{self.project_name}-app'
            
        except Exception as e:
            print(f"Deployment application creation error: {e}")
            return f'{self.project_name}-app'
    
    def create_complete_pipeline(self):
        """Create the complete CI/CD pipeline"""
        
        # Setup all components
        repo_name = self.setup_source_repository()
        build_project = self.create_build_project()
        app_name = self.create_deployment_application()
        
        # Define pipeline structure
        pipeline_definition = {
            'name': f'{self.project_name}-pipeline',
            'roleArn': f'arn:aws:iam::{boto3.client("sts").get_caller_identity()["Account"]}:role/CodePipelineServiceRole',
            'artifactStore': {
                'type': 'S3',
                'location': f'{self.project_name}-pipeline-artifacts'
            },
            'stages': [
                {
                    'name': 'Source',
                    'actions': [{
                        'name': 'SourceAction',
                        'actionTypeId': {
                            'category': 'Source',
                            'owner': 'AWS',
                            'provider': 'CodeCommit',
                            'version': '1'
                        },
                        'configuration': {
                            'RepositoryName': repo_name,
                            'BranchName': 'main',
                            'PollForSourceChanges': 'false'
                        },
                        'outputArtifacts': [{'name': 'SourceOutput'}]
                    }]
                },
                {
                    'name': 'Build',
                    'actions': [{
                        'name': 'BuildAction',
                        'actionTypeId': {
                            'category': 'Build',
                            'owner': 'AWS',
                            'provider': 'CodeBuild',
                            'version': '1'
                        },
                        'configuration': {'ProjectName': build_project},
                        'inputArtifacts': [{'name': 'SourceOutput'}],
                        'outputArtifacts': [{'name': 'BuildOutput'}]
                    }]
                },
                {
                    'name': 'Deploy-Staging',
                    'actions': [{
                        'name': 'DeployToStaging',
                        'actionTypeId': {
                            'category': 'Deploy',
                            'owner': 'AWS',
                            'provider': 'CodeDeploy',
                            'version': '1'
                        },
                        'configuration': {
                            'ApplicationName': app_name,
                            'DeploymentGroupName': f'{self.project_name}-staging-deployment-group'
                        },
                        'inputArtifacts': [{'name': 'BuildOutput'}],
                        'runOrder': 1
                    }]
                },
                {
                    'name': 'Manual-Approval',
                    'actions': [{
                        'name': 'ManualApproval',
                        'actionTypeId': {
                            'category': 'Approval',
                            'owner': 'AWS',
                            'provider': 'Manual',
                            'version': '1'
                        },
                        'configuration': {
                            'CustomData': 'Please review staging deployment and approve for production',
                            'ExternalEntityLink': f'https://{self.project_name}-staging.example.com'
                        }
                    }]
                },
                {
                    'name': 'Deploy-Production',
                    'actions': [{
                        'name': 'DeployToProduction',
                        'actionTypeId': {
                            'category': 'Deploy',
                            'owner': 'AWS',
                            'provider': 'CodeDeploy',
                            'version': '1'
                        },
                        'configuration': {
                            'ApplicationName': app_name,
                            'DeploymentGroupName': f'{self.project_name}-prod-deployment-group'
                        },
                        'inputArtifacts': [{'name': 'BuildOutput'}]
                    }]
                }
            ]
        }
        
        try:
            response = self.codepipeline.create_pipeline(pipeline=pipeline_definition)
            
            print(f"🚀 Complete CI/CD Pipeline Created Successfully!")
            print(f"Pipeline Name: {response['pipeline']['name']}")
            print(f"Pipeline ARN: {response['pipeline']['metadata']['pipelineArn']}")
            print(f"Stages: Source → Build → Deploy-Staging → Manual-Approval → Deploy-Production")
            
            return response
            
        except Exception as e:
            print(f"❌ Pipeline creation error: {e}")
            return None

# Example: Create complete CI/CD pipeline
pipeline_manager = CompleteCICDPipeline('my-web-application')
result = pipeline_manager.create_complete_pipeline()

if result:
    print("\n✅ Your CI/CD pipeline is ready!")
    print("🔄 Automatic triggers on code commits")
    print("🧪 Comprehensive testing at each stage")
    print("🚀 Automated deployment with approval gates")
    print("📊 Built-in monitoring and rollback capabilities")
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def codepipeline_tab():
    """Content for AWS CodePipeline tab"""
    st.markdown("## 🔗 AWS CodePipeline")
    st.markdown("*Continuous delivery service to model, visualize, and automate software release processes*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **AWS CodePipeline** is a continuous delivery service that helps you automate your release pipelines 
    for fast and reliable application and infrastructure updates. It builds, tests, and deploys your code 
    every time there is a code change, based on the release process models you define.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # CodePipeline Actions Overview
    st.markdown("### 🔧 CodePipeline Action Types")
    common.mermaid(create_codepipeline_actions_mermaid(), height=400)
    
    # Interactive Pipeline Builder
    st.markdown("### 🛠️ Interactive Pipeline Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📝 Source Configuration")
        source_provider = st.selectbox("Source Provider:", [
            "AWS CodeCommit", "GitHub", "GitHub Enterprise", "Bitbucket", "Amazon S3"
        ])
        
        if source_provider == "AWS CodeCommit":
            repo_name = st.text_input("Repository Name:", "my-web-app")
            branch_name = st.text_input("Branch Name:", "main")
        elif source_provider in ["GitHub", "GitHub Enterprise"]:
            repo_name = st.text_input("Repository:", "username/repository-name")
            branch_name = st.text_input("Branch Name:", "main")
        elif source_provider == "Amazon S3":
            bucket_name = st.text_input("S3 Bucket:", "my-source-bucket")
            object_key = st.text_input("Object Key:", "source.zip")
        
        trigger_type = st.selectbox("Trigger Type:", [
            "CloudWatch Events (Recommended)", "Polling", "Manual"
        ])
    
    with col2:
        st.markdown("### 🔨 Build Configuration")
        build_provider = st.selectbox("Build Provider:", [
            "AWS CodeBuild", "Jenkins", "TeamCity", "Custom Action"
        ])
        
        if build_provider == "AWS CodeBuild":
            build_project = st.text_input("CodeBuild Project Name:", "my-web-app-build")
            build_spec_type = st.selectbox("BuildSpec Location:", [
                "Use buildspec.yml in source root", "Insert build commands here"
            ])
        
        test_stage = st.checkbox("Include Test Stage", value=True)
        if test_stage:
            test_provider = st.selectbox("Test Provider:", [
                "AWS CodeBuild", "AWS Device Farm", "Third Party"
            ])
    
    # Deployment Configuration
    st.markdown("### 🚀 Deployment Configuration")
    
    col3, col4 = st.columns(2)
    
    with col3:
        deployment_provider = st.selectbox("Deployment Provider:", [
            "AWS CodeDeploy", "Amazon ECS", "AWS Elastic Beanstalk", 
            "Amazon S3", "AWS CloudFormation", "AWS Lambda"
        ])
        
        if deployment_provider == "AWS CodeDeploy":
            app_name = st.text_input("Application Name:", "my-web-application")
            deployment_group = st.text_input("Deployment Group:", "production-servers")
        elif deployment_provider == "Amazon ECS":
            cluster_name = st.text_input("ECS Cluster:", "my-cluster")
            service_name = st.text_input("ECS Service:", "my-service")
        elif deployment_provider == "AWS Elastic Beanstalk":
            app_name = st.text_input("Application Name:", "my-web-app")
            environment_name = st.text_input("Environment Name:", "production")
    
    with col4:
        approval_stage = st.checkbox("Include Manual Approval", value=True)
        if approval_stage:
            approval_message = st.text_area("Approval Message:", 
                "Please review the staging deployment and approve for production release.")
            sns_topic = st.text_input("SNS Topic (optional):", "arn:aws:sns:us-east-1:123456789012:deployment-approvals")
        
        multi_region = st.checkbox("Multi-Region Deployment", value=False)
        if multi_region:
            regions = st.multiselect("Target Regions:", 
                ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
                default=["us-east-1"])
    
    if st.button("🚀 Create CodePipeline", use_container_width=True):
        # Generate pipeline configuration
        pipeline_stages = ["Source", "Build"]
        
        if test_stage:
            pipeline_stages.append("Test")
        
        if approval_stage:
            pipeline_stages.append("Manual Approval")
        
        if multi_region:
            for region in regions:
                pipeline_stages.append(f"Deploy-{region}")
        else:
            pipeline_stages.append("Deploy")
        
        # Estimate pipeline execution time
        stage_times = {
            "Source": 1,
            "Build": 10,
            "Test": 15,
            "Manual Approval": 0,  # Variable
            "Deploy": 8
        }
        
        total_time = sum([stage_times.get(stage.split('-')[0], stage_times.get(stage, 5)) 
                         for stage in pipeline_stages if stage != "Manual Approval"])
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ CodePipeline Configuration Generated!
        
        **Pipeline Details:**
        - **Source**: {source_provider} ({repo_name if 'repo_name' in locals() else 'N/A'})
        - **Build**: {build_provider}
        - **Test Stage**: {'✅ Included' if test_stage else '❌ Not included'}
        - **Deployment**: {deployment_provider}
        - **Manual Approval**: {'✅ Required' if approval_stage else '❌ Not required'}
        - **Multi-Region**: {'✅ Enabled' if multi_region else '❌ Disabled'}
        
        **Pipeline Stages:** {' → '.join(pipeline_stages)}
        **Estimated Execution Time:** {total_time} minutes (excluding approvals)
        
        🔄 **Automated Triggers:** Pipeline will execute on code changes
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # CodePipeline Action Details
    st.markdown("### 📋 CodePipeline Action Types Detailed")
    
    action_details = {
        'Action Type': ['Source', 'Build', 'Test', 'Deploy', 'Approval', 'Invoke'],
        'Purpose': [
            'Retrieve source code from repository',
            'Compile and package application',
            'Run automated tests',
            'Deploy to target environment',
            'Human approval checkpoint',
            'Execute custom functions'
        ],
        'Common Providers': [
            'CodeCommit, GitHub, S3',
            'CodeBuild, Jenkins',
            'CodeBuild, Device Farm',
            'CodeDeploy, ECS, Beanstalk',
            'Manual, SNS notification',
            'Lambda, Step Functions'
        ],
        'Typical Duration': ['1-2 min', '5-15 min', '10-30 min', '5-20 min', 'Variable', '1-5 min']
    }
    
    df_actions = pd.DataFrame(action_details)
    st.dataframe(df_actions, use_container_width=True)
    
    # Pipeline Execution Monitoring
    st.markdown("### 📊 Pipeline Execution Monitoring")
    
    # Simulate pipeline execution data
    execution_data = {
        'Execution': [f'Execution-{i+1}' for i in range(10)],
        'Status': np.random.choice(['Succeeded', 'Failed', 'In Progress'], 10, p=[0.7, 0.2, 0.1]),
        'Duration': np.random.randint(8, 45, 10),
        'Source Commit': [f'abc{np.random.randint(1000, 9999)}' for _ in range(10)],
        'Timestamp': [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d %H:%M') for i in range(10)]
    }
    
    df_executions = pd.DataFrame(execution_data)
    
    # Color code the status
    def color_status(val):
        if val == 'Succeeded':
            return f'background-color: {AWS_COLORS["success"]}; color: white'
        elif val == 'Failed':
            return f'background-color: {AWS_COLORS["warning"]}; color: white'
        else:
            return f'background-color: {AWS_COLORS["light_blue"]}; color: white'
    
    styled_df = df_executions.style.applymap(color_status, subset=['Status'])
    st.dataframe(styled_df, use_container_width=True)
    
    # Success Rate Visualization
    success_rate = (df_executions['Status'] == 'Succeeded').mean() * 100
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Success Rate", f"{success_rate:.0f}%", 
                 f"{'+5%' if success_rate > 70 else '-2%'}")
    
    with col2:
        avg_duration = df_executions['Duration'].mean()
        st.metric("Avg Duration", f"{avg_duration:.0f} min", 
                 f"{'-3 min' if avg_duration < 20 else '+2 min'}")
    
    with col3:
        executions_today = len(df_executions)
        st.metric("Executions Today", str(executions_today), "+2")
    
    # Code Example
    st.markdown("### 💻 Code Example: Advanced CodePipeline Setup")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Advanced CodePipeline setup with comprehensive monitoring and notifications
import boto3
import json
from datetime import datetime, timedelta

class AdvancedCodePipeline:
    def __init__(self, pipeline_name, region='us-east-1'):
        self.pipeline_name = pipeline_name
        self.region = region
        
        # Initialize AWS clients
        self.codepipeline = boto3.client('codepipeline', region_name=region)
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        self.sns = boto3.client('sns', region_name=region)
        self.events = boto3.client('events', region_name=region)
    
    def create_enterprise_pipeline(self):
        """Create enterprise-grade pipeline with all best practices"""
        
        pipeline_definition = {
            'name': self.pipeline_name,
            'roleArn': self.get_pipeline_service_role(),
            'artifactStore': {
                'type': 'S3',
                'location': f'{self.pipeline_name}-artifacts',
                'encryptionKey': {
                    'id': f'arn:aws:kms:{self.region}:123456789012:key/12345678-1234-1234-1234-123456789012',
                    'type': 'KMS'
                }
            },
            'stages': [
                self.create_advanced_source_stage(),
                self.create_build_stage_with_parallel_actions(),
                self.create_comprehensive_test_stage(),
                self.create_security_scan_stage(),
                self.create_approval_stage_with_notifications(),
                self.create_multi_environment_deploy_stage()
            ]
        }
        
        try:
            response = self.codepipeline.create_pipeline(pipeline=pipeline_definition)
            print(f"✅ Enterprise pipeline created: {response['pipeline']['name']}")
            
            # Setup monitoring and notifications
            self.setup_pipeline_monitoring()
            self.create_pipeline_dashboard()
            
            return response
            
        except Exception as e:
            print(f"❌ Error creating pipeline: {e}")
            return None
    
    def create_advanced_source_stage(self):
        """Create source stage with webhook triggers and multiple sources"""
        return {
            'name': 'Source',
            'actions': [
                {
                    'name': 'ApplicationSource',
                    'actionTypeId': {
                        'category': 'Source',
                        'owner': 'AWS',
                        'provider': 'CodeCommit',
                        'version': '1'
                    },
                    'configuration': {
                        'RepositoryName': f'{self.pipeline_name}-app',
                        'BranchName': 'main',
                        'PollForSourceChanges': 'false',
                        'OutputArtifactFormat': 'CODE_ZIP'
                    },
                    'outputArtifacts': [{'name': 'ApplicationSource'}]
                },
                {
                    'name': 'InfrastructureSource',
                    'actionTypeId': {
                        'category': 'Source',
                        'owner': 'AWS',
                        'provider': 'CodeCommit',
                        'version': '1'
                    },
                    'configuration': {
                        'RepositoryName': f'{self.pipeline_name}-infrastructure',
                        'BranchName': 'main',
                        'PollForSourceChanges': 'false'
                    },
                    'outputArtifacts': [{'name': 'InfrastructureSource'}]
                }
            ]
        }
    
    def create_build_stage_with_parallel_actions(self):
        """Create build stage with parallel builds for different components"""
        return {
            'name': 'Build',
            'actions': [
                {
                    'name': 'BuildApplication',
                    'actionTypeId': {
                        'category': 'Build',
                        'owner': 'AWS',
                        'provider': 'CodeBuild',
                        'version': '1'
                    },
                    'configuration': {
                        'ProjectName': f'{self.pipeline_name}-app-build',
                        'PrimarySource': 'ApplicationSource'
                    },
                    'inputArtifacts': [
                        {'name': 'ApplicationSource'}
                    ],
                    'outputArtifacts': [{'name': 'ApplicationBuild'}],
                    'runOrder': 1
                },
                {
                    'name': 'BuildInfrastructure',
                    'actionTypeId': {
                        'category': 'Build',
                        'owner': 'AWS',
                        'provider': 'CodeBuild',
                        'version': '1'
                    },
                    'configuration': {
                        'ProjectName': f'{self.pipeline_name}-infra-build'
                    },
                    'inputArtifacts': [
                        {'name': 'InfrastructureSource'}
                    ],
                    'outputArtifacts': [{'name': 'InfrastructureBuild'}],
                    'runOrder': 1
                }
            ]
        }
    
    def create_comprehensive_test_stage(self):
        """Create comprehensive testing with parallel test types"""
        return {
            'name': 'Test',
            'actions': [
                {
                    'name': 'UnitTests',
                    'actionTypeId': {
                        'category': 'Test',
                        'owner': 'AWS',
                        'provider': 'CodeBuild',
                        'version': '1'
                    },
                    'configuration': {
                        'ProjectName': f'{self.pipeline_name}-unit-tests'
                    },
                    'inputArtifacts': [{'name': 'ApplicationBuild'}],
                    'outputArtifacts': [{'name': 'UnitTestResults'}],
                    'runOrder': 1
                },
                {
                    'name': 'IntegrationTests',
                    'actionTypeId': {
                        'category': 'Test',
                        'owner': 'AWS',
                        'provider': 'CodeBuild',
                        'version': '1'
                    },
                    'configuration': {
                        'ProjectName': f'{self.pipeline_name}-integration-tests'
                    },
                    'inputArtifacts': [{'name': 'ApplicationBuild'}],
                    'outputArtifacts': [{'name': 'IntegrationTestResults'}],
                    'runOrder': 1
                },
                {
                    'name': 'LoadTests',
                    'actionTypeId': {
                        'category': 'Test',
                        'owner': 'AWS',
                        'provider': 'CodeBuild',
                        'version': '1'
                    },
                    'configuration': {
                        'ProjectName': f'{self.pipeline_name}-load-tests'
                    },
                    'inputArtifacts': [{'name': 'ApplicationBuild'}],
                    'runOrder': 2
                }
            ]
        }
    
    def create_security_scan_stage(self):
        """Create security scanning stage"""
        return {
            'name': 'SecurityScan',
            'actions': [
                {
                    'name': 'SecurityScan',
                    'actionTypeId': {
                        'category': 'Test',
                        'owner': 'AWS',
                        'provider': 'CodeBuild',
                        'version': '1'
                    },
                    'configuration': {
                        'ProjectName': f'{self.pipeline_name}-security-scan'
                    },
                    'inputArtifacts': [
                        {'name': 'ApplicationBuild'},
                        {'name': 'InfrastructureBuild'}
                    ],
                    'outputArtifacts': [{'name': 'SecurityScanResults'}]
                }
            ]
        }
    
    def create_approval_stage_with_notifications(self):
        """Create manual approval stage with SNS notifications"""
        return {
            'name': 'ProductionApproval',
            'actions': [
                {
                    'name': 'ManualApproval',
                    'actionTypeId': {
                        'category': 'Approval',
                        'owner': 'AWS',
                        'provider': 'Manual',
                        'version': '1'
                    },
                    'configuration': {
                        'NotificationArn': f'arn:aws:sns:{self.region}:123456789012:pipeline-approvals',
                        'CustomData': json.dumps({
                            'message': 'Production deployment approval required',
                            'pipeline': self.pipeline_name,
                            'timestamp': datetime.now().isoformat(),
                            'test_results_url': f'https://console.aws.amazon.com/codesuite/codebuild/projects/{self.pipeline_name}-tests/history',
                            'security_scan_url': f'https://console.aws.amazon.com/codesuite/codebuild/projects/{self.pipeline_name}-security-scan/history'
                        })
                    }
                }
            ]
        }
    
    def create_multi_environment_deploy_stage(self):
        """Create deployment stage with multiple environments"""
        return {
            'name': 'Deploy',
            'actions': [
                {
                    'name': 'DeployToProduction',
                    'actionTypeId': {
                        'category': 'Deploy',
                        'owner': 'AWS',
                        'provider': 'CodeDeploy',
                        'version': '1'
                    },
                    'configuration': {
                        'ApplicationName': f'{self.pipeline_name}-app',
                        'DeploymentGroupName': 'production-servers'
                    },
                    'inputArtifacts': [{'name': 'ApplicationBuild'}],
                    'runOrder': 1
                },
                {
                    'name': 'UpdateInfrastructure',
                    'actionTypeId': {
                        'category': 'Deploy',
                        'owner': 'AWS',
                        'provider': 'CloudFormation',
                        'version': '1'
                    },
                    'configuration': {
                        'ActionMode': 'CREATE_UPDATE',
                        'StackName': f'{self.pipeline_name}-infrastructure',
                        'TemplatePath': 'InfrastructureBuild::infrastructure.yml',
                        'Capabilities': 'CAPABILITY_IAM',
                        'RoleArn': self.get_cloudformation_role()
                    },
                    'inputArtifacts': [{'name': 'InfrastructureBuild'}],
                    'runOrder': 1
                }
            ]
        }
    
    def setup_pipeline_monitoring(self):
        """Setup CloudWatch monitoring for the pipeline"""
        try:
            # Create CloudWatch rule for pipeline state changes
            self.events.put_rule(
                Name=f'{self.pipeline_name}-state-change',
                EventPattern=json.dumps({
                    'source': ['aws.codepipeline'],
                    'detail-type': ['CodePipeline Pipeline Execution State Change'],
                    'detail': {
                        'pipeline': [self.pipeline_name]
                    }
                }),
                State='ENABLED',
                Description=f'Monitor {self.pipeline_name} pipeline state changes'
            )
            
            # Add SNS target for notifications
            self.events.put_targets(
                Rule=f'{self.pipeline_name}-state-change',
                Targets=[
                    {
                        'Id': '1',
                        'Arn': f'arn:aws:sns:{self.region}:123456789012:pipeline-notifications',
                        'InputTransformer': {
                            'InputPathsMap': {
                                'pipeline': '$.detail.pipeline',
                                'state': '$.detail.state'
                            },
                            'InputTemplate': '{"pipeline": "<pipeline>", "state": "<state>"}'
                        }
                    }
                ]
            )
            
            print("✅ Pipeline monitoring configured")
            
        except Exception as e:
            print(f"⚠️  Monitoring setup warning: {e}")
    
    def get_pipeline_execution_history(self, max_results=10):
        """Get pipeline execution history with detailed analysis"""
        try:
            response = self.codepipeline.list_pipeline_executions(
                pipelineName=self.pipeline_name,
                maxResults=max_results
            )
            
            executions = []
            for execution in response['pipelineExecutionSummaries']:
                execution_detail = self.codepipeline.get_pipeline_execution(
                    pipelineName=self.pipeline_name,
                    pipelineExecutionId=execution['pipelineExecutionId']
                )
                
                executions.append({
                    'execution_id': execution['pipelineExecutionId'],
                    'status': execution['status'],
                    'start_time': execution['startTime'],
                    'last_update': execution['lastUpdateTime'],
                    'source_revisions': execution_detail['pipelineExecution'].get('artifactRevisions', [])
                })
            
            # Analyze execution patterns
            success_rate = len([e for e in executions if e['status'] == 'Succeeded']) / len(executions) * 100
            avg_duration = sum([(e['last_update'] - e['start_time']).total_seconds() for e in executions]) / len(executions) / 60
            
            print(f"📊 Pipeline Analysis:")
            print(f"  Success Rate: {success_rate:.1f}%")
            print(f"  Average Duration: {avg_duration:.1f} minutes")
            print(f"  Total Executions: {len(executions)}")
            
            return executions
            
        except Exception as e:
            print(f"❌ Error getting execution history: {e}")
            return []
    
    def get_pipeline_service_role(self):
        """Get or create pipeline service role ARN"""
        return f'arn:aws:iam::123456789012:role/CodePipelineExecutionRole'
    
    def get_cloudformation_role(self):
        """Get CloudFormation execution role ARN"""
        return f'arn:aws:iam::123456789012:role/CloudFormationExecutionRole'

# Example usage
pipeline_manager = AdvancedCodePipeline('enterprise-web-app')

# Create enterprise-grade pipeline
pipeline = pipeline_manager.create_enterprise_pipeline()

if pipeline:
    print("\n🎉 Enterprise CI/CD Pipeline Created!")
    print("Features included:")
    print("✅ Multi-source repositories")
    print("✅ Parallel build and test execution")
    print("✅ Comprehensive security scanning")
    print("✅ Manual approval with notifications")
    print("✅ Infrastructure as Code deployment")
    print("✅ CloudWatch monitoring and alerting")
    
    # Get execution history
    history = pipeline_manager.get_pipeline_execution_history()
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def application_configuration_tab():
    """Content for Application Configuration tab"""
    st.markdown("## ⚙️ Application Configuration")
    st.markdown("*Manage application dependencies using AWS Systems Manager Parameter Store and AWS Secrets Manager*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Application Configuration** involves managing the dependencies of your code modules (environment variables, 
    configuration files, container images) within the package. AWS provides two primary services for this: 
    **Parameter Store** for configuration values and **Secrets Manager** for sensitive data with automatic rotation.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Configuration Management Architecture
    st.markdown("### 🏗️ Configuration Management Architecture")
    common.mermaid(create_configuration_management_mermaid(), height=900)
    
    # Service Comparison
    st.markdown("### ⚖️ Parameter Store vs Secrets Manager")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🏗️ AWS Systems Manager Parameter Store
        
        **Best For:**
        - Configuration values (database strings, API endpoints)
        - License codes and application settings
        - Environment variables
        - Non-sensitive operational parameters
        
        **Key Features:**
        - ✅ Hierarchical storage (`/app/database/host`)
        - ✅ String, StringList, and SecureString types
        - ✅ Version tracking and history
        - ✅ Integration with IAM for access control
        - ❌ No automatic rotation
        - 💰 Free tier available (up to 10,000 parameters)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔐 AWS Secrets Manager
        
        **Best For:**
        - Database credentials and passwords
        - API keys and tokens
        - Sensitive configuration data
        - Any secrets requiring rotation
        
        **Key Features:**
        - ✅ Automatic rotation capabilities
        - ✅ Cross-region replication
        - ✅ Fine-grained access control
        - ✅ Audit trail and compliance features
        - ✅ Integration with RDS, Aurora, Redshift
        - 💰 Pay per secret per month + API calls
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Configuration Builder
    st.markdown("### 🛠️ Interactive Configuration Builder")
    
    tab1, tab2 = st.tabs(["📊 Parameter Store", "🔐 Secrets Manager"])
    
    with tab1:
        st.markdown("### 📊 Parameter Store Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            param_name = st.text_input("Parameter Name:", "/myapp/database/host")
            param_type = st.selectbox("Parameter Type:", [
                "String", "StringList", "SecureString"
            ])
            param_tier = st.selectbox("Parameter Tier:", [
                "Standard (Free tier)", "Advanced (Paid)"
            ])
        
        with col2:
            param_value = st.text_area("Parameter Value:", "db.example.com")
            param_description = st.text_input("Description:", "Database hostname for production environment")
            param_tags = st.text_input("Tags (key=value, comma separated):", "Environment=prod,Application=myapp")
        
        if st.button("📝 Create Parameter", key="create_param"):
            # Validate parameter name format
            if param_name.startswith('/'):
                st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
                st.markdown(f"""
                ### ✅ Parameter Store Configuration Created!
                
                **Parameter Details:**
                - **Name**: `{param_name}`
                - **Type**: {param_type}
                - **Tier**: {param_tier}
                - **Value**: {'[ENCRYPTED]' if param_type == 'SecureString' else param_value}
                - **Description**: {param_description}
                
                **Access Pattern:**
                ```python
                import boto3
                ssm = boto3.client('ssm')
                
                response = ssm.get_parameter(
                    Name='{param_name}',
                    WithDecryption=True
                )
                value = response['Parameter']['Value']
                ```
                """)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("Parameter name must start with '/' for hierarchical organization")
        
        # Parameter Store Pricing Calculator
        st.markdown("### 💰 Parameter Store Cost Calculator")
        
        col3, col4 = st.columns(2)
        
        with col3:
            num_standard_params = st.number_input("Standard Parameters:", 0, 10000, 100)
            num_advanced_params = st.number_input("Advanced Parameters:", 0, 100000, 50)
        
        with col4:
            api_calls_per_month = st.number_input("API Calls/Month:", 0, 10000000, 50000)
            
        # Calculate costs
        standard_cost = 0  # First 10,000 are free
        advanced_cost = num_advanced_params * 0.05  # $0.05 per parameter per month
        api_cost = max(0, (api_calls_per_month - 10000)) * 0.00005  # First 10,000 free, then $0.05 per 1000
        
        total_cost = standard_cost + advanced_cost + api_cost
        
        st.metric("Estimated Monthly Cost", f"${total_cost:.2f}")
    
    with tab2:
        st.markdown("### 🔐 Secrets Manager Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            secret_name = st.text_input("Secret Name:", "prod/myapp/db-credentials")
            secret_type = st.selectbox("Secret Type:", [
                "Database credentials", "API key", "Custom secret", "Other"
            ])
            auto_rotation = st.checkbox("Enable Automatic Rotation", value=True)
            
            if auto_rotation:
                rotation_interval = st.selectbox("Rotation Interval:", [
                    "30 days", "60 days", "90 days", "Custom"
                ])
        
        with col2:
            if secret_type == "Database credentials":
                db_username = st.text_input("Database Username:", "admin")
                db_password = st.text_input("Database Password:", type="password")
                db_host = st.text_input("Database Host:", "db.example.com")
                db_port = st.number_input("Database Port:", 1, 65535, 5432)
            else:
                secret_value = st.text_area("Secret Value (JSON format):", '{"api_key": "your-secret-key"}')
            
            cross_region = st.checkbox("Enable Cross-Region Replication")
            if cross_region:
                replica_regions = st.multiselect("Replica Regions:", 
                    ["us-west-2", "eu-west-1", "ap-southeast-1"])
        
        if st.button("🔐 Create Secret", key="create_secret"):
            if secret_type == "Database credentials":
                secret_structure = {
                    "username": db_username,
                    "password": "[ENCRYPTED]",
                    "host": db_host,
                    "port": db_port
                }
            else:
                secret_structure = "[ENCRYPTED JSON]"
            
            st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
            st.markdown(f"""
            ### ✅ Secrets Manager Secret Created!
            
            **Secret Details:**
            - **Name**: `{secret_name}`
            - **Type**: {secret_type}
            - **Auto Rotation**: {'✅ Enabled' if auto_rotation else '❌ Disabled'}
            - **Rotation Interval**: {rotation_interval if auto_rotation else 'N/A'}
            - **Cross-Region Replication**: {'✅ Enabled' if cross_region else '❌ Disabled'}
            
            **Secret Structure:**
            ```json
            {json.dumps(secret_structure, indent=2) if isinstance(secret_structure, dict) else secret_structure}
            ```
            
            **Access Pattern:**
            ```python
            import boto3
            secrets = boto3.client('secretsmanager')
            
            response = secrets.get_secret_value(SecretId='{secret_name}')
            secret = json.loads(response['SecretString'])
            ```
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Secrets Manager Cost Calculator
        st.markdown("### 💰 Secrets Manager Cost Calculator")
        
        col3, col4 = st.columns(2)
        
        with col3:
            num_secrets = st.number_input("Number of Secrets:", 1, 10000, 10)
            api_calls_per_month_secrets = st.number_input("API Calls/Month (Secrets):", 0, 1000000, 10000)
        
        with col4:
            replica_count = st.number_input("Replica Regions per Secret:", 0, 10, 0)
        
        # Calculate Secrets Manager costs
        base_secret_cost = num_secrets * 0.40  # $0.40 per secret per month
        replica_cost = num_secrets * replica_count * 0.05  # $0.05 per replica per month
        api_cost_secrets = api_calls_per_month_secrets * 0.00005  # $0.05 per 10,000 API calls
        
        total_secrets_cost = base_secret_cost + replica_cost + api_cost_secrets
        
        st.metric("Estimated Monthly Cost", f"${total_secrets_cost:.2f}")
    
    # Configuration Best Practices
    st.markdown("### 💡 Configuration Management Best Practices")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🏗️ Hierarchical Organization
        - Use **path-based naming** (`/app/env/component`)
        - Group related parameters together
        - Use consistent naming conventions
        - Implement **environment separation**
        
        **Example Structure:**
        ```
        /myapp/prod/database/host
        /myapp/prod/database/port
        /myapp/staging/database/host
        /myapp/dev/api/endpoint
        ```
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔐 Security Best Practices
        - Use **SecureString** for sensitive data
        - Implement **least privilege** IAM policies
        - Enable **CloudTrail logging** for audit
        - Use **automatic rotation** for secrets
        
        **IAM Policy Example:**
        ```json
        {
          "Effect": "Allow",
          "Action": "ssm:GetParameter",
          "Resource": "arn:aws:ssm:region:account:parameter/myapp/*"
        }
        ```
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Integration Patterns
    st.markdown("### 🔗 Integration Patterns & Use Cases")
    
    integration_data = {
        'Use Case': [
            'Database Connection',
            'API Configuration', 
            'Feature Flags',
            'Third-party Keys',
            'Environment Settings',
            'Application Secrets'
        ],
        'Parameter Store': [
            'Host, Port, DB Name',
            'Endpoints, Timeouts',
            'Boolean flags',
            'Non-sensitive keys',
            'Log levels, Debug mode',
            'N/A'
        ],
        'Secrets Manager': [
            'Username, Password',
            'API tokens',
            'N/A',
            'Sensitive API keys',
            'N/A',
            'Encryption keys'
        ],
        'Best Practice': [
            'Combine both services',
            'Separate config from secrets',
            'Use Parameter Store',
            'Use Secrets Manager',
            'Use Parameter Store',
            'Use Secrets Manager'
        ]
    }
    
    df_integration = pd.DataFrame(integration_data)
    st.dataframe(df_integration, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Complete Configuration Management")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Complete configuration management using Parameter Store and Secrets Manager
import boto3
import json
import os
from typing import Dict, Any, Optional
from functools import lru_cache

class ConfigurationManager:
    def __init__(self, region_name='us-east-1', app_name='myapp', environment='prod'):
        self.region_name = region_name
        self.app_name = app_name
        self.environment = environment
        
        # Initialize AWS clients
        self.ssm = boto3.client('ssm', region_name=region_name)
        self.secrets = boto3.client('secretsmanager', region_name=region_name)
        
        # Configuration cache
        self._config_cache = {}
        self._secrets_cache = {}
    
    def get_parameter(self, parameter_name: str, decrypt: bool = True, use_cache: bool = True) -> Optional[str]:
        """Get parameter from Parameter Store with caching"""
        
        # Build full parameter path
        full_path = f'/{self.app_name}/{self.environment}/{parameter_name}'
        
        # Check cache first
        if use_cache and full_path in self._config_cache:
            return self._config_cache[full_path]
        
        try:
            response = self.ssm.get_parameter(
                Name=full_path,
                WithDecryption=decrypt
            )
            
            value = response['Parameter']['Value']
            
            # Cache the value
            if use_cache:
                self._config_cache[full_path] = value
            
            return value
            
        except self.ssm.exceptions.ParameterNotFound:
            print(f"⚠️  Parameter not found: {full_path}")
            return None
        except Exception as e:
            print(f"❌ Error getting parameter {full_path}: {e}")
            return None
    
    def get_parameters_by_path(self, path: str, decrypt: bool = True) -> Dict[str, str]:
        """Get multiple parameters by path prefix"""
        
        full_path = f'/{self.app_name}/{self.environment}/{path}'
        parameters = {}
        
        try:
            paginator = self.ssm.get_paginator('get_parameters_by_path')
            
            for page in paginator.paginate(
                Path=full_path,
                Recursive=True,
                WithDecryption=decrypt
            ):
                for param in page['Parameters']:
                    # Extract the parameter name from the full path
                    param_name = param['Name'].replace(f'/{self.app_name}/{self.environment}/', '')
                    parameters[param_name] = param['Value']
            
            # Cache all parameters
            for name, value in parameters.items():
                cache_key = f'/{self.app_name}/{self.environment}/{name}'
                self._config_cache[cache_key] = value
            
            return parameters
            
        except Exception as e:
            print(f"❌ Error getting parameters by path {full_path}: {e}")
            return {}
    
    def set_parameter(self, parameter_name: str, value: str, parameter_type: str = 'String', 
                     description: str = '', overwrite: bool = True) -> bool:
        """Set parameter in Parameter Store"""
        
        full_path = f'/{self.app_name}/{self.environment}/{parameter_name}'
        
        try:
            self.ssm.put_parameter(
                Name=full_path,
                Value=value,
                Type=parameter_type,
                Description=description,
                Overwrite=overwrite,
                Tags=[
                    {'Key': 'Application', 'Value': self.app_name},
                    {'Key': 'Environment', 'Value': self.environment},
                    {'Key': 'ManagedBy', 'Value': 'ConfigurationManager'}
                ]
            )
            
            # Update cache
            self._config_cache[full_path] = value
            
            print(f"✅ Parameter created/updated: {full_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error setting parameter {full_path}: {e}")
            return False
    
    def get_secret(self, secret_name: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """Get secret from Secrets Manager with caching"""
        
        full_secret_name = f'{self.environment}/{self.app_name}/{secret_name}'
        
        # Check cache first
        if use_cache and full_secret_name in self._secrets_cache:
            return self._secrets_cache[full_secret_name]
        
        try:
            response = self.secrets.get_secret_value(SecretId=full_secret_name)
            
            # Parse the secret value
            secret_value = json.loads(response['SecretString'])
            
            # Cache the secret
            if use_cache:
                self._secrets_cache[full_secret_name] = secret_value
            
            return secret_value
            
        except self.secrets.exceptions.ResourceNotFoundException:
            print(f"⚠️  Secret not found: {full_secret_name}")
            return None
        except json.JSONDecodeError:
            print(f"⚠️  Secret value is not valid JSON: {full_secret_name}")
            return {"value": response['SecretString']}
        except Exception as e:
            print(f"❌ Error getting secret {full_secret_name}: {e}")
            return None
    
    def create_secret(self, secret_name: str, secret_value: Dict[str, Any], 
                     description: str = '', enable_rotation: bool = False) -> bool:
        """Create secret in Secrets Manager"""
        
        full_secret_name = f'{self.environment}/{self.app_name}/{secret_name}'
        
        try:
            create_params = {
                'Name': full_secret_name,
                'SecretString': json.dumps(secret_value),
                'Description': description,
                'Tags': [
                    {'Key': 'Application', 'Value': self.app_name},
                    {'Key': 'Environment', 'Value': self.environment},
                    {'Key': 'ManagedBy', 'Value': 'ConfigurationManager'}
                ]
            }
            
            if enable_rotation:
                create_params['AutomaticRotation'] = {
                    'Rules': {
                        'AutomaticallyAfterDays': 30
                    }
                }
            
            self.secrets.create_secret(**create_params)
            
            # Update cache
            self._secrets_cache[full_secret_name] = secret_value
            
            print(f"✅ Secret created: {full_secret_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating secret {full_secret_name}: {e}")
            return False
    
    @lru_cache(maxsize=128)
    def get_database_config(self) -> Dict[str, Any]:
        """Get complete database configuration combining parameters and secrets"""
        
        try:
            # Get database configuration from Parameter Store
            db_config = self.get_parameters_by_path('database')
            
            # Get database credentials from Secrets Manager
            db_credentials = self.get_secret('database-credentials')
            
            if db_credentials:
                db_config.update(db_credentials)
            
            # Convert port to integer if present
            if 'port' in db_config:
                db_config['port'] = int(db_config['port'])
            
            return db_config
            
        except Exception as e:
            print(f"❌ Error getting database configuration: {e}")
            return {}
    
    def setup_application_config(self):
        """Setup complete application configuration"""
        
        print(f"🔧 Setting up configuration for {self.app_name} ({self.environment})")
        
        # Database configuration parameters
        db_params = {
            'database/host': 'db.example.com',
            'database/port': '5432',
            'database/name': 'myapp_db',
            'database/ssl_mode': 'require',
            'database/connection_pool_size': '20'
        }
        
        for param_name, param_value in db_params.items():
            self.set_parameter(
                parameter_name=param_name,
                value=param_value,
                description=f'Database configuration for {param_name.split("/")[-1]}'
            )
        
        # Application settings
        app_params = {
            'api/timeout': '30',
            'api/retry_attempts': '3',
            'logging/level': 'INFO',
            'features/new_ui_enabled': 'true',
            'cache/ttl_seconds': '3600'
        }
        
        for param_name, param_value in app_params.items():
            self.set_parameter(
                parameter_name=param_name,
                value=param_value,
                description=f'Application setting for {param_name}'
            )
        
        # Sensitive secrets
        db_credentials = {
            'username': 'admin',
            'password': 'super-secret-password',
            'connection_string': 'postgresql://admin:super-secret-password@db.example.com:5432/myapp_db'
        }
        
        self.create_secret(
            secret_name='database-credentials',
            secret_value=db_credentials,
            description='Database credentials with automatic rotation',
            enable_rotation=True
        )
        
        # API keys and tokens
        api_secrets = {
            'stripe_api_key': 'sk_live_...',
            'sendgrid_api_key': 'SG...',
            'jwt_secret': 'your-jwt-secret-key'
        }
        
        self.create_secret(
            secret_name='api-keys',
            secret_value=api_secrets,
            description='Third-party API keys and tokens'
        )
        
        print("✅ Application configuration setup complete!")
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get complete application configuration"""
        
        config = {}
        
        # Get all parameters
        all_params = self.get_parameters_by_path('')
        config.update(all_params)
        
        # Get database credentials
        db_creds = self.get_secret('database-credentials')
        if db_creds:
            for key, value in db_creds.items():
                config[f'database/{key}'] = value
        
        # Get API keys
        api_keys = self.get_secret('api-keys')
        if api_keys:
            for key, value in api_keys.items():
                config[f'api/{key}'] = value
        
        return config
    
    def clear_cache(self):
        """Clear configuration cache"""
        self._config_cache.clear()
        self._secrets_cache.clear()
        print("🗑️  Configuration cache cleared")

# Example usage
def main():
    # Initialize configuration manager
    config_manager = ConfigurationManager(
        region_name='us-east-1',
        app_name='mywebapp',
        environment='production'
    )
    
    # Setup initial configuration
    config_manager.setup_application_config()
    
    # Get database configuration
    db_config = config_manager.get_database_config()
    print(f"📊 Database Config: {db_config}")
    
    # Get specific parameter
    log_level = config_manager.get_parameter('logging/level')
    print(f"📝 Log Level: {log_level}")
    
    # Get all configuration
    all_config = config_manager.get_all_config()
    print(f"⚙️  Total config items: {len(all_config)}")
    
    # Example application startup
    print("\n🚀 Starting application with configuration...")
    
    # Database connection example
    if db_config:
        print(f"🔌 Connecting to database: {db_config.get('host')}:{db_config.get('port')}")
        print(f"📄 Database: {db_config.get('name')}")
        print(f"👤 User: {db_config.get('username')}")
        # Don't print password in real applications!
    
    # API configuration example
    api_timeout = config_manager.get_parameter('api/timeout')
    if api_timeout:
        print(f"⏱️  API timeout set to: {api_timeout} seconds")

if __name__ == '__main__':
    main()
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
    # 🚀 AWS CI/CD
    
    """)
    st.markdown("""<div class="info-box">
                Master continuous integration and deployment with AWS services. Learn release process stages, CI/CD best practices, AWS CodePipeline automation, and application configuration management using Parameter Store and Secrets Manager.
                </div>""", unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔄 Release Process Stages", 
        "🚀 CI/CD", 
        "🔗 AWS CodePipeline",
        "⚙️ Application Configuration"
    ])
    
    with tab1:
        release_process_stages_tab()
    
    with tab2:
        cicd_tab()
    
    with tab3:
        codepipeline_tab()
    
    with tab4:
        application_configuration_tab()
    
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
