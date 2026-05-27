import gradio as gr

from src.controllers.text2motion_controller import Text2MotionController


class Text2MotionView:
    def __init__(self, controller: Text2MotionController) -> None:
        self._controller = controller

    def render_text2moition_tab(self):

        with gr.Tab("Text2Motion"):
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
                        height=550,
                        elem_id="viz_container",
                        interactive=False,
                        autoplay=False,
                    )

            gallery = gr.Gallery(
                value=self._controller.get_recent_controller(),
                label="Recents",
                columns=7,
                object_fit="cover",
                preview=False,
                elem_id="video_gallery",
            )

            generate_btn.click(
                fn=self._controller.generate_tsl_controller,
                inputs=[gloss],
                outputs=[viz_video],
            )

            viz_video.change(
                fn=self._controller.on_video_change_controller,
                inputs=[viz_video, gloss],
                outputs=[gallery, text_labal],
            )
