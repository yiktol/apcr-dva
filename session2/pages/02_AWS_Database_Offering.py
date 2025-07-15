
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
    page_title="AWS Database Offerings Hub",
    page_icon="🗄️",
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
        
        .db-selector {{
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
            - 🗄️ AWS Database Ecosystem - Overview of managed database services
            - ⚖️ Relational vs Non-Relational - Key differences and use cases
            - 🚀 Amazon DynamoDB - NoSQL database deep dive
            - 🐘 Amazon RDS & Aurora - Managed relational databases
            
            **Learning Objectives:**
            - Understand AWS database service categories
            - Learn when to use relational vs non-relational databases
            - Explore DynamoDB features and capabilities
            - Compare database options for different workloads
            """)

def create_database_ecosystem_mermaid():
    """Create mermaid diagram for AWS database ecosystem"""
    return """
    graph TB
        A[AWS Database Services] --> B[Relational Databases]
        A --> C[Non-Relational Databases]
        A --> D[Specialized Databases]
        
        B --> E[Amazon RDS]
        B --> F[Amazon Aurora]
        
        C --> G[Amazon DynamoDB]
        C --> H[Amazon DocumentDB]
        C --> I[Amazon ElastiCache]
        
        D --> J[Amazon Neptune]
        D --> K[Amazon Timestream]
        D --> L[Amazon QLDB]
        
        E --> M[MySQL, PostgreSQL<br/>MariaDB, Oracle<br/>SQL Server]
        F --> N[MySQL Compatible<br/>PostgreSQL Compatible]
        
        G --> O[Key-Value<br/>Document Store]
        H --> P[MongoDB Compatible<br/>Document Database]
        I --> Q[Redis<br/>Memcached]
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style B fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_rds_vs_dynamodb_mermaid():
    """Create comparison diagram between RDS and DynamoDB"""
    return """
    graph LR
        subgraph "Amazon RDS"
            A1[Structured Data]
            A2[ACID Transactions]
            A3[Complex Queries]
            A4[Joins & Relations]
            A5[SQL Language]
        end
        
        subgraph "Amazon DynamoDB"
            B1[Flexible Schema]
            B2[Eventual Consistency*]
            B3[Simple Queries]
            B4[Single Table Design]
            B5[NoSQL API]
        end
        
        A1 -.-> B1
        A2 -.-> B2
        A3 -.-> B3
        A4 -.-> B4
        A5 -.-> B5
        
        style A1 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style A2 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style A3 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style A4 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style A5 fill:#4B9EDB,stroke:#232F3E,color:#fff
        
        style B1 fill:#3FB34F,stroke:#232F3E,color:#fff
        style B2 fill:#3FB34F,stroke:#232F3E,color:#fff
        style B3 fill:#3FB34F,stroke:#232F3E,color:#fff
        style B4 fill:#3FB34F,stroke:#232F3E,color:#fff
        style B5 fill:#3FB34F,stroke:#232F3E,color:#fff
    """

def create_dynamodb_architecture_mermaid():
    """Create DynamoDB architecture diagram"""
    return """
    graph TB
        subgraph "Application Layer"
            A1[Web Application]
            A2[Mobile App]
            A3[API Gateway]
        end
        
        subgraph "Amazon DynamoDB"
            B1[DynamoDB Table]
            B2[Global Secondary Index]
            B3[Local Secondary Index]
            B4[DynamoDB Streams]
        end
        
        subgraph "Additional Features"
            C1[DynamoDB Accelerator - DAX]
            C2[Point-in-Time Recovery]
            C3[Global Tables]
            C4[Auto Scaling]
        end
        
        A1 --> B1
        A2 --> B1
        A3 --> B1
        
        B1 --> B2
        B1 --> B3
        B1 --> B4
        
        B1 --> C1
        B1 --> C2
        B1 --> C3
        B1 --> C4
        
        B4 --> D1[Lambda Functions]
        B4 --> D2[Analytics]
        
        style B1 fill:#FF9900,stroke:#232F3E,color:#fff
        style B2 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style B3 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style B4 fill:#3FB34F,stroke:#232F3E,color:#fff
    """

def aws_database_ecosystem_tab():
    """Content for AWS Database Ecosystem tab"""
    st.markdown("## 🗄️ AWS Database Ecosystem")
    st.markdown("*Comprehensive overview of AWS managed database services*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    AWS offers a comprehensive suite of **purpose-built database services** designed for different data models 
    and use cases. From traditional relational databases to modern NoSQL solutions, AWS provides managed 
    services that eliminate the operational burden of database administration.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Database ecosystem overview
    st.markdown("### 🌐 AWS Database Service Categories")
    common.mermaid(create_database_ecosystem_mermaid(), height=600)
    
    # Database statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 15+\n**Database Engines**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 99.99%\n**Availability SLA**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### Petabyte\n**Scale Support**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### Global\n**Multi-Region**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Database Selector
    st.markdown("### 🎯 Interactive Database Workload Analyzer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Workload Characteristics")
        workload_type = st.selectbox("Primary Workload:", [
            "Web/Mobile Applications", "E-commerce Platform", "Real-time Analytics", 
            "Content Management", "IoT Data Collection", "Enterprise Applications"
        ])
        
        data_structure = st.selectbox("Data Structure:", [
            "Highly Structured (Tables/Relations)", "Semi-Structured (JSON/Documents)", 
            "Key-Value Pairs", "Graph Relationships", "Time-Series Data"
        ])
        
        scale_requirement = st.selectbox("Scale Requirements:", [
            "Small to Medium (< 1TB)", "Large (1TB - 10TB)", 
            "Very Large (10TB - 100TB)", "Massive (> 100TB)"
        ])
    
    with col2:
        st.markdown("### 🎯 Performance Requirements")
        consistency_model = st.selectbox("Consistency Requirements:", [
            "Strong Consistency (ACID)", "Eventual Consistency", 
            "Flexible (Both Options)"
        ])
        
        query_complexity = st.selectbox("Query Complexity:", [
            "Simple Key-Value Lookups", "Complex SQL Queries", 
            "Both Simple and Complex", "Graph Traversals"
        ])
        
        latency_requirement = st.selectbox("Latency Requirements:", [
            "Sub-millisecond", "Single-digit milliseconds", 
            "Low latency (< 100ms)", "Standard (> 100ms)"
        ])
    
    if st.button("🔍 Find Optimal Database Service", use_container_width=True):
        # Database recommendation logic
        recommendations = []
        
        # DynamoDB recommendations
        if (data_structure in ["Key-Value Pairs", "Semi-Structured (JSON/Documents)"] and 
            latency_requirement in ["Sub-millisecond", "Single-digit milliseconds"] and
            consistency_model != "Strong Consistency (ACID)"):
            recommendations.append({
                'service': 'Amazon DynamoDB',
                'match_score': 95,
                'reasons': [
                    'Excellent for key-value and document data',
                    'Single-digit millisecond latency',
                    'Serverless and auto-scaling',
                    'Perfect for web/mobile applications'
                ]
            })
        
        # RDS recommendations
        if (data_structure == "Highly Structured (Tables/Relations)" and
            query_complexity in ["Complex SQL Queries", "Both Simple and Complex"] and
            consistency_model == "Strong Consistency (ACID)"):
            recommendations.append({
                'service': 'Amazon RDS',
                'match_score': 90,
                'reasons': [
                    'Full SQL support for complex queries',
                    'ACID compliance for data integrity',
                    'Familiar relational model',
                    'Multiple engine options'
                ]
            })
        
        # Aurora recommendations
        if (workload_type in ["E-commerce Platform", "Enterprise Applications"] and
            scale_requirement in ["Large (1TB - 10TB)", "Very Large (10TB - 100TB)"]):
            recommendations.append({
                'service': 'Amazon Aurora',
                'match_score': 92,
                'reasons': [
                    '5x faster than MySQL, 3x faster than PostgreSQL',
                    'Auto-scaling storage up to 64TB',
                    'High availability with read replicas',
                    'MySQL and PostgreSQL compatible'
                ]
            })
        
        # ElastiCache recommendations
        if latency_requirement == "Sub-millisecond":
            recommendations.append({
                'service': 'Amazon ElastiCache',
                'match_score': 88,
                'reasons': [
                    'Microsecond latency for caching',
                    'Redis and Memcached support',
                    'Perfect for session storage',
                    'Reduces database load'
                ]
            })
        
        # Sort recommendations by match score
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        if recommendations:
            top_recommendation = recommendations[0]
            
            st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
            st.markdown(f"""
            ### 🎯 Top Recommendation: {top_recommendation['service']}
            **Match Score: {top_recommendation['match_score']}%**
            
            **Why this service fits your needs:**
            """)
            for reason in top_recommendation['reasons']:
                st.markdown(f"✅ {reason}")
            
            if len(recommendations) > 1:
                st.markdown(f"\n**Alternative Options:**")
                for alt in recommendations[1:3]:  # Show up to 2 alternatives
                    st.markdown(f"• {alt['service']} ({alt['match_score']}% match)")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Database Services Overview
    st.markdown("### 📋 AWS Database Services Detailed Overview")
    
    database_data = {
        'Database Service': [
            'Amazon RDS', 'Amazon Aurora', 'Amazon DynamoDB', 
            'Amazon DocumentDB', 'Amazon ElastiCache', 'Amazon Neptune'
        ],
        'Database Type': [
            'Relational', 'Relational', 'NoSQL Key-Value', 
            'NoSQL Document', 'In-Memory Cache', 'Graph Database'
        ],
        'Engine Options': [
            'MySQL, PostgreSQL, MariaDB, Oracle, SQL Server',
            'MySQL-compatible, PostgreSQL-compatible',
            'Proprietary NoSQL',
            'MongoDB-compatible',
            'Redis, Memcached',
            'Gremlin, SPARQL'
        ],
        'Primary Use Cases': [
            'Traditional applications, data warehousing',
            'High-performance applications, cloud-native',
            'Web/mobile apps, gaming, IoT',
            'Content management, catalogs',
            'Caching, session store, real-time analytics',
            'Social networks, fraud detection, recommendations'
        ],
        'Scaling Model': [
            'Vertical + Read Replicas', 'Auto-scaling storage + Read Replicas',
            'Auto-scaling + On-demand', 'Horizontal scaling',
            'Cluster scaling', 'Auto-scaling'
        ]
    }
    
    df_databases = pd.DataFrame(database_data)
    st.dataframe(df_databases, use_container_width=True)
    
    # Migration Paths
    st.markdown("### 🔄 Common Database Migration Paths")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📤 Self-Managed to AWS Managed
        
        **Typical Migration Scenarios:**
        - **On-premises MySQL** → Amazon RDS MySQL
        - **Self-managed PostgreSQL** → Amazon Aurora PostgreSQL
        - **MongoDB on EC2** → Amazon DocumentDB
        - **Redis on EC2** → Amazon ElastiCache for Redis
        
        **Benefits:**
        - Reduced operational overhead
        - Automated backups and patching
        - High availability and disaster recovery
        - Better performance and monitoring
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🏗️ Architecture Modernization
        
        **Modern Application Patterns:**
        - **Monolithic DB** → Microservices with multiple databases
        - **RDBMS** → DynamoDB for web-scale NoSQL needs
        - **Traditional caching** → ElastiCache for performance
        - **Complex relationships** → Neptune for graph data
        
        **Considerations:**
        - Application re-architecture may be required
        - Data model transformation
        - Performance testing and optimization
        - Team training on new technologies
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Database Service Selection Logic")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# AWS Database Service Selection Framework
import boto3
from typing import Dict, List, Any

class DatabaseServiceSelector:
    """Intelligent database service selection based on workload characteristics"""
    
    def __init__(self):
        self.services = {
            'dynamodb': {
                'name': 'Amazon DynamoDB',
                'type': 'NoSQL',
                'strengths': ['low_latency', 'auto_scaling', 'serverless', 'key_value', 'document'],
                'use_cases': ['web_mobile', 'gaming', 'iot', 'real_time'],
                'max_item_size': '400KB',
                'consistency': ['eventual', 'strong_optional']
            },
            'rds': {
                'name': 'Amazon RDS',
                'type': 'Relational',
                'strengths': ['sql_queries', 'acid_compliance', 'multi_engine', 'familiar'],
                'use_cases': ['traditional_apps', 'data_warehouse', 'complex_queries'],
                'engines': ['mysql', 'postgresql', 'mariadb', 'oracle', 'sqlserver'],
                'consistency': ['strong']
            },
            'aurora': {
                'name': 'Amazon Aurora',
                'type': 'Relational',
                'strengths': ['high_performance', 'auto_scaling_storage', 'cloud_native'],
                'use_cases': ['enterprise', 'high_throughput', 'global_apps'],
                'engines': ['mysql', 'postgresql'],
                'consistency': ['strong']
            },
            'elasticache': {
                'name': 'Amazon ElastiCache',
                'type': 'In-Memory',
                'strengths': ['microsecond_latency', 'caching', 'session_store'],
                'use_cases': ['caching', 'session_management', 'real_time_analytics'],
                'engines': ['redis', 'memcached'],
                'consistency': ['eventual']
            }
        }
    
    def analyze_workload(self, requirements: Dict[str, Any]) -> List[Dict]:
        """Analyze workload requirements and recommend database services"""
        recommendations = []
        
        for service_key, service_info in self.services.items():
            score = self._calculate_match_score(requirements, service_info)
            
            if score > 60:  # Only include reasonably good matches
                recommendations.append({
                    'service': service_info['name'],
                    'service_key': service_key,
                    'score': score,
                    'type': service_info['type'],
                    'reasoning': self._generate_reasoning(requirements, service_info)
                })
        
        return sorted(recommendations, key=lambda x: x['score'], reverse=True)
    
    def _calculate_match_score(self, requirements: Dict, service: Dict) -> int:
        """Calculate how well a service matches the requirements"""
        score = 0
        max_score = 0
        
        # Data structure match
        max_score += 25
        if requirements.get('data_structure') == 'relational' and service['type'] == 'Relational':
            score += 25
        elif requirements.get('data_structure') == 'nosql' and service['type'] == 'NoSQL':
            score += 25
        elif requirements.get('data_structure') == 'cache' and service['type'] == 'In-Memory':
            score += 25
        
        # Latency requirements
        max_score += 20
        if requirements.get('latency') == 'microsecond' and 'microsecond_latency' in service['strengths']:
            score += 20
        elif requirements.get('latency') == 'millisecond' and 'low_latency' in service['strengths']:
            score += 20
        elif requirements.get('latency') == 'standard':
            score += 15
        
        # Scaling requirements
        max_score += 20
        if requirements.get('scaling') == 'auto' and 'auto_scaling' in service['strengths']:
            score += 20
        elif requirements.get('scaling') == 'serverless' and 'serverless' in service['strengths']:
            score += 20
        
        # Use case match
        max_score += 20
        use_case = requirements.get('use_case', '')
        if any(uc in service['use_cases'] for uc in [use_case]):
            score += 20
        
        # Consistency requirements
        max_score += 15
        consistency_req = requirements.get('consistency', 'eventual')
        if consistency_req in service.get('consistency', []):
            score += 15
        
        return int((score / max_score) * 100) if max_score > 0 else 0
    
    def _generate_reasoning(self, requirements: Dict, service: Dict) -> List[str]:
        """Generate human-readable reasoning for the recommendation"""
        reasons = []
        
        if service['type'] == 'NoSQL' and requirements.get('data_structure') == 'nosql':
            reasons.append(f"Perfect match for NoSQL data structure requirements")
        
        if 'low_latency' in service['strengths'] and requirements.get('latency') in ['microsecond', 'millisecond']:
            reasons.append(f"Meets low latency requirements for responsive applications")
        
        if 'serverless' in service['strengths']:
            reasons.append(f"Serverless model eliminates infrastructure management")
        
        if 'auto_scaling' in service['strengths']:
            reasons.append(f"Automatic scaling handles traffic variations")
        
        return reasons

def recommend_database_architecture(application_requirements):
    """Recommend complete database architecture for an application"""
    selector = DatabaseServiceSelector()
    
    # Primary database recommendation
    primary_db = selector.analyze_workload(application_requirements)
    
    architecture = {
        'primary_database': primary_db[0] if primary_db else None,
        'caching_layer': None,
        'analytics_store': None,
        'search_service': None
    }
    
    # Add caching recommendation for high-traffic applications
    if application_requirements.get('traffic_level') == 'high':
        cache_requirements = {
            'data_structure': 'cache',
            'latency': 'microsecond',
            'use_case': 'caching'
        }
        cache_recommendation = selector.analyze_workload(cache_requirements)
        architecture['caching_layer'] = cache_recommendation[0] if cache_recommendation else None
    
    # Add analytics store for applications with reporting needs
    if application_requirements.get('analytics_needed', False):
        architecture['analytics_store'] = {
            'service': 'Amazon Redshift',
            'purpose': 'Data warehousing and analytics',
            'integration': 'ETL from primary database'
        }
    
    return architecture

# Example usage scenarios
if __name__ == "__main__":
    # E-commerce application
    ecommerce_requirements = {
        'data_structure': 'nosql',
        'latency': 'millisecond',
        'scaling': 'auto',
        'use_case': 'web_mobile',
        'consistency': 'eventual',
        'traffic_level': 'high',
        'analytics_needed': True
    }
    
    selector = DatabaseServiceSelector()
    recommendations = selector.analyze_workload(ecommerce_requirements)
    
    print("🛒 E-commerce Application Database Recommendations:")
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"{i}. {rec['service']} (Score: {rec['score']}%)")
        print(f"   Type: {rec['type']}")
        for reason in rec['reasoning']:
            print(f"   ✓ {reason}")
        print()
    
    # Get complete architecture recommendation
    architecture = recommend_database_architecture(ecommerce_requirements)
    
    print("🏗️ Recommended Complete Architecture:")
    print(f"Primary Database: {architecture['primary_database']['service']}")
    if architecture['caching_layer']:
        print(f"Caching Layer: {architecture['caching_layer']['service']}")
    if architecture['analytics_store']:
        print(f"Analytics Store: {architecture['analytics_store']['service']}")
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def relational_vs_nonrelational_tab():
    """Content for Relational vs Non-Relational Databases tab"""
    st.markdown("## ⚖️ Relational vs Non-Relational Databases")
    st.markdown("*Understanding the fundamental differences and choosing the right approach*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    The choice between **relational** and **non-relational** databases depends on your data structure, 
    consistency requirements, scaling needs, and query patterns. Each approach has distinct advantages 
    for different use cases and application architectures.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Side-by-side comparison
    st.markdown("### 🔄 Architecture Comparison")
    common.mermaid(create_rds_vs_dynamodb_mermaid(), height=400)
    
    # Detailed comparison table
    st.markdown("### 📊 Detailed Feature Comparison")
    
    comparison_data = {
        'Characteristic': [
            'Data Model', 'Schema', 'Query Language', 'Consistency', 
            'Scaling', 'Transactions', 'Performance', 'Use Cases'
        ],
        'Relational (RDBMS)': [
            'Tables with rows and columns',
            'Fixed schema with relationships',
            'SQL (Structured Query Language)',
            'Strong consistency (ACID)',
            'Vertical scaling, read replicas',
            'Multi-row ACID transactions',
            'Complex queries, joins',
            'Traditional applications, reporting'
        ],
        'Non-Relational (NoSQL)': [
            'Key-value, document, graph, column',
            'Flexible or schema-less',
            'API-based or query languages',
            'Eventual consistency (configurable)',
            'Horizontal scaling, distributed',
            'Limited or single-item transactions',
            'Simple queries, high throughput',
            'Web/mobile apps, real-time, IoT'
        ]
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True)
    
    # Interactive Decision Tree
    st.markdown("### 🌳 Interactive Database Decision Tree")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Application Requirements")
        
        data_relationships = st.selectbox("Data Relationships:", [
            "Complex relationships with joins",
            "Simple parent-child relationships", 
            "Independent data items",
            "Hierarchical or nested data"
        ])
        
        query_patterns = st.selectbox("Query Patterns:", [
            "Complex queries with aggregations",
            "Simple key-based lookups",
            "Full-text search",
            "Range queries and filtering"
        ])
        
        consistency_needs = st.selectbox("Consistency Requirements:", [
            "Strong consistency required",
            "Eventual consistency acceptable",
            "Mixed consistency needs"
        ])
    
    with col2:
        st.markdown("### 🚀 Performance & Scale")
        
        expected_scale = st.selectbox("Expected Data Scale:", [
            "Small to Medium (< 1TB)",
            "Large (1TB - 10TB)",
            "Very Large (10TB+)",
            "Massive web scale"
        ])
        
        read_write_pattern = st.selectbox("Read/Write Pattern:", [
            "Read-heavy with occasional writes",
            "Write-heavy with simple reads",
            "Balanced read/write",
            "Unpredictable traffic spikes"
        ])
        
        development_speed = st.checkbox("Rapid development/iteration needed", value=False)
    
    if st.button("🎯 Get Database Recommendation", use_container_width=True):
        # Decision logic
        relational_score = 0
        non_relational_score = 0
        reasons = {'relational': [], 'non_relational': []}
        
        # Analyze data relationships
        if "Complex relationships" in data_relationships:
            relational_score += 3
            reasons['relational'].append("Complex relationships favor relational model")
        elif "Independent data items" in data_relationships:
            non_relational_score += 3
            reasons['non_relational'].append("Independent data works well with NoSQL")
        
        # Query patterns analysis
        if "Complex queries" in query_patterns:
            relational_score += 2
            reasons['relational'].append("SQL excels at complex queries and aggregations")
        elif "Simple key-based lookups" in query_patterns:
            non_relational_score += 2
            reasons['non_relational'].append("NoSQL optimized for key-based access")
        
        # Consistency requirements
        if consistency_needs == "Strong consistency required":
            relational_score += 2
            reasons['relational'].append("ACID compliance ensures strong consistency")
        elif consistency_needs == "Eventual consistency acceptable":
            non_relational_score += 2
            reasons['non_relational'].append("Eventual consistency enables better performance")
        
        # Scale considerations
        if expected_scale == "Massive web scale":
            non_relational_score += 3
            reasons['non_relational'].append("NoSQL designed for web-scale applications")
        elif expected_scale in ["Small to Medium (< 1TB)", "Large (1TB - 10TB)"]:
            relational_score += 1
            reasons['relational'].append("Traditional scale fits well with relational databases")
        
        # Development considerations
        if development_speed:
            non_relational_score += 1
            reasons['non_relational'].append("Schema flexibility speeds development")
        
        # Make recommendation
        if relational_score > non_relational_score:
            recommendation = "Relational Database (Amazon RDS/Aurora)"
            primary_reasons = reasons['relational']
            confidence = min(95, 60 + (relational_score - non_relational_score) * 8)
        elif non_relational_score > relational_score:
            recommendation = "Non-Relational Database (Amazon DynamoDB)"
            primary_reasons = reasons['non_relational']
            confidence = min(95, 60 + (non_relational_score - relational_score) * 8)
        else:
            recommendation = "Hybrid Approach (Both)"
            primary_reasons = ["Consider using both database types for different data"]
            confidence = 70
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 🎯 Recommendation: {recommendation}
        **Confidence Level: {confidence}%**
        
        **Key Factors Supporting This Choice:**
        """)
        for reason in primary_reasons[:3]:  # Show top 3 reasons
            st.markdown(f"✅ {reason}")
        
        if confidence < 80:
            st.markdown(f"""
            
            **⚠️ Consider Hybrid Approach:**
            Your requirements might benefit from using both database types for different aspects of your application.
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Real-world use case examples
    st.markdown("### 🌟 Real-World Use Case Examples")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🏪 E-commerce Platform
        
        **Relational Database Use:**
        - **Order management** - complex relationships
        - **Inventory tracking** - ACID transactions
        - **Financial reporting** - complex queries
        - **User account management** - structured data
        
        **Recommended Service:** Amazon Aurora
        - High performance for read-heavy workloads
        - Strong consistency for financial data
        - Auto-scaling for traffic spikes
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🏦 Banking Application
        
        **Why Relational:**
        - **ACID compliance** mandatory
        - Complex financial calculations
        - Regulatory compliance requirements
        - Audit trails and reporting
        
        **Recommended Service:** Amazon RDS
        - Oracle or SQL Server for compliance
        - Multi-AZ for high availability
        - Automated backups and point-in-time recovery
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📱 Mobile Gaming App
        
        **NoSQL Database Use:**
        - **Player profiles** - flexible schema
        - **Game sessions** - high write volume
        - **Leaderboards** - simple queries
        - **Real-time features** - low latency
        
        **Recommended Service:** Amazon DynamoDB
        - Single-digit millisecond latency
        - Auto-scaling for viral growth
        - Global tables for worldwide players
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🌐 Content Management System
        
        **Why NoSQL:**
        - **Flexible content types** - varying schemas
        - High read volume
        - Content caching needs
        - Rapid feature development
        
        **Recommended Service:** Amazon DocumentDB
        - MongoDB compatibility
        - JSON document storage
        - Flexible indexing
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Performance comparison visualization
    st.markdown("### 📊 Performance Characteristics Comparison")
    
    # Create comparison charts
    metrics = ['Read Latency', 'Write Latency', 'Query Complexity', 'Scaling Ease', 'Consistency']
    relational_scores = [7, 6, 9, 4, 10]
    nosql_scores = [9, 9, 4, 9, 6]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=relational_scores,
        theta=metrics,
        fill='toself',
        name='Relational (RDS/Aurora)',
        fillcolor='rgba(75, 158, 219, 0.3)',
        line=dict(color='rgb(75, 158, 219)')
    ))
    fig.add_trace(go.Scatterpolar(
        r=nosql_scores,
        theta=metrics,
        fill='toself',
        name='NoSQL (DynamoDB)',
        fillcolor='rgba(63, 179, 79, 0.3)',
        line=dict(color='rgb(63, 179, 79)')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=True,
        title="Database Performance Characteristics (1-10 scale)"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Database Selection and Implementation")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Database Selection and Implementation Examples
import boto3
import json
from datetime import datetime

class DatabaseImplementor:
    """Examples of implementing both relational and non-relational patterns"""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.rds_client = boto3.client('rds')
    
    def create_ecommerce_relational_schema(self):
        """Example: E-commerce schema using relational approach"""
        
        # RDS/Aurora SQL schema for e-commerce
        sql_schema = """
        -- Users table with structured data
        CREATE TABLE users (
            user_id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Products with categories and inventory
        CREATE TABLE products (
            product_id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            price DECIMAL(10,2),
            category_id INTEGER,
            inventory_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Orders with ACID compliance
        CREATE TABLE orders (
            order_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id),
            total_amount DECIMAL(10,2),
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE order_items (
            order_item_id SERIAL PRIMARY KEY,
            order_id INTEGER REFERENCES orders(order_id),
            product_id INTEGER REFERENCES products(product_id),
            quantity INTEGER,
            price DECIMAL(10,2)
        );
        
        -- Complex query examples
        SELECT 
            u.email,
            o.order_id,
            o.total_amount,
            COUNT(oi.order_item_id) as item_count
        FROM users u
        JOIN orders o ON u.user_id = o.user_id
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.created_at >= '2024-01-01'
        GROUP BY u.email, o.order_id, o.total_amount
        ORDER BY o.total_amount DESC;
        """
        
        return sql_schema
    
    def create_gaming_nosql_schema(self):
        """Example: Gaming application using NoSQL approach"""
        
        # Create DynamoDB table for gaming app
        try:
            table = self.dynamodb.create_table(
                TableName='GamePlayerData',
                KeySchema=[
                    {
                        'AttributeName': 'player_id',
                        'KeyType': 'HASH'  # Partition key
                    },
                    {
                        'AttributeName': 'game_session_id',
                        'KeyType': 'RANGE'  # Sort key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'player_id',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'game_session_id',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'score',
                        'AttributeType': 'N'
                    }
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'ScoreIndex',
                        'KeySchema': [
                            {
                                'AttributeName': 'score',
                                'KeyType': 'HASH'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'BillingMode': 'PAY_PER_REQUEST'
                    }
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            print(f"Created DynamoDB table: {table.table_name}")
            return table
            
        except Exception as e:
            print(f"Table might already exist: {e}")
            return self.dynamodb.Table('GamePlayerData')
    
    def insert_gaming_data(self, table):
        """Insert flexible gaming data into DynamoDB"""
        
        # Example player data with flexible schema
        player_data = [
            {
                'player_id': 'player123',
                'game_session_id': 'session001',
                'score': 1500,
                'level': 5,
                'achievements': ['first_win', 'speed_demon'],
                'player_stats': {
                    'games_played': 25,
                    'wins': 18,
                    'average_score': 1200
                },
                'last_played': '2024-07-14T10:30:00Z'
            },
            {
                'player_id': 'player456',
                'game_session_id': 'session002',
                'score': 2100,
                'level': 8,
                'achievements': ['master_player', 'perfect_game'],
                'player_stats': {
                    'games_played': 50,
                    'wins': 35,
                    'average_score': 1800
                },
                'custom_settings': {
                    'sound_enabled': True,
                    'difficulty': 'hard',
                    'preferred_character': 'wizard'
                },
                'last_played': '2024-07-14T11:15:00Z'
            }
        ]
        
        # Insert data with flexible schema
        for player in player_data:
            try:
                table.put_item(Item=player)
                print(f"Inserted data for {player['player_id']}")
            except Exception as e:
                print(f"Error inserting player data: {e}")
    
    def query_examples(self):
        """Examples of querying both database types"""
        
        print("=== RELATIONAL DATABASE QUERIES ===")
        print("1. Complex join query for order analysis:")
        print("""
        SELECT 
            DATE(o.created_at) as order_date,
            COUNT(*) as total_orders,
            SUM(o.total_amount) as daily_revenue,
            AVG(o.total_amount) as avg_order_value
        FROM orders o
        WHERE o.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        GROUP BY DATE(o.created_at)
        ORDER BY order_date DESC;
        """)
        
        print("\n2. Inventory management with transactions:")
        print("""
        BEGIN TRANSACTION;
        
        UPDATE products 
        SET inventory_count = inventory_count - 1 
        WHERE product_id = 123 AND inventory_count > 0;
        
        INSERT INTO order_items (order_id, product_id, quantity, price)
        VALUES (456, 123, 1, 29.99);
        
        COMMIT;
        """)
        
        print("\n=== NOSQL DATABASE QUERIES ===")
        print("DynamoDB query examples:")
        
        # DynamoDB query examples
        table = self.dynamodb.Table('GamePlayerData')
        
        try:
            # Get specific player data
            response = table.get_item(
                Key={
                    'player_id': 'player123',
                    'game_session_id': 'session001'
                }
            )
            print("1. Key-based lookup (single-digit millisecond):")
            print(f"Player data: {response.get('Item', 'Not found')}")
            
            # Query all sessions for a player
            response = table.query(
                KeyConditionExpression='player_id = :pid',
                ExpressionAttributeValues={
                    ':pid': 'player123'
                }
            )
            print(f"\n2. Query player sessions: Found {response['Count']} sessions")
            
            # Query global secondary index for leaderboard
            response = table.query(
                IndexName='ScoreIndex',
                KeyConditionExpression='score = :score',
                ExpressionAttributeValues={
                    ':score': 1500
                },
                ScanIndexForward=False  # Descending order
            )
            print(f"3. Leaderboard query: Found {response['Count']} players with score 1500")
            
        except Exception as e:
            print(f"DynamoDB query error: {e}")
    
    def demonstrate_scaling_patterns(self):
        """Show scaling patterns for both database types"""
        
        scaling_examples = {
            'relational_scaling': {
                'vertical_scaling': 'Increase instance size (CPU, RAM)',
                'read_replicas': 'Create read-only copies for read scaling',
                'sharding': 'Partition data across multiple databases',
                'connection_pooling': 'Manage database connections efficiently'
            },
            'nosql_scaling': {
                'auto_scaling': 'DynamoDB auto-adjusts capacity',
                'on_demand': 'Pay per request with unlimited scale',
                'global_tables': 'Multi-region replication',
                'partition_design': 'Distribute data across partitions'
            }
        }
        
        print("SCALING STRATEGIES COMPARISON:")
        print("\nRelational Database Scaling:")
        for strategy, description in scaling_examples['relational_scaling'].items():
            print(f"  • {strategy}: {description}")
        
        print("\nNoSQL Database Scaling:")
        for strategy, description in scaling_examples['nosql_scaling'].items():
            print(f"  • {strategy}: {description}")

# Example usage
if __name__ == "__main__":
    implementor = DatabaseImplementor()
    
    print("🏗️ Database Implementation Examples")
    print("=" * 50)
    
    # Create schemas
    print("\n📊 RELATIONAL SCHEMA (E-commerce):")
    print(implementor.create_ecommerce_relational_schema())
    
    print("\n🎮 NOSQL SCHEMA (Gaming):")
    gaming_table = implementor.create_gaming_nosql_schema()
    implementor.insert_gaming_data(gaming_table)
    
    print("\n🔍 QUERY EXAMPLES:")
    implementor.query_examples()
    
    print("\n📈 SCALING PATTERNS:")
    implementor.demonstrate_scaling_patterns()
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
    st.markdown("# 🗄️ AWS Database Offerings")
    
    st.markdown("""<div class="info-box">
                Explore AWS managed database services and learn to choose between relational and non-relational approaches based on your application requirements, data patterns, and scaling needs.
                </div>""", unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2 = st.tabs([
        "🗄️ AWS Database Ecosystem", 
        "⚖️ Relational vs Non-Relational"
    ])
    
    with tab1:
        aws_database_ecosystem_tab()
    
    with tab2:
        relational_vs_nonrelational_tab()
    
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
