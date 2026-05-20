import gradio as gr

from src.controllers.text2motion_controller import Text2MotionController


class Text2MotionView:
    def __init__(self, controller: Text2MotionController) -> None:
        self._controller = controller

    def render_text2moition_tab(self, tab_id="text2motion"):

        with gr.Tab("Text2Motion", id=tab_id):
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

                    # histoy list video generated
                    gallery = gr.Gallery(
                        value=[
                            (
                                "/home/thakon/workspaces/tsl-motion-generation/example/angry_tsl.mp4",
                                "Gloss: โกรธ ",
                            ),
                            (
                                "/home/thakon/workspaces/tsl-motion-generation/example/angry_tsl.mp4",
                                "Gloss: กิน ข้าว | Sentence: ฉันกินข้าว",
                            ),
                            (
                                "/home/thakon/workspaces/tsl-motion-generation/example/angry_tsl.mp4",
                                "Gloss: โกรธ | Sentence: ฉันโกรธ",
                            ),
                            (
                                "/home/thakon/workspaces/tsl-motion-generation/example/angry_tsl.mp4",
                                "Gloss: กิน ข้าว | Sentence: ฉันกินข้าว",
                            ),
                            (
                                "/home/thakon/workspaces/tsl-motion-generation/example/angry_tsl.mp4",
                                "Gloss: โกรธ | Sentence: ฉันโกรธ",
                            ),
                            (
                                "/home/thakon/workspaces/tsl-motion-generation/example/angry_tsl.mp4",
                                "Gloss: กิน ข้าว | Sentence: ฉันกินข้าว",
                            ),
                            (
                                "/home/thakon/workspaces/tsl-motion-generation/example/angry_tsl.mp4",
                                "Gloss: โกรธ | Sentence: ฉันโกรธ",
                            ),
                            (
                                "/home/thakon/workspaces/tsl-motion-generation/example/angry_tsl.mp4",
                                "Gloss: กิน ข้าว | Sentence: ฉันกินข้าว",
                            ),
                            (
                                "/home/thakon/workspaces/tsl-motion-generation/example/angry_tsl.mp4",
                                "Gloss: โกรธ | Sentence: ฉันโกรธ",
                            ),
                            (
                                "/home/thakon/workspaces/tsl-motion-generation/example/angry_tsl.mp4",
                                "Gloss: กิน ข้าว | Sentence: ฉันกินข้าว",
                            ),
                            (
                                "/home/thakon/workspaces/tsl-motion-generation/example/angry_tsl.mp4",
                                "Gloss: โกรธ | Sentence: ฉันโกรธ",
                            ),
                            (
                                "/home/thakon/workspaces/tsl-motion-generation/example/angry_tsl.mp4",
                                "Gloss: กิน ข้าว | Sentence: ฉันกินข้าว",
                            ),
                        ],
                        label="Recents",
                        columns=6,
                        rows=10,
                        object_fit="contain",
                        preview=False,
                        elem_id="video_gallery",
                    )

            generate_btn.click(
                fn=self._controller.generate_tsl_controller,
                inputs=[gloss],
                outputs=[viz_video, text_labal],
            )
