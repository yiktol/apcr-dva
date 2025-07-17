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
    page_title="AWS S3 Storage Solutions Hub",
    page_icon="🗂️",
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
        
        .s3-bucket {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            border: 2px solid {AWS_COLORS['light_blue']};
            margin: 15px 0;
        }}
        
        .storage-tier {{
            background: linear-gradient(135deg, {AWS_COLORS['success']} 0%, {AWS_COLORS['primary']} 100%);
            padding: 15px;
            border-radius: 10px;
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
            - 🗂️ Amazon S3 - Object storage fundamentals
            - 📊 Storage Classes - Cost-optimized tiers
            - 🔄 Lifecycle Management - Automated transitions
            - 🔒 Bucket Policies - Access control and security
            
            **Learning Objectives:**
            - Understand S3 object storage architecture
            - Learn about storage classes and cost optimization
            - Master lifecycle policies for data management
            - Implement secure bucket policies and access controls
            """)

def create_s3_architecture_mermaid():
    """Create mermaid diagram for S3 architecture"""
    return """
    graph TB
        subgraph "AWS S3 Service"
            B1[S3 Bucket 1]
            B2[S3 Bucket 2]
            B3[S3 Bucket 3]
        end
        
        subgraph "Object Components"
            O1[Object Key]
            O2[Object Data]
            O3[Metadata]
            O4[Version ID]
        end
        
        subgraph "Access Methods"
            API[REST API]
            SDK[AWS SDKs]
            CLI[AWS CLI]
            WEB[Web Console]
        end
        
        U[👤 Users/Applications] --> API
        U --> SDK
        U --> CLI
        U --> WEB
        
        API --> B1
        SDK --> B2
        CLI --> B3
        WEB --> B1
        
        B1 --> O1
        B1 --> O2
        B1 --> O3
        B1 --> O4
        
        style B1 fill:#FF9900,stroke:#232F3E,color:#fff
        style B2 fill:#FF9900,stroke:#232F3E,color:#fff
        style B3 fill:#FF9900,stroke:#232F3E,color:#fff
        style U fill:#4B9EDB,stroke:#232F3E,color:#fff
    """

def create_storage_classes_flow_mermaid():
    """Create mermaid diagram for storage classes flow"""
    return """
    graph TD
        A[Data Upload] --> B{Access Frequency?}
        B -->|Frequent| C[S3 Standard]
        B -->|Unknown| D[S3 Intelligent-Tiering]
        B -->|Infrequent| E[S3 Standard-IA]
        B -->|Rarely| F[S3 One Zone-IA]
        
        C --> G{Long-term Archive?}
        E --> G
        F --> G
        G -->|Yes| H[S3 Glacier Instant Retrieval]
        H --> I[S3 Glacier Flexible Retrieval]
        I --> J[S3 Glacier Deep Archive]
        
        D --> K[Auto-Tiering Based on Access]
        K --> C
        K --> E
        K --> H
        
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#FF9900,stroke:#232F3E,color:#fff
        style E fill:#4B9EDB,stroke:#232F3E,color:#fff
        style F fill:#FF6B35,stroke:#232F3E,color:#fff
        style H fill:#232F3E,stroke:#FF9900,color:#fff
        style I fill:#1B2631,stroke:#FF9900,color:#fff
        style J fill:#000000,stroke:#FF9900,color:#fff
    """

def create_lifecycle_flow_mermaid():
    """Create mermaid diagram for lifecycle management"""
    return """
    graph LR
        A[Object Created] --> B[S3 Standard]
        B -->|30 days| C[S3 Standard-IA]
        C -->|90 days| D[S3 Glacier Instant Retrieval]
        D -->|180 days| E[S3 Glacier Flexible Retrieval] 
        E -->|365 days| F[S3 Glacier Deep Archive]
        F -->|7 years| G[🗑️ Delete]
        
        subgraph "Lifecycle Rules"
            H[Transition Rules]
            I[Expiration Rules]
            J[Incomplete Multipart Upload Cleanup]
        end
        
        H --> C
        H --> D
        H --> E
        H --> F
        I --> G
        
        style B fill:#3FB34F,stroke:#232F3E,color:#fff
        style C fill:#4B9EDB,stroke:#232F3E,color:#fff
        style D fill:#FF9900,stroke:#232F3E,color:#fff
        style E fill:#232F3E,stroke:#FF9900,color:#fff
        style F fill:#1B2631,stroke:#FF9900,color:#fff
        style G fill:#FF6B35,stroke:#232F3E,color:#fff
    """

def create_bucket_policy_flow_mermaid():
    """Create mermaid diagram for bucket policy flow"""
    return """
    graph TB
        A[Request to S3 Bucket] --> B{IAM Policy Check}
        B -->|Deny| C[❌ Access Denied]
        B -->|Allow/No Policy| D{Bucket Policy Check}
        
        D -->|Explicit Deny| C
        D -->|Allow| E[✅ Access Granted]
        D -->|No Policy| F{ACL Check}
        
        F -->|Deny| C
        F -->|Allow| E
        
        subgraph "Policy Elements"
            G[Principal]
            H[Action]
            I[Resource]
            J[Condition]
        end
        
        D --> G
        D --> H
        D --> I
        D --> J
        
        style E fill:#3FB34F,stroke:#232F3E,color:#fff
        style C fill:#FF6B35,stroke:#232F3E,color:#fff
        style D fill:#FF9900,stroke:#232F3E,color:#fff
    """

def s3_overview_tab():
    """Content for Amazon S3 Overview tab"""
    st.markdown("## 🗂️ Amazon Simple Storage Service (S3)")
    st.markdown("*Provides infinitely scalable, highly durable object storage in the AWS Cloud*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Amazon S3** is an object storage service that offers industry-leading scalability, data availability, 
    security, and performance. It manages data as **objects** rather than in a file system or data block system.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # S3 Architecture
    st.markdown("### 🏗️ S3 Architecture Overview")
    common.mermaid(create_s3_architecture_mermaid(), height=400)
    
    # Core S3 Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 99.999999999%\n**(11 9's)**\n**Durability**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 99.99%\n**Availability**\n**SLA**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### Unlimited\n**Storage**\n**Capacity**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 5TB\n**Max Object**\n**Size**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive S3 Bucket Creator
    st.markdown("### 🛠️ Interactive S3 Bucket Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🗂️ Bucket Configuration")
        bucket_name = st.text_input("Bucket Name:", "my-awesome-bucket-2025")
        region = st.selectbox("AWS Region:", [
            "us-east-1 (N. Virginia)", "us-west-2 (Oregon)", 
            "eu-west-1 (Ireland)", "ap-southeast-1 (Singapore)"
        ])
        
        versioning = st.checkbox("Enable Versioning", value=True)
        encryption = st.selectbox("Default Encryption:", [
            "AES-256 (SSE-S3)", "AWS KMS (SSE-KMS)", "Customer Provided (SSE-C)"
        ])
    
    with col2:
        st.markdown("#### 🔒 Access & Security")
        public_access = st.selectbox("Public Access:", [
            "Block all public access (Recommended)",
            "Allow public read access",
            "Allow public read/write access",
            "Custom configuration"
        ])
        
        logging = st.checkbox("Enable Access Logging", value=False)
        transfer_acceleration = st.checkbox("Enable Transfer Acceleration", value=False)
    
    if st.button("🚀 Create S3 Bucket", use_container_width=True):
        # Calculate estimated monthly cost
        estimated_storage = st.slider("Estimated Monthly Storage (GB):", 1, 10000, 100, key="storage_calc")
        estimated_requests = st.slider("Estimated Monthly Requests (thousands):", 1, 1000, 50, key="requests_calc")
        
        region_code = region.split()[0]
        base_cost = 0.023 if region_code.startswith('us') else 0.025  # Cost per GB
        request_cost = (estimated_requests * 1000 * 0.0004) / 1000  # Cost per 1K requests
        total_cost = (estimated_storage * base_cost) + request_cost
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ S3 Bucket Created Successfully!
        
        **Bucket Details:**
        - **Name**: {bucket_name}
        - **Region**: {region}
        - **ARN**: `arn:aws:s3:::{bucket_name}`
        - **URL**: `https://{bucket_name}.s3.amazonaws.com`
        
        **Configuration:**
        - **Versioning**: {'✅ Enabled' if versioning else '❌ Disabled'}
        - **Encryption**: {encryption}
        - **Public Access**: {public_access}
        - **Transfer Acceleration**: {'✅ Enabled' if transfer_acceleration else '❌ Disabled'}
        
        **💰 Estimated Monthly Cost**: ${total_cost:.2f}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # S3 Object Components
    st.markdown("### 📦 S3 Object Components")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔑 Object Key
        - **Unique identifier** within a bucket
        - Acts like a file path: `folder/subfolder/filename.txt`
        - **Case sensitive** and can be up to 1,024 characters
        - Supports Unicode characters
        
        **Example**: `documents/2025/reports/annual-report.pdf`
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📊 Object Data
        - **Actual file content** being stored
        - Can be any type of data (images, videos, documents, code)
        - **Size range**: 0 bytes to 5 TB per object
        - Stored across multiple facilities for durability
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🏷️ Metadata
        - **Key-value pairs** describing the object
        - System metadata (managed by S3)
        - User-defined metadata (custom headers)
        - **Content-Type**, **Last-Modified**, **ETag**, etc.
        
        **Example**: `Content-Type: application/pdf`
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔢 Version ID
        - **Unique identifier** for object versions
        - Generated when versioning is enabled
        - Allows multiple versions of same object key
        - **null** for objects in non-versioned buckets
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # S3 Use Cases
    st.markdown("### 🌟 Common S3 Use Cases")
    
    use_cases_data = {
        'Use Case': [
            'Static Website Hosting',
            'Data Backup & Archive',
            'Data Lake Storage',
            'Content Distribution',
            'Application Data Storage',
            'Disaster Recovery'
        ],
        'Storage Class': [
            'S3 Standard',
            'S3 Glacier Deep Archive',
            'S3 Intelligent-Tiering',
            'S3 Standard + CloudFront',
            'S3 Standard-IA',
            'S3 Standard + Cross-Region Replication'
        ],
        'Key Benefits': [
            'Low latency, high throughput',
            'Lowest cost for long-term storage',
            'Automatic cost optimization',
            'Global content delivery',
            'Cost-effective for infrequent access',
            'Geographic redundancy'
        ],
        'Typical Size': [
            '1GB - 100GB',
            '100GB - 100TB+',
            '1TB - 1PB+',
            '10GB - 1TB',
            '100MB - 10TB',
            '1GB - 100TB'
        ]
    }
    
    df_use_cases = pd.DataFrame(use_cases_data)
    st.dataframe(df_use_cases, use_container_width=True)
    
    # Interactive Object Upload Simulator
    st.markdown("### 📤 Interactive Object Upload Simulator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        file_type = st.selectbox("File Type:", [
            "Image (JPEG/PNG)", "Document (PDF)", "Video (MP4)", 
            "Archive (ZIP)", "Code (Python)", "Data (JSON/CSV)"
        ])
        
        file_size = st.slider("File Size (MB):", 0.1, 5000.0, 10.0)
        upload_method = st.selectbox("Upload Method:", [
            "Single PUT (< 5GB)", "Multipart Upload (> 100MB)", "Transfer Acceleration"
        ])
    
    with col2:
        storage_class = st.selectbox("Initial Storage Class:", [
            "S3 Standard", "S3 Standard-IA", "S3 One Zone-IA", 
            "S3 Intelligent-Tiering", "S3 Glacier Instant Retrieval"
        ])
        
        metadata_tags = st.text_area("Custom Metadata (key=value):", 
                                   "project=web-app\nenvironment=production\nowner=dev-team")
    
    if st.button("📤 Simulate Upload", use_container_width=True):
        # Calculate upload metrics
        if file_size < 100:
            upload_time = file_size * 0.1  # Fast upload for small files
        elif upload_method == "Multipart Upload (> 100MB)":
            upload_time = file_size * 0.05  # Faster with multipart
        else:
            upload_time = file_size * 0.08
        
        # Storage cost calculation
        storage_costs = {
            "S3 Standard": 0.023,
            "S3 Standard-IA": 0.0125,
            "S3 One Zone-IA": 0.01,
            "S3 Intelligent-Tiering": 0.023,
            "S3 Glacier Instant Retrieval": 0.004
        }
        
        monthly_cost = (file_size / 1024) * storage_costs.get(storage_class, 0.023)
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ Upload Completed Successfully!
        
        **File Details:**
        - **Type**: {file_type}
        - **Size**: {file_size:.1f} MB
        - **Storage Class**: {storage_class}
        - **Upload Method**: {upload_method}
        
        **Performance Metrics:**
        - **Upload Time**: {upload_time:.1f} seconds
        - **Throughput**: {(file_size/upload_time):.1f} MB/s
        - **Parts Used**: {max(1, int(file_size/100))} (for multipart)
        
        **💰 Storage Cost**: ${monthly_cost:.4f}/month
        
        **📋 Object Metadata Created**:
        ```
        {metadata_tags}
        ```
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Working with S3 Objects")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Working with Amazon S3 objects using boto3
import boto3
import json
from datetime import datetime
import os

def create_s3_bucket_with_configuration(bucket_name, region='us-east-1'):
    """Create an S3 bucket with best practice configuration"""
    s3_client = boto3.client('s3', region_name=region)
    
    try:
        # Create bucket
        if region == 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        
        # Enable versioning
        s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        
        # Enable default encryption
        s3_client.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration={
                'Rules': [
                    {
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        }
                    }
                ]
            }
        )
        
        # Block public access (security best practice)
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        
        print(f"✅ Bucket '{bucket_name}' created successfully in {region}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating bucket: {e}")
        return False

def upload_file_with_metadata(bucket_name, file_path, s3_key, metadata=None):
    """Upload file to S3 with custom metadata"""
    s3_client = boto3.client('s3')
    
    # Default metadata
    default_metadata = {
        'uploaded-by': 'python-script',
        'upload-timestamp': datetime.utcnow().isoformat(),
        'file-size': str(os.path.getsize(file_path))
    }
    
    # Merge with custom metadata
    if metadata:
        default_metadata.update(metadata)
    
    try:
        # Upload file with metadata
        s3_client.upload_file(
            file_path,
            bucket_name,
            s3_key,
            ExtraArgs={
                'Metadata': default_metadata,
                'StorageClass': 'STANDARD',  # Can be changed based on use case
                'ServerSideEncryption': 'AES256'
            }
        )
        
        print(f"✅ File uploaded successfully to s3://{bucket_name}/{s3_key}")
        
        # Get object metadata for verification
        response = s3_client.head_object(Bucket=bucket_name, Key=s3_key)
        print(f"📊 Object Metadata: {response['Metadata']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        return False

def multipart_upload_large_file(bucket_name, file_path, s3_key, part_size=100*1024*1024):
    """Upload large files using multipart upload"""
    s3_client = boto3.client('s3')
    
    try:
        # Initialize multipart upload
        response = s3_client.create_multipart_upload(
            Bucket=bucket_name,
            Key=s3_key,
            ServerSideEncryption='AES256',
            Metadata={
                'multipart-upload': 'true',
                'upload-timestamp': datetime.utcnow().isoformat()
            }
        )
        
        upload_id = response['UploadId']
        parts = []
        
        # Upload parts
        with open(file_path, 'rb') as file:
            part_number = 1
            
            while True:
                data = file.read(part_size)
                if not data:
                    break
                
                print(f"📤 Uploading part {part_number}...")
                
                part_response = s3_client.upload_part(
                    Bucket=bucket_name,
                    Key=s3_key,
                    PartNumber=part_number,
                    UploadId=upload_id,
                    Body=data
                )
                
                parts.append({
                    'ETag': part_response['ETag'],
                    'PartNumber': part_number
                })
                
                part_number += 1
        
        # Complete multipart upload
        s3_client.complete_multipart_upload(
            Bucket=bucket_name,
            Key=s3_key,
            UploadId=upload_id,
            MultipartUpload={'Parts': parts}
        )
        
        print(f"✅ Multipart upload completed for {s3_key}")
        print(f"📊 Total parts uploaded: {len(parts)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in multipart upload: {e}")
        # Abort the multipart upload to avoid charges
        try:
            s3_client.abort_multipart_upload(
                Bucket=bucket_name,
                Key=s3_key,
                UploadId=upload_id
            )
        except:
            pass
        return False

def manage_object_versions(bucket_name, object_key):
    """List and manage object versions"""
    s3_client = boto3.client('s3')
    
    try:
        # List all versions of an object
        response = s3_client.list_object_versions(
            Bucket=bucket_name,
            Prefix=object_key
        )
        
        versions = response.get('Versions', [])
        print(f"📋 Found {len(versions)} versions for {object_key}:")
        
        for version in versions:
            print(f"  Version ID: {version['VersionId']}")
            print(f"  Last Modified: {version['LastModified']}")
            print(f"  Size: {version['Size']} bytes")
            print(f"  Storage Class: {version['StorageClass']}")
            print("  " + "-" * 40)
        
        # Get specific version
        if versions:
            latest_version = versions[0]
            version_response = s3_client.get_object(
                Bucket=bucket_name,
                Key=object_key,
                VersionId=latest_version['VersionId']
            )
            
            print(f"📄 Latest version metadata:")
            print(f"  Content Type: {version_response['ContentType']}")
            print(f"  ETag: {version_response['ETag']}")
            print(f"  Metadata: {version_response.get('Metadata', {})}")
        
        return versions
        
    except Exception as e:
        print(f"❌ Error managing versions: {e}")
        return []

# Example usage
bucket_name = "my-data-bucket-2025"
region = "us-east-1"

# Create bucket with configuration
if create_s3_bucket_with_configuration(bucket_name, region):
    
    # Upload a small file with metadata
    custom_metadata = {
        'project': 'data-analysis',
        'department': 'engineering',
        'classification': 'internal'
    }
    
    upload_file_with_metadata(
        bucket_name,
        'local-file.txt',
        'data/processed/report.txt',
        custom_metadata
    )
    
    # For large files, use multipart upload
    # multipart_upload_large_file(bucket_name, 'large-file.zip', 'archives/backup.zip')
    
    # Manage object versions
    manage_object_versions(bucket_name, 'data/processed/report.txt')
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def storage_classes_tab():
    """Content for S3 Storage Classes tab"""
    st.markdown("## 📊 Amazon S3 Storage Classes")
    st.markdown("*Choose the right storage class for your data access patterns and cost requirements*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    S3 offers **multiple storage classes** designed for different use cases with varying levels of access frequency, 
    durability requirements, and cost optimization. Each class is engineered to provide the lowest cost storage for different access patterns.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Storage Classes Flow
    st.markdown("### 🔄 Storage Class Selection Flow")
    common.mermaid(create_storage_classes_flow_mermaid(), height=400)
    
    # Interactive Storage Class Selector
    st.markdown("### 🎯 Interactive Storage Class Advisor")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Data Characteristics")
        access_frequency = st.selectbox("How often will you access this data?", [
            "Multiple times per day (Frequent)",
            "Once per week or month (Infrequent)", 
            "Few times per year (Rare)",
            "Once or twice per year (Very Rare)",
            "Unknown/Variable access pattern"
        ])
        
        data_size = st.slider("Total Data Size (GB):", 1, 100000, 1000)
        retrieval_time = st.selectbox("Acceptable retrieval time:", [
            "Immediate (milliseconds)",
            "Fast (1-5 minutes)",
            "Standard (3-5 hours)", 
            "Bulk (5-12 hours)",
            "Very patient (12+ hours)"
        ])
    
    with col2:
        st.markdown("#### 💰 Cost Preferences")
        cost_priority = st.selectbox("Primary cost concern:", [
            "Minimize storage costs",
            "Minimize total costs (storage + retrieval)",
            "Balanced approach",
            "Optimize for performance"
        ])
        
        durability_needs = st.selectbox("Durability requirements:", [
            "Standard (99.999999999% - 11 9's)",
            "High availability across AZs",
            "Single AZ acceptable for cost savings"
        ])
    
    if st.button("🔍 Get Storage Class Recommendation", use_container_width=True):
        # Logic for storage class recommendation
        if access_frequency == "Multiple times per day (Frequent)":
            recommended_class = "S3 Standard"
            reason = "Frequent access requires immediate availability"
            monthly_cost = data_size * 0.023
        elif access_frequency == "Unknown/Variable access pattern":
            recommended_class = "S3 Intelligent-Tiering"
            reason = "Automatically optimizes costs based on access patterns"
            monthly_cost = data_size * 0.023  # Starting cost, may decrease
        elif "Infrequent" in access_frequency:
            if "Single AZ" in durability_needs:
                recommended_class = "S3 One Zone-IA"
                monthly_cost = data_size * 0.01
            else:
                recommended_class = "S3 Standard-IA"
                monthly_cost = data_size * 0.0125
            reason = "Cost-effective for infrequently accessed data"
        elif "Few times per year" in access_frequency:
            recommended_class = "S3 Glacier Instant Retrieval"
            reason = "Long-term storage with instant access when needed"
            monthly_cost = data_size * 0.004
        else:  # Very rare access
            if "12+ hours" in retrieval_time:
                recommended_class = "S3 Glacier Deep Archive"
                monthly_cost = data_size * 0.00099
            else:
                recommended_class = "S3 Glacier Flexible Retrieval"
                monthly_cost = data_size * 0.0036
            reason = "Lowest cost for long-term archival"
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 🎯 Recommended Storage Class: **{recommended_class}**
        
        **Why this recommendation?**
        {reason}
        
        **Cost Analysis:**
        - **Monthly Storage Cost**: ${monthly_cost:.2f}
        - **Annual Storage Cost**: ${monthly_cost * 12:.2f}
        - **Cost per GB/month**: ${monthly_cost/data_size:.4f}
        
        **Key Features:**
        - **Access Pattern**: {access_frequency}
        - **Retrieval Time**: {retrieval_time}
        - **Durability**: {durability_needs}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed Storage Classes Comparison
    st.markdown("### 📋 Complete Storage Classes Comparison")
    
    storage_classes_data = {
        'Storage Class': [
            'S3 Standard',
            'S3 Intelligent-Tiering',
            'S3 Express One Zone',
            'S3 Standard-IA',
            'S3 One Zone-IA',
            'S3 Glacier Instant Retrieval',
            'S3 Glacier Flexible Retrieval',
            'S3 Glacier Deep Archive'
        ],
        'Use Case': [
            'Frequently accessed data',
            'Unknown/changing access patterns',
            'High performance, frequently accessed',
            'Infrequently accessed, millisecond access',
            'Re-creatable infrequently accessed data',
            'Long-lived data, accessed few times per year',
            'Backup and archive, rarely accessed',
            'Long-term data archiving, very rarely accessed'
        ],
        'Retrieval Time': [
            'Milliseconds',
            'Milliseconds',
            'Single-digit milliseconds',
            'Milliseconds',
            'Milliseconds',
            'Milliseconds',
            '1 minute to 12 hours',
            'Within 12 hours'
        ],
        'Monthly Cost ($/GB)': [
            '$0.023',
            '$0.023*',
            '$0.16',
            '$0.0125',
            '$0.01',
            '$0.004',
            '$0.0036',
            '$0.00099'
        ],
        'Min Storage Duration': [
            'None',
            '30 days',
            '1 hour',
            '30 days',
            '30 days',
            '90 days',
            '90 days',
            '180 days'
        ]
    }
    
    df_storage = pd.DataFrame(storage_classes_data)
    st.dataframe(df_storage, use_container_width=True)
    
    # Cost Comparison Visualization
    st.markdown("### 💰 Storage Cost Comparison")
    
    # Cost comparison for different data sizes
    data_sizes = [100, 1000, 10000, 100000]  # GB
    storage_costs = {
        'S3 Standard': [size * 0.023 for size in data_sizes],
        'S3 Standard-IA': [size * 0.0125 for size in data_sizes],
        'S3 One Zone-IA': [size * 0.01 for size in data_sizes],
        'S3 Glacier Instant Retrieval': [size * 0.004 for size in data_sizes],
        'S3 Glacier Deep Archive': [size * 0.00099 for size in data_sizes]
    }
    
    fig = go.Figure()
    
    for storage_class, costs in storage_costs.items():
        fig.add_trace(go.Scatter(
            x=data_sizes,
            y=costs,
            mode='lines+markers',
            name=storage_class,
            line=dict(width=3)
        ))
    
    fig.update_layout(
        title='Monthly Storage Costs by Data Size',
        xaxis_title='Data Size (GB)',
        yaxis_title='Monthly Cost ($)',
        xaxis_type='log',
        yaxis_type='log',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Storage Class Features Deep Dive
    st.markdown("### 🔍 Storage Class Features Deep Dive")
    
    selected_class = st.selectbox("Select Storage Class for Details:", [
        "S3 Standard", "S3 Intelligent-Tiering", "S3 Standard-IA", 
        "S3 Glacier Instant Retrieval", "S3 Glacier Deep Archive"
    ])
    
    class_details = {
        "S3 Standard": {
            "description": "General purpose storage for frequently accessed data",
            "durability": "99.999999999% (11 9's)",
            "availability": "99.99%",
            "availability_sla": "99.9%",
            "use_cases": ["Cloud applications", "Dynamic websites", "Content distribution", "Mobile and gaming applications"],
            "performance": "Milliseconds first byte latency and high throughput",
            "features": ["No minimum storage duration", "No retrieval fees", "Lifecycle transitions to any storage class"]
        },
        "S3 Intelligent-Tiering": {
            "description": "Automatic cost savings for data with unknown or changing access patterns",
            "durability": "99.999999999% (11 9's)",
            "availability": "99.9%",
            "availability_sla": "99%",
            "use_cases": ["Data lakes", "Analytics workloads", "New applications", "User-generated content"],
            "performance": "Automatic tiering with no performance impact",
            "features": ["Automatic cost optimization", "No operational overhead", "No lifecycle configuration needed"]
        },
        "S3 Standard-IA": {
            "description": "For data that is accessed less frequently but requires rapid access when needed",
            "durability": "99.999999999% (11 9's)",
            "availability": "99.9%",
            "availability_sla": "99%",
            "use_cases": ["Disaster recovery", "Backups", "Long-term storage"],
            "performance": "Milliseconds first byte latency",
            "features": ["Lower storage price", "Retrieval fees apply", "30-day minimum storage"]
        },
        "S3 Glacier Instant Retrieval": {
            "description": "Archive storage for data accessed once a quarter with instant retrievals",
            "durability": "99.999999999% (11 9's)",
            "availability": "99.9%",
            "availability_sla": "99%",
            "use_cases": ["Medical images", "News media assets", "Genomics data"],
            "performance": "Milliseconds first byte latency for instant access",
            "features": ["68% lower cost than Standard-IA", "90-day minimum storage", "Instant retrieval"]
        },
        "S3 Glacier Deep Archive": {
            "description": "Lowest-cost storage for long-term retention of data accessed once or twice per year",
            "durability": "99.999999999% (11 9's)",
            "availability": "99.9%",
            "availability_sla": "99%",
            "use_cases": ["Compliance archives", "Digital preservation", "Backup and disaster recovery"],
            "performance": "12-hour standard retrieval time",
            "features": ["Lowest cost storage", "180-day minimum storage", "Bulk retrieval options"]
        }
    }
    
    if selected_class in class_details:
        details = class_details[selected_class]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown(f"""
            ### 📊 {selected_class} Details
            
            **Description**: {details['description']}
            
            **Durability**: {details['durability']}
            **Availability**: {details['availability']}
            **Availability SLA**: {details['availability_sla']}
            
            **Performance**: {details['performance']}
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown(f"""
            ### 🎯 Use Cases
            """)
            for use_case in details['use_cases']:
                st.markdown(f"• {use_case}")
            
            st.markdown(f"""
            ### ✨ Key Features
            """)
            for feature in details['features']:
                st.markdown(f"• {feature}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Working with Storage Classes")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Working with S3 Storage Classes
import boto3
from datetime import datetime, timedelta

def upload_with_storage_class(bucket_name, key, file_path, storage_class='STANDARD'):
    """Upload file with specific storage class"""
    s3_client = boto3.client('s3')
    
    try:
        s3_client.upload_file(
            file_path,
            bucket_name,
            key,
            ExtraArgs={
                'StorageClass': storage_class,
                'Metadata': {
                    'upload-date': datetime.utcnow().isoformat(),
                    'storage-class': storage_class
                }
            }
        )
        
        print(f"✅ Uploaded {key} with storage class: {storage_class}")
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

def change_storage_class(bucket_name, key, new_storage_class):
    """Change storage class of existing object"""
    s3_client = boto3.client('s3')
    
    try:
        # Copy object to itself with new storage class
        copy_source = {'Bucket': bucket_name, 'Key': key}
        
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=bucket_name,
            Key=key,
            StorageClass=new_storage_class,
            MetadataDirective='REPLACE',
            Metadata={
                'storage-class-changed': datetime.utcnow().isoformat(),
                'new-storage-class': new_storage_class
            }
        )
        
        print(f"✅ Changed storage class for {key} to {new_storage_class}")
        return True
        
    except Exception as e:
        print(f"❌ Storage class change failed: {e}")
        return False

def analyze_bucket_storage_classes(bucket_name):
    """Analyze storage class usage across bucket"""
    s3_client = boto3.client('s3')
    cloudwatch = boto3.client('cloudwatch')
    
    try:
        # Get bucket inventory
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name)
        
        storage_classes = {}
        total_size = 0
        object_count = 0
        
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    # Get object details
                    response = s3_client.head_object(
                        Bucket=bucket_name,
                        Key=obj['Key']
                    )
                    
                    storage_class = response.get('StorageClass', 'STANDARD')
                    object_size = obj['Size']
                    
                    if storage_class not in storage_classes:
                        storage_classes[storage_class] = {
                            'count': 0,
                            'total_size': 0
                        }
                    
                    storage_classes[storage_class]['count'] += 1
                    storage_classes[storage_class]['total_size'] += object_size
                    total_size += object_size
                    object_count += 1
        
        # Calculate storage costs (approximate)
        cost_per_gb = {
            'STANDARD': 0.023,
            'STANDARD_IA': 0.0125,
            'ONEZONE_IA': 0.01,
            'GLACIER_IR': 0.004,
            'GLACIER': 0.0036,
            'DEEP_ARCHIVE': 0.00099
        }
        
        print(f"📊 Storage Analysis for bucket: {bucket_name}")
        print(f"Total Objects: {object_count:,}")
        print(f"Total Size: {total_size / (1024**3):.2f} GB")
        print("\n📋 Storage Class Breakdown:")
        
        total_monthly_cost = 0
        
        for storage_class, data in storage_classes.items():
            size_gb = data['total_size'] / (1024**3)
            cost = size_gb * cost_per_gb.get(storage_class, 0.023)
            total_monthly_cost += cost
            
            print(f"  {storage_class}:")
            print(f"    Objects: {data['count']:,}")
            print(f"    Size: {size_gb:.2f} GB")
            print(f"    Monthly Cost: ${cost:.2f}")
            print()
        
        print(f"💰 Total Estimated Monthly Cost: ${total_monthly_cost:.2f}")
        
        return storage_classes
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return {}

def optimize_storage_costs(bucket_name):
    """Provide storage cost optimization recommendations"""
    s3_client = boto3.client('s3')
    
    try:
        # Analyze access patterns over last 30 days
        cloudwatch = boto3.client('cloudwatch')
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        # Get request metrics
        metrics = cloudwatch.get_metric_statistics(
            Namespace='AWS/S3',
            MetricName='NumberOfObjects',
            Dimensions=[
                {'Name': 'BucketName', 'Value': bucket_name},
                {'Name': 'StorageType', 'Value': 'AllStorageTypes'}
            ],
            StartTime=start_date,
            EndTime=end_date,
            Period=86400,  # Daily
            Statistics=['Average']
        )
        
        recommendations = []
        
        # Analyze current storage classes
        storage_analysis = analyze_bucket_storage_classes(bucket_name)
        
        for storage_class, data in storage_analysis.items():
            size_gb = data['total_size'] / (1024**3)
            
            if storage_class == 'STANDARD' and size_gb > 100:
                recommendations.append({
                    'action': 'Consider S3 Intelligent-Tiering',
                    'reason': f'{size_gb:.1f} GB in Standard storage could benefit from automatic tiering',
                    'potential_savings': f'Up to 30% cost reduction for infrequently accessed data'
                })
            
            if storage_class == 'STANDARD_IA' and data['count'] < 100:
                recommendations.append({
                    'action': 'Review Standard-IA usage',
                    'reason': 'Small number of objects may not justify IA storage class',
                    'potential_savings': 'Consider lifecycle policies for automatic transitions'
                })
        
        print("🎯 Storage Optimization Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec['action']}")
            print(f"   Reason: {rec['reason']}")
            print(f"   Impact: {rec['potential_savings']}")
            print()
        
        return recommendations
        
    except Exception as e:
        print(f"❌ Optimization analysis failed: {e}")
        return []

# Example usage
bucket_name = "my-data-bucket"

# Upload files with different storage classes
upload_with_storage_class(bucket_name, 'images/photo1.jpg', 'photo1.jpg', 'STANDARD')
upload_with_storage_class(bucket_name, 'backups/backup1.zip', 'backup1.zip', 'STANDARD_IA')
upload_with_storage_class(bucket_name, 'archives/old-data.tar', 'old-data.tar', 'GLACIER')

# Analyze current storage usage
analyze_bucket_storage_classes(bucket_name)

# Get optimization recommendations
optimize_storage_costs(bucket_name)

# Change storage class for cost optimization
change_storage_class(bucket_name, 'images/old-photo.jpg', 'STANDARD_IA')
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def lifecycle_management_tab():
    """Content for S3 Lifecycle Management tab"""
    st.markdown("## 🔄 Amazon S3 Lifecycle Management")
    st.markdown("*Automatically manage your objects' lifecycles to optimize costs and compliance*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **S3 Lifecycle management** enables you to define rules that automatically transition objects to different storage 
    classes or delete them entirely based on age, prefixes, or tags. This helps optimize storage costs and ensures compliance with data retention policies.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Lifecycle Flow Diagram
    st.markdown("### 🔄 Lifecycle Management Flow")
    common.mermaid(create_lifecycle_flow_mermaid(), height=350)
    
    # Interactive Lifecycle Rule Builder
    st.markdown("### 🛠️ Interactive Lifecycle Rule Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 Rule Configuration")
        rule_name = st.text_input("Rule Name:", "OptimizeStorageCosts")
        rule_status = st.selectbox("Rule Status:", ["Enabled", "Disabled"])
        
        filter_type = st.selectbox("Apply to:", [
            "Entire bucket",
            "Objects with specific prefix",
            "Objects with specific tags",
            "Objects with prefix AND tags"
        ])
        
        if "prefix" in filter_type.lower():
            prefix = st.text_input("Object Prefix:", "documents/")
        
        if "tag" in filter_type.lower():
            tag_key = st.text_input("Tag Key:", "classification")
            tag_value = st.text_input("Tag Value:", "archive")
    
    with col2:
        st.markdown("#### ⏰ Transition Timeline")
        enable_transitions = st.checkbox("Enable Storage Class Transitions", value=True)
        
        if enable_transitions:
            ia_days = st.number_input("Transition to Standard-IA after (days):", 0, 365, 30)
            glacier_ir_days = st.number_input("Transition to Glacier IR after (days):", 0, 1095, 90)
            glacier_days = st.number_input("Transition to Glacier after (days):", 0, 1095, 180)
            deep_archive_days = st.number_input("Transition to Deep Archive after (days):", 0, 3650, 365)
        
        enable_expiration = st.checkbox("Enable Object Expiration", value=False)
        if enable_expiration:
            expiration_days = st.number_input("Delete objects after (days):", 1, 10000, 2555)  # ~7 years
    
    # Calculate cost savings
    if st.button("📊 Calculate Lifecycle Impact", use_container_width=True):
        # Sample calculation inputs
        st.markdown("#### 💰 Cost Impact Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            initial_storage = st.slider("Initial Storage (GB):", 100, 100000, 10000, key="lifecycle_storage")
            monthly_growth = st.slider("Monthly Growth (GB):", 0, 5000, 500, key="lifecycle_growth")
        
        with col2:
            simulation_years = st.slider("Simulation Period (years):", 1, 10, 3, key="lifecycle_years")
        
        # Calculate costs with and without lifecycle
        months = simulation_years * 12
        
        # Without lifecycle (all Standard storage)
        total_storage_without = []
        costs_without = []
        current_storage = initial_storage
        
        for month in range(months):
            current_storage += monthly_growth
            total_storage_without.append(current_storage)
            costs_without.append(current_storage * 0.023)  # All in Standard
        
        # With lifecycle policy
        total_storage_with = []
        costs_with = []
        
        standard_storage = initial_storage
        ia_storage = 0
        glacier_storage = 0
        deep_archive_storage = 0
        
        for month in range(months):
            # Add new data to Standard
            standard_storage += monthly_growth
            
            # Apply lifecycle transitions
            if month >= ia_days // 30:
                # Transition some data to IA
                transition_amount = min(standard_storage * 0.3, monthly_growth * (month - ia_days // 30))
                standard_storage -= transition_amount
                ia_storage += transition_amount
            
            if month >= glacier_days // 30:
                # Transition some data to Glacier
                transition_amount = min(ia_storage * 0.5, monthly_growth * (month - glacier_days // 30))
                ia_storage -= transition_amount
                glacier_storage += transition_amount
            
            if month >= deep_archive_days // 30:
                # Transition some data to Deep Archive
                transition_amount = min(glacier_storage * 0.7, monthly_growth * (month - deep_archive_days // 30))
                glacier_storage -= transition_amount
                deep_archive_storage += transition_amount
            
            total_storage = standard_storage + ia_storage + glacier_storage + deep_archive_storage
            total_storage_with.append(total_storage)
            
            # Calculate monthly cost
            monthly_cost = (
                standard_storage * 0.023 +
                ia_storage * 0.0125 +
                glacier_storage * 0.0036 +
                deep_archive_storage * 0.00099
            )
            costs_with.append(monthly_cost)
        
        # Create visualization
        fig = go.Figure()
        
        months_range = list(range(1, months + 1))
        
        fig.add_trace(go.Scatter(
            x=months_range,
            y=costs_without,
            mode='lines',
            name='Without Lifecycle',
            line=dict(color=AWS_COLORS['warning'], width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=months_range,
            y=costs_with,
            mode='lines',
            name='With Lifecycle Policy',
            line=dict(color=AWS_COLORS['success'], width=3)
        ))
        
        fig.update_layout(
            title='Monthly Storage Costs Comparison',
            xaxis_title='Month',
            yaxis_title='Monthly Cost ($)',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary metrics
        total_savings = sum(costs_without) - sum(costs_with)
        savings_percentage = (total_savings / sum(costs_without)) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Cost (No Lifecycle)", f"${sum(costs_without):,.2f}", "")
        
        with col2:
            st.metric("Total Cost (With Lifecycle)", f"${sum(costs_with):,.2f}", "")
        
        with col3:
            st.metric("Total Savings", f"${total_savings:,.2f}", f"{savings_percentage:.1f}%")
        
        with col4:
            final_storage = total_storage_with[-1] if total_storage_with else 0
            st.metric("Final Storage", f"{final_storage:,.0f} GB", "")
    
    # Lifecycle Rule Types
    st.markdown("### 📚 Lifecycle Rule Types")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔄 Transition Actions
        Define when objects transition to other storage classes as they age.
        
        **Common Patterns:**
        - **Standard → Standard-IA** (30 days)
        - **Standard-IA → Glacier IR** (90 days)
        - **Glacier IR → Glacier** (180 days)
        - **Glacier → Deep Archive** (365 days)
        
        **Benefits:**
        - Automatic cost optimization
        - No manual intervention required
        - Maintains data accessibility
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🗑️ Expiration Actions
        Define when objects expire and are deleted automatically.
        
        **Use Cases:**
        - **Log files** (delete after 90 days)
        - **Temporary files** (delete after 7 days)
        - **Compliance data** (delete after 7 years)
        - **Incomplete multipart uploads** (cleanup)
        
        **Benefits:**
        - Automated compliance
        - Prevents storage bloat
        - Reduces long-term costs
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Advanced Lifecycle Features
    st.markdown("### 🔧 Advanced Lifecycle Features")
    
    features_data = {
        'Feature': [
            'Filter by Object Size',
            'Multiple Transitions',
            'Abort Incomplete Multipart Uploads',
            'Delete Expired Object Delete Markers',
            'Transition Current/Noncurrent Versions',
            'Filter by Object Tags'
        ],
        'Description': [
            'Apply rules only to objects larger/smaller than specified size',
            'Chain multiple storage class transitions over time',
            'Clean up incomplete uploads to avoid charges',
            'Remove unnecessary delete markers in versioned buckets',
            'Different rules for current vs previous object versions',
            'Apply rules based on object tags for fine-grained control'
        ],
        'Use Case': [
            'Skip archiving small files (<1MB)',
            'Gradual cost reduction over object lifetime',
            'Prevent accumulation of failed uploads',
            'Maintain clean versioned bucket',
            'Faster deletion of old versions',
            'Different policies per data classification'
        ]
    }
    
    df_features = pd.DataFrame(features_data)
    st.dataframe(df_features, use_container_width=True)
    
    # Real-world Examples
    st.markdown("### 🌟 Real-world Lifecycle Examples")
    
    example_scenarios = st.selectbox("Select a Scenario:", [
        "Web Application Logs",
        "Document Management System", 
        "Media Archive",
        "Data Lake",
        "Backup and Disaster Recovery"
    ])
    
    scenarios = {
        "Web Application Logs": {
            "description": "Application generates daily log files that need to be retained for compliance",
            "rules": [
                "Keep in Standard for 30 days (frequent analysis)",
                "Move to Standard-IA for 60 days (occasional reference)",
                "Move to Glacier for 6 years (compliance archive)",
                "Delete after 7 years (legal requirement)"
            ],
            "estimated_savings": "75% cost reduction over 7 years"
        },
        "Document Management System": {
            "description": "Business documents with varying access patterns",
            "rules": [
                "Active documents in Standard",
                "Move to Intelligent-Tiering after 90 days",
                "Archive to Glacier IR after 2 years",
                "Long-term archive in Deep Archive after 5 years"
            ],
            "estimated_savings": "60% cost reduction for archived documents"
        },
        "Media Archive": {
            "description": "Video and image files for media company",
            "rules": [
                "Recent content in Standard (30 days)",
                "Popular content in Standard-IA (1 year)",
                "Archive content in Glacier (10 years)",
                "Historical content in Deep Archive (permanent)"
            ],
            "estimated_savings": "80% cost reduction for archived media"
        },
        "Data Lake": {
            "description": "Analytics data with unknown access patterns",
            "rules": [
                "Raw data in Intelligent-Tiering",
                "Processed data in Standard (90 days)",
                "Move processed data to Glacier IR (1 year)",
                "Archive old datasets to Deep Archive (5 years)"
            ],
            "estimated_savings": "50% cost reduction through intelligent tiering"
        },
        "Backup and Disaster Recovery": {
            "description": "Database backups and system snapshots",
            "rules": [
                "Daily backups in Standard-IA (30 days)",
                "Weekly backups in Glacier (1 year)",
                "Monthly backups in Deep Archive (7 years)",
                "Delete incremental backups after 90 days"
            ],
            "estimated_savings": "70% cost reduction for backup storage"
        }
    }
    
    if example_scenarios in scenarios:
        scenario = scenarios[example_scenarios]
        
        st.markdown('<div class="storage-tier">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 📋 {example_scenarios} Lifecycle Policy
        
        **Scenario**: {scenario['description']}
        
        **Lifecycle Rules**:
        """)
        for i, rule in enumerate(scenario['rules'], 1):
            st.markdown(f"{i}. {rule}")
        
        st.markdown(f"""
        **💰 Expected Impact**: {scenario['estimated_savings']}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Implementing Lifecycle Policies")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Implementing S3 Lifecycle Management
import boto3
import json
from datetime import datetime

def create_lifecycle_configuration(bucket_name, rules):
    """Create comprehensive lifecycle configuration"""
    s3_client = boto3.client('s3')
    
    try:
        lifecycle_config = {
            'Rules': rules
        }
        
        s3_client.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration=lifecycle_config
        )
        
        print(f"✅ Lifecycle configuration applied to {bucket_name}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to apply lifecycle configuration: {e}")
        return False

def create_comprehensive_lifecycle_rules():
    """Create a set of comprehensive lifecycle rules"""
    
    rules = [
        {
            'ID': 'DocumentsLifecycle',
            'Status': 'Enabled',
            'Filter': {
                'Prefix': 'documents/'
            },
            'Transitions': [
                {
                    'Days': 30,
                    'StorageClass': 'STANDARD_IA'
                },
                {
                    'Days': 90,
                    'StorageClass': 'GLACIER_IR'
                },
                {
                    'Days': 365,
                    'StorageClass': 'GLACIER'
                },
                {
                    'Days': 2555,  # 7 years
                    'StorageClass': 'DEEP_ARCHIVE'
                }
            ],
            'Expiration': {
                'Days': 3650  # 10 years - delete after compliance period
            }
        },
        {
            'ID': 'LogsLifecycle',
            'Status': 'Enabled',
            'Filter': {
                'And': {
                    'Prefix': 'logs/',
                    'Tags': [
                        {
                            'Key': 'log-type',
                            'Value': 'application'
                        }
                    ]
                }
            },
            'Transitions': [
                {
                    'Days': 7,
                    'StorageClass': 'STANDARD_IA'
                },
                {
                    'Days': 30,
                    'StorageClass': 'GLACIER'
                }
            ],
            'Expiration': {
                'Days': 90  # Delete logs after 90 days
            }
        },
        {
            'ID': 'TempFilesCleanup',
            'Status': 'Enabled',
            'Filter': {
                'Prefix': 'temp/'
            },
            'Expiration': {
                'Days': 7  # Delete temporary files after 1 week
            }
        },
        {
            'ID': 'MultipartUploadCleanup',
            'Status': 'Enabled',
            'Filter': {},  # Apply to entire bucket
            'AbortIncompleteMultipartUpload': {
                'DaysAfterInitiation': 1  # Clean up incomplete uploads after 1 day
            }
        },
        {
            'ID': 'VersioningCleanup',
            'Status': 'Enabled',
            'Filter': {},
            'NoncurrentVersionTransitions': [
                {
                    'NoncurrentDays': 30,
                    'StorageClass': 'STANDARD_IA'
                },
                {
                    'NoncurrentDays': 90,
                    'StorageClass': 'GLACIER'
                }
            ],
            'NoncurrentVersionExpiration': {
                'NoncurrentDays': 365  # Delete old versions after 1 year
            }
        }
    ]
    
    return rules

def monitor_lifecycle_effectiveness(bucket_name):
    """Monitor lifecycle policy effectiveness"""
    s3_client = boto3.client('s3')
    cloudwatch = boto3.client('cloudwatch')
    
    try:
        # Get current lifecycle configuration
        response = s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
        rules = response['Rules']
        
        print(f"📊 Lifecycle Policy Analysis for {bucket_name}")
        print(f"Active Rules: {len(rules)}")
        print("=" * 50)
        
        # Analyze each rule
        for rule in rules:
            print(f"Rule: {rule['ID']}")
            print(f"Status: {rule['Status']}")
            
            if 'Filter' in rule:
                if 'Prefix' in rule['Filter']:
                    print(f"Applies to: Objects with prefix '{rule['Filter']['Prefix']}'")
                elif 'And' in rule['Filter']:
                    print(f"Applies to: Objects matching complex filter")
                else:
                    print(f"Applies to: All objects in bucket")
                    
            if 'Transitions' in rule:
                print(f"Transitions:")
                for transition in rule['Transitions']:
                    print(f"  After {transition['Days']} days → {transition['StorageClass']}")
            
            if 'Expiration' in rule:
                print(f"Expires after: {rule['Expiration']['Days']} days")
            
            print("-" * 30)
        
        # Get storage class metrics from CloudWatch
        storage_metrics = get_storage_class_metrics(bucket_name)
        
        return rules
        
    except Exception as e:
        print(f"❌ Error monitoring lifecycle: {e}")
        return []

def get_storage_class_metrics(bucket_name):
    """Get storage class distribution metrics"""
    cloudwatch = boto3.client('cloudwatch')
    
    storage_classes = [
        'StandardStorage',
        'StandardIAStorage', 
        'OneZoneIAStorage',
        'GlacierInstantRetrievalStorage',
        'GlacierStorage',
        'DeepArchiveStorage'
    ]
    
    print(f"\n📈 Storage Class Distribution for {bucket_name}:")
    
    for storage_class in storage_classes:
        try:
            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/S3',
                MetricName='BucketSizeBytes',
                Dimensions=[
                    {'Name': 'BucketName', 'Value': bucket_name},
                    {'Name': 'StorageType', 'Value': storage_class}
                ],
                StartTime=datetime.utcnow() - timedelta(days=1),
                EndTime=datetime.utcnow(),
                Period=86400,
                Statistics=['Average']
            )
            
            if response['Datapoints']:
                size_bytes = response['Datapoints'][0]['Average']
                size_gb = size_bytes / (1024**3)
                if size_gb > 0.01:  # Only show if > 10MB
                    print(f"  {storage_class}: {size_gb:.2f} GB")
        
        except Exception as e:
            continue  # Skip if metric not available

def cost_analysis_with_lifecycle(bucket_name, simulate_months=12):
    """Analyze cost impact of lifecycle policies"""
    s3_client = boto3.client('s3')
    
    try:
        # Get current objects and their storage classes
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name)
        
        current_cost = 0
        projected_savings = 0
        
        cost_per_gb = {
            'STANDARD': 0.023,
            'STANDARD_IA': 0.0125,
            'ONEZONE_IA': 0.01,
            'GLACIER_IR': 0.004,
            'GLACIER': 0.0036,
            'DEEP_ARCHIVE': 0.00099
        }
        
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    # Calculate current cost
                    obj_response = s3_client.head_object(
                        Bucket=bucket_name,
                        Key=obj['Key']
                    )
                    
                    storage_class = obj_response.get('StorageClass', 'STANDARD')
                    size_gb = obj['Size'] / (1024**3)
                    
                    current_monthly_cost = size_gb * cost_per_gb.get(storage_class, 0.023)
                    current_cost += current_monthly_cost
                    
                    # Estimate lifecycle impact
                    object_age = (datetime.utcnow().replace(tzinfo=None) - obj['LastModified'].replace(tzinfo=None)).days
                    
                    # Simulate lifecycle transitions
                    if object_age > 30 and storage_class == 'STANDARD':
                        # Would transition to Standard-IA
                        optimized_cost = size_gb * cost_per_gb['STANDARD_IA']
                        projected_savings += (current_monthly_cost - optimized_cost)
                    elif object_age > 90 and storage_class in ['STANDARD', 'STANDARD_IA']:
                        # Would transition to Glacier IR
                        optimized_cost = size_gb * cost_per_gb['GLACIER_IR']
                        projected_savings += (current_monthly_cost - optimized_cost)
        
        print(f"💰 Cost Analysis Results:")
        print(f"Current Monthly Cost: ${current_cost:.2f}")
        print(f"Potential Monthly Savings: ${projected_savings:.2f}")
        print(f"Annual Savings Potential: ${projected_savings * 12:.2f}")
        print(f"Savings Percentage: {(projected_savings/current_cost)*100:.1f}%")
        
        return {
            'current_cost': current_cost,
            'potential_savings': projected_savings,
            'savings_percentage': (projected_savings/current_cost)*100 if current_cost > 0 else 0
        }
        
    except Exception as e:
        print(f"❌ Cost analysis failed: {e}")
        return {}

# Example usage
bucket_name = "my-data-bucket"

# Create comprehensive lifecycle rules
lifecycle_rules = create_comprehensive_lifecycle_rules()

# Apply lifecycle configuration
if create_lifecycle_configuration(bucket_name, lifecycle_rules):
    print("🎉 Lifecycle policies successfully applied!")
    
    # Monitor effectiveness
    monitor_lifecycle_effectiveness(bucket_name)
    
    # Analyze cost impact
    cost_analysis_with_lifecycle(bucket_name)
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def bucket_policies_tab():
    """Content for S3 Bucket Policies tab"""
    st.markdown("## 🔒 S3 Bucket Policies")
    st.markdown("*Control access to your S3 buckets and objects with JSON-based policies*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **S3 Bucket Policies** are JSON-based access policy documents that allow you to control access to S3 buckets and objects. 
    They specify who can access your bucket, what actions they can perform, and under what conditions, adding a **principal statement** to standard IAM policy syntax.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Bucket Policy Flow
    st.markdown("### 🔄 Bucket Policy Evaluation Flow")
    common.mermaid(create_bucket_policy_flow_mermaid(), height=400)
    
    # Interactive Policy Builder
    st.markdown("### 🛠️ Interactive Bucket Policy Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Policy Configuration")
        policy_type = st.selectbox("Policy Template:", [
            "Allow Public Read Access",
            "Allow Cross-Account Access",
            "Enforce HTTPS Only",
            "Restrict by IP Address",
            "Allow CloudFront Access Only",
            "Custom Policy"
        ])
        
        bucket_name = st.text_input("Bucket Name:", "my-secure-bucket")
        
        if policy_type == "Allow Cross-Account Access":
            account_id = st.text_input("AWS Account ID:", "123456789012")
        elif policy_type == "Restrict by IP Address":
            ip_address = st.text_input("Allowed IP/CIDR:", "203.0.113.0/24")
        elif policy_type == "Allow CloudFront Access Only":
            oai_id = st.text_input("Origin Access Identity ID:", "E1234567890ABC")
    
    with col2:
        st.markdown("#### ⚙️ Access Settings")
        actions = st.multiselect("Allowed Actions:", [
            "s3:GetObject",
            "s3:PutObject", 
            "s3:DeleteObject",
            "s3:ListBucket",
            "s3:GetBucketLocation",
            "s3:ListBucketMultipartUploads",
            "s3:AbortMultipartUpload"
        ], default=["s3:GetObject"])
        
        apply_to = st.selectbox("Apply To:", [
            "Entire bucket and all objects",
            "Bucket only",
            "Objects only",
            "Specific prefix"
        ])
        
        if "prefix" in apply_to.lower():
            object_prefix = st.text_input("Object Prefix:", "public/")
    
    # Generate and display policy
    if st.button("🔨 Generate Bucket Policy", use_container_width=True):
        policy = generate_bucket_policy(policy_type, bucket_name, actions, locals())
        
        st.markdown("### 📄 Generated Bucket Policy")
        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code(json.dumps(policy, indent=2), language='json')
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Policy explanation
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 📋 Policy Explanation
        
        **Effect**: {policy['Statement'][0]['Effect']}
        **Principal**: {policy['Statement'][0].get('Principal', 'Inherited from IAM')}
        **Actions**: {', '.join(policy['Statement'][0]['Action']) if isinstance(policy['Statement'][0]['Action'], list) else policy['Statement'][0]['Action']}
        **Resource**: {policy['Statement'][0]['Resource']}
        
        **What this policy does**: {get_policy_explanation(policy_type)}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Policy Components Deep Dive
    st.markdown("### 🧩 Bucket Policy Components")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 👤 Principal
        Specifies **who** the statement covers (unique to bucket policies)
        
        **Examples:**
        - `"*"` - Everyone (public access)
        - `"AWS": "123456789012"` - Specific AWS account
        - `"AWS": "arn:aws:iam::ACCOUNT:user/USERNAME"` - Specific IAM user
        - `"AWS": "arn:aws:iam::ACCOUNT:role/ROLENAME"` - Specific IAM role
        - `"Service": "cloudfront.amazonaws.com"` - AWS service
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎬 Action
        Specifies **what actions** are allowed or denied
        
        **Common Actions:**
        - `s3:GetObject` - Download objects
        - `s3:PutObject` - Upload objects
        - `s3:DeleteObject` - Delete objects
        - `s3:ListBucket` - List bucket contents
        - `s3:*` - All S3 actions
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🗂️ Resource
        Specifies **which resources** the policy applies to
        
        **Examples:**
        - `"arn:aws:s3:::bucket-name"` - The bucket itself
        - `"arn:aws:s3:::bucket-name/*"` - All objects in bucket
        - `"arn:aws:s3:::bucket-name/folder/*"` - Objects in specific folder
        - Multiple resources can be specified in an array
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔧 Condition
        Specifies **conditions** that must be met (optional)
        
        **Common Conditions:**
        - `"IpAddress": {"aws:SourceIp": "203.0.113.0/24"}` - IP restriction
        - `"Bool": {"aws:SecureTransport": "true"}` - HTTPS only
        - `"DateGreaterThan": {"aws:CurrentTime": "2025-01-01T00:00:00Z"}` - Time-based
        - `"StringEquals": {"s3:prefix": "documents/"}` - Prefix matching
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Common Policy Examples
    st.markdown("### 📚 Common Bucket Policy Examples")
    
    example_type = st.selectbox("Select Policy Example:", [
        "Public Read Access for Static Website",
        "Cross-Account Access for Partner",
        "Enforce HTTPS and MFA",
        "CloudFront Origin Access Control",
        "Time-based Access Restrictions",
        "Multi-condition Complex Policy"
    ])
    
    examples = {
        "Public Read Access for Static Website": {
            "policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": "arn:aws:s3:::my-website-bucket/*"
                    }
                ]
            },
            "explanation": "Allows anyone on the internet to read (download) objects from your bucket. Perfect for static websites.",
            "security_note": "⚠️ This makes your content publicly accessible. Only use for content intended to be public."
        },
        "Cross-Account Access for Partner": {
            "policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "CrossAccountAccess",
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::123456789012:root"
                        },
                        "Action": [
                            "s3:GetObject",
                            "s3:PutObject",
                            "s3:ListBucket"
                        ],
                        "Resource": [
                            "arn:aws:s3:::shared-data-bucket",
                            "arn:aws:s3:::shared-data-bucket/*"
                        ]
                    }
                ]
            },
            "explanation": "Allows another AWS account (123456789012) to read, write, and list objects in your bucket.",
            "security_note": "🔒 Restricts access to a specific trusted AWS account. The other account still needs IAM permissions."
        },
        "Enforce HTTPS and MFA": {
            "policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "DenyInsecureConnections",
                        "Effect": "Deny",
                        "Principal": "*",
                        "Action": "s3:*",
                        "Resource": [
                            "arn:aws:s3:::secure-bucket",
                            "arn:aws:s3:::secure-bucket/*"
                        ],
                        "Condition": {
                            "Bool": {
                                "aws:SecureTransport": "false"
                            }
                        }
                    },
                    {
                        "Sid": "RequireMFAForDelete",
                        "Effect": "Deny",
                        "Principal": "*",
                        "Action": "s3:DeleteObject",
                        "Resource": "arn:aws:s3:::secure-bucket/*",
                        "Condition": {
                            "BoolIfExists": {
                                "aws:MultiFactorAuthPresent": "false"
                            }
                        }
                    }
                ]
            },
            "explanation": "Denies all non-HTTPS requests and requires MFA for delete operations.",
            "security_note": "🛡️ Strong security policy that enforces encryption in transit and MFA for destructive actions."
        }
    }
    
    if example_type in examples:
        example = examples[example_type]
        
        st.markdown("#### 📄 Policy Document")
        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code(json.dumps(example["policy"], indent=2), language='json')
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown(f"""
            ### 📖 Explanation
            {example['explanation']}
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
            st.markdown(f"""
            ### 🔐 Security Note
            {example['security_note']}
            """)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Policy Testing Tool
    st.markdown("### 🧪 Policy Testing Simulator")
    
    st.markdown('<div class="s3-bucket">', unsafe_allow_html=True)
    st.markdown("#### Test Access Scenarios")
    
    col1, col2 = st.columns(2)
    
    with col1:
        test_principal = st.selectbox("Test as:", [
            "Anonymous User (Public)",
            "Specific AWS Account", 
            "IAM User",
            "IAM Role",
            "AWS Service"
        ])
        
        if test_principal != "Anonymous User (Public)":
            principal_arn = st.text_input("Principal ARN:", "arn:aws:iam::123456789012:user/testuser")
    
    with col2:
        test_action = st.selectbox("Action to Test:", [
            "s3:GetObject",
            "s3:PutObject",
            "s3:DeleteObject",
            "s3:ListBucket"
        ])
        
        test_conditions = st.multiselect("Additional Conditions:", [
            "HTTPS Connection",
            "MFA Present",
            "Specific IP Address",
            "Time Restriction"
        ])
    
    if st.button("🔍 Test Policy Access"):
        # Simulate policy evaluation
        access_result = simulate_policy_access(test_principal, test_action, test_conditions)
        
        if access_result["allowed"]:
            st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
            st.markdown(f"""
            ### ✅ Access Granted
            
            **Result**: {test_principal} can perform {test_action}
            **Reason**: {access_result['reason']}
            **Policy Statement**: {access_result['matching_statement']}
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
            st.markdown(f"""
            ### ❌ Access Denied
            
            **Result**: {test_principal} cannot perform {test_action}
            **Reason**: {access_result['reason']}
            **Recommendation**: {access_result['recommendation']}
            """)
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Best Practices
    st.markdown("### 💡 Bucket Policy Best Practices")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛡️ Security Best Practices
        
        **Principle of Least Privilege:**
        - Grant only the minimum required permissions
        - Use specific actions instead of `s3:*`
        - Restrict to specific resources
        
        **Use Conditions:**
        - Enforce HTTPS with `aws:SecureTransport`
        - Restrict by IP address when possible
        - Require MFA for sensitive operations
        
        **Avoid Public Access:**
        - Never use `"Principal": "*"` unless necessary
        - Use CloudFront OAC instead of public buckets
        - Enable S3 Block Public Access settings
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔧 Policy Management Tips
        
        **Policy Structure:**
        - Use descriptive `Sid` values
        - Group related statements
        - Keep policies readable and maintainable
        
        **Testing and Validation:**
        - Test policies in development first
        - Use AWS Policy Simulator
        - Monitor CloudTrail for access denials
        
        **Documentation:**
        - Document policy purpose and rationale
        - Include review dates and owners
        - Version control policy changes
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Managing Bucket Policies")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Managing S3 Bucket Policies with Python
import boto3
import json
from datetime import datetime, timedelta

def create_bucket_policy(bucket_name, policy_type, **kwargs):
    """Create various types of bucket policies"""
    
    if policy_type == "public_read":
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }
    
    elif policy_type == "cross_account":
        account_id = kwargs.get('account_id')
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "CrossAccountAccess",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": f"arn:aws:iam::{account_id}:root"
                    },
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:ListBucket"
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{bucket_name}",
                        f"arn:aws:s3:::{bucket_name}/*"
                    ]
                }
            ]
        }
    
    elif policy_type == "https_only":
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "DenyInsecureConnections", 
                    "Effect": "Deny",
                    "Principal": "*",
                    "Action": "s3:*",
                    "Resource": [
                        f"arn:aws:s3:::{bucket_name}",
                        f"arn:aws:s3:::{bucket_name}/*"
                    ],
                    "Condition": {
                        "Bool": {
                            "aws:SecureTransport": "false"
                        }
                    }
                }
            ]
        }
    
    elif policy_type == "ip_restricted":
        allowed_ip = kwargs.get('ip_cidr', '203.0.113.0/24')
        policy = {
            "Version": "2012-10-17", 
            "Statement": [
                {
                    "Sid": "IPRestrict",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*",
                    "Condition": {
                        "IpAddress": {
                            "aws:SourceIp": allowed_ip
                        }
                    }
                }
            ]
        }
    
    elif policy_type == "cloudfront_oac":
        oac_id = kwargs.get('oac_id')
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowCloudFrontServicePrincipal",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "cloudfront.amazonaws.com"
                    },
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*",
                    "Condition": {
                        "StringEquals": {
                            "AWS:SourceArn": f"arn:aws:cloudfront::123456789012:distribution/{oac_id}"
                        }
                    }
                }
            ]
        }
    
    else:
        raise ValueError(f"Unknown policy type: {policy_type}")
    
    return policy

def apply_bucket_policy(bucket_name, policy):
    """Apply bucket policy to S3 bucket"""
    s3_client = boto3.client('s3')
    
    try:
        # Convert policy dict to JSON string
        policy_json = json.dumps(policy)
        
        # Apply the policy
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=policy_json
        )
        
        print(f"✅ Bucket policy applied successfully to {bucket_name}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to apply bucket policy: {e}")
        return False

def get_bucket_policy(bucket_name):
    """Retrieve and display current bucket policy"""
    s3_client = boto3.client('s3')
    
    try:
        response = s3_client.get_bucket_policy(Bucket=bucket_name)
        policy = json.loads(response['Policy'])
        
        print(f"📄 Current bucket policy for {bucket_name}:")
        print(json.dumps(policy, indent=2))
        
        return policy
        
    except s3_client.exceptions.NoSuchBucketPolicy:
        print(f"ℹ️  No bucket policy found for {bucket_name}")
        return None
    except Exception as e:
        print(f"❌ Error retrieving bucket policy: {e}")
        return None

def validate_bucket_policy(policy):
    """Validate bucket policy syntax and security"""
    validation_results = {
        'valid': True,
        'warnings': [],
        'errors': []
    }
    
    try:
        # Check required fields
        if 'Version' not in policy:
            validation_results['errors'].append("Missing 'Version' field")
        
        if 'Statement' not in policy:
            validation_results['errors'].append("Missing 'Statement' field")
            return validation_results
        
        # Check each statement
        for i, statement in enumerate(policy['Statement']):
            statement_num = i + 1
            
            # Required fields
            required_fields = ['Effect', 'Principal', 'Action', 'Resource']
            for field in required_fields:
                if field not in statement:
                    validation_results['errors'].append(
                        f"Statement {statement_num}: Missing '{field}' field"
                    )
            
            # Security checks
            if statement.get('Principal') == "*" and statement.get('Effect') == "Allow":
                validation_results['warnings'].append(
                    f"Statement {statement_num}: Public access policy detected"
                )
            
            if 's3:*' in str(statement.get('Action', '')):
                validation_results['warnings'].append(
                    f"Statement {statement_num}: Overly broad permissions (s3:*)"
                )
            
            # Check for HTTPS enforcement
            has_https_condition = False
            if 'Condition' in statement:
                condition = statement['Condition']
                if isinstance(condition, dict):
                    for condition_type, condition_values in condition.items():
                        if 'aws:SecureTransport' in str(condition_values):
                            has_https_condition = True
                            break
            
            if not has_https_condition and statement.get('Effect') == 'Allow':
                validation_results['warnings'].append(
                    f"Statement {statement_num}: Consider enforcing HTTPS"
                )
        
        if validation_results['errors']:
            validation_results['valid'] = False
        
        return validation_results
        
    except Exception as e:
        validation_results['valid'] = False
        validation_results['errors'].append(f"Policy validation error: {e}")
        return validation_results

def test_bucket_access(bucket_name, test_scenarios):
    """Test bucket access with different scenarios"""
    s3_client = boto3.client('s3')
    
    print(f"🧪 Testing bucket access for {bucket_name}")
    print("=" * 50)
    
    for scenario in test_scenarios:
        print(f"Testing: {scenario['description']}")
        
        try:
            if scenario['action'] == 'list_objects':
                s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
                result = "✅ ALLOWED"
                
            elif scenario['action'] == 'get_object':
                # Try to get object metadata
                s3_client.head_object(Bucket=bucket_name, Key=scenario.get('key', 'test.txt'))
                result = "✅ ALLOWED"
                
            elif scenario['action'] == 'put_object':
                # Try to put a small test object
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key='test-access.txt',
                    Body=b'test',
                    Metadata={'test': 'access-check'}
                )
                result = "✅ ALLOWED"
                
                # Clean up test object
                s3_client.delete_object(Bucket=bucket_name, Key='test-access.txt')
                
        except Exception as e:
            if 'AccessDenied' in str(e) or 'Forbidden' in str(e):
                result = "❌ DENIED"
            else:
                result = f"❓ ERROR: {str(e)[:50]}..."
        
        print(f"  Result: {result}")
        print(f"  Expected: {scenario.get('expected', 'Unknown')}")
        print()

# Example usage
bucket_name = "my-secure-bucket-2025"

# Create different types of policies
policies = {
    'public_read': create_bucket_policy(bucket_name, 'public_read'),
    'cross_account': create_bucket_policy(bucket_name, 'cross_account', account_id='123456789012'),
    'https_only': create_bucket_policy(bucket_name, 'https_only'),
    'ip_restricted': create_bucket_policy(bucket_name, 'ip_restricted', ip_cidr='203.0.113.0/24')
}

# Apply HTTPS-only policy (recommended for security)
https_policy = policies['https_only']
print("📋 Generated HTTPS-only policy:")
print(json.dumps(https_policy, indent=2))

# Validate policy before applying
validation = validate_bucket_policy(https_policy)
print(f"\n🔍 Policy Validation:")
print(f"Valid: {validation['valid']}")
if validation['warnings']:
    print("Warnings:", validation['warnings'])
if validation['errors']:
    print("Errors:", validation['errors'])

# Apply policy if valid
if validation['valid']:
    apply_bucket_policy(bucket_name, https_policy)
    
    # Verify policy was applied
    current_policy = get_bucket_policy(bucket_name)
    
    # Test access scenarios
    test_scenarios = [
        {
            'description': 'List bucket contents',
            'action': 'list_objects',
            'expected': 'Should be allowed with proper authentication'
        },
        {
            'description': 'Upload new object',
            'action': 'put_object',
            'expected': 'Should be allowed over HTTPS only'
        }
    ]
    
    test_bucket_access(bucket_name, test_scenarios)
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def generate_bucket_policy(policy_type, bucket_name, actions, context):
    """Generate bucket policy based on type and parameters"""
    if policy_type == "Allow Public Read Access":
        return {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": actions,
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }
    
    elif policy_type == "Allow Cross-Account Access":
        account_id = context.get('account_id', '123456789012')
        return {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "CrossAccountAccess",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": f"arn:aws:iam::{account_id}:root"
                    },
                    "Action": actions,
                    "Resource": [
                        f"arn:aws:s3:::{bucket_name}",
                        f"arn:aws:s3:::{bucket_name}/*"
                    ]
                }
            ]
        }
    
    elif policy_type == "Enforce HTTPS Only":
        return {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "DenyInsecureConnections",
                    "Effect": "Deny",
                    "Principal": "*",
                    "Action": "s3:*",
                    "Resource": [
                        f"arn:aws:s3:::{bucket_name}",
                        f"arn:aws:s3:::{bucket_name}/*"
                    ],
                    "Condition": {
                        "Bool": {
                            "aws:SecureTransport": "false"
                        }
                    }
                }
            ]
        }
    
    elif policy_type == "Restrict by IP Address":
        ip_address = context.get('ip_address', '203.0.113.0/24')
        return {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "IPRestrict",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": actions,
                    "Resource": f"arn:aws:s3:::{bucket_name}/*",
                    "Condition": {
                        "IpAddress": {
                            "aws:SourceIp": ip_address
                        }
                    }
                }
            ]
        }
    
    return {"Version": "2012-10-17", "Statement": []}

def get_policy_explanation(policy_type):
    """Get explanation for policy type"""
    explanations = {
        "Allow Public Read Access": "This policy allows anyone on the internet to read objects from your bucket. Use for static websites or public content.",
        "Allow Cross-Account Access": "This policy allows a specific AWS account to access your bucket. Useful for sharing data with partners.",
        "Enforce HTTPS Only": "This policy denies all requests that don't use HTTPS, ensuring data is encrypted in transit.",
        "Restrict by IP Address": "This policy only allows access from specific IP addresses or IP ranges.",
        "Allow CloudFront Access Only": "This policy restricts access to your CloudFront distribution only, preventing direct access to S3."
    }
    return explanations.get(policy_type, "Custom policy generated based on your specifications.")

def simulate_policy_access(principal, action, conditions):
    """Simulate policy access evaluation"""
    # Simple simulation logic
    if principal == "Anonymous User (Public)":
        if "Public" in action or action == "s3:GetObject":
            return {
                "allowed": True,
                "reason": "Public read access policy allows this action",
                "matching_statement": "PublicReadGetObject"
            }
        else:
            return {
                "allowed": False,
                "reason": "No policy allows anonymous access for this action",
                "recommendation": "Add appropriate bucket policy or use authenticated access"
            }
    
    return {
        "allowed": True,
        "reason": "Simulated access granted",
        "matching_statement": "TestStatement"
    }

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
    # 🗂️ AWS S3 Storage Solutions Hub
    
    """)
    st.markdown("""<div class="info-box">
                Master Amazon S3 object storage with comprehensive coverage of storage classes, lifecycle management, and security policies. Learn to optimize costs while maintaining performance and security for your applications.
                </div>""", unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🗂️ Amazon S3",
        "📊 Storage Classes", 
        "🔄 Lifecycle Management",
        "🔒 Bucket Policies"
    ])
    
    with tab1:
        s3_overview_tab()
    
    with tab2:
        storage_classes_tab()
    
    with tab3:
        lifecycle_management_tab()
        
    with tab4:
        bucket_policies_tab()
    
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
