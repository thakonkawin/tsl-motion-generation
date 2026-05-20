import gradio as gr

from src.controllers.text2motion_controller import Text2MotionController

VIDEOS = [
    {
        "video": "/home/thakon/workspaces/tsl-motion-generation/example/angry_tsl.mp4",
        "text": "test a very long string here to see if it wraps or not",
    },
    {
        "video": "/home/thakon/workspaces/tsl-motion-generation/example/angry_tsl.mp4",
        "text": "another very very very long sentence for testing width",
    },
]


class Text2MotionView:
    def __init__(self, controller: Text2MotionController) -> None:
        self._controller = controller

    def render_text2moition_tab(self, tab_id="text2motion"):

        with gr.Tab("Text2Motion", id=tab_id):
            with gr.Row():
                # RIGHT
                with gr.Column(scale=2):
                    text_labal = gr.Textbox(
                        label="Sentence",
                        interactive=False,
                    )

                    viz_video = gr.Video(
                        label="TSL Video",
                        height=550,
                        interactive=False,
                    )

                # LEFT
                with gr.Column(scale=1):
                    gloss = gr.Textbox(
                        label="Gloss sequence",
                        placeholder="เช่น: ข้าวผัด ฉัน กิน",
                    )

                    generate_btn = gr.Button(
                        "Generate",
                        variant="primary",
                    )

                    gr.Markdown("## Recent Videos")

                    for item in VIDEOS:
                        gr.HTML(
                            f"""
                            <div style="
                                border:1px solid #ddd;
                                border-radius:10px;
                                padding:10px;
                                margin-bottom:12px;
                            ">
                                <video width="20%" controls>
                                    <source
                                        src="/gradio_api/file={item["video"]}"
                                        type="video/mp4"
                                    >
                                </video>

                                <p style="
                                    margin-top:8px;
                                    font-size:14px;
                                    line-height:1.4;
                                ">
                                    {item["text"]}
                                </p>
                            </div>
                            """
                        )

            generate_btn.click(
                fn=self._controller.generate_tsl_controller,
                inputs=[gloss],
                outputs=[viz_video, text_labal],
            )
