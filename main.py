from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import re

app = FastAPI()
app.mount("/static", StaticFiles(directory="/root/personal_site/static"), name="static")
templates = Jinja2Templates(directory="templates")

def split_for_superscript(chord):
   match = re.search(r'(\d|min|Maj|sus)', chord)
   if match:
       index = match.start()
       return chord[:index], chord[index:]
   else:
       return chord, ''

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

# @app.get("/chord/{chord_slug}", response_class=HTMLResponse)
# async def chord(request: Request, chord_slug: str):
#     return templates.TemplateResponse("chord.html", {"request": request, "chord_slug": chord_slug})

@app.get("/uke/{tuning_name}/{chord_abbrv}", response_class=HTMLResponse)
async def chord(request: Request, chord_abbrv: str, tuning_name: str, id: int = -1):
    try:
        def split_chord(chord: str) -> tuple:
            match = re.match(r'([A-Ga-g][s]?)(.*)', chord)
            if match:
                return match.group(1), match.group(2)
            else:
                return '', ''
        root_note, chord_abbrv = split_chord(chord_abbrv)
        conn = sqlite3.connect('chords.db')
        conn.row_factory = sqlite3.Row
        conn.set_trace_callback(print)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM strums WHERE root_note = ? AND chord_abbrv = ? AND tuning_name = ? AND fret_stretch <= 3 AND mute_count = 0 ORDER BY fret_score_beta DESC', [root_note.replace('s','#'), chord_abbrv, tuning_name])
        chord_data = cursor.fetchall()
        cursor.execute('SELECT * FROM tunings ORDER BY CASE WHEN name = ? THEN 1 ELSE 0 END DESC', [tuning_name])
        tunings_data = cursor.fetchall()
        cursor.execute('SELECT * FROM notes ORDER BY CASE WHEN str = ? THEN 1 ELSE 0 END DESC', [root_note.replace('s', '#')])
        roots_data = cursor.fetchall()
        cursor.execute('SELECT * FROM chord_types ORDER BY CASE WHEN abbrv = ? THEN 1 ELSE 0 END DESC', [chord_abbrv])
        chord_types_data = cursor.fetchall()
        if chord_data is None or tunings_data is None or roots_data is None or chord_types_data is None:
            raise HTTPException(status_code=404, detail="Chord not found")

        return templates.TemplateResponse("chord.html", {
            "request": request, 
            "id": id,
            "tuning_name": tuning_name, 
            "chord_data": [dict(i) for i in chord_data],
            "fixed_abbrv": list(split_for_superscript(dict(chord_data[0])['chord_text_abbrv'])),
            "tunings_data": tunings_data,
            "roots_data": roots_data,
            "chord_types_data": chord_types_data
        })

    except Exception as error:
        print(f"An error occurred: {error}")

    finally:
        if conn:
            conn.close()

@app.get("/uke/{tuning_name}", response_class=HTMLResponse)
async def root(request: Request, tuning_name: str):
    try:
        conn = sqlite3.connect('chords.db')
        conn.row_factory = sqlite3.Row
        conn.set_trace_callback(print)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM chord_types ORDER BY id')
        chord_types = cursor.fetchall()
        cursor.execute('SELECT * FROM notes ORDER BY id')
        roots = cursor.fetchall() 

        if chord_types is None or roots is None:
            raise HTTPException(status_code=404, detail="Query returned nothing, probably.")

        return templates.TemplateResponse("chords.html", {
            "request": request, 
            "chord_types": chord_types,
            "roots": roots,
            "tuning_name": tuning_name
        })
    
    except Exception as error:
        print(f"An error occurred: {error}")

    finally:
        if conn:
            conn.close()

@app.get("/uke", response_class=HTMLResponse)
async def root(request: Request):
    try:
        conn = sqlite3.connect('chords.db')
        conn.row_factory = sqlite3.Row
        conn.set_trace_callback(print)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tunings ORDER BY id")
        tunings = cursor.fetchall()

        if tunings is None:
            raise HTTPException(status_code=404, detail="Query returned nothing, probably.")

        return templates.TemplateResponse("uke.html", {
            "request": request, 
            "tunings": tunings
        })
    
    except Exception as error:
        print(f"An error occurred: {error}")

    finally:
        if conn:
            conn.close()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    try:
        conn = sqlite3.connect('chords.db')
        conn.row_factory = sqlite3.Row
        conn.set_trace_callback(print)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tunings ORDER BY id")
        tunings = cursor.fetchall()

        if tunings is None:
            raise HTTPException(status_code=404, detail="Query returned nothing, probably.")

        return "This is my homepage. If you want content, try: https://shivers.dev/uke"
    
    except Exception as error:
        print(f"An error occurred: {error}")

    finally:
        if conn:
            conn.close()