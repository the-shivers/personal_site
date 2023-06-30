from fastapi import FastAPI, Request
#from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/nice-text")
async def nice_text(request: Request):
    return templates.TemplateResponse("nice_text.html", {"request": request})

@app.get("/data")
async def get_data():
    # Create/connect to the SQLite database
    conn = sqlite3.connect('chords.db')
    cursor = conn.cursor()

    # Execute a SELECT query
    cursor.execute("SELECT * FROM chords")
    rows = cursor.fetchall()

    # Close the database connection
    conn.close()
    return rows

@app.get("/testywesty")
async def testywesty(request: Request):
    return templates.TemplateResponse("testywesty.html", {"request": request})

