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

class MyStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        
        # Add custom headers here
        response.headers['Cache-Control'] = 'public, max-age=31536000'
        return response

app.mount("/media", MyStaticFiles(directory="/root/personal_site/media"), name="media")

def split_for_superscript(chord):
   match = re.search(r'(\d|min|Maj|sus)', chord)
   if match:
       index = match.start()
       return chord[:index], chord[index:]
   else:
       return chord, ''
   
def split_chord(chord: str) -> tuple:
    match = re.match(r'([A-Ga-g][s]?)(.*)', chord)
    if match:
        return match.group(1), match.group(2)
    else:
        return '', ''

@app.get("/uke/{tuning_name}/{chord_abbrv}", response_class=HTMLResponse)
async def chord(request: Request, chord_abbrv: str, tuning_name: str, id: int = -1):
    try:
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