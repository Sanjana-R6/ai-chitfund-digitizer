import gradio as gr
import pandas as pd

sample_data = [
    {"name": "Ravi",    "amount": 5000, "paid": "✅", "dividend": 500, "due": 0},
    {"name": "Lakshmi","amount": 5000, "paid": "✅", "dividend": 500, "due": 0},
    {"name": "Suresh", "amount": 5000, "paid": "❌", "dividend": 500, "due": 5000},
    {"name": "Priya",  "amount": 5000, "paid": "✅", "dividend": 500, "due": 0},
    {"name": "Ramesh", "amount": 5000, "paid": "❌", "dividend": 500, "due": 5000},
]

def show_ledger(image):
    df = pd.DataFrame(sample_data)
    return df

with gr.Blocks(title="Chit Fund Agent") as app:
    gr.Markdown("# 🏦 Chit Fund Digitizer")
    gr.Markdown("Upload a photo of your chit book to get a digital ledger instantly.")
    
    with gr.Row():
        image_input = gr.Image(label="Upload Chit Book Photo")
    
    submit_btn = gr.Button("Digitize ✨", variant="primary")
    output_table = gr.Dataframe(label="Digital Ledger")
    
    submit_btn.click(show_ledger, inputs=image_input, outputs=output_table)

app.launch()