import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory="backend/applications/datastar_todo_app/static"),
    name="static",
)
templates = Jinja2Templates(
    directory="backend/applications/datastar_todo_app/templates"
)


@app.get("/", response_class=HTMLResponse)
def get_main_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


def start():
    uvicorn.run(
        "backend.applications.datastar_todo_app.app:start", host="0.0.0.0", port=8001
    )


# if __name__ == "__main__":
#     start()
