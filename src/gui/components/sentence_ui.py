import gradio as gr

from gui.handlers.sentence_handler import    generate_tsl


def build_sentence_tab():
    with gr.Tab("Sentences"):
        with gr.Row():
            with gr.Column(scale=1):
                gloss = gr.Textbox(
                    label="Gloss sequence",
                    placeholder="เช่น: ข้าวผัด ฉัน กิน",
                    info="ใส่คำศัพท์ไวยากรณ์ภาษามือไทย โดยคั่นด้วยช่องว่าง",
                    interactive=True,
                )


                generate_btn = gr.Button("Generate", variant="primary")

            with gr.Column(scale=2): 
                
                viz_video = gr.Video( 
                    label="TSL Video", 
                    height=650, 
                    elem_id="viz_container", 
                    interactive=False, 
                    autoplay=False,
                )
                
        generate_btn.click(
            fn=generate_tsl,
            inputs=[gloss],
        )