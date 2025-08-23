import gradio as gr
import json
from main import transcribe_audio, process_query

def run_interface(text_input: str, audio_input=None):
    """
    Main function to run the Gradio interface. It handles inputs,
    calls the processing logic, and formats the outputs.
    """
    query = text_input.strip()
    if not query and audio_input:
        print("[INFO] Transcribing audio input...")
        query = transcribe_audio(audio_input)
        if "[ERROR]" in query:
            return query, "", "", ""

    if not query:
        return "Please provide a query in the text box or use the microphone.", "", "", ""

    print(f"[INFO] Processing query: '{query}'")
    result = process_query(query)

    if "error" in result:
        error_message = f"An error occurred: {result['error']}"
        raw_response = result.get('raw_response', '')
        return error_message, "", raw_response, ""

    try:
        topic = result.get("topic", "N/A")
        summary = result.get("summary", "No summary provided.")
        topic_summary_output = f"## {topic}\n{summary}"

        filtered_result = {
            "company_name": result.get("company_name"),
            "ticker_symbol": result.get("ticker_symbol"),
            "accuracy_score": result.get("accuracy"),
            "stock_data": result.get("stock_data"),
            "recent_news": result.get("recent_news_summary")
        }
        filtered_json_output = json.dumps(filtered_result, indent=2)

        similar_research_output = result.get("similar_research", "N/A")
        extra_info_output = result.get("extra_info", "N/A")

        return filtered_json_output, topic_summary_output, similar_research_output, extra_info_output

    except Exception as e:
        print(f"[ERROR] Failed to format the final response: {e}")
        return f"An error occurred while displaying the result: {e}", "", "", ""

html_3d_background = """
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
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
</head>
<body>
    <canvas id="bg-animation"></canvas>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('bg-animation'), alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);

        const particles = 5000;
        const geometry = new THREE.BufferGeometry();
        const positions = new Float32Array(particles * 3);

        for (let i = 0; i < particles * 3; i++) {
            positions[i] = (Math.random() - 0.5) * 15;
        }
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

        const material = new THREE.PointsMaterial({
            size: 0.008,
            color: 0x00ff9a // A vibrant green accent color
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
    </script>
</body>
"""

css = """
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

with gr.Blocks(theme=gr.themes.Base(), css=css) as iface:
    gr.HTML(html_3d_background)
    with gr.Column():
        gr.Markdown(
            """
            <h1>📈 Financial Research <span>Agent</span></h1>
            <p class="subtitle">Your AI-powered assistant for comprehensive financial insights and market analysis.</p>
            """
        )

        with gr.Row():
            text_input = gr.Textbox(
                lines=2,
                placeholder="e.g., 'What is the latest stock price for Microsoft?' or 'Summarize recent news about NVIDIA'",
                label="Text Query",
                elem_id="text_query"
            )
            audio_input = gr.Audio(
                sources=["microphone"],
                type="filepath",
                label="Or Speak Your Query",
            )

        submit_btn = gr.Button("Analyze", variant="primary")

        with gr.Accordion("📝 Summary", open=True):
            topic_summary = gr.Markdown()

        with gr.Tabs():
            with gr.TabItem("📊 Key Data"):
                stock_data = gr.Code(label="Structured Data (JSON)", language="json")
            with gr.TabItem("📚 Similar Research"):
                similar_research = gr.Markdown()
            with gr.TabItem("ℹ️ Extra Info"):
                extra_info = gr.Textbox(label="Tool Outputs (e.g., Wikipedia)", lines=10)

    submit_btn.click(
        fn=run_interface,
        inputs=[text_input, audio_input],
        outputs=[stock_data, topic_summary, similar_research, extra_info]
    )

if __name__ == "__main__":
    iface.launch(debug=True)
