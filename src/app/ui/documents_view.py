import gradio as gr


class DocumentView:
    def __init__(self) -> None:
        pass

    def render_documents_tab(self):

        with gr.Tab("Documents"):
            gr.Markdown("## Documents")
