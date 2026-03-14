import gradio as gr
from app_en import en_app
from app_te import te_app

if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: en_app.launch(server_port=7861, prevent_thread_lock=True)).start()
    threading.Thread(target=lambda: te_app.launch(server_port=7862, prevent_thread_lock=True)).start()
    
    with gr.Blocks(
        title="ChitSync",
        css="""
        footer { display: none !important; }
        .gradio-container { max-width: 900px !important; margin: auto !important; padding: 40px !important; }
        #en-btn {
            background: #1d4ed8 !important;
            color: white !important;
            border: none !important;
            border-radius: 16px !important;
            font-size: 18px !important;
            font-weight: 600 !important;
            height: 100px !important;
        }
        #te-btn {
            background: #ea580c !important;
            color: white !important;
            border: none !important;
            border-radius: 16px !important;
            font-size: 18px !important;
            font-weight: 600 !important;
            height: 100px !important;
        }
        """
    ) as landing:

        gr.Markdown("""
        <div style='text-align:center;padding:40px 0 20px'>
            <div style='font-size:56px'>🏦</div>
            <h1 style='font-size:36px;font-weight:700;margin:12px 0 4px'>ChitSync</h1>
            <p style='font-size:16px;color:#64748b'>Transparent. Digital. Instant. — Built for India</p>
            <p style='font-size:18px;font-weight:500;color:#1e293b;margin-top:24px'>
                Choose your language / మీ భాష ఎంచుకోండి
            </p>
        </div>
        """)

        with gr.Row(equal_height=True):
            gr.Button(
                "Continue in English 🇬🇧",
                elem_id="en-btn",
                scale=1,
                link="http://127.0.0.1:7861"
            )
            gr.Button(
                "తెలుగు 🇮🇳",
                elem_id="te-btn",
                scale=1,
                link="http://127.0.0.1:7862"
            )

        gr.Markdown("""
        <div style='text-align:center;margin-top:48px;color:#94a3b8;font-size:12px'>
            Powered by Ollama + EasyOCR + Gradio
        </div>
        """)

    landing.launch(server_port=7860)