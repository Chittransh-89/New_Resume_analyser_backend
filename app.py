import gradio as gr
from gradio.routes import mount_gradio_app

from main import app as fastapi_app


# Minimal Gradio interface for the Hugging Face Space.
# The actual Resume Analyzer API remains the existing FastAPI app.
demo = gr.Interface(
    fn=lambda: "Resume Analyzer FastAPI backend is running.",
    inputs=None,
    outputs="text",
    title="Resume Analyzer Backend",
    description="FastAPI backend deployed on Hugging Face Spaces.",
)

# Mount Gradio onto the existing FastAPI application.
# Existing FastAPI routes remain available.
app = mount_gradio_app(
    fastapi_app,
    demo,
    path="/",
)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=7860)