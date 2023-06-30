from fastapi import FastAPI, Request
#from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()
app.mount("/static", StaticFiles(directory="/root/personal_site/static"), name="static")
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
    cursor.execute(
        "SELECT s.*, f.fret_stretch, f.fret_max, f.fret_sum, f.f1, f.f2, f.f3, f.f4 \
        FROM strums s \
        JOIN fingerings f \
            ON s.fingering_id = f.id \
        WHERE fret_max < 4 AND fret_stretch <= 4 AND tuning_id = 1 AND chord_id <> ''"
        )
    rows = cursor.fetchall()

    # Close the database connection
    conn.close()
    return rows

@app.get("/testywesty")
async def testywesty(request: Request):
    return templates.TemplateResponse("testywesty.html", {"request": request})

