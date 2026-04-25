import gradio as gr

def add_row(rows):
    rows.append({"word": "", "expr": "F1"})
    return rows

def del_row(rows):
    if len(rows) > 0:
        rows.pop()
    return rows

def build_sentence_tab():
    with gr.Tab("Sentences"):
        with gr.Row():
            with gr.Column(scale=1):

                state = gr.State([{"word": "", "expr": "F1"}])

                # 🔹 GROUP: WORD INPUT
                with gr.Group(elem_classes=["box"]):
                    gr.Markdown("### Create sentence")

                    with gr.Row():
                        add_btn = gr.Button("+ Add", elem_classes=["green-btn"])
                        
                        del_btn = gr.Button("- Delete", elem_classes=["red-btn"])

                    gr.Markdown("")  # 

                    @gr.render(inputs=state)
                    def show(rows):
                        with gr.Column():
                            for i, row in enumerate(rows):
                                with gr.Row():
                                    gr.Textbox(value=row["word"], label=f"Word {i+1}")
                                    gr.Dropdown(
                                        ["F1","F2","F3"],
                                        value=row["expr"],
                                        label="Expression",
                                        interactive=True,
                                    )


                with gr.Group(elem_classes=["box"]):
                    gr.Markdown("### Gender")
                    gr.Radio(["Male", "Female", "Nutral"], value="Male", label="Gender", interactive=True)

                # 🔹 GROUP: RESOLUTION
                with gr.Group(elem_classes=["box"]):
                    gr.Markdown("### Resolution")
                    gr.Radio([512, 720, 1080], value=512, label="Resolution", interactive=True)

                generate_button = gr.Button("Generate", variant="primary")

            with gr.Column(scale=2): 
                gr.Textbox(label=f"Gloss sequence")
                viz_video = gr.Video( 
                    label="TSL Video", 
                    height=650, 
                    elem_id="viz_container", 
                    interactive=False, 
                    autoplay=False,
                )
                
        add_btn.click(
                    fn=add_row,
                    inputs=state,
                    outputs=state
                )

        del_btn.click(
                    fn=del_row,
                    inputs=state,
                    outputs=state
                )