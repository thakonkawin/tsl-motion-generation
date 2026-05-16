import time

import gradio as gr

from src.services.dataset_service import DatasetService

# from src.services.motion_service import MotionService
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
                text_labal = gr.Textbox(label="Sentence", interactive=False)
                viz_video = gr.Video(
                    label="TSL Video",
                    height=600,
                    elem_id="viz_container",
                    interactive=False,
                    autoplay=False,
                )

                # histoy list video generated
                # gr.Examples(
                #     examples=[
                #         ["example/angry_tsl.mp4"],
                #         ["example/angry_tsl.mp4"],
                #         ["example/angry_tsl.mp4"],
                #     ],
                #     inputs=[viz_video],
                #     outputs=[viz_video],
                #     fn=None,
                #     cache_examples=False,
                #     label="Recents",
                #     examples_per_page=3,  #
                # )

        generate_btn.click(
            fn=generate_tsl_controller, inputs=[gloss], outputs=[viz_video, text_labal]
        )


def generate_tsl_controller(text_input):
    start = time.time()
    cleaned_text = text_input.strip()

    glosses = cleaned_text.split()

    result_query = DatasetService.search_gloss_sequence(glosses=glosses)
    if not result_query.success:
        raise gr.Error(result_query.message)

    result = RenderService.render_sentence(df=result_query.data)
    if not result.success:
        raise gr.Error(result.message)

    elapsed = time.time() - start
    print(f"Time Redering: {elapsed / 60:.2f} นาที")
    return result.data, cleaned_text
