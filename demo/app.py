"""
APCR-DVA Session 1 - Inventory API Client
Streamlit application acting as a client for the serverless microservice.
"""

import streamlit as st
import requests
import json
import time

# ─────────────────────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Inventory API - APCR-DVA",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# Custom CSS for modern UI
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    .metric-card h3 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
    }
    .metric-card p {
        margin: 0.5rem 0 0 0;
        opacity: 0.85;
        font-size: 0.9rem;
    }

    /* Status badges */
    .status-healthy {
        display: inline-block;
        background: #10b981;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-error {
        display: inline-block;
        background: #ef4444;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* Response panel */
    .response-panel {
        background: #1e1e2e;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.85rem;
        color: #cdd6f4;
        overflow-x: auto;
    }

    /* Info boxes */
    .info-box {
        background: #f0f9ff;
        border-left: 4px solid #0ea5e9;
        border-radius: 0 8px 8px 0;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
    }
    .info-box-orange {
        background: #fff7ed;
        border-left: 4px solid #f97316;
        border-radius: 0 8px 8px 0;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: #f8fafc;
    }

    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Table styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Sidebar Configuration
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown("### ⚙️ Configuration")

    api_source = st.radio(
        "API Endpoint",
        ["API Gateway (Direct)", "CloudFront (CDN)"],
        help="Choose whether to hit API Gateway directly or through CloudFront CDN",
    )

    api_gateway_url = st.text_input(
        "API Gateway URL",
        value="https://apcr-dva-api.aws.yikyakyuk.com",
        help="From CloudFormation stack output: ApiGatewayUrl",
    )

    cloudfront_url = st.text_input(
        "CloudFront URL",
        value="https://apcr-dva-cdn.aws.yikyakyuk.com",
        help="From CloudFormation stack output: CloudFrontUrl",
    )

    base_url = cloudfront_url if api_source == "CloudFront (CDN)" else api_gateway_url

    st.markdown("---")
    st.markdown("### 📋 Concepts")
    st.markdown("""
    - **VPC** — Isolated network
    - **Private Subnets** — No internet access
    - **Security Groups** — Stateful firewall
    - **NACLs** — Stateless filtering
    - **VPC Endpoint** — Private DynamoDB access
    - **IAM Roles** — Least privilege
    - **API Gateway** — REST API frontend
    - **CloudFront** — CDN caching
    - **Lambda** — Serverless compute
    - **DynamoDB** — NoSQL database
    """)


# ─────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────
def make_request(method, path, body=None):
    """Make API request and return response details."""
    if not base_url:
        return None, None, "⚠️ Please configure the API URL in the sidebar."

    url = f"{base_url.rstrip('/')}{path}"
    if not url.startswith("http"):
        url = f"https://{url}"
    start = time.time()

    try:
        if method == "GET":
            resp = requests.get(url, timeout=20)
        elif method == "POST":
            resp = requests.post(url, json=body, timeout=20)
        else:
            return None, None, f"Unsupported method: {method}"

        elapsed = (time.time() - start) * 1000  # ms

        response_data = {
            "status_code": resp.status_code,
            "latency_ms": round(elapsed, 1),
            "headers": dict(resp.headers),
            "body": resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text,
            "url": url,
            "via_cloudfront": "x-cache" in resp.headers,
            "cache_status": resp.headers.get("x-cache", "N/A"),
        }
        return resp.status_code, response_data, None

    except requests.exceptions.Timeout:
        return None, None, "⏱️ Request timed out (15s). Lambda may not be able to reach DynamoDB — check VPC endpoint."
    except requests.exceptions.ConnectionError:
        return None, None, "🔌 Connection error. Check the API URL."
    except Exception as e:
        return None, None, f"❌ Error: {str(e)}"


def display_response(response_data):
    """Display API response in a formatted panel."""
    if not response_data:
        return

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        status = response_data["status_code"]
        color = "🟢" if status < 400 else "🔴"
        st.metric("Status", f"{color} {status}")
    with col2:
        st.metric("Latency", f"{response_data['latency_ms']} ms")
    with col3:
        st.metric("Via CloudFront", "Yes" if response_data["via_cloudfront"] else "No")
    with col4:
        st.metric("Cache", response_data["cache_status"])

    with st.expander("📄 Response Body", expanded=True):
        st.json(response_data["body"])

    with st.expander("📨 Response Headers"):
        st.json(response_data["headers"])

    with st.expander("🔗 Request Details"):
        st.code(f"{response_data['url']}", language="text")


# ─────────────────────────────────────────────────────────────
# Main Content
# ─────────────────────────────────────────────────────────────
st.markdown("# 📦 Inventory API Client")
st.markdown(f"**Endpoint:** `{base_url or 'Not configured'}` → via **{api_source}**")

with st.expander("📐 Architecture & Info", expanded=False):
    arch_tab, about_tab = st.tabs(["🏗️ Architecture", "ℹ️ About this App"])
    with arch_tab:
        st.image("architecture-diagram.png", use_container_width=True)
    with about_tab:
        st.markdown("""
        **Serverless Microservice with Private Networking**

        This application deploys a fully serverless inventory API that covers key AWS Developer Associate exam concepts:

        | Layer | Service | Concept |
        |-------|---------|---------|
        | CDN | CloudFront | Content delivery, edge caching |
        | API | API Gateway | REST API, proxy integration |
        | Compute | Lambda | Serverless, event-driven, VPC-attached |
        | Database | DynamoDB | NoSQL, on-demand capacity |
        | Network | VPC + Private Subnets | Isolation, no internet route |
        | Network | VPC Gateway Endpoint | Private access to DynamoDB |
        | Security | Security Groups | Stateful, instance-level firewall |
        | Security | NACLs | Stateless, subnet-level filtering |
        | Identity | IAM Roles + STS | Least privilege, temporary credentials |

        **Data flow:** Users → CloudFront → API Gateway → Lambda (private subnet) → VPC Endpoint → DynamoDB

        The Lambda function has **no internet access**. It reaches DynamoDB exclusively through the VPC Gateway Endpoint, keeping all traffic on the AWS private backbone.
        """)

st.markdown("---")

# Tabs for different operations
tab_health, tab_list, tab_get, tab_create = st.tabs([
    "🏥 Health Check",
    "📋 List Inventory",
    "🔍 Get Item",
    "➕ Create Item",
])

# ─── Health Check Tab ───
with tab_health:
    st.markdown("### Service Health Check")
    st.markdown("""
    <div class="info-box">
        <strong>How it works:</strong> The <code>/health</code> endpoint responds without touching DynamoDB.
        If this works but inventory calls fail, the issue is between Lambda and DynamoDB (VPC endpoint or IAM).
    </div>
    """, unsafe_allow_html=True)

    if st.button("🏥 Check Health", type="primary", key="health_btn"):
        with st.spinner("Checking health..."):
            status, data, error = make_request("GET", "/health")
        if error:
            st.error(error)
        else:
            display_response(data)

# ─── List Inventory Tab ───
with tab_list:
    st.markdown("### List All Inventory Items")
    st.markdown("""
    <div class="info-box">
        <strong>How it works:</strong> Lambda performs a <code>DynamoDB Scan</code> through the VPC Gateway Endpoint.
        Traffic never leaves the AWS private network.
    </div>
    """, unsafe_allow_html=True)

    if st.button("📋 List All Items", type="primary", key="list_btn"):
        with st.spinner("Fetching inventory..."):
            status, data, error = make_request("GET", "/inventory")
        if error:
            st.error(error)
        elif data:
            display_response(data)
            # Show as table too
            if isinstance(data["body"], dict) and "items" in data["body"]:
                items = data["body"]["items"]
                if items:
                    st.markdown("#### 📊 Inventory Table")
                    st.dataframe(
                        items,
                        use_container_width=True,
                        column_config={
                            "itemId": st.column_config.TextColumn("Item ID", width="small"),
                            "name": st.column_config.TextColumn("Name", width="medium"),
                            "category": st.column_config.TextColumn("Category", width="small"),
                            "quantity": st.column_config.NumberColumn("Qty", width="small"),
                            "warehouse": st.column_config.TextColumn("Warehouse Region", width="small"),
                        },
                    )

# ─── Get Item Tab ───
with tab_get:
    st.markdown("### Get Single Item")
    st.markdown("""
    <div class="info-box">
        <strong>How it works:</strong> Lambda performs a <code>DynamoDB GetItem</code> — a point read
        using the partition key, which is the most efficient DynamoDB operation.
    </div>
    """, unsafe_allow_html=True)

    item_id = st.text_input(
        "Item ID",
        value="ITEM-001",
        placeholder="e.g. ITEM-001",
        key="get_item_id",
    )

    if st.button("🔍 Get Item", type="primary", key="get_btn"):
        with st.spinner(f"Fetching {item_id}..."):
            status, data, error = make_request("GET", f"/inventory/{item_id}")
        if error:
            st.error(error)
        else:
            display_response(data)

# ─── Create Item Tab ───
with tab_create:
    st.markdown("### Create New Inventory Item")
    st.markdown("""
    <div class="info-box">
        <strong>How it works:</strong> Lambda performs a <code>DynamoDB PutItem</code> — writes go through
        the same VPC Endpoint. The IAM role must explicitly allow <code>dynamodb:PutItem</code>.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        new_id = st.text_input("Item ID", value="ITEM-006", key="create_id")
        new_name = st.text_input("Name", value="Laptop Stand", key="create_name")
        new_category = st.selectbox("Category", ["Electronics", "Accessories", "Furniture"], key="create_cat")
    with col2:
        new_qty = st.number_input("Quantity", min_value=1, value=50, key="create_qty")
        new_warehouse = st.selectbox(
            "Warehouse Region",
            ["ap-southeast-1", "us-east-1", "eu-west-1", "us-west-2", "ap-southeast-2"],
            key="create_wh",
        )

    if st.button("➕ Create Item", type="primary", key="create_btn"):
        payload = {
            "itemId": new_id,
            "name": new_name,
            "category": new_category,
            "quantity": new_qty,
            "warehouse": new_warehouse,
        }
        with st.spinner("Creating item..."):
            status, data, error = make_request("POST", "/inventory", body=payload)
        if error:
            st.error(error)
        else:
            display_response(data)
            if status == 201:
                st.success(f"✅ Item `{new_id}` created successfully!")


