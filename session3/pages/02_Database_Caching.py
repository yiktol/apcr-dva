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
    page_title="AWS Database Caching Hub",
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
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            border-left: 5px solid #00A1C9;
        }}
        
        .footer {{
            margin-top: 20px;
            margin-bottom: 5px;
            padding: 10px;
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
        
        .comparison-table {{
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
            - 🗄️ Amazon ElastiCache - Fully managed in-memory caching
            - ⚖️ Redis vs. Memcached - Compare caching engines
            - 🎯 Use Cases - Real-world caching scenarios
            - 📋 Caching Strategies - Implementation patterns
            
            **Learning Objectives:**
            - Understand in-memory caching concepts
            - Compare Redis and Memcached features
            - Learn caching strategies and best practices
            - Practice with interactive examples and code
            """)

def create_elasticache_architecture_mermaid():
    """Create mermaid diagram for ElastiCache architecture"""
    return """
    graph TB
        subgraph "Application Layer"
            APP[Web Application]
            API[API Server]
        end
        
        subgraph "ElastiCache Layer"
            CACHE[ElastiCache Cluster]
            NODE1[Cache Node 1]
            NODE2[Cache Node 2]
            NODE3[Cache Node 3]
        end
        
        subgraph "Database Layer"
            RDS[(RDS Database)]
            DDB[(DynamoDB)]
        end
        
        APP --> CACHE
        API --> CACHE
        CACHE --> NODE1
        CACHE --> NODE2
        CACHE --> NODE3
        
        CACHE -.->|Cache Miss| RDS
        CACHE -.->|Cache Miss| DDB
        
        style CACHE fill:#FF9900,stroke:#232F3E,color:#fff
        style NODE1 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style NODE2 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style NODE3 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style RDS fill:#3FB34F,stroke:#232F3E,color:#fff
        style DDB fill:#3FB34F,stroke:#232F3E,color:#fff
    """

def create_caching_strategies_mermaid():
    """Create mermaid diagram for caching strategies"""
    return """
    graph TD
        A[Application Request] --> B{Check Cache}
        
        B -->|Hit| C[Return Cached Data]
        B -->|Miss| D[Fetch from Database]
        
        D --> E[Store in Cache]
        E --> F[Return Data to App]
        
        subgraph "Lazy Loading Strategy"
            G[Cache Miss] --> H[Load from DB]
            H --> I[Write to Cache]
        end
        
        subgraph "Write Through Strategy"
            J[Write Data] --> K[Write to Cache]
            K --> L[Write to Database]
        end
        
        subgraph "Write Behind Strategy"
            M[Write Data] --> N[Write to Cache]
            N --> O[Async Write to DB]
        end
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#FF9900,stroke:#232F3E,color:#fff
        style E fill:#FF9900,stroke:#232F3E,color:#fff
    """

def create_redis_vs_memcached_mermaid():
    """Create comparison diagram for Redis vs Memcached"""
    return """
    graph LR
        subgraph "Redis Features"
            R1[Advanced Data Structures]
            R2[Persistence/Snapshots]
            R3[Replication]
            R4[Pub/Sub]
            R5[Transactions]
            R6[Single Threaded]
        end
        
        subgraph "Memcached Features"
            M1[Simple Key-Value]
            M2[No Persistence]
            M3[Data Partitioning]
            M4[Multi-threaded]
            M5[Simpler Architecture]
            M6[Lower Memory Overhead]
        end
        
        subgraph "Common Features"
            C1[Sub-millisecond Latency]
            C2[Horizontal Scaling]
            C3[AWS Managed Service]
        end
        
        style R1 fill:#FF6B35,stroke:#232F3E,color:#fff
        style R2 fill:#FF6B35,stroke:#232F3E,color:#fff
        style R3 fill:#FF6B35,stroke:#232F3E,color:#fff
        style M1 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style M4 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style M5 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C1 fill:#3FB34F,stroke:#232F3E,color:#fff
        style C2 fill:#3FB34F,stroke:#232F3E,color:#fff
        style C3 fill:#3FB34F,stroke:#232F3E,color:#fff
    """

def amazon_elasticache_tab():
    """Content for Amazon ElastiCache overview tab"""
    st.markdown("## 🗄️ Amazon ElastiCache")
    st.markdown("*Fully managed, in-memory caching service supporting flexible, real-time use cases*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Amazon ElastiCache** is a fully managed, in-memory caching service that supports flexible, real-time use cases. 
    It provides sub-millisecond latency and can dramatically improve application performance by storing frequently 
    accessed data in memory rather than fetching it from slower disk-based databases.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ElastiCache Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### <1ms\n**Latency**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 99.99%\n**Availability**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 2\n**Engine Types**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 100x\n**Performance Boost**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Architecture Overview
    st.markdown("### 🏗️ ElastiCache Architecture")
    common.mermaid(create_elasticache_architecture_mermaid(), height=500)
    
    # Interactive Cache Configuration
    st.markdown("### ⚙️ Interactive Cache Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔧 Cache Settings")
        
        engine_type = st.selectbox("Cache Engine:", ["Redis", "Memcached"])
        node_type = st.selectbox("Node Type:", [
            "cache.t3.micro (0.5 GB)", "cache.t3.small (1.37 GB)", 
            "cache.m5.large (6.38 GB)", "cache.r5.large (13.07 GB)"
        ])
        
        num_nodes = st.slider("Number of Nodes:", 1, 20, 3)
        
        if engine_type == "Redis":
            enable_clustering = st.checkbox("Enable Cluster Mode", value=False)
            enable_backup = st.checkbox("Enable Automatic Backup", value=True)
            multi_az = st.checkbox("Multi-AZ Deployment", value=True)
        else:
            enable_clustering = st.checkbox("Enable Auto Discovery", value=True)
            enable_backup = False
            multi_az = False
    
    with col2:
        st.markdown("### 💰 Cost Estimation")
        
        # Calculate estimated costs
        node_costs = {
            "cache.t3.micro (0.5 GB)": 0.017,
            "cache.t3.small (1.37 GB)": 0.034,
            "cache.m5.large (6.38 GB)": 0.192,
            "cache.r5.large (13.07 GB)": 0.252
        }
        
        base_cost = node_costs.get(node_type, 0.017)
        total_hourly = base_cost * num_nodes
        monthly_cost = total_hourly * 24 * 30
        
        if multi_az:
            monthly_cost *= 1.5  # Additional cost for Multi-AZ
        
        st.metric("Hourly Cost", f"${total_hourly:.3f}")
        st.metric("Monthly Cost", f"${monthly_cost:.2f}")
        st.metric("Total Memory", f"{num_nodes * float(node_type.split('(')[1].split(' GB')[0]):.1f} GB")
        
    if st.button("🚀 Deploy ElastiCache Cluster", use_container_width=True):
        cluster_id = f"my-{engine_type.lower()}-cluster-{np.random.randint(1000, 9999)}"
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ ElastiCache Cluster Deployed!
        
        **Cluster Configuration:**
        - **Cluster ID**: {cluster_id}
        - **Engine**: {engine_type}
        - **Node Type**: {node_type}
        - **Number of Nodes**: {num_nodes}
        - **Clustering**: {'✅ Enabled' if enable_clustering else '❌ Disabled'}
        - **Backup**: {'✅ Enabled' if enable_backup else '❌ Disabled'}
        - **Multi-AZ**: {'✅ Enabled' if multi_az else '❌ Disabled'}
        
        **Estimated Performance:**
        - **Latency**: <1ms response time
        - **Throughput**: {num_nodes * 100000:,} operations/sec
        - **High Availability**: {'99.99%' if multi_az else '99.9%'} uptime
        
        🔧 **Endpoint**: {cluster_id}.abc123.cache.amazonaws.com:6379
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Key Benefits
    st.markdown("### ✨ Key Benefits of Amazon ElastiCache")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚡ Performance
        - **Sub-millisecond latency** for data access
        - Dramatically reduce database load
        - **High throughput** - millions of operations/sec
        - In-memory data storage for speed
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛠️ Fully Managed
        - **Automated patching** and updates
        - Hardware provisioning handled
        - **Monitoring and alerting** included
        - Backup and recovery automation
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔒 Secure & Reliable
        - **VPC isolation** and security groups
        - Encryption at rest and in transit
        - **Multi-AZ deployment** options
        - Automatic failover capabilities
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Performance Comparison
    st.markdown("### 📊 Performance Impact Visualization")
    
    # Simulate performance data
    scenarios = ['Without Cache', 'With ElastiCache']
    response_times = [250, 2]  # milliseconds
    database_load = [100, 20]  # percentage
    cost_efficiency = [100, 140]  # relative efficiency
    
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('Response Time (ms)', 'Database Load (%)', 'Cost Efficiency'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]]
    )
    
    fig.add_trace(
        go.Bar(x=scenarios, y=response_times, name='Response Time', 
               marker_color=AWS_COLORS['primary']),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=scenarios, y=database_load, name='Database Load',
               marker_color=AWS_COLORS['light_blue']),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Bar(x=scenarios, y=cost_efficiency, name='Cost Efficiency',
               marker_color=AWS_COLORS['success']),
        row=1, col=3
    )
    
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Basic ElastiCache Implementation")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Basic ElastiCache implementation with Python
import boto3
import redis
import json
from datetime import datetime, timedelta

class ElastiCacheManager:
    def __init__(self, cluster_endpoint, port=6379):
        """Initialize ElastiCache connection"""
        self.redis_client = redis.Redis(
            host=cluster_endpoint,
            port=port,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        
    def get_data(self, key):
        """Get data from cache"""
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set_data(self, key, data, ttl=3600):
        """Set data in cache with TTL (default 1 hour)"""
        try:
            serialized_data = json.dumps(data, default=str)
            return self.redis_client.setex(key, ttl, serialized_data)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete_data(self, key):
        """Delete data from cache"""
        try:
            return self.redis_client.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def get_cache_info(self):
        """Get cache statistics"""
        try:
            info = self.redis_client.info()
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'instantaneous_ops_per_sec': info.get('instantaneous_ops_per_sec', 0)
            }
        except Exception as e:
            print(f"Cache info error: {e}")
            return {}

def create_elasticache_cluster():
    """Create ElastiCache Redis cluster using boto3"""
    client = boto3.client('elasticache')
    
    try:
        response = client.create_cache_cluster(
            CacheClusterId='my-redis-cluster',
            Engine='redis',
            CacheNodeType='cache.t3.micro',
            NumCacheNodes=1,
            Port=6379,
            CacheParameterGroupName='default.redis7',
            CacheSubnetGroupName='my-cache-subnet-group',
            SecurityGroupIds=['sg-12345678'],
            Tags=[
                {
                    'Key': 'Environment',
                    'Value': 'Development'
                },
                {
                    'Key': 'Application',
                    'Value': 'WebApp'
                }
            ]
        )
        
        print("✅ Cache cluster creation initiated")
        print(f"Cluster ID: {response['CacheCluster']['CacheClusterId']}")
        print(f"Status: {response['CacheCluster']['CacheClusterStatus']}")
        
        return response['CacheCluster']['CacheClusterId']
        
    except Exception as e:
        print(f"❌ Error creating cluster: {e}")
        return None

# Example usage with database fallback pattern
def get_user_profile(user_id, cache_manager, database_connection=None):
    """Get user profile with cache-aside pattern"""
    cache_key = f"user_profile:{user_id}"
    
    # Try to get from cache first
    user_data = cache_manager.get_data(cache_key)
    
    if user_data:
        print(f"✅ Cache HIT for user {user_id}")
        return user_data
    
    print(f"❌ Cache MISS for user {user_id}")
    
    # Fallback to database (simulated)
    if database_connection:
        # Simulate database query
        user_data = {
            'user_id': user_id,
            'name': f'User {user_id}',
            'email': f'user{user_id}@example.com',
            'last_login': datetime.now().isoformat(),
            'preferences': {
                'theme': 'dark',
                'notifications': True
            }
        }
        
        # Store in cache for next time (TTL: 1 hour)
        cache_manager.set_data(cache_key, user_data, ttl=3600)
        print(f"💾 Stored user {user_id} in cache")
        
        return user_data
    
    return None

# Example implementation
if __name__ == "__main__":
    # Initialize cache manager
    cache = ElastiCacheManager('my-redis-cluster.abc123.cache.amazonaws.com')
    
    # Test the cache
    user_profile = get_user_profile(1001, cache, database_connection=True)
    print(f"User Profile: {user_profile}")
    
    # Get cache statistics
    stats = cache.get_cache_info()
    print(f"Cache Stats: {stats}")
    
    # Create new cluster (if needed)
    # cluster_id = create_elasticache_cluster()
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def redis_vs_memcached_tab():
    """Content for Redis vs Memcached comparison tab"""
    st.markdown("## ⚖️ Redis vs. Memcached")
    st.markdown("*Compare the two caching engines supported by Amazon ElastiCache*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    Amazon ElastiCache supports two popular open-source caching engines: **Redis** and **Memcached**. 
    Each has unique strengths and is optimized for different use cases. Understanding their differences 
    helps you choose the right engine for your application needs.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Visual Comparison
    st.markdown("### 🔄 Engine Comparison Overview")
    common.mermaid(create_redis_vs_memcached_mermaid(), height=510)
    
    # Interactive Comparison Tool
    st.markdown("### 🎯 Interactive Engine Selector")
    
    st.markdown("**Answer a few questions to get a recommendation:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        data_structures = st.multiselect("What data structures do you need?", [
            "Simple key-value pairs", "Lists", "Sets", "Sorted sets", 
            "Hashes", "Bit arrays", "HyperLogLogs"
        ])
        
        persistence_needed = st.radio("Do you need data persistence?", 
                                    ["No persistence needed", "Snapshots for backup", "Full persistence"])
        
        replication_needed = st.radio("Do you need replication?", 
                                    ["No replication", "Read replicas", "Multi-master"])
    
    with col2:
        performance_priority = st.radio("Performance priority:", 
                                      ["Maximum throughput", "Lowest latency", "Balanced"])
        
        complexity_preference = st.radio("Architecture preference:", 
                                       ["Simple and straightforward", "Feature-rich and flexible"])
        
        use_case = st.selectbox("Primary use case:", [
            "Simple caching", "Session store", "Real-time analytics", 
            "Gaming leaderboards", "Chat/messaging", "Pub/Sub messaging"
        ])
    
    if st.button("🤖 Get Engine Recommendation", use_container_width=True):
        # Simple recommendation logic
        redis_score = 0
        memcached_score = 0
        
        # Score based on data structures
        if len([x for x in data_structures if x != "Simple key-value pairs"]) > 0:
            redis_score += 3
        else:
            memcached_score += 2
        
        # Score based on persistence
        if "persistence" in persistence_needed.lower():
            redis_score += 3
        else:
            memcached_score += 1
        
        # Score based on replication
        if "replicas" in replication_needed or "Multi-master" in replication_needed:
            redis_score += 2
        
        # Score based on performance
        if performance_priority == "Maximum throughput":
            memcached_score += 2
        elif performance_priority == "Lowest latency":
            redis_score += 1
        
        # Score based on complexity
        if complexity_preference == "Simple and straightforward":
            memcached_score += 2
        else:
            redis_score += 2
        
        # Score based on use case
        complex_use_cases = ["Real-time analytics", "Gaming leaderboards", "Chat/messaging", "Pub/Sub messaging"]
        if use_case in complex_use_cases:
            redis_score += 3
        else:
            memcached_score += 1
        
        recommended_engine = "Redis" if redis_score > memcached_score else "Memcached"
        confidence = abs(redis_score - memcached_score) * 10
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 🎯 Recommendation: {recommended_engine}
        
        **Confidence Level**: {min(confidence, 95)}%
        
        **Reasoning:**
        - **Data Structures**: {'Advanced structures needed' if len([x for x in data_structures if x != "Simple key-value pairs"]) > 0 else 'Simple key-value sufficient'}
        - **Persistence**: {persistence_needed}
        - **Replication**: {replication_needed}
        - **Performance Focus**: {performance_priority}
        - **Use Case**: {use_case}
        """)
        
        if recommended_engine == "Redis":
            st.markdown("""
            **Why Redis?**
            - Advanced data structures support your needs
            - Persistence and replication capabilities
            - Better suited for complex use cases
            - Rich feature set matches requirements
            """)
        else:
            st.markdown("""
            **Why Memcached?**
            - Simple architecture fits your needs
            - Multi-threaded performance advantage
            - Lower overhead for basic caching
            - Easier to manage and maintain
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed Feature Comparison
    st.markdown("### 📋 Detailed Feature Comparison")
    
    comparison_data = {
        'Feature': [
            'Data Structures', 'Persistence', 'Replication', 'Transactions', 
            'Pub/Sub', 'Multi-threading', 'Memory Usage', 'Snapshots',
            'Partitioning', 'Lua Scripts', 'Geospatial', 'Clustering'
        ],
        'Redis': [
            '✅ Lists, Sets, Hashes, etc.', '✅ RDB & AOF', '✅ Master-Slave', 
            '✅ MULTI/EXEC', '✅ Built-in', '❌ Single-threaded', 
            'Higher', '✅ Point-in-time', '✅ Hash-based', 
            '✅ Server-side scripting', '✅ Geographic data', '✅ Redis Cluster'
        ],
        'Memcached': [
            '❌ Key-Value only', '❌ No persistence', '❌ No replication',
            '❌ No transactions', '❌ No pub/sub', '✅ Multi-threaded',
            'Lower', '❌ No snapshots', '✅ Consistent hashing',
            '❌ No scripting', '❌ No geospatial', '❌ Simple scaling'
        ]
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True)
    
    # Performance Benchmarks
    st.markdown("### 📊 Performance Benchmarks")
    
    benchmark_data = {
        'Metric': ['Throughput (ops/sec)', 'Memory Efficiency', 'CPU Usage', 'Network Efficiency'],
        'Redis': [100000, 85, 'Single-core intensive', 'Efficient'],
        'Memcached': [150000, 90, 'Multi-core optimized', 'Very efficient'],
        'Winner': ['Memcached', 'Memcached', 'Memcached', 'Memcached']
    }
    
    # Create performance comparison chart
    operations_data = pd.DataFrame({
        'Engine': ['Redis', 'Memcached'],
        'Read Operations': [110000, 150000],
        'Write Operations': [90000, 130000],
        'Mixed Workload': [100000, 140000]
    })
    
    fig = px.bar(operations_data, x='Engine', y=['Read Operations', 'Write Operations', 'Mixed Workload'],
                 title='Performance Comparison (Operations per Second)',
                 color_discrete_sequence=[AWS_COLORS['primary'], AWS_COLORS['light_blue'], AWS_COLORS['success']])
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Use Case Matrix
    st.markdown("### 🎯 Use Case Decision Matrix")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎮 Choose Redis When:
        
        **Complex Data Operations:**
        - Gaming leaderboards (sorted sets)
        - Real-time analytics (multiple data types)
        - Social media feeds (lists, sets)
        - Geographic applications (geospatial)
        
        **Advanced Features Needed:**
        - Data persistence and backup
        - Pub/Sub messaging
        - Read replicas for scaling
        - Complex queries and scripts
        
        **Example Use Cases:**
        - Gaming platforms
        - Real-time chat applications  
        - IoT data processing
        - Machine learning feature storage
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🚀 Choose Memcached When:
        
        **Simple Caching Needs:**
        - Database query result caching
        - Session storage (simple key-value)
        - Page fragment caching
        - API response caching
        
        **Performance Critical:**
        - High-throughput applications
        - Multi-threaded workloads
        - Memory-constrained environments
        - Simple horizontal scaling
        
        **Example Use Cases:**
        - E-commerce websites
        - Content management systems
        - Web application acceleration
        - Database query optimization
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Examples
    st.markdown("### 💻 Code Examples: Redis vs Memcached")
    
    tab1, tab2 = st.tabs(["🔴 Redis Example", "🔵 Memcached Example"])
    
    with tab1:
        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code('''
# Redis Advanced Features Example
import redis
import json
from datetime import datetime

class RedisAdvancedCache:
    def __init__(self, host, port=6379):
        self.redis = redis.Redis(host=host, port=port, decode_responses=True)
    
    def gaming_leaderboard(self, game_id):
        """Implement gaming leaderboard using Redis sorted sets"""
        leaderboard_key = f"leaderboard:{game_id}"
        
        # Add players with scores
        self.redis.zadd(leaderboard_key, {
            "player1": 1500,
            "player2": 2100,
            "player3": 1800,
            "player4": 2300
        })
        
        # Get top 10 players
        top_players = self.redis.zrevrange(leaderboard_key, 0, 9, withscores=True)
        return [(player, int(score)) for player, score in top_players]
    
    def real_time_analytics(self, event_type, data):
        """Store real-time analytics using Redis hashes and lists"""
        # Store event in time-series list
        event_key = f"events:{event_type}:{datetime.now().strftime('%Y-%m-%d')}"
        self.redis.lpush(event_key, json.dumps({
            'timestamp': datetime.now().isoformat(),
            'data': data
        }))
        
        # Update counters in hash
        counter_key = f"counters:{event_type}"
        self.redis.hincrby(counter_key, 'total_events', 1)
        self.redis.hincrby(counter_key, 'daily_events', 1)
        
        # Set expiry for daily counter
        self.redis.expire(counter_key, 86400)  # 24 hours
    
    def pub_sub_messaging(self):
        """Implement pub/sub messaging system"""
        def message_handler(message):
            print(f"Received: {message['data']}")
        
        # Subscribe to channels
        pubsub = self.redis.pubsub()
        pubsub.subscribe('notifications', 'alerts')
        
        # Publish messages
        self.redis.publish('notifications', 'New user registered')
        self.redis.publish('alerts', 'High CPU usage detected')
        
        return pubsub
    
    def geospatial_features(self):
        """Use Redis geospatial features for location-based services"""
        locations_key = "driver_locations"
        
        # Add driver locations (longitude, latitude)
        self.redis.geoadd(locations_key, [
            (-122.4194, 37.7749, "driver1"),  # San Francisco
            (-118.2437, 34.0522, "driver2"),  # Los Angeles  
            (-74.0060, 40.7128, "driver3")    # New York
        ])
        
        # Find drivers within 10km of a location
        nearby_drivers = self.redis.georadius(
            locations_key, -122.4194, 37.7749, 10, unit='km'
        )
        
        return nearby_drivers
    
    def advanced_data_structures(self):
        """Demonstrate various Redis data structures"""
        examples = {}
        
        # Lists - for activity feeds
        self.redis.lpush("user:1001:feed", "Post 1", "Post 2", "Post 3")
        examples['feed'] = self.redis.lrange("user:1001:feed", 0, -1)
        
        # Sets - for tags or categories
        self.redis.sadd("article:123:tags", "python", "redis", "caching", "database")
        examples['tags'] = self.redis.smembers("article:123:tags")
        
        # Hashes - for object storage
        self.redis.hset("user:1001", mapping={
            "name": "John Doe",
            "email": "john@example.com", 
            "last_login": datetime.now().isoformat()
        })
        examples['user'] = self.redis.hgetall("user:1001")
        
        return examples

# Example usage
cache = RedisAdvancedCache('my-redis-cluster.amazonaws.com')

# Gaming leaderboard
leaderboard = cache.gaming_leaderboard("game_123")
print(f"Top players: {leaderboard}")

# Real-time analytics
cache.real_time_analytics("page_view", {"page": "/home", "user_id": 1001})

# Advanced data structures
examples = cache.advanced_data_structures()
print(f"Data structure examples: {examples}")
        ''', language='python')
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code('''
# Memcached Simple and Efficient Caching Example
import memcache
import json
import hashlib
from datetime import datetime, timedelta

class MemcachedSimpleCache:
    def __init__(self, servers):
        """Initialize Memcached client with multiple servers"""
        self.mc = memcache.Client(servers, debug=0)
        self.default_ttl = 3600  # 1 hour
    
    def database_query_cache(self, query, params=None):
        """Cache database query results"""
        # Create cache key from query and parameters
        cache_key = self._generate_cache_key(query, params)
        
        # Try to get from cache
        result = self.mc.get(cache_key)
        if result:
            print(f"✅ Cache HIT for query: {query[:50]}...")
            return json.loads(result)
        
        print(f"❌ Cache MISS for query: {query[:50]}...")
        
        # Simulate database query (replace with actual DB call)
        result = self._simulate_database_query(query, params)
        
        # Store in cache with TTL
        self.mc.set(cache_key, json.dumps(result, default=str), time=self.default_ttl)
        
        return result
    
    def session_storage(self, session_id, session_data=None):
        """Simple session storage and retrieval"""
        session_key = f"session:{session_id}"
        
        if session_data is not None:
            # Store session data (expires in 2 hours)
            success = self.mc.set(session_key, json.dumps(session_data), time=7200)
            return success
        else:
            # Retrieve session data
            data = self.mc.get(session_key)
            return json.loads(data) if data else None
    
    def page_fragment_cache(self, page_id, fragment_name, content=None):
        """Cache page fragments for faster rendering"""
        fragment_key = f"page:{page_id}:fragment:{fragment_name}"
        
        if content is not None:
            # Store page fragment (expires in 30 minutes)
            return self.mc.set(fragment_key, content, time=1800)
        else:
            # Retrieve page fragment
            return self.mc.get(fragment_key)
    
    def api_response_cache(self, endpoint, params, response=None):
        """Cache API responses to reduce external calls"""
        api_key = f"api:{endpoint}:{self._hash_params(params)}"
        
        if response is not None:
            # Cache API response (expires in 5 minutes)
            return self.mc.set(api_key, json.dumps(response), time=300)
        else:
            # Get cached API response
            cached = self.mc.get(api_key)
            return json.loads(cached) if cached else None
    
    def distributed_caching(self):
        """Demonstrate distributed caching across multiple nodes"""
        # Memcached automatically distributes keys across multiple servers
        # based on consistent hashing
        
        test_data = {
            "user:1001": {"name": "Alice", "role": "admin"},
            "user:1002": {"name": "Bob", "role": "user"}, 
            "user:1003": {"name": "Charlie", "role": "moderator"}
        }
        
        # Store data (will be distributed across servers)
        for key, data in test_data.items():
            self.mc.set(key, json.dumps(data), time=3600)
        
        # Retrieve data (client handles which server to query)
        retrieved_data = {}
        for key in test_data.keys():
            cached = self.mc.get(key)
            if cached:
                retrieved_data[key] = json.loads(cached)
        
        return retrieved_data
    
    def batch_operations(self, keys_data):
        """Efficient batch operations for high throughput"""
        # Batch set multiple keys
        success = self.mc.set_multi(keys_data, time=self.default_ttl)
        
        # Batch get multiple keys  
        results = self.mc.get_multi(list(keys_data.keys()))
        
        return results
    
    def cache_statistics(self):
        """Get cache statistics from all servers"""
        stats = self.mc.get_stats()
        
        total_stats = {
            'total_items': 0,
            'total_bytes': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'hit_rate': 0
        }
        
        for server, server_stats in stats:
            if server_stats:
                total_stats['total_items'] += int(server_stats.get('curr_items', 0))
                total_stats['total_bytes'] += int(server_stats.get('bytes', 0))
                total_stats['cache_hits'] += int(server_stats.get('get_hits', 0))
                total_stats['cache_misses'] += int(server_stats.get('get_misses', 0))
        
        # Calculate hit rate
        total_requests = total_stats['cache_hits'] + total_stats['cache_misses']
        if total_requests > 0:
            total_stats['hit_rate'] = (total_stats['cache_hits'] / total_requests) * 100
        
        return total_stats
    
    def _generate_cache_key(self, query, params):
        """Generate consistent cache key from query and parameters"""
        key_data = f"{query}:{params}" if params else query
        return hashlib.md5(key_data.encode()).hexdigest()[:16]
    
    def _hash_params(self, params):
        """Hash parameters for consistent cache keys"""
        param_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(param_str.encode()).hexdigest()[:8]
    
    def _simulate_database_query(self, query, params):
        """Simulate database query execution"""
        # This would be replaced with actual database calls
        return {
            'query': query,
            'params': params,
            'results': [{'id': 1, 'name': 'Sample Data'}],
            'execution_time': 0.150,  # 150ms
            'timestamp': datetime.now().isoformat()
        }

# Example usage
servers = [
    'memcached-node1.amazonaws.com:11211',
    'memcached-node2.amazonaws.com:11211', 
    'memcached-node3.amazonaws.com:11211'
]

cache = MemcachedSimpleCache(servers)

# Database query caching
result = cache.database_query_cache(
    "SELECT * FROM users WHERE active = %s", 
    params=[True]
)

# Session management
cache.session_storage('sess_123', {'user_id': 1001, 'logged_in': True})
session = cache.session_storage('sess_123')

# Page fragment caching  
cache.page_fragment_cache('homepage', 'header', '<header>Welcome!</header>')
header = cache.page_fragment_cache('homepage', 'header')

# Get cache statistics
stats = cache.cache_statistics()
print(f"Cache Statistics: {stats}")
        ''', language='python')
        st.markdown('</div>', unsafe_allow_html=True)

def use_cases_tab():
    """Content for ElastiCache use cases tab"""
    st.markdown("## 🎯 Amazon ElastiCache - Use Cases")
    st.markdown("*Real-world scenarios where ElastiCache provides ultrafast performance and cost savings*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **ElastiCache Use Cases** span various industries and applications where **sub-millisecond latency** and 
    **high throughput** are critical. The primary purpose is to provide ultrafast access to copies of data, 
    reducing database load and improving user experience.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Use Case Explorer
    st.markdown("### 🔍 Interactive Use Case Explorer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        industry = st.selectbox("Select Industry:", [
            "E-commerce & Retail", "Gaming", "Media & Entertainment", 
            "Financial Services", "Healthcare", "IoT & Real-time Analytics"
        ])
        
        application_type = st.selectbox("Application Type:", [
            "Web Application", "Mobile App", "API Service", 
            "Real-time Dashboard", "Gaming Platform", "IoT System"
        ])
    
    with col2:
        performance_requirement = st.selectbox("Performance Requirement:", [
            "Sub-millisecond response", "High throughput", "Real-time updates",
            "Reduced database load", "Session management", "Cache invalidation"
        ])
        
        data_pattern = st.selectbox("Data Access Pattern:", [
            "Read-heavy workload", "Write-heavy workload", "Mixed workload",
            "Seasonal traffic", "Burst traffic", "Consistent load"
        ])
    
    if st.button("🎯 Find Optimal Use Case", use_container_width=True):
        # Generate recommendations based on selections
        use_case_recommendations = {
            "E-commerce & Retail": {
                "primary_use": "Product catalog caching and session management",
                "specific_benefits": ["Product details cache", "Shopping cart sessions", "Inventory tracking"],
                "expected_improvement": "60-80% faster page loads",
                "cache_strategy": "Write-through with TTL"
            },
            "Gaming": {
                "primary_use": "Leaderboards, player sessions, and real-time data",
                "specific_benefits": ["Gaming leaderboards", "Player state caching", "Real-time multiplayer data"],
                "expected_improvement": "90% reduction in database queries",
                "cache_strategy": "Write-behind with sorted sets"
            },
            "Financial Services": {
                "primary_use": "High-frequency trading data and fraud detection",
                "specific_benefits": ["Market data caching", "Risk calculations", "Fraud pattern detection"],
                "expected_improvement": "Sub-millisecond trading decisions",
                "cache_strategy": "Write-through with high availability"
            }
        }
        
        recommendation = use_case_recommendations.get(industry, use_case_recommendations["E-commerce & Retail"])
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 🎯 Optimal Use Case: {recommendation['primary_use']}
        
        **Industry**: {industry}
        **Application**: {application_type}
        
        **Specific Benefits:**
        - {recommendation['specific_benefits'][0]}
        - {recommendation['specific_benefits'][1]}
        - {recommendation['specific_benefits'][2]}
        
        **Expected Improvement**: {recommendation['expected_improvement']}
        **Recommended Strategy**: {recommendation['cache_strategy']}
        **Performance Requirement**: {performance_requirement}
        **Data Pattern**: {data_pattern}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed Use Cases
    st.markdown("### 🌟 Detailed Use Case Scenarios")
    
    use_case_tabs = st.tabs([
        "🛒 E-commerce", "🎮 Gaming", "📱 Social Media", 
        "💰 FinTech", "🏥 Healthcare", "🏭 IoT & Analytics"
    ])
    
    with use_case_tabs[0]:  # E-commerce
        st.markdown("### 🛒 E-commerce & Retail Applications")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 🏪 Product Catalog Caching
            **Challenge**: Database overload during peak shopping
            
            **Solution**: Cache product details, prices, inventory
            - **Cache TTL**: 15 minutes for prices, 1 hour for descriptions
            - **Cache Strategy**: Write-through with invalidation
            - **Performance Gain**: 70% faster product pages
            - **Cost Savings**: 60% reduction in database queries
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 🛍️ Shopping Cart Sessions
            **Challenge**: Session data persistence and scalability
            
            **Solution**: Store cart data in ElastiCache
            - **Session TTL**: 30 minutes idle timeout
            - **Data Structure**: Hash for cart items
            - **Benefit**: Instant cart updates across devices
            - **Scalability**: Handle millions of concurrent sessions
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 📊 Real-time Inventory
            **Challenge**: Accurate inventory during flash sales
            
            **Solution**: Cache inventory counts with atomic operations
            - **Update Strategy**: Decrement on purchase
            - **Consistency**: Redis transactions for accuracy
            - **Performance**: Handle 10,000+ purchases/second
            - **Recovery**: Database sync for data consistency
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 🎯 Personalized Recommendations
            **Challenge**: Real-time personalization at scale
            
            **Solution**: Cache user preferences and recommendations
            - **Machine Learning**: Store ML model results
            - **User Behavior**: Track clicks, views, purchases
            - **Real-time**: Update recommendations instantly
            - **A/B Testing**: Cache different recommendation variants
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # E-commerce metrics
        ecommerce_metrics = {
            'Metric': ['Page Load Time', 'Database Load', 'Cart Abandonment', 'Conversion Rate'],
            'Before Cache': ['3.2s', '85%', '68%', '2.1%'],
            'After Cache': ['0.8s', '25%', '45%', '3.8%'],
            'Improvement': ['75% faster', '60% reduction', '23% reduction', '81% increase']
        }
        
        df_ecommerce = pd.DataFrame(ecommerce_metrics)
        st.dataframe(df_ecommerce, use_container_width=True)
    
    with use_case_tabs[1]:  # Gaming
        st.markdown("### 🎮 Gaming Platform Applications")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 🏆 Gaming Leaderboards
            **Challenge**: Real-time rankings for millions of players
            
            **Solution**: Redis Sorted Sets for leaderboards
            - **Data Structure**: ZADD for score updates
            - **Queries**: ZRANGE for top players
            - **Performance**: Update scores in <1ms
            - **Scalability**: Handle millions of players
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 👤 Player Session Management
            **Challenge**: Maintain player state across game sessions
            
            **Solution**: Cache player profiles and game state
            - **Player Stats**: Level, achievements, inventory
            - **Game State**: Current position, progress, settings
            - **Cross-platform**: Sync across mobile, web, console
            - **Persistence**: Backup to database periodically
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### ⚡ Real-time Multiplayer
            **Challenge**: Low-latency multiplayer interactions
            
            **Solution**: Cache game world state and player actions
            - **World State**: Map data, NPC positions
            - **Player Actions**: Movement, attacks, chat
            - **Pub/Sub**: Real-time event broadcasting
            - **Latency**: <10ms response times
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 🎲 Game Analytics
            **Challenge**: Real-time game analytics and metrics
            
            **Solution**: Stream analytics data through cache
            - **Player Behavior**: Track actions, preferences
            - **Game Balance**: Monitor difficulty, progression
            - **Revenue Metrics**: In-app purchases, retention
            - **A/B Testing**: Game feature experiments
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Gaming performance simulation
        st.markdown("### 🎮 Gaming Performance Simulator")
        
        player_count = st.slider("Concurrent Players:", 1000, 1000000, 50000)
        update_frequency = st.slider("Updates per Second:", 10, 1000, 100)
        
        # Calculate gaming metrics
        total_operations = player_count * update_frequency
        cache_memory = (player_count * 2) / 1024  # 2KB per player profile
        estimated_latency = max(1, 50 - (np.log10(player_count) * 5))  # Logarithmic scaling
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Operations/Second", f"{total_operations:,}")
        with col2:
            st.metric("Memory Required", f"{cache_memory:.1f} GB")
        with col3:
            st.metric("Estimated Latency", f"{estimated_latency:.1f}ms")
    
    with use_case_tabs[2]:  # Social Media
        st.markdown("### 📱 Social Media Applications")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 📰 News Feed Caching
            **Challenge**: Personalized feeds for millions of users
            
            **Solution**: Cache user timelines and popular content
            - **Timeline Cache**: Recent posts for each user
            - **Popular Content**: Trending posts across platform
            - **Real-time Updates**: New posts appear instantly
            - **Memory Management**: LRU eviction for old content
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 💬 Real-time Messaging
            **Challenge**: Instant message delivery and chat history
            
            **Solution**: Redis Pub/Sub for real-time messaging
            - **Message Delivery**: Instant push notifications
            - **Chat History**: Recent messages in cache
            - **Online Status**: Track user presence
            - **Group Chats**: Broadcast to multiple users
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 👥 Social Graph Caching
            **Challenge**: Friend networks and relationship data
            
            **Solution**: Cache social connections and interactions
            - **Friend Lists**: User connections and followers
            - **Mutual Friends**: Common connections calculation
            - **Activity Feeds**: Friend activities and updates
            - **Recommendation Engine**: Friend suggestions
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 📈 Content Analytics
            **Challenge**: Real-time engagement metrics
            
            **Solution**: Track likes, shares, comments in real-time
            - **Engagement Counters**: Likes, shares, views
            - **Trending Analysis**: Viral content detection
            - **User Analytics**: Behavior patterns, preferences
            - **Content Optimization**: A/B test different formats
            """)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with use_case_tabs[3]:  # FinTech
        st.markdown("### 💰 Financial Services Applications")
        
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚡ High-Frequency Trading & Risk Management
        Financial services require the lowest possible latency for trading decisions and risk calculations.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 📊 Market Data Caching
            **Challenge**: Real-time market data for trading algorithms
            
            **Solution**: Cache streaming market data
            - **Price Feeds**: Stock prices, currency rates
            - **Order Book**: Bid/ask spreads, market depth
            - **Technical Indicators**: Moving averages, RSI
            - **Latency**: <100 microseconds for critical data
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 🛡️ Fraud Detection
            **Challenge**: Real-time fraud pattern detection
            
            **Solution**: Cache user behavior patterns
            - **Transaction History**: Recent transaction patterns
            - **Risk Scoring**: Real-time risk calculations
            - **Anomaly Detection**: Unusual activity flagging
            - **Response Time**: Flag suspicious activity in <50ms
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### ⚖️ Risk Management
            **Challenge**: Real-time portfolio risk calculations
            
            **Solution**: Cache risk metrics and exposures
            - **Portfolio Positions**: Real-time position tracking
            - **Risk Metrics**: VaR, Greeks, correlations
            - **Stress Testing**: Scenario analysis results
            - **Compliance**: Real-time limit monitoring
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 💳 Payment Processing
            **Challenge**: High-throughput payment validation
            
            **Solution**: Cache payment rules and user data
            - **Payment Rules**: Validation logic, limits
            - **User Profiles**: Payment history, preferences
            - **Merchant Data**: Processing rules, fees
            - **Throughput**: Process 100,000+ payments/second
            """)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with use_case_tabs[4]:  # Healthcare
        st.markdown("### 🏥 Healthcare Applications")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 📋 Electronic Health Records
            **Challenge**: Fast access to patient data
            
            **Solution**: Cache frequently accessed patient records
            - **Patient Data**: Demographics, medical history
            - **Recent Tests**: Lab results, imaging reports
            - **Medications**: Current prescriptions, allergies
            - **Access Control**: Role-based data access
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 🔬 Medical Imaging
            **Challenge**: Fast retrieval of large medical images
            
            **Solution**: Cache medical images and metadata
            - **Image Cache**: X-rays, MRIs, CT scans
            - **Metadata**: Patient info, study details
            - **Preprocessing**: Cached image analysis results
            - **Performance**: Instant image loading for diagnosis
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 📱 Telemedicine
            **Challenge**: Real-time patient monitoring
            
            **Solution**: Cache vital signs and patient status
            - **Vital Signs**: Heart rate, blood pressure, temperature
            - **Alert Thresholds**: Patient-specific warning levels
            - **Medication Reminders**: Dosage schedules
            - **Communication**: Doctor-patient messaging
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 🧬 Research Data
            **Challenge**: Complex medical research queries
            
            **Solution**: Cache research datasets and analysis
            - **Clinical Trials**: Patient data, trial results
            - **Genomics**: DNA sequence analysis results
            - **Drug Discovery**: Compound screening data
            - **Performance**: Accelerate research by 10x
            """)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with use_case_tabs[5]:  # IoT & Analytics
        st.markdown("### 🏭 IoT & Real-time Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 🌡️ IoT Sensor Data
            **Challenge**: High-volume sensor data processing
            
            **Solution**: Cache sensor readings and aggregations
            - **Sensor Readings**: Temperature, humidity, pressure
            - **Time Series**: Historical trends and patterns
            - **Aggregations**: Min, max, average over time periods
            - **Alerts**: Threshold-based notifications
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 🏭 Industrial Monitoring
            **Challenge**: Real-time equipment monitoring
            
            **Solution**: Cache equipment status and metrics
            - **Equipment Status**: Operational state, health
            - **Performance Metrics**: Efficiency, utilization
            - **Predictive Maintenance**: Failure predictions
            - **Downtime Prevention**: Proactive maintenance alerts
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 📊 Real-time Dashboards
            **Challenge**: Live analytics dashboards
            
            **Solution**: Cache dashboard data and KPIs
            - **KPI Calculations**: Real-time metric computation
            - **Data Aggregation**: Roll-up summaries
            - **Visualization Data**: Chart and graph data
            - **Update Frequency**: Dashboard refresh every second
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 🚗 Smart City Applications
            **Challenge**: City-wide data integration
            
            **Solution**: Cache urban data for smart city services
            - **Traffic Data**: Real-time traffic conditions
            - **Public Transport**: Bus/train schedules, delays
            - **Environmental**: Air quality, noise levels
            - **Emergency Services**: Resource allocation, response
            """)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # ROI Calculator
    st.markdown("### 💰 ElastiCache ROI Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Current Infrastructure")
        database_queries_per_second = st.number_input("Database Queries/Second:", 100, 100000, 1000)
        average_query_time = st.number_input("Average Query Time (ms):", 10, 1000, 100)
        database_server_cost = st.number_input("Monthly Database Server Cost ($):", 100, 10000, 500)
        
    with col2:
        st.markdown("#### ⚡ With ElastiCache")
        cache_hit_rate = st.slider("Expected Cache Hit Rate (%):", 50, 95, 80)
        cache_response_time = st.number_input("Cache Response Time (ms):", 0.1, 10.0, 1.0)
        elasticache_cost = st.number_input("Monthly ElastiCache Cost ($):", 50, 2000, 200)
    
    if st.button("💰 Calculate ROI", use_container_width=True):
        # Calculate performance improvements
        cached_queries = database_queries_per_second * (cache_hit_rate / 100)
        database_queries = database_queries_per_second * ((100 - cache_hit_rate) / 100)
        
        # Average response time with cache
        avg_response_with_cache = (cached_queries * cache_response_time + database_queries * average_query_time) / database_queries_per_second
        
        # Performance improvement
        performance_improvement = ((average_query_time - avg_response_with_cache) / average_query_time) * 100
        
        # Cost analysis
        total_monthly_cost = database_server_cost + elasticache_cost
        cost_per_query_improvement = (performance_improvement / 100) * database_server_cost
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 💰 ROI Analysis Results
        
        **Performance Improvements:**
        - **Response Time**: {average_query_time:.1f}ms → {avg_response_with_cache:.1f}ms
        - **Performance Improvement**: {performance_improvement:.1f}% faster
        - **Database Load Reduction**: {cache_hit_rate}% of queries served from cache
        
        **Cost Analysis:**
        - **Total Monthly Cost**: ${total_monthly_cost:.2f}
        - **Additional Cost**: ${elasticache_cost:.2f} for ElastiCache
        - **Performance per Dollar**: {performance_improvement/elasticache_cost:.2f}% improvement per $
        
        **Business Impact:**
        - **User Experience**: {performance_improvement:.1f}% faster application
        - **Scalability**: Handle {cache_hit_rate}% more users with same database
        - **Cost Efficiency**: Reduce database infrastructure needs
        """)
        st.markdown('</div>', unsafe_allow_html=True)

def strategies_tab():
    """Content for ElastiCache strategies tab"""
    st.markdown("## 📋 Amazon ElastiCache - Strategies")
    st.markdown("*Implementation patterns for populating and maintaining your cache*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Caching Strategies** determine how you populate and maintain your cache based on your data patterns and 
    access requirements. The right strategy depends on what data you cache, how frequently it changes, 
    and your application's tolerance for stale data.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Caching Strategies Overview
    st.markdown("### 🔄 Caching Strategies Flow")
    common.mermaid(create_caching_strategies_mermaid(), height=1000)
    
    # Interactive Strategy Selector
    st.markdown("### 🎯 Interactive Strategy Selector")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Data Characteristics")
        data_change_frequency = st.selectbox("How often does your data change?", [
            "Rarely (hours/days)", "Occasionally (minutes/hours)", 
            "Frequently (seconds/minutes)", "Constantly (real-time)"
        ])
        
        read_write_ratio = st.selectbox("Read vs Write Pattern:", [
            "Read-heavy (90% reads)", "Balanced (50/50)", "Write-heavy (90% writes)"
        ])
        
        data_consistency = st.selectbox("Data Consistency Requirement:", [
            "Strong consistency required", "Eventual consistency acceptable", 
            "Stale data acceptable (within limits)"
        ])
    
    with col2:
        st.markdown("#### ⚡ Performance Requirements")
        application_type = st.selectbox("Application Type:", [
            "Web application", "Real-time dashboard", "API service", 
            "Gaming platform", "IoT data processing"
        ])
        
        latency_tolerance = st.selectbox("Latency Tolerance:", [
            "Sub-millisecond required", "Low latency preferred", "Moderate latency acceptable"
        ])
        
        failure_handling = st.selectbox("Cache Failure Handling:", [
            "Must gracefully degrade", "Can accept brief downtime", "Critical - no failures"
        ])
    
    if st.button("🎯 Recommend Caching Strategy", use_container_width=True):
        # Strategy recommendation logic
        strategy_scores = {
            "Lazy Loading": 0,
            "Write Through": 0,
            "Write Behind": 0,
            "Refresh Ahead": 0
        }
        
        # Score based on data change frequency
        if "Rarely" in data_change_frequency:
            strategy_scores["Lazy Loading"] += 3
        elif "Frequently" in data_change_frequency:
            strategy_scores["Write Through"] += 2
            strategy_scores["Write Behind"] += 3
        elif "Constantly" in data_change_frequency:
            strategy_scores["Write Behind"] += 3
            strategy_scores["Refresh Ahead"] += 2
        
        # Score based on read/write pattern
        if "Read-heavy" in read_write_ratio:
            strategy_scores["Lazy Loading"] += 3
            strategy_scores["Refresh Ahead"] += 2
        elif "Write-heavy" in read_write_ratio:
            strategy_scores["Write Through"] += 2
            strategy_scores["Write Behind"] += 3
        
        # Score based on consistency requirements
        if "Strong consistency" in data_consistency:
            strategy_scores["Write Through"] += 3
        elif "Eventual consistency" in data_consistency:
            strategy_scores["Write Behind"] += 2
            strategy_scores["Lazy Loading"] += 1
        else:
            strategy_scores["Lazy Loading"] += 2
            strategy_scores["Refresh Ahead"] += 1
        
        # Find recommended strategy
        recommended_strategy = max(strategy_scores, key=strategy_scores.get)
        confidence = strategy_scores[recommended_strategy] * 10
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 🎯 Recommended Strategy: {recommended_strategy}
        
        **Confidence Level**: {min(confidence, 95)}%
        
        **Why this strategy?**
        - **Data Pattern**: {data_change_frequency}
        - **Access Pattern**: {read_write_ratio}
        - **Consistency**: {data_consistency}
        - **Application**: {application_type}
        """)
        
        strategy_descriptions = {
            "Lazy Loading": "Load data into cache only when needed. Good for read-heavy workloads with acceptable stale data.",
            "Write Through": "Write to cache and database simultaneously. Ensures data consistency but adds write latency.",
            "Write Behind": "Write to cache immediately, database asynchronously. Best performance but complexity in failure handling.",
            "Refresh Ahead": "Proactively refresh cache before expiration. Good for predictable access patterns."
        }
        
        st.markdown(f"**Strategy Details**: {strategy_descriptions[recommended_strategy]}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed Strategy Explanations
    st.markdown("### 📚 Detailed Caching Strategies")
    
    strategy_tabs = st.tabs([
        "🔄 Lazy Loading", "✍️ Write Through", 
        "⚡ Write Behind", "🔮 Refresh Ahead"
    ])
    
    with strategy_tabs[0]:  # Lazy Loading
        st.markdown("### 🔄 Lazy Loading (Cache-Aside)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### ✅ How Lazy Loading Works
            
            1. **Application requests data**
            2. **Check cache first**
            3. **If cache hit**: Return cached data
            4. **If cache miss**: 
               - Fetch from database
               - Store in cache
               - Return data
            
            **Cache Population**: On-demand only
            **Write Pattern**: Cache updated only on reads
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 👍 Advantages
            - **Simple to implement**
            - **Only caches requested data**
            - **Fault tolerant** (cache failure = slower performance)
            - **Memory efficient**
            - **Good for read-heavy workloads**
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 👎 Disadvantages
            - **Cache miss penalty** (extra database call)
            - **Stale data possible**
            - **Initial requests are slow**
            - **Cache warming needed** for performance
            - **Not suitable for write-heavy workloads**
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 🎯 Best Use Cases
            - **E-commerce product catalogs**
            - **User profile data**
            - **Configuration settings**
            - **Reference data**
            - **Read-heavy applications**
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Lazy Loading Implementation
        st.markdown("### 💻 Lazy Loading Implementation")
        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code('''
# Lazy Loading (Cache-Aside) Pattern Implementation
import redis
import json
import time
from typing import Any, Optional

class LazyLoadingCache:
    def __init__(self, redis_host: str, redis_port: int = 6379):
        self.redis_client = redis.Redis(
            host=redis_host, 
            port=redis_port, 
            decode_responses=True
        )
        self.default_ttl = 3600  # 1 hour
    
    def get_user_profile(self, user_id: int) -> Optional[dict]:
        """
        Get user profile with lazy loading pattern
        """
        cache_key = f"user:profile:{user_id}"
        
        # Step 1: Try to get from cache
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                print(f"✅ Cache HIT for user {user_id}")
                return json.loads(cached_data)
        except Exception as e:
            print(f"Cache error: {e}, falling back to database")
        
        # Step 2: Cache miss - fetch from database
        print(f"❌ Cache MISS for user {user_id}")
        user_data = self._fetch_user_from_database(user_id)
        
        if user_data:
            # Step 3: Store in cache for future requests
            try:
                self.redis_client.setex(
                    cache_key, 
                    self.default_ttl, 
                    json.dumps(user_data)
                )
                print(f"💾 Cached user {user_id} data")
            except Exception as e:
                print(f"Cache write error: {e}")
        
        return user_data
    
    def get_product_details(self, product_id: int) -> Optional[dict]:
        """
        Get product details with lazy loading
        """
        cache_key = f"product:{product_id}"
        
        # Check cache first
        try:
            cached_product = self.redis_client.get(cache_key)
            if cached_product:
                print(f"✅ Cache HIT for product {product_id}")
                return json.loads(cached_product)
        except Exception as e:
            print(f"Cache read error: {e}")
        
        # Fetch from database
        print(f"❌ Cache MISS for product {product_id}")
        product_data = self._fetch_product_from_database(product_id)
        
        if product_data:
            # Cache with different TTL based on product type
            ttl = 7200 if product_data.get('type') == 'popular' else 3600
            
            try:
                self.redis_client.setex(
                    cache_key,
                    ttl,
                    json.dumps(product_data)
                )
                print(f"💾 Cached product {product_id} with TTL {ttl}")
            except Exception as e:
                print(f"Cache write error: {e}")
        
        return product_data
    
    def get_multiple_products(self, product_ids: list) -> dict:
        """
        Batch fetch multiple products with lazy loading
        """
        results = {}
        cache_misses = []
        
        # Step 1: Try to get all from cache
        cache_keys = [f"product:{pid}" for pid in product_ids]
        
        try:
            cached_products = self.redis_client.mget(cache_keys)
            
            for i, cached_data in enumerate(cached_products):
                product_id = product_ids[i]
                
                if cached_data:
                    results[product_id] = json.loads(cached_data)
                    print(f"✅ Cache HIT for product {product_id}")
                else:
                    cache_misses.append(product_id)
                    print(f"❌ Cache MISS for product {product_id}")
        
        except Exception as e:
            print(f"Batch cache read error: {e}")
            cache_misses = product_ids  # Treat all as cache misses
        
        # Step 2: Fetch cache misses from database
        if cache_misses:
            db_products = self._fetch_products_batch(cache_misses)
            
            # Step 3: Cache the fetched products
            cache_data = {}
            for product_id, product_data in db_products.items():
                cache_key = f"product:{product_id}"
                cache_data[cache_key] = json.dumps(product_data)
                results[product_id] = product_data
            
            # Batch cache write
            if cache_data:
                try:
                    # Set multiple keys at once
                    pipe = self.redis_client.pipeline()
                    for key, data in cache_data.items():
                        pipe.setex(key, self.default_ttl, data)
                    pipe.execute()
                    print(f"💾 Batch cached {len(cache_data)} products")
                except Exception as e:
                    print(f"Batch cache write error: {e}")
        
        return results
    
    def invalidate_cache(self, cache_key: str) -> bool:
        """
        Manually invalidate cache entry (for data consistency)
        """
        try:
            result = self.redis_client.delete(cache_key)
            if result:
                print(f"🗑️ Invalidated cache key: {cache_key}")
                return True
            else:
                print(f"❌ Cache key not found: {cache_key}")
                return False
        except Exception as e:
            print(f"Cache invalidation error: {e}")
            return False
    
    def _fetch_user_from_database(self, user_id: int) -> Optional[dict]:
        """Simulate database fetch (replace with actual DB query)"""
        time.sleep(0.05)  # Simulate database latency
        return {
            'user_id': user_id,
            'name': f'User {user_id}',
            'email': f'user{user_id}@example.com',
            'created_at': '2024-01-01T00:00:00Z',
            'profile_pic': f'https://example.com/pics/{user_id}.jpg'
        }
    
    def _fetch_product_from_database(self, product_id: int) -> Optional[dict]:
        """Simulate database fetch for product"""
        time.sleep(0.08)  # Simulate database latency
        return {
            'product_id': product_id,
            'name': f'Product {product_id}',
            'price': 29.99 + (product_id % 100),
            'description': f'Description for product {product_id}',
            'type': 'popular' if product_id % 5 == 0 else 'regular',
            'in_stock': True
        }
    
    def _fetch_products_batch(self, product_ids: list) -> dict:
        """Simulate batch database fetch"""
        time.sleep(0.1)  # Simulate database latency
        return {
            pid: self._fetch_product_from_database(pid) 
            for pid in product_ids
        }

# Example usage and performance testing
def test_lazy_loading_performance():
    cache = LazyLoadingCache('localhost')
    
    print("=== Lazy Loading Performance Test ===")
    
    # Test single product fetch
    start_time = time.time()
    product = cache.get_product_details(1001)
    first_fetch_time = time.time() - start_time
    
    # Test cached product fetch
    start_time = time.time()
    cached_product = cache.get_product_details(1001)
    cached_fetch_time = time.time() - start_time
    
    print(f"First fetch time: {first_fetch_time*1000:.2f}ms")
    print(f"Cached fetch time: {cached_fetch_time*1000:.2f}ms")
    print(f"Performance improvement: {(first_fetch_time/cached_fetch_time):.1f}x faster")
    
    # Test batch operations
    product_ids = [2001, 2002, 2003, 2004, 2005]
    
    start_time = time.time()
    results = cache.get_multiple_products(product_ids)
    batch_time = time.time() - start_time
    
    print(f"Batch fetch time: {batch_time*1000:.2f}ms for {len(product_ids)} products")
    print(f"Average per product: {(batch_time/len(product_ids))*1000:.2f}ms")

# Run the test
if __name__ == "__main__":
    test_lazy_loading_performance()
        ''', language='python')
        st.markdown('</div>', unsafe_allow_html=True)
    
    with strategy_tabs[1]:  # Write Through
        st.markdown("### ✍️ Write Through Strategy")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### ✅ How Write Through Works
            
            1. **Application writes data**
            2. **Write to cache first**
            3. **Write to database second**
            4. **Both succeed or fail together**
            5. **Cache always consistent with database**
            
            **Cache Population**: On every write
            **Consistency**: Strong consistency guaranteed
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 👍 Advantages
            - **Strong data consistency**
            - **No stale data**
            - **Simple cache management**
            - **Cache always populated**
            - **Fault tolerance built-in**
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 👎 Disadvantages
            - **Higher write latency**
            - **Both cache and DB must be available**
            - **More complex error handling**
            - **Cache pollution** (unused data cached)
            - **Higher infrastructure cost**
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 🎯 Best Use Cases
            - **Financial transactions**
            - **User authentication data**
            - **Critical configuration**
            - **Audit logs**
            - **Strong consistency requirements**
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Write Through Implementation
        st.markdown("### 💻 Write Through Implementation")
        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code('''
# Write Through Pattern Implementation
import redis
import json
import time
import logging
from typing import Any, Optional
from contextlib import contextmanager

class WriteThroughCache:
    def __init__(self, redis_host: str, redis_port: int = 6379):
        self.redis_client = redis.Redis(
            host=redis_host, 
            port=redis_port, 
            decode_responses=True
        )
        self.default_ttl = 3600
        self.logger = logging.getLogger(__name__)
    
    def update_user_profile(self, user_id: int, profile_data: dict) -> bool:
        """
        Update user profile with write-through pattern
        """
        cache_key = f"user:profile:{user_id}"
        
        try:
            # Start transaction-like operation
            with self._write_through_transaction():
                # Step 1: Write to cache
                cache_success = self._write_to_cache(cache_key, profile_data)
                if not cache_success:
                    raise Exception("Cache write failed")
                
                # Step 2: Write to database
                db_success = self._write_to_database('users', user_id, profile_data)
                if not db_success:
                    # Rollback cache if database fails
                    self.redis_client.delete(cache_key)
                    raise Exception("Database write failed")
                
                self.logger.info(f"✅ Write-through success for user {user_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Write-through failed for user {user_id}: {e}")
            return False
    
    def create_order(self, order_data: dict) -> Optional[int]:
        """
        Create order with write-through pattern
        """
        order_id = self._generate_order_id()
        order_data['order_id'] = order_id
        order_data['created_at'] = time.time()
        
        cache_key = f"order:{order_id}"
        
        try:
            with self._write_through_transaction():
                # Write to cache first
                cache_success = self._write_to_cache(
                    cache_key, 
                    order_data, 
                    ttl=7200  # Orders cached for 2 hours
                )
                
                if not cache_success:
                    raise Exception("Failed to cache order")
                
                # Write to database
                db_success = self._write_to_database('orders', order_id, order_data)
                
                if not db_success:
                    # Cleanup cache on database failure
                    self.redis_client.delete(cache_key)
                    raise Exception("Failed to save order to database")
                
                # Update related caches (user's order history)
                self._update_user_order_cache(order_data['user_id'], order_id)
                
                self.logger.info(f"✅ Order {order_id} created successfully")
                return order_id
                
        except Exception as e:
            self.logger.error(f"❌ Order creation failed: {e}")
            return None
    
    def update_inventory(self, product_id: int, quantity: int) -> bool:
        """
        Update inventory with write-through pattern
        Critical for e-commerce to avoid overselling
        """
        cache_key = f"inventory:{product_id}"
        
        try:
            with self._write_through_transaction():
                # Get current inventory
                current_inventory = self._get_current_inventory(product_id)
                
                if current_inventory is None:
                    raise Exception(f"Product {product_id} not found")
                
                new_quantity = current_inventory['quantity'] + quantity
                
                if new_quantity < 0:
                    raise Exception("Insufficient inventory")
                
                updated_inventory = {
                    **current_inventory,
                    'quantity': new_quantity,
                    'last_updated': time.time()
                }
                
                # Write to cache
                cache_success = self._write_to_cache(cache_key, updated_inventory)
                if not cache_success:
                    raise Exception("Cache update failed")
                
                # Write to database
                db_success = self._write_to_database(
                    'inventory', 
                    product_id, 
                    updated_inventory
                )
                
                if not db_success:
                    # Rollback cache
                    self._write_to_cache(cache_key, current_inventory)
                    raise Exception("Database update failed")
                
                self.logger.info(f"✅ Inventory updated for product {product_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Inventory update failed: {e}")
            return False
    
    def batch_write_through(self, updates: list) -> dict:
        """
        Batch write-through operations for better performance
        """
        results = {'success': [], 'failed': []}
        
        # Group updates by type for batch processing
        cache_operations = []
        db_operations = []
        
        for update in updates:
            cache_key = update['cache_key']
            data = update['data']
            table = update.get('table', 'default')
            
            cache_operations.append((cache_key, data))
            db_operations.append((table, update['id'], data))
        
        try:
            with self._write_through_transaction():
                # Batch cache writes
                cache_success = self._batch_cache_write(cache_operations)
                if not cache_success:
                    raise Exception("Batch cache write failed")
                
                # Batch database writes
                db_success = self._batch_database_write(db_operations)
                if not db_success:
                    # Rollback cache operations
                    self._batch_cache_delete([op[0] for op in cache_operations])
                    raise Exception("Batch database write failed")
                
                results['success'] = [update['id'] for update in updates]
                self.logger.info(f"✅ Batch write-through success: {len(updates)} operations")
                
        except Exception as e:
            results['failed'] = [update['id'] for update in updates]
            self.logger.error(f"❌ Batch write-through failed: {e}")
        
        return results
    
    @contextmanager
    def _write_through_transaction(self):
        """
        Context manager for write-through transactions
        """
        try:
            yield
        except Exception as e:
            # Transaction failed - could implement more sophisticated rollback
            self.logger.error(f"Transaction failed: {e}")
            raise
    
    def _write_to_cache(self, key: str, data: dict, ttl: int = None) -> bool:
        """Write data to cache"""
        try:
            ttl = ttl or self.default_ttl
            result = self.redis_client.setex(key, ttl, json.dumps(data))
            return result
        except Exception as e:
            self.logger.error(f"Cache write error: {e}")
            return False
    
    def _write_to_database(self, table: str, record_id: int, data: dict) -> bool:
        """Simulate database write (replace with actual DB operations)"""
        try:
            # Simulate database latency
            time.sleep(0.01)
            
            # Simulate database operation
            self.logger.info(f"DB Write: {table}.{record_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Database write error: {e}")
            return False
    
    def _batch_cache_write(self, operations: list) -> bool:
        """Batch write to cache"""
        try:
            pipe = self.redis_client.pipeline()
            for key, data in operations:
                pipe.setex(key, self.default_ttl, json.dumps(data))
            
            results = pipe.execute()
            return all(results)
            
        except Exception as e:
            self.logger.error(f"Batch cache write error: {e}")
            return False
    
    def _batch_database_write(self, operations: list) -> bool:
        """Batch write to database"""
        try:
            # Simulate batch database operation
            time.sleep(0.05)  # Batch operations are more efficient
            return True
            
        except Exception as e:
            self.logger.error(f"Batch database write error: {e}")
            return False
    
    def _get_current_inventory(self, product_id: int) -> Optional[dict]:
        """Get current inventory from cache or database"""
        cache_key = f"inventory:{product_id}"
        
        # Try cache first
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception:
            pass
        
        # Fallback to database (simulate)
        return {
            'product_id': product_id,
            'quantity': 100,
            'last_updated': time.time()
        }
    
    def _generate_order_id(self) -> int:
        """Generate unique order ID"""
        return int(time.time() * 1000) % 1000000

# Example usage
def test_write_through():
    cache = WriteThroughCache('localhost')
    
    # Test user profile update
    profile_data = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'preferences': {'theme': 'dark', 'notifications': True}
    }
    
    success = cache.update_user_profile(1001, profile_data)
    print(f"Profile update: {'✅ Success' if success else '❌ Failed'}")
    
    # Test order creation
    order_data = {
        'user_id': 1001,
        'items': [{'product_id': 2001, 'quantity': 2}],
        'total': 59.98
    }
    
    order_id = cache.create_order(order_data)
    print(f"Order creation: {'✅ Success' if order_id else '❌ Failed'} - Order ID: {order_id}")
    
    # Test inventory update
    success = cache.update_inventory(2001, -2)  # Reduce inventory by 2
    print(f"Inventory update: {'✅ Success' if success else '❌ Failed'}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_write_through()
        ''', language='python')
        st.markdown('</div>', unsafe_allow_html=True)
    
    with strategy_tabs[2]:  # Write Behind
        st.markdown("### ⚡ Write Behind (Write Back) Strategy")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### ✅ How Write Behind Works
            
            1. **Application writes data**
            2. **Write to cache immediately**
            3. **Return success to application**
            4. **Write to database asynchronously**
            5. **Background process handles DB writes**
            
            **Cache Population**: Immediate
            **Database Updates**: Asynchronous
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 👍 Advantages
            - **Lowest write latency**
            - **High write throughput**
            - **Better user experience**
            - **Batch database operations**
            - **Reduced database load**
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 👎 Disadvantages
            - **Risk of data loss**
            - **Complex failure handling**
            - **Eventual consistency only**
            - **Requires background processes**
            - **More complex to implement**
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 🎯 Best Use Cases
            - **Gaming leaderboards**
            - **Social media likes/views**
            - **Analytics data collection**
            - **High-frequency updates**
            - **Non-critical data**
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Write Behind Implementation
        st.markdown("### 💻 Write Behind Implementation")
        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code('''
# Write Behind (Write Back) Pattern Implementation
import redis
import json
import time
import threading
import queue
import logging
from typing import Any, Dict, List
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

@dataclass
class WriteOperation:
    operation_type: str  # 'insert', 'update', 'delete'
    table: str
    key: str
    data: dict
    timestamp: float
    retry_count: int = 0

class WriteBehindCache:
    def __init__(self, redis_host: str, redis_port: int = 6379, 
                 batch_size: int = 100, flush_interval: int = 5):
        self.redis_client = redis.Redis(
            host=redis_host, 
            port=redis_port, 
            decode_responses=True
        )
        
        # Write-behind configuration
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.write_queue = queue.Queue()
        self.pending_writes = {}  # Key: cache_key, Value: WriteOperation
        
        # Background processing
        self.running = True
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.background_thread = threading.Thread(target=self._background_writer)
        self.background_thread.daemon = True
        self.background_thread.start()
        
        self.logger = logging.getLogger(__name__)
    
    def update_user_score(self, user_id: int, score: int) -> bool:
        """
        Update user score with write-behind pattern
        Perfect for gaming leaderboards where immediate consistency isn't critical
        """
        cache_key = f"user:score:{user_id}"
        
        try:
            # Step 1: Update cache immediately
            current_score = self._get_current_score(user_id)
            new_score = max(current_score, score)  # Keep highest score
            
            cache_success = self.redis_client.set(cache_key, new_score)
            
            if cache_success:
                # Step 2: Queue database write for later
                write_op = WriteOperation(
                    operation_type='update',
                    table='user_scores',
                    key=cache_key,
                    data={'user_id': user_id, 'score': new_score},
                    timestamp=time.time()
                )
                
                self._queue_write_operation(write_op)
                self.logger.info(f"✅ Score updated in cache for user {user_id}: {new_score}")
                return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update score for user {user_id}: {e}")
            return False
    
    def increment_page_views(self, page_url: str, increment: int = 1) -> bool:
        """
        Increment page view counter with write-behind
        High-frequency updates that don't need immediate database consistency
        """
        cache_key = f"pageviews:{hash(page_url) % 10000}"  # Simple key hashing
        
        try:
            # Atomic increment in cache
            new_count = self.redis_client.incr(cache_key, increment)
            
            # Queue database update (will be batched)
            write_op = WriteOperation(
                operation_type='increment',
                table='page_analytics',
                key=cache_key,
                data={'page_url': page_url, 'views': increment},
                timestamp=time.time()
            )
            
            self._queue_write_operation(write_op)
            self.logger.debug(f"Page views incremented: {page_url} -> {new_count}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to increment page views: {e}")
            return False
    
    def batch_update_social_metrics(self, updates: List[Dict]) -> bool:
        """
        Batch update social metrics (likes, shares, comments)
        """
        try:
            # Batch update cache
            pipe = self.redis_client.pipeline()
            write_operations = []
            
            for update in updates:
                post_id = update['post_id']
                metric_type = update['metric_type']  # 'likes', 'shares', 'comments'
                increment = update.get('increment', 1)
                
                cache_key = f"social:{post_id}:{metric_type}"
                pipe.incr(cache_key, increment)
                
                # Queue database write
                write_op = WriteOperation(
                    operation_type='increment',
                    table='social_metrics',
                    key=cache_key,
                    data={
                        'post_id': post_id,
                        'metric_type': metric_type,
                        'increment': increment
                    },
                    timestamp=time.time()
                )
                write_operations.append(write_op)
            
            # Execute batch cache updates
            results = pipe.execute()
            
            # Queue all database operations
            for write_op in write_operations:
                self._queue_write_operation(write_op)
            
            self.logger.info(f"✅ Batch updated {len(updates)} social metrics")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Batch social metrics update failed: {e}")
            return False
    
    def create_user_activity(self, user_id: int, activity_type: str, 
                           activity_data: dict) -> bool:
        """
        Create user activity record with write-behind
        """
        activity_id = f"{user_id}_{int(time.time()*1000)}"
        cache_key = f"activity:{activity_id}"
        
        activity_record = {
            'user_id': user_id,
            'activity_type': activity_type,
            'data': activity_data,
            'timestamp': time.time()
        }
        
        try:
            # Store in cache immediately
            cache_success = self.redis_client.setex(
                cache_key, 
                3600,  # 1 hour TTL
                json.dumps(activity_record)
            )
            
            if cache_success:
                # Queue database write
                write_op = WriteOperation(
                    operation_type='insert',
                    table='user_activities',
                    key=cache_key,
                    data=activity_record,
                    timestamp=time.time()
                )
                
                self._queue_write_operation(write_op)
                self.logger.info(f"✅ Activity recorded for user {user_id}")
                return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to record activity: {e}")
            return False
    
    def _queue_write_operation(self, write_op: WriteOperation):
        """Queue write operation for background processing"""
        # Deduplicate operations for the same key
        self.pending_writes[write_op.key] = write_op
        
        # If queue is getting full, trigger immediate flush
        if len(self.pending_writes) >= self.batch_size:
            self._flush_pending_writes()
    
    def _background_writer(self):
        """Background thread that processes queued writes"""
        while self.running:
            try:
                time.sleep(self.flush_interval)
                if self.pending_writes:
                    self._flush_pending_writes()
                    
            except Exception as e:
                self.logger.error(f"Background writer error: {e}")
    
    def _flush_pending_writes(self):
        """Flush pending writes to database"""
        if not self.pending_writes:
            return
        
        # Get snapshot of pending writes
        writes_to_process = list(self.pending_writes.values())
        self.pending_writes.clear()
        
        try:
            # Group writes by table for batch processing
            writes_by_table = {}
            for write_op in writes_to_process:
                table = write_op.table
                if table not in writes_by_table:
                    writes_by_table[table] = []
                writes_by_table[table].append(write_op)
            
            # Process each table's writes
            for table, operations in writes_by_table.items():
                success = self._batch_write_to_database(table, operations)
                
                if success:
                    self.logger.info(f"✅ Flushed {len(operations)} operations to {table}")
                else:
                    # Re-queue failed operations with retry logic
                    self._handle_failed_writes(operations)
                    
        except Exception as e:
            self.logger.error(f"❌ Flush failed: {e}")
            # Re-queue all operations
            for write_op in writes_to_process:
                if write_op.retry_count < 3:  # Max 3 retries
                    write_op.retry_count += 1
                    self.pending_writes[write_op.key] = write_op
    
    def _batch_write_to_database(self, table: str, operations: List[WriteOperation]) -> bool:
        """Batch write operations to database"""
        try:
            # Group operations by type
            inserts = []
            updates = []
            increments = {}
            
            for op in operations:
                if op.operation_type == 'insert':
                    inserts.append(op.data)
                elif op.operation_type == 'update':
                    updates.append(op.data)
                elif op.operation_type == 'increment':
                    key = f"{op.data.get('post_id', '')}_{op.data.get('metric_type', '')}"
                    if key in increments:
                        increments[key] += op.data.get('increment', 0)
                    else:
                        increments[key] = op.data.get('increment', 0)
            
            # Simulate batch database operations
            if inserts:
                self._batch_insert(table, inserts)
            
            if updates:
                self._batch_update(table, updates)
            
            if increments:
                self._batch_increment(table, increments)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Batch database write failed: {e}")
            return False
    
    def _batch_insert(self, table: str, records: List[dict]):
        """Simulate batch insert to database"""
        time.sleep(0.02)  # Simulate database latency
        self.logger.debug(f"Batch inserted {len(records)} records to {table}")
    
    def _batch_update(self, table: str, records: List[dict]):
        """Simulate batch update to database"""
        time.sleep(0.02)  # Simulate database latency
        self.logger.debug(f"Batch updated {len(records)} records in {table}")
    
    def _batch_increment(self, table: str, increments: Dict[str, int]):
        """Simulate batch increment operations"""
        time.sleep(0.01)  # Simulate database latency
        self.logger.debug(f"Batch incremented {len(increments)} counters in {table}")
    
    def _handle_failed_writes(self, failed_operations: List[WriteOperation]):
        """Handle failed write operations with retry logic"""
        for op in failed_operations:
            if op.retry_count < 3:
                op.retry_count += 1
                self.pending_writes[op.key] = op
                self.logger.warning(f"Retrying write operation: {op.key} (attempt {op.retry_count})")
            else:
                self.logger.error(f"Write operation failed permanently: {op.key}")
    
    def _get_current_score(self, user_id: int) -> int:
        """Get current score from cache"""
        cache_key = f"user:score:{user_id}"
        try:
            score = self.redis_client.get(cache_key)
            return int(score) if score else 0
        except:
            return 0
    
    def shutdown(self):
        """Graceful shutdown - flush all pending writes"""
        self.running = False
        self._flush_pending_writes()
        self.executor.shutdown(wait=True)
        self.logger.info("Write-behind cache shut down gracefully")

# Example usage and testing
def test_write_behind():
    cache = WriteBehindCache('localhost', batch_size=50, flush_interval=2)
    
    try:
        # Test gaming scores
        for user_id in range(1001, 1051):
            score = user_id * 10 + (user_id % 100)
            cache.update_user_score(user_id, score)
        
        # Test page view increments
        pages = ['/home', '/products', '/about', '/contact']
        for _ in range(100):
            page = pages[_ % len(pages)]
            cache.increment_page_views(page, 1)
        
        # Test social metrics
        social_updates = []
        for post_id in range(2001, 2021):
            social_updates.extend([
                {'post_id': post_id, 'metric_type': 'likes', 'increment': 5},
                {'post_id': post_id, 'metric_type': 'shares', 'increment': 2},
                {'post_id': post_id, 'metric_type': 'comments', 'increment': 3}
            ])
        
        cache.batch_update_social_metrics(social_updates)
        
        print("✅ Write-behind operations queued")
        print("⏳ Waiting for background flush...")
        
        # Wait for background processing
        time.sleep(6)
        
    finally:
        cache.shutdown()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_write_behind()
        ''', language='python')
        st.markdown('</div>', unsafe_allow_html=True)
    
    with strategy_tabs[3]:  # Refresh Ahead
        st.markdown("### 🔮 Refresh Ahead Strategy")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### ✅ How Refresh Ahead Works
            
            1. **Monitor cache expiration times**
            2. **Before data expires, refresh it**
            3. **Background process fetches fresh data**
            4. **Update cache with new data**
            5. **Users always get cached data**
            
            **Cache Population**: Proactive refresh
            **User Experience**: Always fast responses
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 👍 Advantages
            - **No cache miss penalty**
            - **Consistent performance**
            - **Predictable response times**
            - **Reduced database load spikes**
            - **Better user experience**
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 👎 Disadvantages
            - **Complex to implement**
            - **Background processing overhead**
            - **May refresh unused data**
            - **Requires access pattern prediction**
            - **Higher infrastructure costs**
            """)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown("""
            ### 🎯 Best Use Cases
            - **News feeds and articles**
            - **Product catalogs**
            - **Weather data**
            - **Stock prices**
            - **Any predictable access patterns**
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Refresh Ahead Implementation
        st.markdown("### 💻 Refresh Ahead Implementation")
        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code('''
# Refresh Ahead Pattern Implementation
import redis
import json
import time
import threading
import schedule
import logging
from typing import Any, Dict, List, Callable, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

@dataclass
class CacheEntry:
    key: str
    data: Any
    created_at: float
    ttl: int
    refresh_threshold: float  # Refresh when this much time is left
    refresh_function: Callable
    access_count: int = 0
    last_accessed: float = 0

class RefreshAheadCache:
    def __init__(self, redis_host: str, redis_port: int = 6379):
        self.redis_client = redis.Redis(
            host=redis_host, 
            port=redis_port, 
            decode_responses=True
        )
        
        # Refresh-ahead management
        self.tracked_keys = {}  # Key: cache_key, Value: CacheEntry
        self.refresh_executor = ThreadPoolExecutor(max_workers=5)
        
        # Background monitoring
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_cache_expiration)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        # Statistics
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'refresh_operations': 0,
            'refresh_failures': 0
        }
        
        self.logger = logging.getLogger(__name__)
    
    def get_news_feed(self, user_id: int, category: str = 'general') -> List[dict]:
        """
        Get news feed with refresh-ahead pattern
        Perfect for content that updates regularly but users expect fast access
        """
        cache_key = f"news:feed:{user_id}:{category}"
        
        # Try to get from cache
        cached_data = self._get_from_cache_with_tracking(cache_key)
        
        if cached_data:
            self.stats['cache_hits'] += 1
            return cached_data
        
        # Cache miss - fetch immediately and set up refresh-ahead
        self.stats['cache_misses'] += 1
        self.logger.info(f"Cache MISS for news feed: {cache_key}")
        
        # Fetch fresh data
        news_data = self._fetch_news_from_api(user_id, category)
        
        if news_data:
            # Cache with refresh-ahead tracking
            self._cache_with_refresh_ahead(
                cache_key=cache_key,
                data=news_data,
                ttl=1800,  # 30 minutes
                refresh_threshold=300,  # Refresh when 5 minutes left
                refresh_function=lambda: self._fetch_news_from_api(user_id, category)
            )
        
        return news_data or []
    
    def get_product_recommendations(self, user_id: int) -> List[dict]:
        """
        Get product recommendations with predictive refresh
        """
        cache_key = f"recommendations:{user_id}"
        
        cached_data = self._get_from_cache_with_tracking(cache_key)
        
        if cached_data:
            self.stats['cache_hits'] += 1
            return cached_data
        
        self.stats['cache_misses'] += 1
        
        # Generate recommendations
        recommendations = self._generate_recommendations(user_id)
        
        if recommendations:
            # Cache with refresh-ahead (refresh every 2 hours, cache for 3 hours)
            self._cache_with_refresh_ahead(
                cache_key=cache_key,
                data=recommendations,
                ttl=10800,  # 3 hours
                refresh_threshold=3600,  # Refresh when 1 hour left
                refresh_function=lambda: self._generate_recommendations(user_id)
            )
        
        return recommendations or []
    
    def get_weather_data(self, location: str) -> dict:
        """
        Get weather data with refresh-ahead pattern
        Weather data has predictable refresh patterns
        """
        cache_key = f"weather:{location.lower().replace(' ', '_')}"
        
        cached_data = self._get_from_cache_with_tracking(cache_key)
        
        if cached_data:
            self.stats['cache_hits'] += 1
            return cached_data
        
        self.stats['cache_misses'] += 1
        
        # Fetch weather data
        weather_data = self._fetch_weather_from_api(location)
        
        if weather_data:
            # Weather updates every 15 minutes, cache for 20 minutes
            self._cache_with_refresh_ahead(
                cache_key=cache_key,
                data=weather_data,
                ttl=1200,  # 20 minutes
                refresh_threshold=300,  # Refresh when 5 minutes left
                refresh_function=lambda: self._fetch_weather_from_api(location)
            )
        
        return weather_data or {}
    
    def get_stock_prices(self, symbols: List[str]) -> Dict[str, dict]:
        """
        Get stock prices with high-frequency refresh
        """
        results = {}
        
        for symbol in symbols:
            cache_key = f"stock:{symbol.upper()}"
            
            cached_data = self._get_from_cache_with_tracking(cache_key)
            
            if cached_data:
                self.stats['cache_hits'] += 1
                results[symbol] = cached_data
            else:
                self.stats['cache_misses'] += 1
                
                # Fetch stock data
                stock_data = self._fetch_stock_price(symbol)
                
                if stock_data:
                    # Stock prices update frequently during market hours
                    self._cache_with_refresh_ahead(
                        cache_key=cache_key,
                        data=stock_data,
                        ttl=60,  # 1 minute cache
                        refresh_threshold=15,  # Refresh when 15 seconds left
                        refresh_function=lambda s=symbol: self._fetch_stock_price(s)
                    )
                    results[symbol] = stock_data
        
        return results
    
    def _cache_with_refresh_ahead(self, cache_key: str, data: Any, ttl: int, 
                                refresh_threshold: int, refresh_function: Callable):
        """
        Cache data with refresh-ahead tracking
        """
        try:
            # Store in Redis
            self.redis_client.setex(cache_key, ttl, json.dumps(data, default=str))
            
            # Track for refresh-ahead
            cache_entry = CacheEntry(
                key=cache_key,
                data=data,
                created_at=time.time(),
                ttl=ttl,
                refresh_threshold=refresh_threshold,
                refresh_function=refresh_function,
                access_count=1,
                last_accessed=time.time()
            )
            
            self.tracked_keys[cache_key] = cache_entry
            self.logger.debug(f"Cached with refresh-ahead: {cache_key}")
            
        except Exception as e:
            self.logger.error(f"Cache with refresh-ahead failed: {e}")
    
    def _get_from_cache_with_tracking(self, cache_key: str) -> Optional[Any]:
        """
        Get from cache and update access tracking
        """
        try:
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                # Update access tracking
                if cache_key in self.tracked_keys:
                    entry = self.tracked_keys[cache_key]
                    entry.access_count += 1
                    entry.last_accessed = time.time()
                
                return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Cache get error: {e}")
            return None
    
    def _monitor_cache_expiration(self):
        """
        Background thread that monitors cache entries for refresh-ahead
        """
        while self.monitoring_active:
            try:
                current_time = time.time()
                keys_to_refresh = []
                
                # Check all tracked keys
                for cache_key, entry in list(self.tracked_keys.items()):
                    time_since_creation = current_time - entry.created_at
                    time_until_expiry = entry.ttl - time_since_creation
                    
                    # Check if it's time to refresh
                    if time_until_expiry <= entry.refresh_threshold and time_until_expiry > 0:
                        # Only refresh if accessed recently (within last TTL period)
                        if (current_time - entry.last_accessed) < entry.ttl:
                            keys_to_refresh.append(cache_key)
                    
                    # Clean up expired entries
                    elif time_until_expiry <= 0:
                        del self.tracked_keys[cache_key]
                
                # Trigger refresh operations
                for cache_key in keys_to_refresh:
                    self._schedule_refresh(cache_key)
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Cache monitoring error: {e}")
                time.sleep(10)  # Wait longer on error
    
    def _schedule_refresh(self, cache_key: str):
        """
        Schedule background refresh of cache entry
        """
        if cache_key not in self.tracked_keys:
            return
        
        entry = self.tracked_keys[cache_key]
        
        # Submit refresh task to thread pool
        future = self.refresh_executor.submit(self._refresh_cache_entry, cache_key, entry)
        
        # Log the refresh operation
        self.logger.info(f"🔄 Scheduled refresh for: {cache_key}")
    
    def _refresh_cache_entry(self, cache_key: str, entry: CacheEntry):
        """
        Refresh a cache entry in the background
        """
        try:
            # Call the refresh function
            fresh_data = entry.refresh_function()
            
            if fresh_data:
                # Update cache with fresh data
                self.redis_client.setex(
                    cache_key, 
                    entry.ttl, 
                    json.dumps(fresh_data, default=str)
                )
                
                # Update tracking info
                entry.data = fresh_data
                entry.created_at = time.time()
                
                self.stats['refresh_operations'] += 1
                self.logger.info(f"✅ Refreshed cache: {cache_key}")
            else:
                self.stats['refresh_failures'] += 1
                self.logger.warning(f"❌ Refresh failed: {cache_key}")
                
        except Exception as e:
            self.stats['refresh_failures'] += 1
            self.logger.error(f"❌ Refresh error for {cache_key}: {e}")
    
    def get_cache_statistics(self) -> dict:
        """
        Get cache performance statistics
        """
        total_requests = self.stats['cache_hits'] + self.stats['cache_misses']
        hit_rate = (self.stats['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.stats,
            'hit_rate': round(hit_rate, 2),
            'tracked_keys': len(self.tracked_keys),
            'active_refreshes': len([
                k for k, v in self.tracked_keys.items() 
                if time.time() - v.last_accessed < v.ttl
            ])
        }
    
    # Simulation methods (replace with actual API calls)
    def _fetch_news_from_api(self, user_id: int, category: str) -> List[dict]:
        """Simulate news API call"""
        time.sleep(0.1)  # Simulate API latency
        return [
            {
                'id': f'news_{int(time.time())}_{i}',
                'title': f'Breaking News {i}',
                'category': category,
                'timestamp': time.time()
            }
            for i in range(10)
        ]
    
    def _generate_recommendations(self, user_id: int) -> List[dict]:
        """Simulate ML recommendation generation"""
        time.sleep(0.2)  # Simulate ML processing time
        return [
            {
                'product_id': 1000 + i,
                'name': f'Product {1000 + i}',
                'score': 0.9 - (i * 0.1),
                'reason': f'Based on your preferences'
            }
            for i in range(5)
        ]
    
    def _fetch_weather_from_api(self, location: str) -> dict:
        """Simulate weather API call"""
        time.sleep(0.05)  # Simulate API latency
        return {
            'location': location,
            'temperature': 22 + (hash(location) % 20),
            'condition': 'sunny',
            'timestamp': time.time()
        }
    
    def _fetch_stock_price(self, symbol: str) -> dict:
        """Simulate stock price API call"""
        time.sleep(0.02)  # Simulate API latency
        base_price = 100 + (hash(symbol) % 100)
        return {
            'symbol': symbol,
            'price': base_price + (time.time() % 10),
            'change': (time.time() % 5) - 2.5,
            'timestamp': time.time()
        }
    
    def shutdown(self):
        """Graceful shutdown"""
        self.monitoring_active = False
        self.refresh_executor.shutdown(wait=True)
        self.logger.info("Refresh-ahead cache shut down gracefully")

# Example usage and testing
def test_refresh_ahead():
    cache = RefreshAheadCache('localhost')
    
    try:
        print("=== Testing Refresh-Ahead Cache ===")
        
        # Test news feed
        news = cache.get_news_feed(1001, 'technology')
        print(f"News articles: {len(news)}")
        
        # Test recommendations
        recommendations = cache.get_product_recommendations(1001)
        print(f"Recommendations: {len(recommendations)}")
        
        # Test weather
        weather = cache.get_weather_data('New York')
        print(f"Weather: {weather.get('temperature', 'N/A')}°")
        
        # Test stock prices
        stocks = cache.get_stock_prices(['AAPL', 'GOOGL', 'MSFT'])
        print(f"Stock prices: {len(stocks)} symbols")
        
        # Wait and check statistics
        time.sleep(10)
        stats = cache.get_cache_statistics()
        print(f"Cache statistics: {stats}")
        
        # Test cache hits
        print("\n=== Testing Cache Hits ===")
        news2 = cache.get_news_feed(1001, 'technology')  # Should be cache hit
        weather2 = cache.get_weather_data('New York')    # Should be cache hit
        
        final_stats = cache.get_cache_statistics()
        print(f"Final statistics: {final_stats}")
        
    finally:
        cache.shutdown()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_refresh_ahead()
        ''', language='python')
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Strategy Comparison Summary
    st.markdown("### 📊 Strategy Comparison Summary")
    
    comparison_data = {
        'Strategy': ['Lazy Loading', 'Write Through', 'Write Behind', 'Refresh Ahead'],
        'Write Latency': ['N/A (Read-only)', 'High', 'Very Low', 'N/A (Read-only)'],
        'Read Latency': ['Medium (cache miss)', 'Low', 'Low', 'Very Low'],
        'Data Consistency': ['Eventual', 'Strong', 'Eventual', 'Eventual'],
        'Implementation': ['Simple', 'Medium', 'Complex', 'Complex'],
        'Use Case': ['Read-heavy', 'Transactional', 'High-write volume', 'Predictable access']
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True)
    
    # Best Practices
    st.markdown("### 💡 Caching Strategy Best Practices")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Strategy Selection Guidelines
    
    **Consider Your Requirements:**
    - **Latency**: How fast do users need responses?
    - **Consistency**: How important is data accuracy?
    - **Volume**: How many reads vs writes?
    - **Complexity**: What can your team maintain?
    
    **Hybrid Approaches:**
    - Combine multiple strategies for different data types
    - Use **Lazy Loading** for reference data
    - Use **Write Through** for critical transactions
    - Use **Write Behind** for analytics data
    - Use **Refresh Ahead** for popular content
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
    st.markdown("""
    # 🗄️ AWS Database Caching
    
    """)
    st.markdown("""<div class="info-box">
                Master Amazon ElastiCache for high-performance, in-memory caching. Learn to choose between Redis and Memcached, implement optimal caching strategies, and design scalable applications with sub-millisecond response times.
                </div>""", unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🗄️ Amazon ElastiCache", 
        "⚖️ Redis vs. Memcached", 
        "🎯 Use Cases",
        "📋 Caching Strategies"
    ])
    
    with tab1:
        amazon_elasticache_tab()
    
    with tab2:
        redis_vs_memcached_tab()
    
    with tab3:
        use_cases_tab()
    
    with tab4:
        strategies_tab()
    
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
