"""Financial Research Agent Web Interface.

This module provides a Gradio-based web interface for the Financial AI Agent.
It handles user inputs (text and audio), processes queries through the main agent,
and formats outputs for display in a beautiful, dark-themed interface with 3D
visualizations.

Author: rah-9
License: MIT
"""

import gradio as gr
import json
from main import transcribe_audio, process_query


def run_interface(text_input: str, audio_input=None):
    """Run the main Gradio interface.
    
    This function handles inputs from the web interface, calls the processing
    logic, and formats the outputs for display. It supports both text and
    audio inputs.
    
    Args:
        text_input (str): The text query from the user.
        audio_input (str, optional): Path to audio file for transcription.
                                      Defaults to None.
    
    Returns:
        tuple: A tuple containing four elements:
            - filtered_json_output (str): JSON formatted key data
            - topic_summary_output (str): Formatted summary with topic
            - similar_research_output (str): Similar research from memory
            - extra_info_output (str): Additional information and tool outputs
    """
    query = text_input.strip()
    
    # Handle audio input if no text provided
    if not query and audio_input:
        print("[INFO] Transcribing audio input...")
        query = transcribe_audio(audio_input)
        if "[ERROR]" in query:
            return query, "", "", ""
    
    # Validate query input
    if not query:
        error_message = (
            "Please provide a query in the text box or use the microphone."
        )
        return error_message, "", "", ""
    
    print(f"[INFO] Processing query: '{query}'")
    result = process_query(query)
    
    # Handle processing errors
    if "error" in result:
        error_message = f"An error occurred: {result['error']}"
        raw_response = result.get('raw_response', '')
        return error_message, "", raw_response, ""
    
    try:
        # Extract and format core components
        topic = result.get("topic", "N/A")
        summary = result.get("summary", "No summary provided.")
        topic_summary_output = f"## {topic}\n{summary}"
        
        # Create filtered result for JSON display
        filtered_result = {
            "company_name": result.get("company_name"),
            "ticker_symbol": result.get("ticker_symbol"),
            "accuracy_score": result.get("accuracy"),
            "stock_data": result.get("stock_data"),
            "recent_news": result.get("recent_news_summary")
        }
        
        # Format outputs
        filtered_json_output = json.dumps(filtered_result, indent=2)
        similar_research_output = result.get("similar_research", "N/A")
        extra_info_output = result.get("extra_info", "N/A")
        
        return (
            filtered_json_output,
            topic_summary_output,
            similar_research_output,
            extra_info_output
        )
    
    except Exception as e:
        print(f"[ERROR] Failed to format the final response: {e}")
        error_message = f"An error occurred while displaying the result: {e}"
        return error_message, "", "", ""


# HTML template for 3D background animation
HTML_3D_BACKGROUND = """    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
        #bg-animation {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            opacity: 0.5;
        }
        .gradio-container {
            position: relative;
            z-index: 1;
            background-color: rgba(17, 24, 39, 0.8) !important;
            backdrop-filter: blur(10px);
        }
    </style>
    <canvas id="bg-animation"></canvas>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(
            75, 
            window.innerWidth / window.innerHeight, 
            0.1, 
            1000
        );
        const renderer = new THREE.WebGLRenderer({
            canvas: document.getElementById('bg-animation'),
            alpha: true
        });
        renderer.setSize(window.innerWidth, window.innerHeight);
        
        const particles = 5000;
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(particles * 3);
        
        for (let i = 0; i < particles * 3; i++) {
            positions[i] = (Math.random() - 0.5) * 15;
        }
        
        geometry.setAttribute(
            'position', 
            new THREE.BufferAttribute(positions, 3)
        );
        
        const material = new THREE.PointsMaterial({
            size: 0.008,
            color: 0x00ff9a  // A vibrant green accent color
        });
        
        const particleSystem = new THREE.Points(geometry, material);
        scene.add(particleSystem);
        camera.position.z = 5;
        
        function animate() {
            requestAnimationFrame(animate);
            particleSystem.rotation.x += 0.0001;
            particleSystem.rotation.y += 0.0002;
            renderer.render(scene, camera);
        }
        
        animate();
        
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>"""

# CSS styles for the interface
CSS_STYLES = """
body, .gradio-container {
    background-color: #111827; /* Dark blue-gray background */
    font-family: 'Inter', sans-serif;
    color: #f9fafb;
}

h1 {
    color: #f9fafb;
    font-weight: 700;
    text-align: center;
    font-size: 2.5rem !important;
}

h1 > span {
    color: #00ff9a;
}

p.subtitle {
    text-align: center;
    color: #9ca3af;
    font-size: 1.1rem;
}

.gr-button {
    background: #00ff9a;
    color: #111827;
    font-weight: bold;
    border-radius: 8px !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(0, 255, 154, 0.2);
    transition: all 0.3s ease;
}

.gr-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 255, 154, 0.3);
}

.gr-input, .gr-textbox, .gr-code, .gr-json {
    background-color: #1f2937 !important;
    color: #f9fafb !important;
    border-color: #374151 !important;
    border-radius: 8px !important;
}

.gr-tabs button {
    background-color: transparent !important;
    color: #9ca3af !important;
    border: none !important;
}

.gr-tabs button.selected {
    color: #00ff9a !important;
    border-bottom: 2px solid #00ff9a !important;
}

.gr-accordion {
    background-color: #1f2937 !important;
    border-color: #374151 !important;
    border-radius: 8px !important;
}
"""


def create_interface():
    """Create and configure the Gradio interface.
    
    Returns:
        gr.Blocks: The configured Gradio interface object.
    """
    with gr.Blocks(theme=gr.themes.Base(), css=CSS_STYLES) as interface:
        gr.HTML(HTML_3D_BACKGROUND)
        
        with gr.Column():
            gr.Markdown(
                """
                📈 Financial Research Agent
                <p class="subtitle">Your AI-powered assistant for 
                comprehensive financial insights and market analysis.</p>
                """
            )
            
            # Input section
            with gr.Row():
                text_input = gr.Textbox(
                    lines=2,
                    placeholder=(
                        "e.g., 'What is the latest stock price for "
                        "Microsoft?' or 'Summarize recent news about NVIDIA'"
                    ),
                    label="Text Query",
                    elem_id="text_query"
                )
                audio_input = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="Or Speak Your Query",
                )
            
            submit_btn = gr.Button("Analyze", variant="primary")
            
            # Output section
            with gr.Accordion("📝 Summary", open=True):
                topic_summary = gr.Markdown()
            
            with gr.Tabs():
                with gr.TabItem("📊 Key Data"):
                    stock_data = gr.Code(
                        label="Structured Data (JSON)", 
                        language="json"
                    )
                
                with gr.TabItem("📚 Similar Research"):
                    similar_research = gr.Markdown()
                
                with gr.TabItem("ℹ️ Extra Info"):
                    extra_info = gr.Textbox(
                        label="Tool Outputs (e.g., Wikipedia)", 
                        lines=10
                    )
        
        # Connect interface events
        submit_btn.click(
            fn=run_interface,
            inputs=[text_input, audio_input],
            outputs=[stock_data, topic_summary, similar_research, extra_info]
        )
    
    return interface


def main():
    """Launch the Financial Research Agent web interface.
    
    This function creates and launches the Gradio interface with debugging
    enabled for development purposes.
    """
    interface = create_interface()
    interface.launch(debug=True)


if __name__ == "__main__":
    main()
