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
    mutes: str = 'false',
    limit: int = 1,
    disallowed_roots: str = '',
    disallowed_types: str = 'added,jazz_variations_2,jazz_variations_1,altered,extended'
):
    conn = sqlite3.connect('chords.db')
    conn.row_factory = sqlite3.Row   # This allows dictionaries to be returned from the fetch methods. 
    conn.set_trace_callback(print)
    cursor = conn.cursor()

    # my_query = f"""
    #     SELECT *
    #     FROM strums
    #     WHERE chord_id <> ''
    #         AND fret_max <= :fret_max
    #         AND fret_stretch <= :fret_stretch
    #         AND tuning_name = :tuning_name
    #         AND mute_count <= :mutes
    #         AND chord_type NOT IN (:format_disallowed_types)
    #         AND root_note NOT IN (:format_disallowed_roots)
    #     ORDER BY RANDOM() 
    #     LIMIT :limit;
    # """

    def build_dict(input_string, base_key):
        print('in build_dict, inptu string is', input_string)
        items = input_string.split(',')
        result_dict = {(f'{base_key}{i}'):(item.replace('s', '#') if len(item) <= 2 else item) for i, item in enumerate(items) }
        print('in build_dict, results dict', result_dict)
        return result_dict
    
    format_disallowed_roots = build_dict(disallowed_roots, 'root')
    format_disallowed_types = build_dict(disallowed_types, 'type') 

    placeholders_roots = ', '.join(':' + str(i) for i in format_disallowed_roots.keys())
    placeholders_types = ', '.join(':' + str(i) for i in format_disallowed_types.keys())

    my_query = f"""
        SELECT *
        FROM strums
        WHERE chord_id <> ''
            AND fret_max <= :fret_max
            AND fret_stretch <= :fret_stretch
            AND tuning_name = :tuning_name
            AND mute_count <= :mutes
            AND chord_cat NOT IN ({placeholders_types})
            AND root_note NOT IN ({placeholders_roots})
        ORDER BY RANDOM() 
        LIMIT :limit;
    """

    mutes_param = 4 if mutes == 'false' else 3
    my_params = {
        'mutes': mutes_param,
        'fret_max': fret_max,
        'fret_stretch': fret_stretch,
        'tuning_name': tuning_name,
        'limit': limit
    }
    my_params = {**my_params, **format_disallowed_roots, **format_disallowed_types}
    print('my params', my_params)
    cursor.execute(my_query, my_params)
    print('executed')
    rows = cursor.fetchall()
    print('fetched')
    conn.close()
    return rows

@app.get("/testywesty")
async def testywesty(request: Request):
    return templates.TemplateResponse("testywesty.html", {"request": request})

