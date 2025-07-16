import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import boto3
import json
from datetime import datetime, timedelta
import utils.common as common
import utils.authenticate as authenticate

# Page configuration
st.set_page_config(
    page_title="AWS Monitoring Tools Hub",
    page_icon="📊",
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
    'info': '#00A1C9'
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
            border-left: 5px solid {AWS_COLORS['info']};
        }}
        
        .log-entry {{
            background-color: {AWS_COLORS['dark_blue']};
            color: #00FF00;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            margin: 10px 0;
            border-left: 4px solid {AWS_COLORS['success']};
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
        
        .alarm-card {{
            background: white;
            padding: 15px;
            border-radius: 12px;
            border: 2px solid {AWS_COLORS['warning']};
            margin: 10px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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
            - 🔍 AWS CloudTrail - API call auditing and governance
            - 📊 Amazon CloudWatch - Monitoring and observability
            
            **Learning Objectives:**
            - Understand AWS monitoring and logging capabilities
            - Learn to set up comprehensive monitoring solutions
            - Practice with real-world monitoring scenarios
            - Explore automation with alarms and notifications
            - Master log analysis and troubleshooting techniques
            """)

def create_cloudtrail_architecture_mermaid():
    """Create mermaid diagram for CloudTrail architecture"""
    return """
    graph TB
        A[👤 User Action] --> B[🔑 AWS API Call]
        B --> C[☁️ AWS Service]
        C --> D[📝 CloudTrail Event]
        
        D --> E[📁 S3 Bucket Storage]
        D --> F[📊 CloudWatch Logs]
        
        F --> G[🔍 Metric Filter]
        G --> H[🚨 CloudWatch Alarm]
        H --> I[📧 SNS Notification]
        I --> J[👨‍💼 Security Admin]
        
        E --> K[🗂️ Long-term Storage]
        E --> L[🔎 AWS Config Analysis]
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style D fill:#FF9900,stroke:#232F3E,color:#fff
        style E fill:#3FB34F,stroke:#232F3E,color:#fff
        style H fill:#FF6B35,stroke:#232F3E,color:#fff
        style J fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_cloudwatch_architecture_mermaid():
    """Create mermaid diagram for CloudWatch architecture"""
    return """
    graph LR
        A[🖥️ EC2 Instances] --> E[📊 CloudWatch]
        B[🗄️ RDS Database] --> E
        C[⚡ Lambda Functions] --> E
        D[🌐 Application Load Balancer] --> E
        
        E --> F[📈 Metrics]
        E --> G[📋 Logs]
        E --> H[🚨 Alarms]
        E --> I[📊 Dashboards]
        
        F --> J[📊 Custom Dashboards]
        G --> K[🔍 Log Insights]
        H --> L[📧 SNS Notifications]
        H --> M[🔄 Auto Scaling Actions]
        
        L --> N[👨‍💼 Operations Team]
        M --> O[🚀 Scale Resources]
        
        style E fill:#FF9900,stroke:#232F3E,color:#fff
        style F fill:#4B9EDB,stroke:#232F3E,color:#fff
        style G fill:#3FB34F,stroke:#232F3E,color:#fff
        style H fill:#FF6B35,stroke:#232F3E,color:#fff
        style N fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_monitoring_flow_mermaid():
    """Create mermaid diagram for monitoring workflow"""
    return """
    graph TD
        A[Unauthorized IAM Change] --> B[CloudTrail Captures Event]
        B --> C[Event Sent to CloudWatch Logs]
        C --> D[Metric Filter Triggered]
        D --> E[CloudWatch Alarm Activated]
        E --> F[SNS Topic Notification]
        F --> G[Security Team Alerted]
        
        H[CloudTrail] --> I[S3 Storage]
        B --> I
        
        style A fill:#FF6B35,stroke:#232F3E,color:#fff
        style B fill:#FF9900,stroke:#232F3E,color:#fff
        style D fill:#4B9EDB,stroke:#232F3E,color:#fff
        style E fill:#FF6B35,stroke:#232F3E,color:#fff
        style G fill:#232F3E,stroke:#FF9900,color:#fff
    """

def cloudtrail_tab():
    """Content for AWS CloudTrail tab"""
    st.markdown("## 🔍 AWS CloudTrail")
    st.markdown("*Auditing, security monitoring, and operational troubleshooting by tracking user activity and API usage*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **AWS CloudTrail** enables auditing, security monitoring, and operational troubleshooting by tracking user activity 
    and API usage across your AWS infrastructure, giving you control over storage, analysis, and remediation actions.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # CloudTrail Features
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 📝\n**Event Logging**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🔒\n**Security Analysis**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 📊\n**Compliance**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🔍\n**Investigation**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # CloudTrail Architecture
    st.markdown("### 🏗️ CloudTrail Architecture")
    common.mermaid(create_cloudtrail_architecture_mermaid(), height=1000)
    
    # Interactive CloudTrail Event Explorer
    st.markdown("### 🔍 Interactive CloudTrail Event Explorer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        event_source = st.selectbox("Event Source:", [
            "iam.amazonaws.com", "ec2.amazonaws.com", "s3.amazonaws.com", 
            "rds.amazonaws.com", "lambda.amazonaws.com", "cloudformation.amazonaws.com"
        ])
        
        event_name = st.selectbox("Event Name:", [
            "CreateUser", "AttachUserPolicy", "RunInstances", "CreateBucket",
            "DeleteBucket", "CreateFunction", "UpdateFunction"
        ])
    
    with col2:
        user_name = st.text_input("User Name:", "Mary_Major")
        source_ip = st.text_input("Source IP Address:", "203.0.113.12")
        user_agent = st.text_input("User Agent:", "aws-cli/2.0.0 Python/3.8.0")
    
    if st.button("🔍 Generate CloudTrail Event", use_container_width=True):
        # Generate sample CloudTrail event
        event_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        sample_event = {
            "eventVersion": "1.05",
            "userIdentity": {
                "type": "IAMUser",
                "principalId": f"AIDA{np.random.randint(100000000000, 999999999999)}",
                "arn": f"arn:aws:iam::123456789012:user/{user_name}",
                "accountId": "123456789012",
                "userName": user_name
            },
            "eventTime": event_time,
            "eventSource": event_source,
            "eventName": event_name,
            "awsRegion": "us-east-1",
            "sourceIPAddress": source_ip,
            "userAgent": user_agent,
            "requestParameters": {
                "userName": user_name if event_name == "CreateUser" else None,
                "policyArn": "arn:aws:iam::aws:policy/PowerUserAccess" if "Policy" in event_name else None
            },
            "responseElements": {
                "user": {
                    "path": "/",
                    "userName": user_name,
                    "userId": f"AIDA{np.random.randint(100000000000, 999999999999)}",
                    "arn": f"arn:aws:iam::123456789012:user/{user_name}",
                    "createDate": event_time
                } if event_name == "CreateUser" else None
            },
            "requestID": f"{np.random.randint(10000000, 99999999)}-{np.random.randint(1000, 9999)}-{np.random.randint(1000, 9999)}-{np.random.randint(1000, 9999)}-{np.random.randint(100000000000, 999999999999)}",
            "eventID": f"{np.random.randint(10000000, 99999999)}-{np.random.randint(1000, 9999)}-{np.random.randint(1000, 9999)}-{np.random.randint(1000, 9999)}-{np.random.randint(100000000000, 999999999999)}",
            "eventType": "AwsApiCall",
            "recipientAccountId": "123456789012",
            "serviceEventDetails": {
                "responseElements": None,
                "additionalEventData": None,
                "requestParameters": None,
                "eventCategory": "Management"
            }
        }
        
        st.markdown('<div class="log-entry">', unsafe_allow_html=True)
        st.json(sample_event)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Event Analysis
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 📊 Event Analysis
        
        **Key Information:**
        - **User**: {user_name} (IAM User)
        - **Action**: {event_name} on {event_source}
        - **Time**: {event_time}
        - **Source IP**: {source_ip}
        - **User Agent**: {user_agent}
        - **Success**: ✅ API call completed successfully
        - **MFA Used**: ❌ No multi-factor authentication detected
        
        🚨 **Security Note**: User was not using MFA for sensitive operations!
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # CloudTrail Event Types
    st.markdown("### 📋 CloudTrail Event Types")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔧 Management Events
        - **IAM operations** (users, roles, policies)
        - Resource creation/deletion
        - Configuration changes
        - **Security-related** activities
        
        **Examples:**
        - CreateUser, DeleteUser
        - RunInstances, TerminateInstances
        - CreateBucket, DeleteBucket
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📊 Data Events
        - **S3 object-level** operations
        - Lambda function invocations
        - DynamoDB API calls
        - **High-volume** activities
        
        **Examples:**
        - GetObject, PutObject
        - Invoke (Lambda)
        - GetItem, PutItem (DynamoDB)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔍 Insight Events
        - **Unusual activity** patterns
        - Error rate analysis
        - **Automated detection** of anomalies
        - Advanced analytics
        
        **Examples:**
        - Unusual API call patterns
        - Failed authentication attempts
        - Resource access anomalies
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # CloudTrail Best Practices
    st.markdown("### 💡 CloudTrail Best Practices")
    
    practices_data = {
        'Best Practice': [
            'Enable in All Regions',
            'Use Organization Trail',
            'Enable Log File Validation',
            'Encrypt CloudTrail Logs',
            'Set Up Log Monitoring',
            'Regular Access Review'
        ],
        'Why Important': [
            'Complete visibility across all AWS regions',
            'Centralized logging for multiple accounts',
            'Detect tampering or corruption',
            'Protect sensitive audit information',
            'Real-time security alerting',
            'Ensure least privilege access'
        ],
        'Implementation': [
            'Create multi-region trail',
            'Enable organizational CloudTrail',
            'Turn on log file validation',
            'Use KMS encryption keys',
            'CloudWatch Logs integration',
            'Automated access reviews'
        ]
    }
    
    df_practices = pd.DataFrame(practices_data)
    st.dataframe(df_practices, use_container_width=True)
    
    # Security Monitoring Scenario
    st.markdown("### 🚨 Security Monitoring Scenario")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🔥 Real-World Security Scenario
    
    **Situation**: Unauthorized IAM changes detected in production environment
    
    **CloudTrail Response Flow:**
    1. **Staff** makes unauthorized IAM policy changes
    2. **CloudTrail** captures the API calls and sends to S3 & CloudWatch Logs
    3. **CloudWatch Logs** metric filter triggers on suspicious IAM activities
    4. **CloudWatch Alarm** activates and sends notification to SNS
    5. **Security Admins** receive immediate alerts for investigation
    
    **Key Benefits:**
    - **Real-time detection** of security violations
    - **Complete audit trail** for forensic analysis
    - **Automated alerting** reduces response time
    - **Compliance evidence** for regulatory requirements
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive CloudTrail Cost Calculator
    st.markdown("### 💰 CloudTrail Cost Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        management_events = st.slider("Management Events per Month (thousands):", 10, 1000, 100)
        data_events = st.slider("Data Events per Month (millions):", 0, 100, 10)
        retention_months = st.slider("Log Retention (months):", 1, 120, 12)
    
    with col2:
        regions_enabled = st.slider("Number of Regions:", 1, 20, 3)
        encryption_enabled = st.checkbox("KMS Encryption", value=True)
        insights_enabled = st.checkbox("CloudTrail Insights", value=False)
    
    if st.button("💰 Calculate CloudTrail Costs", use_container_width=True):
        # CloudTrail pricing calculations
        management_cost = 0  # First copy of management events is free
        data_events_cost = (data_events * 1_000_000 / 100_000) * 0.10  # $0.10 per 100,000 events
        
        # Storage costs (S3)
        avg_event_size_kb = 1.5  # Average CloudTrail event size
        total_events = (management_events * 1000) + (data_events * 1_000_000)
        storage_gb_per_month = (total_events * avg_event_size_kb) / (1024 * 1024)
        storage_cost = storage_gb_per_month * 0.023 * retention_months  # S3 Standard pricing
        
        # KMS encryption costs
        kms_cost = 100 * 0.03 if encryption_enabled else 0  # $0.03 per 10,000 requests
        
        # CloudTrail Insights
        insights_cost = data_events * 0.35 if insights_enabled else 0  # $0.35 per 100,000 events
        
        total_monthly_cost = data_events_cost + (storage_cost / retention_months) + kms_cost + insights_cost
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Data Events", f"${data_events_cost:.2f}/month", "Per 100K events")
        
        with col2:
            st.metric("Storage (S3)", f"${storage_cost/retention_months:.2f}/month", f"{storage_gb_per_month:.1f} GB")
        
        with col3:
            st.metric("KMS Encryption", f"${kms_cost:.2f}/month", "If enabled")
        
        with col4:
            st.metric("Total Monthly", f"${total_monthly_cost:.2f}", f"Annual: ${total_monthly_cost * 12:.2f}")
    
    # Code Example
    st.markdown("### 💻 Code Example: CloudTrail Setup and Monitoring")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Set up AWS CloudTrail with monitoring and alerting
import boto3
import json
from datetime import datetime

def create_cloudtrail_with_monitoring():
    """Create CloudTrail with CloudWatch integration for security monitoring"""
    
    # Initialize AWS clients
    cloudtrail = boto3.client('cloudtrail')
    logs = boto3.client('logs')
    cloudwatch = boto3.client('cloudwatch')
    sns = boto3.client('sns')
    s3 = boto3.client('s3')
    
    # Create S3 bucket for CloudTrail logs
    bucket_name = f"my-cloudtrail-logs-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    try:
        s3.create_bucket(Bucket=bucket_name)
        
        # S3 bucket policy for CloudTrail
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AWSCloudTrailAclCheck",
                    "Effect": "Allow",
                    "Principal": {"Service": "cloudtrail.amazonaws.com"},
                    "Action": "s3:GetBucketAcl",
                    "Resource": f"arn:aws:s3:::{bucket_name}"
                },
                {
                    "Sid": "AWSCloudTrailWrite",
                    "Effect": "Allow",
                    "Principal": {"Service": "cloudtrail.amazonaws.com"},
                    "Action": "s3:PutObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*",
                    "Condition": {
                        "StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}
                    }
                }
            ]
        }
        
        s3.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        
        print(f"✅ Created S3 bucket: {bucket_name}")
        
    except Exception as e:
        print(f"❌ Error creating S3 bucket: {e}")
        return None
    
    # Create CloudWatch Log Group for CloudTrail
    log_group_name = '/aws/cloudtrail/security-monitoring'
    
    try:
        logs.create_log_group(logGroupName=log_group_name)
        print(f"✅ Created CloudWatch Log Group: {log_group_name}")
    except logs.exceptions.ResourceAlreadyExistsException:
        print(f"ℹ️  Log group already exists: {log_group_name}")
    
    # Create SNS topic for alerts
    topic_response = sns.create_topic(Name='security-alerts')
    topic_arn = topic_response['TopicArn']
    print(f"✅ Created SNS topic: {topic_arn}")
    
    # Create CloudTrail
    trail_name = 'security-monitoring-trail'
    
    try:
        cloudtrail_response = cloudtrail.create_trail(
            Name=trail_name,
            S3BucketName=bucket_name,
            IncludeGlobalServiceEvents=True,
            IsMultiRegionTrail=True,
            EnableLogFileValidation=True,
            CloudWatchLogsLogGroupArn=f"arn:aws:logs:us-east-1:123456789012:log-group:{log_group_name}:*",
            CloudWatchLogsRoleArn="arn:aws:iam::123456789012:role/CloudTrail_CloudWatchLogs_Role"
        )
        
        # Start logging
        cloudtrail.start_logging(Name=trail_name)
        
        print(f"✅ Created and started CloudTrail: {trail_name}")
        
    except Exception as e:
        print(f"❌ Error creating CloudTrail: {e}")
        return None
    
    # Create metric filter for unauthorized IAM changes
    metric_filter_name = 'UnauthorizedIAMChanges'
    
    filter_pattern = '[version,account,time,region,source,principal,access,sourceIP,agent,error,request,response,additional,stage,resource,service]'
    
    try:
        logs.put_metric_filter(
            logGroupName=log_group_name,
            filterName=metric_filter_name,
            filterPattern='{ ($.eventName = CreateUser) || ($.eventName = DeleteUser) || ($.eventName = CreateRole) || ($.eventName = DeleteRole) || ($.eventName = AttachUserPolicy) || ($.eventName = DetachUserPolicy) }',
            metricTransformations=[
                {
                    'metricName': 'UnauthorizedIAMChanges',
                    'metricNamespace': 'Security/CloudTrail',
                    'metricValue': '1',
                    'defaultValue': 0
                }
            ]
        )
        
        print(f"✅ Created metric filter: {metric_filter_name}")
        
    except Exception as e:
        print(f"❌ Error creating metric filter: {e}")
    
    # Create CloudWatch alarm
    try:
        cloudwatch.put_metric_alarm(
            AlarmName='UnauthorizedIAMChangesAlarm',
            ComparisonOperator='GreaterThanThreshold',
            EvaluationPeriods=1,
            MetricName='UnauthorizedIAMChanges',
            Namespace='Security/CloudTrail',
            Period=300,  # 5 minutes
            Statistic='Sum',
            Threshold=0.0,
            ActionsEnabled=True,
            AlarmActions=[topic_arn],
            AlarmDescription='Alert on unauthorized IAM changes',
            Unit='Count'
        )
        
        print("✅ Created CloudWatch alarm for IAM changes")
        
    except Exception as e:
        print(f"❌ Error creating alarm: {e}")
    
    return {
        'trail_name': trail_name,
        'bucket_name': bucket_name,
        'log_group': log_group_name,
        'topic_arn': topic_arn
    }

def analyze_cloudtrail_events(bucket_name, days_back=7):
    """Analyze CloudTrail events for security insights"""
    s3 = boto3.client('s3')
    
    # List recent CloudTrail log files
    response = s3.list_objects_v2(
        Bucket=bucket_name,
        Prefix='AWSLogs/',
        MaxKeys=100
    )
    
    security_events = {
        'failed_logins': 0,
        'root_account_usage': 0,
        'iam_changes': 0,
        'unusual_locations': [],
        'suspicious_activities': []
    }
    
    # Analyze log files (simplified example)
    for obj in response.get('Contents', []):
        if obj['Key'].endswith('.json.gz'):
            try:
                # Download and analyze log file
                log_obj = s3.get_object(Bucket=bucket_name, Key=obj['Key'])
                # In reality, you'd decompress and parse the JSON logs
                
                # Simulated analysis
                security_events['iam_changes'] += np.random.randint(0, 5)
                security_events['failed_logins'] += np.random.randint(0, 3)
                
                if np.random.random() > 0.8:
                    security_events['unusual_locations'].append({
                        'ip': f"203.0.113.{np.random.randint(1, 254)}",
                        'country': np.random.choice(['Unknown', 'Russia', 'China'])
                    })
                
            except Exception as e:
                print(f"Error analyzing {obj['Key']}: {e}")
    
    return security_events

def generate_security_report(analysis_results):
    """Generate security analysis report"""
    print("🔍 CLOUDTRAIL SECURITY ANALYSIS REPORT")
    print("=" * 50)
    
    print(f"📊 Event Summary (Last 7 days):")
    print(f"  Failed Login Attempts: {analysis_results['failed_logins']}")
    print(f"  Root Account Usage: {analysis_results['root_account_usage']}")
    print(f"  IAM Changes: {analysis_results['iam_changes']}")
    
    if analysis_results['unusual_locations']:
        print(f"\n🚨 Unusual Access Locations:")
        for location in analysis_results['unusual_locations']:
            print(f"  IP: {location['ip']} (Country: {location['country']})")
    
    # Security recommendations
    print(f"\n💡 Security Recommendations:")
    if analysis_results['failed_logins'] > 10:
        print("  - Review failed login attempts and consider IP blocking")
    if analysis_results['root_account_usage'] > 0:
        print("  - Root account usage detected - review necessity")
    if analysis_results['iam_changes'] > 20:
        print("  - High IAM activity - verify authorized changes")
    
    return analysis_results

# Example usage
print("🚀 Setting up CloudTrail security monitoring...")
setup_result = create_cloudtrail_with_monitoring()

if setup_result:
    print(f"\n📋 Setup Complete:")
    print(f"  Trail: {setup_result['trail_name']}")
    print(f"  Bucket: {setup_result['bucket_name']}")
    print(f"  Log Group: {setup_result['log_group']}")
    print(f"  Alerts: {setup_result['topic_arn']}")
    
    # Analyze recent events
    analysis = analyze_cloudtrail_events(setup_result['bucket_name'])
    generate_security_report(analysis)
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def cloudwatch_tab():
    """Content for Amazon CloudWatch tab"""
    st.markdown("## 📊 Amazon CloudWatch")
    st.markdown("*Monitoring and operational data in the form of logs, metrics, and events*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Amazon CloudWatch** collects monitoring and operational data in the form of logs, metrics, and events, 
    providing you with a unified view of AWS resources, applications, and services that run on AWS and on-premises.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # CloudWatch Components
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 📈\n**Metrics**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 📋\n**Logs**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🚨\n**Alarms**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 📊\n**Dashboards**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # CloudWatch Architecture
    st.markdown("### 🏗️ CloudWatch Architecture")
    common.mermaid(create_cloudwatch_architecture_mermaid(), height=500)
    
    # Interactive CloudWatch Metrics Explorer
    st.markdown("### 📊 Interactive CloudWatch Metrics Explorer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        service_type = st.selectbox("AWS Service:", [
            "Amazon EC2", "Amazon RDS", "AWS Lambda", "Application Load Balancer",
            "Amazon S3", "Amazon DynamoDB", "Amazon ECS", "Amazon EKS"
        ])
        
        metric_name = st.selectbox("Metric:", {
            "Amazon EC2": ["CPUUtilization", "NetworkIn", "NetworkOut", "DiskReadBytes"],
            "Amazon RDS": ["CPUUtilization", "DatabaseConnections", "ReadLatency", "WriteLatency"],
            "AWS Lambda": ["Duration", "Invocations", "Errors", "Throttles"],
            "Application Load Balancer": ["RequestCount", "TargetResponseTime", "HTTPCode_Target_2XX_Count"],
            "Amazon S3": ["BucketRequests", "BucketBytes", "4xxErrors", "5xxErrors"],
            "Amazon DynamoDB": ["ConsumedReadCapacityUnits", "ConsumedWriteCapacityUnits", "ThrottledRequests"],
            "Amazon ECS": ["CPUUtilization", "MemoryUtilization", "RunningTaskCount"],
            "Amazon EKS": ["cluster_cpu_utilization", "cluster_memory_utilization", "cluster_node_count"]
        }.get(service_type, ["CPUUtilization"]))
    
    with col2:
        time_range = st.selectbox("Time Range:", [
            "Last 1 hour", "Last 24 hours", "Last 7 days", "Last 30 days"
        ])
        
        statistic = st.selectbox("Statistic:", [
            "Average", "Maximum", "Minimum", "Sum", "SampleCount"
        ])
        
        period = st.selectbox("Period:", ["1 minute", "5 minutes", "15 minutes", "1 hour"])
    
    if st.button("📊 Generate CloudWatch Metrics", use_container_width=True):
        # Generate sample metrics data
        hours = {"Last 1 hour": 1, "Last 24 hours": 24, "Last 7 days": 168, "Last 30 days": 720}[time_range]
        periods = {"1 minute": 1, "5 minutes": 5, "15 minutes": 15, "1 hour": 60}[period]
        
        # Generate time series data
        timestamps = pd.date_range(
            end=datetime.now(), 
            periods=min(hours * 60 // periods, 288),  # Limit to 288 points
            freq=f'{periods}min'
        )
        
        # Generate realistic metric values based on service and metric
        if metric_name == "CPUUtilization":
            base_value = 45
            values = [max(0, min(100, base_value + np.random.normal(0, 15))) for _ in timestamps]
        elif "Duration" in metric_name:
            base_value = 250
            values = [max(0, base_value + np.random.normal(0, 50)) for _ in timestamps]
        elif "RequestCount" in metric_name or "Invocations" in metric_name:
            base_value = 1000
            values = [max(0, base_value + np.random.normal(0, 200)) for _ in timestamps]
        else:
            base_value = 50
            values = [max(0, base_value + np.random.normal(0, 10)) for _ in timestamps]
        
        # Create the plot
        fig = px.line(
            x=timestamps, 
            y=values,
            title=f'{service_type} - {metric_name} ({statistic})',
            labels={'x': 'Time', 'y': metric_name}
        )
        
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_color=AWS_COLORS['secondary']
        )
        
        fig.update_traces(line_color=AWS_COLORS['primary'])
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Metrics Summary
        current_value = values[-1] if values else 0
        avg_value = np.mean(values) if values else 0
        max_value = np.max(values) if values else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Value", f"{current_value:.2f}", f"{current_value - avg_value:.2f}")
        
        with col2:
            st.metric("Average", f"{avg_value:.2f}")
        
        with col3:
            st.metric("Peak Value", f"{max_value:.2f}")
    
    # CloudWatch Logs
    st.markdown("### 📋 CloudWatch Logs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔍 Key Concepts
        
        **Log Event**: A record of activity by application or resource
        
        **Log Stream**: Sequence of log events from the same source
        
        **Log Group**: Collection of log streams with same retention, monitoring, and access control
        
        **Retention Settings**: How long log events are kept (1 day to never expire)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📊 Log Sources
        
        CloudWatch Logs can collect from **30+ AWS services**:
        - **Amazon EC2** instances (via CloudWatch agent)
        - **VPC Flow Logs** (network traffic)
        - **AWS CloudTrail** (API calls)
        - **AWS Lambda** functions
        - **On-premises servers** (via unified agent)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Log Entry Generator
    st.markdown("### 📝 Interactive Log Entry Generator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        log_source = st.selectbox("Log Source:", [
            "EC2 Instance", "Lambda Function", "VPC Flow Logs", 
            "Application Load Balancer", "Custom Application"
        ])
        
        log_level = st.selectbox("Log Level:", ["INFO", "WARN", "ERROR", "DEBUG"])
    
    with col2:
        instance_id = st.text_input("Instance/Resource ID:", "i-1234567890abcdef0")
        custom_message = st.text_input("Custom Message:", "User authentication successful")
    
    if st.button("📝 Generate Log Entries", use_container_width=True):
        # Generate sample log entries
        timestamp = datetime.now()
        
        log_entries = []
        
        for i in range(5):
            entry_time = timestamp - timedelta(minutes=i * 2)
            
            if log_source == "EC2 Instance":
                log_entry = f"[{entry_time.strftime('%Y-%m-%d %H:%M:%S')}] [{log_level}] EC2-Instance {instance_id}: {custom_message}"
            elif log_source == "Lambda Function":
                log_entry = f"[{entry_time.strftime('%Y-%m-%d %H:%M:%S')}] [{log_level}] LAMBDA RequestId: {instance_id} Duration: {np.random.randint(100, 1000)}ms Memory: {np.random.randint(64, 256)}MB {custom_message}"
            elif log_source == "VPC Flow Logs":
                log_entry = f"{entry_time.strftime('%Y-%m-%d %H:%M:%S')} eni-{instance_id[-10:]} 10.0.1.{np.random.randint(1, 254)} 203.0.113.{np.random.randint(1, 254)} 443 {np.random.randint(30000, 65000)} 6 {np.random.randint(1, 20)} {np.random.randint(1000, 5000)} ACCEPT OK"
            else:
                log_entry = f"[{entry_time.strftime('%Y-%m-%d %H:%M:%S')}] [{log_level}] {log_source}: {custom_message}"
            
            log_entries.append(log_entry)
        
        st.markdown('<div class="log-entry">', unsafe_allow_html=True)
        for entry in log_entries:
            st.text(entry)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # CloudWatch Alarms
    st.markdown("### 🚨 CloudWatch Alarms")
    
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 CloudWatch Alarms Features
    
    **High Resolution Alarms**: Monitor metrics with 1-second granularity
    
    **Actions Supported**:
    - Send notification to **SNS topic**
    - **Auto Scaling** actions (scale out/in)
    - **EC2 actions** (stop, terminate, reboot, recover)
    
    **Alarm States**: OK, ALARM, INSUFFICIENT_DATA
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Alarm Builder
    st.markdown("### ⚙️ Interactive CloudWatch Alarm Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        alarm_metric = st.selectbox("Select Metric to Monitor:", [
            "EC2 CPU Utilization", "RDS CPU Utilization", "Lambda Error Rate",
            "ALB Request Count", "S3 4XX Errors", "DynamoDB Throttled Requests"
        ])
        
        threshold_value = st.number_input("Threshold Value:", 0.0, 100.0, 80.0)
        comparison = st.selectbox("Comparison:", [
            "GreaterThanThreshold", "LessThanThreshold", 
            "GreaterThanOrEqualToThreshold", "LessThanOrEqualToThreshold"
        ])
    
    with col2:
        evaluation_periods = st.slider("Evaluation Periods:", 1, 10, 2)
        period_minutes = st.selectbox("Period:", [1, 5, 15, 30, 60])
        
        alarm_actions = st.multiselect("Alarm Actions:", [
            "Send SNS Notification", "Auto Scaling Action", "EC2 Action", "Lambda Function"
        ])
    
    if st.button("🚨 Create CloudWatch Alarm", use_container_width=True):
        alarm_name = f"{alarm_metric.replace(' ', '')}_Alarm_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        st.markdown('<div class="alarm-card">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ CloudWatch Alarm Created!
        
        **Alarm Configuration:**
        - **Name**: {alarm_name}
        - **Metric**: {alarm_metric}
        - **Threshold**: {comparison} {threshold_value}
        - **Evaluation**: {evaluation_periods} periods of {period_minutes} minutes
        
        **Actions When ALARM State:**
        {chr(10).join(f"- {action}" for action in alarm_actions)}
        
        **Estimated Cost**: $0.10/month per alarm
        ⏱️ **Monitoring**: Every {period_minutes} minute(s)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # CloudWatch Dashboards
    st.markdown("### 📊 CloudWatch Dashboards")
    
    # Sample dashboard metrics
    dashboard_data = {
        'Widget Type': ['Line Graph', 'Number', 'Bar Chart', 'Log Insights', 'Alarm Status'],
        'Best For': [
            'Time-series metrics over time',
            'Current metric values',
            'Comparing multiple metrics',
            'Log query results',
            'Quick status overview'
        ],
        'Example Use Case': [
            'CPU utilization trends',
            'Current active connections',
            'Error rates by service',
            'Recent application logs',
            'Infrastructure health status'
        ],
        'Refresh Rate': ['1 minute', 'Real-time', '5 minutes', '1 minute', 'Real-time']
    }
    
    df_dashboard = pd.DataFrame(dashboard_data)
    st.dataframe(df_dashboard, use_container_width=True)
    
    # Monitoring Scenario Demonstration
    st.markdown("### 🔄 Real-World Monitoring Scenario")
    common.mermaid(create_monitoring_flow_mermaid(), height=800)
    
    # CloudWatch Pricing Calculator
    st.markdown("### 💰 CloudWatch Pricing Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        custom_metrics = st.slider("Custom Metrics per Month:", 0, 10000, 1000)
        api_requests = st.slider("API Requests (thousands):", 0, 1000, 100)
        dashboard_count = st.slider("Number of Dashboards:", 0, 50, 5)
    
    with col2:
        log_ingestion_gb = st.slider("Log Ingestion (GB/month):", 0, 1000, 100)
        log_storage_gb = st.slider("Log Storage (GB):", 0, 5000, 500)
        alarms_count = st.slider("Number of Alarms:", 0, 1000, 50)
    
    if st.button("💰 Calculate CloudWatch Costs", use_container_width=True):
        # CloudWatch pricing (US East 1)
        metrics_cost = max(0, custom_metrics - 10) * 0.30  # First 10 free
        api_cost = max(0, (api_requests * 1000) - 1_000_000) * 0.01 / 1000  # First 1M free
        dashboard_cost = max(0, dashboard_count - 3) * 3.00  # First 3 free
        
        log_ingestion_cost = log_ingestion_gb * 0.50
        log_storage_cost = log_storage_gb * 0.03
        alarms_cost = max(0, alarms_count - 10) * 0.10  # First 10 free
        
        total_cost = metrics_cost + api_cost + dashboard_cost + log_ingestion_cost + log_storage_cost + alarms_cost
        
        # Display cost breakdown
        cost_data = {
            'Component': ['Custom Metrics', 'API Requests', 'Dashboards', 'Log Ingestion', 'Log Storage', 'Alarms'],
            'Quantity': [custom_metrics, f"{api_requests}K", dashboard_count, f"{log_ingestion_gb} GB", f"{log_storage_gb} GB", alarms_count],
            'Monthly Cost': [f"${metrics_cost:.2f}", f"${api_cost:.2f}", f"${dashboard_cost:.2f}", 
                           f"${log_ingestion_cost:.2f}", f"${log_storage_cost:.2f}", f"${alarms_cost:.2f}"]
        }
        
        df_costs = pd.DataFrame(cost_data)
        st.dataframe(df_costs, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Monthly Cost", f"${total_cost:.2f}")
        with col2:
            st.metric("Annual Cost", f"${total_cost * 12:.2f}")
    
    # Code Example
    st.markdown("### 💻 Code Example: Complete CloudWatch Setup")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Complete CloudWatch monitoring setup with alarms and dashboards
import boto3
import json
from datetime import datetime, timedelta

def setup_comprehensive_monitoring():
    """Set up comprehensive CloudWatch monitoring for an application"""
    
    cloudwatch = boto3.client('cloudwatch')
    logs = boto3.client('logs')
    sns = boto3.client('sns')
    
    print("🚀 Setting up comprehensive CloudWatch monitoring...")
    
    # Create SNS topic for alerts
    topic_response = sns.create_topic(Name='monitoring-alerts')
    topic_arn = topic_response['TopicArn']
    print(f"✅ Created SNS topic: {topic_arn}")
    
    # Subscribe email to topic
    sns.subscribe(
        TopicArn=topic_arn,
        Protocol='email',
        Endpoint='admin@company.com'
    )
    
    # Create log group for application logs
    log_group_name = '/aws/application/webapp'
    
    try:
        logs.create_log_group(
            logGroupName=log_group_name,
            retentionInDays=30  # Retain logs for 30 days
        )
        print(f"✅ Created log group: {log_group_name}")
    except logs.exceptions.ResourceAlreadyExistsException:
        print(f"ℹ️  Log group already exists: {log_group_name}")
    
    # Create metric filter for application errors
    logs.put_metric_filter(
        logGroupName=log_group_name,
        filterName='ApplicationErrors',
        filterPattern='[timestamp, request_id, level="ERROR", ...]',
        metricTransformations=[
            {
                'metricName': 'ApplicationErrors',
                'metricNamespace': 'Application/WebApp',
                'metricValue': '1',
                'defaultValue': 0
            }
        ]
    )
    print("✅ Created metric filter for application errors")
    
    # Define alarms to create
    alarms = [
        {
            'name': 'HighCPUUtilization',
            'metric_name': 'CPUUtilization',
            'namespace': 'AWS/EC2',
            'threshold': 80,
            'comparison': 'GreaterThanThreshold',
            'description': 'Alert when EC2 CPU > 80%'
        },
        {
            'name': 'ApplicationErrorRate',
            'metric_name': 'ApplicationErrors',
            'namespace': 'Application/WebApp',
            'threshold': 5,
            'comparison': 'GreaterThanThreshold',
            'description': 'Alert when application errors > 5 per period'
        },
        {
            'name': 'DatabaseConnections',
            'metric_name': 'DatabaseConnections',
            'namespace': 'AWS/RDS',
            'threshold': 80,
            'comparison': 'GreaterThanThreshold',
            'description': 'Alert when DB connections > 80'
        }
    ]
    
    # Create alarms
    for alarm in alarms:
        try:
            cloudwatch.put_metric_alarm(
                AlarmName=alarm['name'],
                ComparisonOperator=alarm['comparison'],
                EvaluationPeriods=2,
                MetricName=alarm['metric_name'],
                Namespace=alarm['namespace'],
                Period=300,  # 5 minutes
                Statistic='Average',
                Threshold=alarm['threshold'],
                ActionsEnabled=True,
                AlarmActions=[topic_arn],
                AlarmDescription=alarm['description'],
                Unit='Percent' if 'CPU' in alarm['metric_name'] else 'Count'
            )
            print(f"✅ Created alarm: {alarm['name']}")
            
        except Exception as e:
            print(f"❌ Error creating alarm {alarm['name']}: {e}")
    
    # Create custom dashboard
    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "x": 0, "y": 0,
                "width": 12, "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/EC2", "CPUUtilization", "InstanceId", "i-1234567890abcdef0"],
                        ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "myapp-database"],
                        ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", "app/my-load-balancer/50dc6c495c0c9188"]
                    ],
                    "period": 300,
                    "stat": "Average",
                    "region": "us-east-1",
                    "title": "System Performance Overview"
                }
            },
            {
                "type": "metric",
                "x": 0, "y": 6,
                "width": 6, "height": 6,
                "properties": {
                    "metrics": [
                        ["Application/WebApp", "ApplicationErrors"]
                    ],
                    "period": 300,
                    "stat": "Sum",
                    "region": "us-east-1",
                    "title": "Application Errors"
                }
            },
            {
                "type": "log",
                "x": 6, "y": 6,
                "width": 6, "height": 6,
                "properties": {
                    "query": f"SOURCE '{log_group_name}' | fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 20",
                    "region": "us-east-1",
                    "title": "Recent Error Logs",
                    "view": "table"
                }
            }
        ]
    }
    
    try:
        cloudwatch.put_dashboard(
            DashboardName='ApplicationMonitoring',
            DashboardBody=json.dumps(dashboard_body)
        )
        print("✅ Created CloudWatch dashboard: ApplicationMonitoring")
    
    except Exception as e:
        print(f"❌ Error creating dashboard: {e}")
    
    return {
        'topic_arn': topic_arn,
        'log_group': log_group_name,
        'dashboard_url': 'https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=ApplicationMonitoring'
    }

def send_custom_metrics():
    """Send custom application metrics to CloudWatch"""
    cloudwatch = boto3.client('cloudwatch')
    
    # Example: Send business metrics
    try:
        # User registration metric
        cloudwatch.put_metric_data(
            Namespace='Application/WebApp',
            MetricData=[
                {
                    'MetricName': 'UserRegistrations',
                    'Value': 15,
                    'Unit': 'Count',
                    'Timestamp': datetime.utcnow()
                },
                {
                    'MetricName': 'ActiveUsers',
                    'Value': 1250,
                    'Unit': 'Count',
                    'Timestamp': datetime.utcnow()
                },
                {
                    'MetricName': 'ResponseTime',
                    'Value': 245.5,
                    'Unit': 'Milliseconds',
                    'Timestamp': datetime.utcnow(),
                    'Dimensions': [
                        {
                            'Name': 'Environment',
                            'Value': 'Production'
                        },
                        {
                            'Name': 'Service',
                            'Value': 'UserAPI'
                        }
                    ]
                }
            ]
        )
        
        print("✅ Custom metrics sent to CloudWatch")
        
    except Exception as e:
        print(f"❌ Error sending custom metrics: {e}")

def query_cloudwatch_insights(log_group_name, hours_back=24):
    """Query CloudWatch Logs Insights for analysis"""
    logs = boto3.client('logs')
    
    # Calculate time range
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours_back)
    
    # Example queries
    queries = [
        {
            'name': 'Error Analysis',
            'query': 'fields @timestamp, @message | filter @message like /ERROR/ | stats count() by bin(5m)'
        },
        {
            'name': 'Top Error Messages',
            'query': 'fields @message | filter @message like /ERROR/ | stats count() by @message | sort count desc | limit 10'
        },
        {
            'name': 'Response Time Analysis',
            'query': 'fields @timestamp, @message | filter @message like /response_time/ | parse @message "response_time=*ms" as response_time | stats avg(response_time), max(response_time), min(response_time) by bin(5m)'
        }
    ]
    
    results = {}
    
    for query_info in queries:
        try:
            print(f"🔍 Running query: {query_info['name']}")
            
            response = logs.start_query(
                logGroupName=log_group_name,
                startTime=int(start_time.timestamp()),
                endTime=int(end_time.timestamp()),
                queryString=query_info['query']
            )
            
            query_id = response['queryId']
            
            # Wait for query to complete (simplified - in practice, you'd poll)
            import time
            time.sleep(5)
            
            results_response = logs.get_query_results(queryId=query_id)
            results[query_info['name']] = results_response.get('results', [])
            
            print(f"✅ Query completed: {len(results[query_info['name']])} results")
            
        except Exception as e:
            print(f"❌ Error running query {query_info['name']}: {e}")
    
    return results

# Example usage
print("🚀 Setting up comprehensive monitoring...")
setup_result = setup_comprehensive_monitoring()

if setup_result:
    print(f"\n📋 Setup Complete!")
    print(f"  SNS Topic: {setup_result['topic_arn']}")
    print(f"  Log Group: {setup_result['log_group']}")
    print(f"  Dashboard: {setup_result['dashboard_url']}")
    
    # Send some custom metrics
    send_custom_metrics()
    
    # Query recent logs
    insights_results = query_cloudwatch_insights(setup_result['log_group'])
    
    print(f"\n📊 Log Insights Results:")
    for query_name, results in insights_results.items():
        print(f"  {query_name}: {len(results)} results found")
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
    # 📊 AWS Monitoring Tools
    
    """)
    st.markdown("""<div class="info-box">
                Master AWS monitoring and logging capabilities with CloudTrail for auditing and CloudWatch for comprehensive observability. Learn to implement real-time monitoring, automated alerting, and log analysis for production AWS environments.
                </div>""", unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2 = st.tabs([
        "🔍 AWS CloudTrail", 
        "📊 Amazon CloudWatch"
    ])
    
    with tab1:
        cloudtrail_tab()
    
    with tab2:
        cloudwatch_tab()
    
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
