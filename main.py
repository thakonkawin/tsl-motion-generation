from src.gradio_app import Application

app = Application()
demo = app.build()


app.run()
