import gradio as gr

from core.controllers.sentence_controller import SentenceController


class SentenceTab:
    def __init__(self, controller: SentenceController) -> None:
        self._controller = controller

    def build_sentence_tab(self):
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
                    # text_labal = gr.Textbox(label="Sentence", interactive=False)
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
                fn=self._controller.generate_tsl_controller,
                inputs=[gloss],
                outputs=[viz_video],
            )
