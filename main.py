from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/nice-text")
async def nice_text(request: Request):
    return templates.TemplateResponse("nice_text.html", {"request": request})

