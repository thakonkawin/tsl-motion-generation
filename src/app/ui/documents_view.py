import gradio as gr


class DocumentView:
    def __init__(self) -> None:
        pass

    def render_documents_tab(self, tab_id="documents"):

        with gr.Tab("Documents", id=tab_id):
            gr.Markdown("## Documents")
            # btn_home = gr.Button("🏠 Home")
            # btn_users = gr.Button("👤 Users")
            # btn_reports = gr.Button("📊 Reports")
            # btn_settings = gr.Button("⚙️ Settings")
