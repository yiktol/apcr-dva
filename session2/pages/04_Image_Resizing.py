import streamlit as st
import boto3
import json
import time
from PIL import Image
import io
import requests
from botocore.exceptions import ClientError, NoCredentialsError
import uuid
import logging
import sys
from datetime import datetime
from typing import Optional, Tuple
import utils.common as common
import utils.authenticate as authenticate


# Configure page
st.set_page_config(
    page_title="Smart Image Resizer",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

class CloudWatchLogger:
    """Custom logger that writes to both CloudWatch and terminal"""
    
    def __init__(self, log_group_name: str = "smart-image-resizer", log_stream_name: str = None):
        self.log_group_name = log_group_name
        self.log_stream_name = log_stream_name or f"streamlit-app-{datetime.now().strftime('%Y-%m-%d')}"
        
        # Initialize CloudWatch client
        try:
            self.cloudwatch_client = boto3.client('logs', region_name='ap-southeast-1')
            self._setup_cloudwatch_logging()
        except Exception as e:
            print(f"Failed to initialize CloudWatch logging: {e}")
            self.cloudwatch_client = None
        
        # Setup terminal logging
        self._setup_terminal_logging()
    
    def _setup_terminal_logging(self):
        """Setup terminal logging with custom formatter"""
        self.logger = logging.getLogger('smart_image_resizer')
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers to prevent duplicates
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Custom formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler for local development
        try:
            file_handler = logging.FileHandler('smart_image_resizer.log')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            self.logger.warning(f"Could not create file handler: {e}")
    
    def _setup_cloudwatch_logging(self):
        """Setup CloudWatch log group and stream"""
        try:
            # Create log group if it doesn't exist
            try:
                self.cloudwatch_client.create_log_group(logGroupName=self.log_group_name)
                self.logger.info(f"Created CloudWatch log group: {self.log_group_name}")
            except ClientError as e:
                if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                    raise
            
            # Create log stream if it doesn't exist
            try:
                self.cloudwatch_client.create_log_stream(
                    logGroupName=self.log_group_name,
                    logStreamName=self.log_stream_name
                )
                self.logger.info(f"Created CloudWatch log stream: {self.log_stream_name}")
            except ClientError as e:
                if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                    raise
                    
        except Exception as e:
            self.logger.error(f"CloudWatch setup failed: {e}")
            raise
    
    def _send_to_cloudwatch(self, level: str, message: str, extra_data: dict = None):
        """Send log message to CloudWatch"""
        if not self.cloudwatch_client:
            return
        
        try:
            # Prepare log event
            log_event = {
                'timestamp': int(time.time() * 1000),
                'message': json.dumps({
                    'timestamp': datetime.now().isoformat(),
                    'level': level,
                    'message': message,
                    'source': 'streamlit-app',
                    'session_id': st.session_state.get('session_id', 'unknown'),
                    **(extra_data or {})
                })
            }
            
            # Send to CloudWatch
            self.cloudwatch_client.put_log_events(
                logGroupName=self.log_group_name,
                logStreamName=self.log_stream_name,
                logEvents=[log_event]
            )
        except Exception as e:
            # Don't let CloudWatch errors break the app
            self.logger.error(f"Failed to send log to CloudWatch: {e}")
    
    def info(self, message: str, extra_data: dict = None):
        """Log info message"""
        self.logger.info(message)
        self._send_to_cloudwatch('INFO', message, extra_data)
    
    def error(self, message: str, extra_data: dict = None):
        """Log error message"""
        self.logger.error(message)
        self._send_to_cloudwatch('ERROR', message, extra_data)
    
    def warning(self, message: str, extra_data: dict = None):
        """Log warning message"""
        self.logger.warning(message)
        self._send_to_cloudwatch('WARNING', message, extra_data)
    
    def debug(self, message: str, extra_data: dict = None):
        """Log debug message"""
        self.logger.debug(message)
        self._send_to_cloudwatch('DEBUG', message, extra_data)

# Initialize global logger
@st.cache_resource
def get_logger():
    """Get or create logger instance"""
    try:
        return CloudWatchLogger()
    except Exception as e:
        st.error(f"Failed to initialize logger: {e}")
        # Fallback to basic logging
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger('smart_image_resizer_fallback')

logger = get_logger()

# Custom CSS for modern UI (same as before)
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .upload-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #dee2e6;
        text-align: center;
        margin: 1rem 0;
    }
    
    .status-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .success-card {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    
    .info-card {
        background: #d1ecf1;
        border: 1px solid #b8daff;
        color: #0c5460;
    }
    
    .error-card {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    
    .sidebar-content {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .log-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        font-family: monospace;
        font-size: 12px;
        max-height: 200px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

class ImageProcessor:
    """Handles AWS operations for image processing with logging"""
    
    def __init__(self, logger):
        self.logger = logger
        self.s3_client = None
        self.bucket_name = None
        self.processed_bucket_name = None
        self.initialize_aws_clients()
    
    def initialize_aws_clients(self):
        """Initialize AWS clients with error handling and logging"""
        try:
            self.logger.info("Initializing AWS clients...")
            self.s3_client = boto3.client('s3', region_name='ap-southeast-1')
            
            # Get bucket names from environment or Streamlit secrets
            self.bucket_name = st.secrets.get("S3_UPLOAD_BUCKET", "image-processor-upload-875692608981")
            self.processed_bucket_name = st.secrets.get("S3_PROCESSED_BUCKET", "image-processor-processed-dev-875692608981")
            
            self.logger.info("AWS clients initialized successfully", {
                'upload_bucket': self.bucket_name,
                'processed_bucket': self.processed_bucket_name
            })
            
        except Exception as e:
            error_msg = f"Failed to initialize AWS clients: {str(e)}"
            self.logger.error(error_msg, {'error_type': type(e).__name__})
            st.error(error_msg)
    
    def upload_image(self, image_file, filename: str) -> bool:
        """Upload image to S3 bucket with logging"""
        try:
            self.logger.info(f"Starting image upload: {filename}", {
                'filename': filename,
                'file_size': image_file.size if hasattr(image_file, 'size') else 'unknown'
            })
            
            if not self.s3_client:
                raise Exception("S3 client not initialized")
            
            # Upload file
            self.s3_client.upload_fileobj(
                image_file,
                self.bucket_name,
                filename,
                ExtraArgs={'ContentType': 'image/jpg'}
            )
            
            self.logger.info(f"Image uploaded successfully: {filename}", {
                'filename': filename,
                'bucket': self.bucket_name,
                'status': 'success'
            })
            
            return True
            
        except Exception as e:
            error_msg = f"Upload failed: {str(e)}"
            self.logger.error(error_msg, {
                'filename': filename,
                'bucket': self.bucket_name,
                'error_type': type(e).__name__
            })
            st.error(f"{error_msg}, Bucket Name {self.bucket_name}")
            return False
    
    def check_processed_image(self, filename: str, max_attempts: int = 30) -> Tuple[Optional[str], Optional[str]]:
        """Check if processed image is available and return URL with logging"""
        base_name = filename.rsplit('.', 1)[0]
        
        self.logger.info(f"Checking for processed image: {filename}", {
            'filename': filename,
            'base_name': base_name,
            'max_attempts': max_attempts
        })
        
        for attempt in range(max_attempts):
            self.logger.debug(f"Attempt {attempt + 1}/{max_attempts} for {filename}")
            
            try:
                # Check for different size variants
                for size in ['web', 'mobile', 'tablet']:
                    key = f"{base_name}_{size}.jpg"
                    
                    try:
                        self.s3_client.head_object(Bucket=self.processed_bucket_name, Key=key)
                        
                        # Generate presigned URL
                        url = self.s3_client.generate_presigned_url(
                            'get_object',
                            Params={'Bucket': self.processed_bucket_name, 'Key': key},
                            ExpiresIn=3600
                        )
                        
                        self.logger.info(f"Found processed image: {key}", {
                            'filename': filename,
                            'size_variant': size,
                            'key': key,
                            'attempt': attempt + 1
                        })
                        
                        return url, size
                        
                    except ClientError as e:
                        if e.response['Error']['Code'] != 'NoSuchKey':
                            self.logger.warning(f"Unexpected error checking {key}: {e}")
                        continue
                        
            except Exception as e:
                self.logger.error(f"Error in attempt {attempt + 1}: {e}", {
                    'filename': filename,
                    'attempt': attempt + 1,
                    'error_type': type(e).__name__
                })
                
            if attempt < max_attempts - 1:
                time.sleep(2)
        
        self.logger.warning(f"Processed image not found after {max_attempts} attempts", {
            'filename': filename,
            'max_attempts': max_attempts
        })
        
        return None, None

def initialize_session():
    """Initialize session state with logging"""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        logger.info("New session started", {'session_id': st.session_state.session_id})

def main():
    """Main Streamlit application with comprehensive logging"""
    initialize_session()
    
    logger.info("Application started", {
        'session_id': st.session_state.session_id,
        'timestamp': datetime.now().isoformat()
    })
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📸 Smart Image Resizer</h1>
        <p>Upload your images and get them automatically resized for web, mobile, and tablet devices</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize processor
    processor = ImageProcessor(logger)
    
    # Sidebar
    with st.sidebar:
        
        common.render_sidebar()
        
        st.markdown("### ⚙️ Configuration")
        
        st.markdown("""
        <div class="sidebar-content">
            <h4>How it works:</h4>
            <ol>
                <li>📤 Upload your image</li>
                <li>☁️ Image stored in S3</li>
                <li>⚡ Lambda function triggered</li>
                <li>🔄 Auto-resize for multiple devices</li>
                <li>✅ Download processed images</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Settings
        max_file_size = st.slider("Max file size (MB)", 1, 10, 5)
        auto_refresh = st.checkbox("Auto-refresh results", value=True)
        
        if auto_refresh:
            refresh_interval = st.slider("Refresh interval (seconds)", 2, 10, 5)
        
        # Debug section
        show_logs = st.checkbox("Show debug logs")
        
        if show_logs:
            st.markdown("### 📋 Session Info")
            st.markdown(f"**Session ID:** `{st.session_state.session_id[:8]}...`")
            
            if hasattr(st.session_state, 'processing_file'):
                st.markdown(f"**Processing:** `{st.session_state.processing_file}`")
                elapsed = int(time.time() - st.session_state.upload_time)
                st.markdown(f"**Elapsed:** `{elapsed}s`")
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📤 Upload Image")
        
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg'],
            help=f"Maximum file size: {max_file_size}MB"
        )
        
        if uploaded_file:
            # Log file upload
            logger.info("File uploaded via UI", {
                'filename': uploaded_file.name,
                'file_size': uploaded_file.size,
                'file_type': uploaded_file.type
            })
            
            # Validate file size
            if uploaded_file.size > max_file_size * 1024 * 1024:
                error_msg = f"File size exceeds {max_file_size}MB limit"
                logger.warning(error_msg, {
                    'filename': uploaded_file.name,
                    'file_size': uploaded_file.size,
                    'max_size': max_file_size * 1024 * 1024
                })
                st.error(error_msg)
                return
            
            # Display original image
            st.markdown("#### Original Image")
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption=f"Original: {uploaded_file.name}", use_container_width=True)
                
                logger.debug("Image displayed successfully", {
                    'filename': uploaded_file.name,
                    'image_size': image.size,
                    'image_mode': image.mode
                })
                
            except Exception as e:
                logger.error(f"Failed to display image: {e}", {
                    'filename': uploaded_file.name,
                    'error_type': type(e).__name__
                })
                st.error("Failed to display image")
                return
            
            # Upload button
            if st.button("🚀 Process Image", type="primary"):
                logger.info("Process image button clicked", {'filename': uploaded_file.name})
                
                with st.spinner("Uploading image..."):
                    # Generate unique filename
                    unique_filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
                    
                    # Reset file pointer
                    uploaded_file.seek(0)
                    
                    # Upload to S3
                    if processor.upload_image(uploaded_file, unique_filename):
                        st.success("✅ Image uploaded successfully!")
                        st.session_state.processing_file = unique_filename
                        st.session_state.upload_time = time.time()
                        
                        logger.info("Image processing started", {
                            'original_filename': uploaded_file.name,
                            'unique_filename': unique_filename,
                            'upload_time': st.session_state.upload_time
                        })
                        
                        st.rerun()
    
    with col2:
        st.markdown("### 🔄 Processing Status")
        
        if hasattr(st.session_state, 'processing_file'):
            filename = st.session_state.processing_file
            elapsed_time = int(time.time() - st.session_state.upload_time)
            
            # Status card
            st.markdown(f"""
            <div class="status-card info-card">
                <h4>⏳ Processing: {filename}</h4>
                <p>Elapsed time: {elapsed_time} seconds</p>
                <div style="width: 100%; background-color: #e9ecef; border-radius: 5px;">
                    <div style="width: {min(elapsed_time * 2, 100)}%; background-color: #007bff; height: 10px; border-radius: 5px; transition: width 0.5s;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Check for processed images
            with st.spinner("Checking for processed images..."):
                processed_url, size_variant = processor.check_processed_image(filename)
                
                if processed_url:
                    logger.info("Processing completed successfully", {
                        'filename': filename,
                        'size_variant': size_variant,
                        'processing_time': elapsed_time
                    })
                    
                    st.markdown(f"""
                    <div class="status-card success-card">
                        <h4>✅ Processing Complete!</h4>
                        <p>Your image has been successfully processed and resized.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display processed image
                    st.markdown("#### Processed Image")
                    try:
                        response = requests.get(processed_url)
                        processed_image = Image.open(io.BytesIO(response.content))
                        st.image(
                            processed_image, 
                            caption=f"Processed ({size_variant} size): {processed_image.size}",
                            use_container_width=True
                        )
                        
                        # Download button
                        st.download_button(
                            label="💾 Download Processed Image",
                            data=response.content,
                            file_name=f"processed_{filename}",
                            mime="image/jpg"
                        )
                        
                        logger.info("Processed image displayed and download enabled", {
                            'filename': filename,
                            'processed_size': processed_image.size
                        })
                        
                    except Exception as e:
                        error_msg = f"Error displaying processed image: {str(e)}"
                        logger.error(error_msg, {
                            'filename': filename,
                            'error_type': type(e).__name__
                        })
                        st.error(error_msg)
                    
                    # Cleanup session state
                    if st.button("🔄 Process Another Image"):
                        logger.info("Starting new processing session", {
                            'previous_filename': filename
                        })
                        del st.session_state.processing_file
                        del st.session_state.upload_time
                        st.rerun()
            
            # Auto-refresh
            if auto_refresh and not processed_url:
                logger.debug(f"Auto-refresh triggered, waiting {refresh_interval}s", {
                    'filename': filename,
                    'elapsed_time': elapsed_time
                })
                time.sleep(refresh_interval)
                st.rerun()
    


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

