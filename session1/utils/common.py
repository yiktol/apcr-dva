import streamlit as st
import uuid
from datetime import datetime
from typing import Optional
import utils.authenticate as authenticate
import streamlit.components.v1 as components


def reset_session():
    """Reset the session state"""
    for key in st.session_state.keys():
        if key not in ["authenticated", "user_cognito_groups", "auth_code","user_info"]:
            del st.session_state[key]  
    
def render_sidebar():
    """Render the sidebar with session information and reset button"""
    st.markdown("#### 🔑 Session Info")
    if 'auth_code' not in st.session_state:
        st.caption(f"**Session ID:** {st.session_state.session_id[:8]}")
    else:
        st.caption(f"**Session ID:** {st.session_state['auth_code'][:8]}")

    if st.button("🔄 Reset Session", use_container_width=True):
        reset_session()
        st.success("Session has been reset successfully!")
        st.rerun()  # Force a rerun to refresh the page

def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]
    
    if "start_time" not in st.session_state:
        st.session_state.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# def reset_session():
#     """Reset all session state variables."""
    
#     # Keep only the session ID but generate a new one
#     st.session_state.session_id = str(uuid.uuid4())[:8]
#     st.session_state.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
#     # Reset all game scores and submissions
#     for i in range(1, 9):  # 8 games
#         st.session_state[f"game{i}_score"] = 0
#         st.session_state[f"game{i}_submitted"] = [False] * 5

def show_tip(tip_text):
    """Display a formatted tip box with the provided text."""
    
    st.markdown(f"""
    <div class="tip-box">
        <strong>💡 Learning Tip:</strong> {tip_text}
    </div>
    """, unsafe_allow_html=True)

       
def apply_styles():
    """Apply custom styling to the Streamlit app."""
    
    # AWS color scheme
    aws_orange = "#FF9900"
    aws_dark = "#232F3E"
    aws_blue = "#1A73E8"
    aws_background = "#FFFFFF"
    
    # CSS for styling
    st.markdown(f"""
    <style>
        .main-header {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #FF9900;
            margin-bottom: 1rem;
        }}
        .sub-header {{
            font-size: 1.8rem;
            font-weight: bold;
            color: #232F3E;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }}
        .section-header {{
            font-size: 1.5rem;
            font-weight: bold;
            color: #232F3E;
            margin-top: 0.8rem;
            margin-bottom: 0.3rem;
        }}
        .info-box {{
            background-color: #F0F2F6;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .success-box {{
            background-color: #D1FAE5;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .warning-box {{
            background-color: #FEF3C7;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .tip-box {{
            background-color: #E0F2FE;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 5px solid #0EA5E9;
        }}
        .step-box {{
            background-color: #FFFFFF;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            border: 1px solid #E5E7EB;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}
        .card {{
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            background-color: white;
            transition: transform 0.3s;
        }}
        .card:hover {{
            transform: translateY(-5px);
        }}
        .aws-orange {{
            color: #FF9900;
        }}
        .aws-blue {{
            color: #232F3E;
        }}
        hr {{
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        /* Make the tab content container take full height */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        .stTabs [data-baseweb="tab"] {{
            height: 50px;
            white-space: pre-wrap;
            background-color: #F8F9FA;
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
            padding-left: 16px;
            padding-right: 16px;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: #FF9900 !important;
            color: white !important;
        }}
        .definition {{
            background-color: #EFF6FF;
            border-left: 5px solid #3B82F6;
            padding: 10px 15px;
            margin: 15px 0;
            border-radius: 0 5px 5px 0;
        }}
        .code-box {{
            background-color: #F8F9FA;
            padding: 15px;
            border-radius: 5px;
            font-family: monospace;
            margin: 15px 0;
            border: 1px solid #E5E7EB;
        }}
        .stButton>button {{
            background-color: #FF9900;
            color: white;
        }}
        .stButton>button:hover {{
            background-color: #FFAC31;
        }}    
        .stApp {{
            color: {aws_dark};
            background-color: {aws_background};
            font-family: 'Amazon Ember', Arial, sans-serif;
        }}
        
        
        /* Success styling */
        .correct-answer {{
            background-color: #D4EDDA;
            color: #155724;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        
        /* Error styling */
        .incorrect-answer {{
            background-color: #F8D7DA;
            color: #721C24;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        
        /* Custom card styling */
        .game-card {{
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        /* Progress bar styling */
        .stProgress > div > div > div {{
            background-color: {aws_orange};
        }}
        
        /* Tip box styling */
        .tip-box {{
            background-color: #E7F3FE;
            border-left: 6px solid {aws_blue};
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }}
        
        /* Make images responsive */
        img {{
            max-width: 100%;
            height: auto;
        }}
        
        /* Score display */
        .score-display {{
            font-size: 1.2rem;
            font-weight: bold;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            margin: 15px 0;
            background-color: #F1F8FF;
        }}
    </style>
    """, unsafe_allow_html=True)

def mermaid(
    code: str, 
    width: str = "auto", 
    height: str = "auto", 
    pan: bool = True, 
    zoom: bool = True, 
    show_controls: bool = True, 
    key: Optional[str] = None
) -> None:
    """Render Mermaid diagrams in Streamlit with configurable dimensions and interactive controls.
    
    Args:
        code: The Mermaid diagram code to render
        width: Width of the container ("auto", "100%", "500px", etc.)
        height: Height of the container ("auto", "100%", "400px", etc.)
        pan: Enable panning functionality
        zoom: Enable zoom functionality
        show_controls: Show zoom control buttons
        key: Optional unique key for the component
    """
    
    def estimate_diagram_height(mermaid_code: str) -> int:
        """Quick estimation for initial render when height is auto."""
        lines = [line.strip() for line in mermaid_code.strip().split('\n') if line.strip()]
        
        # Count meaningful lines (exclude comments and styling)
        content_lines = [line for line in lines 
                        if not line.startswith('%%') 
                        and not line.startswith('classDef') 
                        and not line.startswith('class')]
        
        diagram_type = lines[0].lower() if lines else ""
        node_count = len([line for line in content_lines if '-->' in line or '{' in line])
        
        if 'flowchart' in diagram_type and ('td' in diagram_type or 'tb' in diagram_type):
            return max(300, min(800, 200 + node_count * 60))
        else:
            return max(250, min(600, 150 + node_count * 50))
    
    # Generate unique ID using key, code hash, and timestamp to ensure uniqueness
    import time
    unique_id = key if key else f"{abs(hash(code))}{int(time.time() * 1000) % 10000}"
    
    # Handle height calculation
    if height == "auto":
        calculated_height = estimate_diagram_height(code)
        container_height = f"{calculated_height + (60 if show_controls else 20)}px"
        content_height = calculated_height
    else:
        # Parse height value
        height_str = str(height)
        if height_str.endswith('px'):
            content_height = int(height_str.replace('px', ''))
        elif height_str.endswith('%'):
            content_height = 400  # Default fallback for percentage
        else:
            try:
                content_height = int(height_str)
            except ValueError:
                content_height = 400
        container_height = height_str
    
    # Handle width
    container_width = width if width != "auto" else "100%"
    
    # Build CSS classes and styles based on parameters
    container_cursor = "grab" if pan else "default"
    container_overflow = "auto" if pan else "hidden"
    
    # Zoom control visibility
    zoom_controls_display = "flex" if show_controls and zoom else "none"
    
    components.html(
        f"""
        <div class="mermaid-wrapper" id="mermaid-wrapper-{unique_id}">
            <!-- Zoom Controls -->
            <div class="zoom-controls" id="zoom-controls-{unique_id}" style="display: {zoom_controls_display};">
                <button id="zoom-in-{unique_id}" class="zoom-btn" title="Zoom In">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="11" cy="11" r="8"></circle>
                        <path d="m21 21-4.35-4.35"></path>
                        <line x1="8" y1="11" x2="14" y2="11"></line>
                        <line x1="11" y1="8" x2="11" y2="14"></line>
                    </svg>
                </button>
                <button id="zoom-out-{unique_id}" class="zoom-btn" title="Zoom Out">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="11" cy="11" r="8"></circle>
                        <path d="m21 21-4.35-4.35"></path>
                        <line x1="8" y1="11" x2="14" y2="11"></line>
                    </svg>
                </button>
                <button id="zoom-reset-{unique_id}" class="zoom-btn" title="Reset Zoom">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M3 3l18 18"></path>
                        <path d="M9 9h6v6"></path>
                        <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                </button>
                <span id="zoom-level-{unique_id}" class="zoom-level">100%</span>
            </div>
            
            <!-- Mermaid Container -->
            <div class="mermaid-container" id="mermaid-container-{unique_id}">
                <div class="mermaid-content" id="mermaid-content-{unique_id}">
                    <!-- Mermaid will render here -->
                    <div id="mermaid-diagram-{unique_id}"></div>
                </div>
            </div>
        </div>

        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            
            // Initialize mermaid with unique configuration
            mermaid.initialize({{ 
                startOnLoad: false,  // We'll manually trigger rendering
                theme: 'default',
                flowchart: {{ useMaxWidth: true }},
                themeVariables: {{ primaryColor: '#ff0000' }}
            }});
            
            const containerId = 'mermaid-container-{unique_id}';
            const contentId = 'mermaid-content-{unique_id}';
            const diagramId = 'mermaid-diagram-{unique_id}';
            const container = document.getElementById(containerId);
            const content = document.getElementById(contentId);
            const diagramElement = document.getElementById(diagramId);
            
            // Feature flags
            const zoomEnabled = {str(zoom).lower()};
            const panEnabled = {str(pan).lower()};
            const showControls = {str(show_controls).lower()};
            
            // Function to render mermaid diagram
            async function renderMermaidDiagram() {{
                try {{
                    // Clear any existing content
                    diagramElement.innerHTML = '';
                    
                    // Generate a unique ID for this specific render
                    const renderingId = `mermaid-{unique_id}-${{Date.now()}}`;
                    
                    // Use mermaid.render() for explicit rendering
                    const {{ svg }} = await mermaid.render(renderingId, `{code.strip()}`);
                    
                    // Insert the rendered SVG
                    diagramElement.innerHTML = svg;
                    
                    // Adjust height if auto after rendering
                    if ("{height}" === "auto") {{
                        setTimeout(() => {{
                            const svgElement = diagramElement.querySelector('svg');
                            if (svgElement) {{
                                const rect = svgElement.getBoundingClientRect();
                                const newHeight = Math.max(rect.height + 60, {content_height});
                                container.style.minHeight = newHeight + 'px';
                                
                                // Trigger a resize event for Streamlit
                                if (window.parent) {{
                                    window.parent.postMessage({{
                                        type: 'streamlit:componentReady',
                                        height: newHeight + (showControls ? 60 : 20)
                                    }}, '*');
                                }}
                            }}
                        }}, 100);
                    }}
                    
                }} catch (error) {{
                    console.error('Error rendering Mermaid diagram:', error);
                    diagramElement.innerHTML = `<div style="color: red; padding: 20px;">Error rendering diagram: ${{error.message}}</div>`;
                }}
            }}
            
            // Zoom functionality
            if (zoomEnabled) {{
                const zoomInBtn = document.getElementById('zoom-in-{unique_id}');
                const zoomOutBtn = document.getElementById('zoom-out-{unique_id}');
                const zoomResetBtn = document.getElementById('zoom-reset-{unique_id}');
                const zoomLevelSpan = document.getElementById('zoom-level-{unique_id}');
                
                let currentZoom = 1.0;
                const minZoom = 0.5;
                const maxZoom = 5.0;
                const zoomStep = 0.2;
                
                function updateZoom(newZoom) {{
                    currentZoom = Math.max(minZoom, Math.min(maxZoom, newZoom));
                    content.style.transform = `scale(${{currentZoom}})`;
                    
                    if (showControls && zoomLevelSpan) {{
                        zoomLevelSpan.textContent = Math.round(currentZoom * 100) + '%';
                    }}
                    
                    // Update button states
                    if (showControls) {{
                        if (zoomInBtn) zoomInBtn.disabled = currentZoom >= maxZoom;
                        if (zoomOutBtn) zoomOutBtn.disabled = currentZoom <= minZoom;
                    }}
                }}
                
                // Zoom control event listeners
                if (showControls) {{
                    if (zoomInBtn) zoomInBtn.addEventListener('click', () => updateZoom(currentZoom + zoomStep));
                    if (zoomOutBtn) zoomOutBtn.addEventListener('click', () => updateZoom(currentZoom - zoomStep));
                    if (zoomResetBtn) zoomResetBtn.addEventListener('click', () => updateZoom(1.0));
                }}
                
                // Mouse wheel zoom
                container.addEventListener('wheel', (e) => {{
                    if (e.ctrlKey || e.metaKey) {{
                        e.preventDefault();
                        const delta = e.deltaY > 0 ? -zoomStep : zoomStep;
                        updateZoom(currentZoom + delta);
                    }}
                }});
                
                // Keyboard zoom
                container.addEventListener('keydown', (e) => {{
                    if ((e.ctrlKey || e.metaKey) && (e.key === '+' || e.key === '-' || e.key === '0')) {{
                        e.preventDefault();
                        if (e.key === '+') updateZoom(currentZoom + zoomStep);
                        else if (e.key === '-') updateZoom(currentZoom - zoomStep);
                        else if (e.key === '0') updateZoom(1.0);
                    }}
                }});
                
                // Initialize zoom
                updateZoom(1.0);
            }}
            
            // Pan functionality
            if (panEnabled) {{
                let isPanning = false;
                let startX, startY, scrollLeft, scrollTop;
                
                container.addEventListener('mousedown', (e) => {{
                    if (e.button === 0) {{ // Left mouse button
                        isPanning = true;
                        startX = e.pageX - container.offsetLeft;
                        startY = e.pageY - container.offsetTop;
                        scrollLeft = container.scrollLeft;
                        scrollTop = container.scrollTop;
                        container.style.cursor = 'grabbing';
                    }}
                }});
                
                container.addEventListener('mouseleave', () => {{
                    isPanning = false;
                    container.style.cursor = '{container_cursor}';
                }});
                
                container.addEventListener('mouseup', () => {{
                    isPanning = false;
                    container.style.cursor = '{container_cursor}';
                }});
                
                container.addEventListener('mousemove', (e) => {{
                    if (!isPanning) return;
                    e.preventDefault();
                    const x = e.pageX - container.offsetLeft;
                    const y = e.pageY - container.offsetTop;
                    const walkX = (x - startX) * 1;
                    const walkY = (y - startY) * 1;
                    container.scrollLeft = scrollLeft - walkX;
                    container.scrollTop = scrollTop - walkY;
                }});
            }}
            
            // Make container focusable for keyboard events
            if (zoomEnabled) {{
                container.setAttribute('tabindex', '0');
            }}
            
            // Initialize and render the diagram
            document.addEventListener('DOMContentLoaded', renderMermaidDiagram);
            
            // Also render immediately if DOM is already loaded
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', renderMermaidDiagram);
            }} else {{
                renderMermaidDiagram();
            }}
        </script>

        <style>
            .mermaid-wrapper {{
                position: relative;
                width: {container_width};
                height: {container_height};
                border: 1px solid #e1e5e9;
                border-radius: 6px;
                background: #fafafa;
            }}
            
            .zoom-controls {{
                position: absolute;
                top: 10px;
                right: 10px;
                gap: 5px;
                align-items: center;
                background: rgba(255, 255, 255, 0.9);
                padding: 5px 8px;
                border-radius: 20px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                z-index: 10;
                backdrop-filter: blur(4px);
            }}
            
            .zoom-btn {{
                background: #fff;
                border: 1px solid #ddd;
                border-radius: 4px;
                width: 28px;
                height: 28px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.2s ease;
                color: #555;
            }}
            
            .zoom-btn:hover:not(:disabled) {{
                background: #f0f0f0;
                border-color: #bbb;
                transform: translateY(-1px);
            }}
            
            .zoom-btn:active {{
                transform: translateY(0);
            }}
            
            .zoom-btn:disabled {{
                opacity: 0.5;
                cursor: not-allowed;
            }}
            
            .zoom-level {{
                font-size: 12px;
                color: #666;
                font-weight: 500;
                min-width: 35px;
                text-align: center;
                margin-left: 5px;
            }}
            
            .mermaid-container {{
                height: 100%;
                padding: 20px;
                overflow: {container_overflow};
                display: flex;
                justify-content: center;
                align-items: flex-start;
                position: relative;
                cursor: {container_cursor};
            }}
            
            .mermaid-container:active {{
                cursor: {"grabbing" if pan else container_cursor};
            }}
            
            .mermaid-content {{
                transform-origin: top center;
                transition: transform 0.3s ease;
                min-width: 100%;
                display: flex;
                justify-content: center;
            }}
            
            #mermaid-diagram-{unique_id} {{
                width: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            
            /* Scrollbar styling - only show if panning is enabled */
            {".mermaid-container::-webkit-scrollbar" if pan else ".mermaid-container-hidden-scroll::-webkit-scrollbar"} {{
                width: 8px;
                height: 8px;
            }}
            
            {".mermaid-container::-webkit-scrollbar-track" if pan else ".mermaid-container-hidden-scroll::-webkit-scrollbar-track"} {{
                background: #f1f1f1;
                border-radius: 4px;
            }}
            
            {".mermaid-container::-webkit-scrollbar-thumb" if pan else ".mermaid-container-hidden-scroll::-webkit-scrollbar-thumb"} {{
                background: #c1c1c1;
                border-radius: 4px;
            }}
            
            {".mermaid-container::-webkit-scrollbar-thumb:hover" if pan else ".mermaid-container-hidden-scroll::-webkit-scrollbar-thumb:hover"} {{
                background: #a8a8a8;
            }}
            
            /* Responsive design */
            @media (max-width: 640px) {{
                .zoom-controls {{
                    top: 5px;
                    right: 5px;
                    padding: 3px 6px;
                }}
                
                .zoom-btn {{
                    width: 24px;
                    height: 24px;
                }}
                
                .zoom-level {{
                    font-size: 11px;
                }}
            }}
        </style>
        """,
        height=content_height + (80 if show_controls else 40),  # Dynamic height based on controls
    )


