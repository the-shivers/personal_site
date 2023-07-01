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
    conn = sqlite3.connect('chords.db')
    conn.row_factory = sqlite3.Row   # This allows dictionaries to be returned from the fetch methods. 
    cursor = conn.cursor()
    my_query = """
    SELECT s.*, f.fret_stretch, f.fret_max, f.fret_sum, f.f1, f.f2, f.f3, f.f4, f.mute_count, c.root_note, ct.cat, t.name as tuning_name 
        FROM strums s
        JOIN fingerings f
            ON s.fingering_id = f.id
        LEFT JOIN chords c
            ON s.chord_id = c.id
        JOIN chord_types ct
            ON c.chord_type_id = ct.id
        LEFT JOIN tunings t
            ON s.tuning_id = t.id
        WHERE s.chord_id <> ''
            AND f.mute_count = 0
            AND (ct.cat = 'basics' or ct.cat = 'common')
            AND t.name = 'high_g'
            AND f.fret_max <= 4
            AND f.fret_stretch <= 4
        LIMIT 200;
    """
    print(my_query)
    cursor.execute(my_query)
    print('executed')
    rows = cursor.fetchall()
    print('fetched')
    conn.close()
    print(rows[0], rows[0][0])
    return rows

@app.get("/testywesty")
async def testywesty(request: Request):
    return templates.TemplateResponse("testywesty.html", {"request": request})

