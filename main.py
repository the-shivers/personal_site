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
async def get_data(
    fret_max: int = 3,
    fret_stretch: int = 3,
    tuning_name: str = 'high_g',
    mutes: int = 0,
    limit: int = 200,
    disallowed_roots: str = '',
    disallowed_types: str = 'added,jazz_variations_2,jazz_variations_1,altered,extended'
):
    conn = sqlite3.connect('chords.db')
    conn.row_factory = sqlite3.Row   # This allows dictionaries to be returned from the fetch methods. 
    cursor = conn.cursor()

    my_query = f"""
        SELECT *
        FROM strums
        WHERE chord_id <> ''
            AND mute_count == :mutes
            AND fret_max <= :fret_max
            AND fret_stretch <= :fret_stretch
            AND tuning_name = :tuning_name
            AND chord_type NOT IN (:format_disallowed_types)
            AND chord_root NOT IN (:format_disallowed_roots)
        LIMIT :limit;
    """

    format_disallowed_roots = ', '.join([f"'{i}'" for i in disallowed_roots.split(',') if i != ''])
    format_disallowed_types = ', '.join([f"'{i}'" for i in disallowed_types.split(',') if i != ''])
    my_params = {
        'mutes': mutes,
        'fret_max': fret_max,
        'fret_stretch': fret_stretch,
        'tuning_name': tuning_name,
        'format_disallowed_types': format_disallowed_types,
        'format_disallowed_roots': format_disallowed_roots,
        'limit': limit
    }

    print(my_query)
    cursor.execute(my_query, my_params)
    print('executed')
    rows = cursor.fetchall()
    print('fetched')
    conn.close()
    print(rows[0], rows[0][0])
    return rows

@app.get("/testywesty")
async def testywesty(request: Request):
    return templates.TemplateResponse("testywesty.html", {"request": request})

