import gradio as gr
from src.services.dataset_service import DatasetService
from src.services.motion_service import MotionService
from src.services.render_service import RenderService


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
            fn=generate_tsl_controller, inputs=[gloss], outputs=[viz_video]
        )


def generate_tsl_controller(text_input):
    cleaned_text = text_input.strip()

    glosses = cleaned_text.split()

    result_query = DatasetService.search_gloss_sequence(glosses=glosses)
    if not result_query.success:
        gr.Warning(result_query.message)

    result = RenderService.render_sentence(df=result_query.data)
    if not result.success:
        gr.Warning(result.message)

    return result.data
