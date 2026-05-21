import gradio as gr


class DocumentView:
    def __init__(self) -> None:
        pass

    def render_documents_tab(self):

        with gr.Tab("Documents"):
            gr.Markdown("## Documents")
            # btn_home = gr.Button("🏠 Home")
            # btn_users = gr.Button("👤 Users")
            # btn_reports = gr.Button("📊 Reports")
            # btn_settings = gr.Button("⚙️ Settings")
