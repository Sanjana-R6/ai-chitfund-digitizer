import gradio as gr
from app_en import en_app
from app_te import te_app

if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: en_app.launch(
        server_port=7861,
        prevent_thread_lock=True,
        quiet=True,
        
    )).start()
    threading.Thread(target=lambda: te_app.launch(
        server_port=7862,
        prevent_thread_lock=True,
        quiet=True,
        
    )).start()


    with gr.Blocks(
        title="Chit Fund",
        css="""
        :root {
          --primary: #00f2fe;     /* Neon Cyan */
          --secondary: #3a7bd5;   /* Deep Blue */
          --bg-dark: #0b0e14;     /* Deep Navy */
          --text-main: #f8fafc;
          --text-muted: #94a3b8;
          --glass-border: rgba(255, 255, 255, 0.1);
        }

        body, .gradio-container {
            background: radial-gradient(circle at top right, #1e293b 0%, var(--bg-dark) 100%) !important;
            font-family: 'Times New Roman', Times, serif !important;
            color: var(--text-main) !important;
            border: none !important;
        }

        .header-area {
            padding: 30px 0;
            border-bottom: 1px solid var(--glass-border);
            margin-bottom: 60px;
        }

        .main-container {
            max-width: 1200px !important;
            margin: auto !important;
            padding: 0 20px;
        }

        .hero-section {
            text-align: center;
            padding: 100px 40px;
            background: rgba(255, 255, 255, 0.02);
            backdrop-filter: blur(15px);
            border: 1px solid var(--glass-border);
            border-radius: 30px;
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.4);
        }

        .main-title {
            font-size: 80px !important;
            font-weight: 800 !important;
            color: #ffffff !important;
            text-shadow: 0 0 30px rgba(0, 242, 254, 0.5);
            margin-bottom: 20px !important;
            font-family: 'Times New Roman', Times, serif !important;
        }

        .subtitle {
            font-size: 24px !important;
            color: var(--text-muted) !important;
            margin-bottom: 60px !important;
            font-family: 'Times New Roman', Times, serif !important;
        }

        .lang-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 30px;
            transition: all 0.3s ease;
            cursor: pointer;
            border: 1px solid transparent;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 15px;
            text-decoration: none !important;
        }

        .lang-card:hover {
            background: rgba(0, 242, 254, 0.1);
            border-color: var(--primary);
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0, 242, 254, 0.15);
        }

        .lang-icon { font-size: 50px; }
        .lang-label { font-size: 24px; font-weight: 700; color: white; }

        footer { display: none !important; }
        """
    ) as landing:
        with gr.Column(elem_classes="main-container"):
            # Header matching dashboard frame
            with gr.Row(elem_classes="header-area"):
                with gr.Column(scale=8):
                    gr.HTML("<div style='font-size:32px; font-weight:800; color:var(--primary); font-family: \"Times New Roman\", serif'>🏦 Chit Fund</div>")
                    gr.Markdown("### Transparent. Digital. Instant. — Built for India")
                with gr.Column(scale=2):
                    gr.HTML("<div style='text-align:right; font-size:14px; color:var(--text-muted); padding-top:15px; font-family: \"Times New Roman\", serif'>PORTAL ACCESS</div>")

            with gr.Column(elem_classes="hero-section"):
                gr.HTML("""
                <h1 class="main-title">Chit Fund</h1>
                <p class="subtitle">Empowering local communities with digital transparency.</p>
                """)

                gr.Markdown("<p style='font-size: 18px; font-weight: 600; color: var(--primary); margin-bottom: 40px; letter-spacing: 2px; text-transform: uppercase; font-family: \"Times New Roman\", serif'>Select Language / భాషను ఎంచుకోండి</p>")
                
                with gr.Row():
                    with gr.Column():
                        gr.HTML("""
                        <a href="http://127.0.0.1:7861" class="lang-card">
                            <div class="lang-label">ENGLISH</div>
                        </a>
                        """)
                    with gr.Column():
                        gr.HTML("""
                        <a href="http://127.0.0.1:7862" class="lang-card">
                            <div class="lang-label">తెలుగు</div>
                        </a>
                        """)

                gr.HTML("""
                <div style='margin-top:100px; color:var(--text-muted); font-size:13px; font-weight: 400; opacity: 0.6; font-family: \"Times New Roman\", serif'>
                    POWERED BY OLLAMA + EASYOCR + GRADIO
                </div>
                """)
landing.launch(server_port=7860)