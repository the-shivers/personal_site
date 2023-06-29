import sqlite3
import re

# constants
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
NOTES_LEN = len(NOTES)
NOTES_DICT = dict(zip(NOTES, range(NOTES_LEN)))
OCTAVES = 8
ABS_NOTES = [note + str(i) for i in range(1, 1 + OCTAVES) for note in NOTES]
ABS_NOTES_LEN = len(ABS_NOTES)
ABS_NOTES_DICT = dict(zip(ABS_NOTES, range(ABS_NOTES_LEN)))
MAX_FRET = 16
MAX_STRETCH = 7
CHORD_TYPES = [
    {
        'type': 'major',
        'abbrv': '',
        'ints': [0, 4, 7]
    },
    {
        'type': 'minor',
        'abbrv': 'm',
        'ints': [0, 3, 7]
    },
    {
        'type': 'diminished',
        'abbrv': 'dim',
        'ints': [0, 3, 6]
    },
    {
        'type': 'augmented',
        'abbrv': 'aug',
        'ints': [0, 4, 8]
    },
    {
        'type': 'minor7',
        'abbrv': 'm7',
        'ints': [0, 3, 7, 10]
    },
    {
        'type': '7',
        'abbrv': '7',
        'ints': [0, 4, 7, 10]
    },
    {
        'type': 'major7',
        'abbrv': 'Maj7',
        'ints': [0, 4, 7, 11]
    }
]

TUNINGS = [
    {'name': 'high_g', 'abs_notes': ['G4', 'C4', 'E4', 'A4']},
    {'name': 'low_g', 'abs_notes': ['G3', 'C4', 'E4', 'A4']},
    {'name': 'baritone', 'abs_notes': ['D3', 'G3', 'B3', 'E4']}
]

FINGERINGS = []
counter = 0
for g in range(-1, MAX_FRET + 1):
    for c in range(-1, MAX_FRET + 1):
        for e in range(-1, MAX_FRET + 1):
            for a in range(-1, MAX_FRET + 1):
                # Open and muted strings don't count towards stretch or sum.
                zeroless_fingering = [num for num in [g, c, e, a] if num not in [0, -1]]
                FINGERINGS += [{
                    'id': counter,
                    'fingering_str': ",".join([str(g), str(c), str(e), str(a)]),
                    'str1': g,
                    'str2': c,
                    'str3': e,
                    'str4': a,
                    'fret_max': max(zeroless_fingering) if zeroless_fingering else 0,
                    'fret_sum': sum(zeroless_fingering) if zeroless_fingering else 0,
                    'fret_stretch': max(zeroless_fingering) - max(0, min(zeroless_fingering)) 
                        if zeroless_fingering else 0
                }]
                counter += 1



# functions
def note_add_rel(note, n):
    current_index = NOTES_DICT[note]
    new_index = (current_index + n) % NOTES_LEN
    return NOTES[new_index]

def note_add_abs(abs_note, n):
    current_index = ABS_NOTES_DICT[abs_note]
    new_index = current_index + n
    return ABS_NOTES[new_index]

def get_rel_note(abs_note):
    return re.sub(r'\d', '', abs_note)



##############
### SQLite ###
##############
conn = sqlite3.connect('chords.db')
cursor = conn.cursor()

# Notes table
notes_table_name = 'notes'
notes_table_schema = """
    id INTEGER PRIMARY KEY,
    str TEXT NOT NULL UNIQUE
"""
cursor.execute(f'CREATE TABLE IF NOT EXISTS {notes_table_name} ({notes_table_schema})')
for i in range(len(NOTES)):
    placeholders = ['?, ?']
    values = [i, NOTES[i]]
    cursor.execute(f'INSERT INTO {notes_table_name} (id, str) VALUES (?, ?)', values)


# Chord Types
chord_types_table_name = 'chord_types'
chord_types_table_schema = """
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL UNIQUE,
    abbrv TEXT NOT NULL UNIQUE,
    int_str TEXT NOT NULL UNIQUE
"""
cursor.execute(f'CREATE TABLE IF NOT EXISTS {chord_types_table_name} ({chord_types_table_schema})')
for i in range(len(CHORD_TYPES)):
    placeholders = '?, ?, ?, ?'
    values = [
        i, 
        CHORD_TYPES[i]['type'], 
        CHORD_TYPES[i]['abbrv'], 
        ','.join([str(x) for x in CHORD_TYPES[i]['ints']])
    ]
    cursor.execute(f'INSERT INTO {chord_types_table_name} (id, type, abbrv, int_str) VALUES ({placeholders})', values)


# Chords
chords = []
counter = 0
for note in NOTES:
    for chord_type in CHORD_TYPES:
        chord_notes = []
        for i in chord_type['ints']:
            chord_notes += [note_add_rel(note, i)]
        chords += [{
            'id': counter,
            'root': note,
            'type': chord_type['type'],
            'notes': chord_notes,
            'notes_str': ','.join(chord_notes)
        }]
        counter += 1

chords_table_name = 'chords'
chords_table_schema = """
    id INTEGER PRIMARY KEY,
    root_note_id INTEGER NOT NULL,
    root_note TEXT NOT NULL,
    chord_type_id INTEGER NOT NULL,
    chord_type TEXT NOT NULL,
    rel_notes_str TEXT NOT NULL,
    FOREIGN KEY (root_note_id) REFERENCES notes (id),
    FOREIGN KEY (chord_type_id) REFERENCES chord_types (id)
"""
cursor.execute(f'CREATE TABLE IF NOT EXISTS {chords_table_name} ({chords_table_schema})')
result = cursor.execute(
    'select \
        notes.id as root_note_id, \
        notes.str as root_note, \
        chord_types.id as chord_type_id, \
        chord_types.type as chord_type, \
        chord_types.int_str \
    from notes cross join chord_types order by 1, 2')
data = result.fetchall()
for i in range(len(data)):
    placeholders = '?, ?, ?, ?, ?, ?'
    values = [
        i, 
        data[i][0], 
        data[i][1], 
        data[i][2], 
        data[i][3],
        ",".join(sorted([note_add_rel(data[i][1], int(x)) for x in data[i][4].split(',')]))
    ]
    cursor.execute(f'INSERT INTO {chords_table_name} (id, root_note_id, root_note, chord_type_id, chord_type, rel_notes_str) VALUES ({placeholders})', values)


# Fingerings
fingerings_table_name = 'fingerings'
fingerings_table_schema = """
        id INTEGER PRIMARY KEY,
        fingering_str TEXT NOT NULL UNIQUE,
        f1 INTEGER NOT NULL,
        f2 INTEGER NOT NULL,
        f3 INTEGER NOT NULL,
        f4 INTEGER NOT NULL,
        fret_max INTEGER NOT NULL,
        fret_sum INTEGER NOT NULL,
        fret_stretch INTEGER NOT NULL
"""
cursor.execute(f'CREATE TABLE IF NOT EXISTS {fingerings_table_name} ({fingerings_table_schema})')
for i in range(len(FINGERINGS)):
    placeholders = '?, ?, ?, ?, ?, ?, ?, ?, ?'
    values = [
        i,
        f"{FINGERINGS[i]['str1']},{FINGERINGS[i]['str2']},{FINGERINGS[i]['str3']},{FINGERINGS[i]['str4']}",
        FINGERINGS[i]['str1'],
        FINGERINGS[i]['str2'],
        FINGERINGS[i]['str3'],
        FINGERINGS[i]['str4'],
        FINGERINGS[i]['fret_max'],
        FINGERINGS[i]['fret_sum'],
        FINGERINGS[i]['fret_stretch']
    ]
    cursor.execute(
        f'INSERT INTO {fingerings_table_name} (id, fingering_str, f1, f2, f3, f4, fret_max, fret_sum, fret_stretch) VALUES ({placeholders})', values
    )


# Tunings
tunings_table_name = 'tunings'
tunings_table_schema = """
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    str1 TEXT NOT NULL,
    str2 TEXT NOT NULL,
    str3 TEXT NOT NULL,
    str4 TEXT NOT NULL
"""
cursor.execute(f'CREATE TABLE IF NOT EXISTS {tunings_table_name} ({tunings_table_schema})')
for i in range(len(TUNINGS)):
    placeholders = '?, ?, ?, ?, ?, ?'
    values = [
        i,
        TUNINGS[i]['name'],
        TUNINGS[i]['abs_notes'][0],
        TUNINGS[i]['abs_notes'][1],
        TUNINGS[i]['abs_notes'][2],
        TUNINGS[i]['abs_notes'][3]
    ]
    cursor.execute(
        f'INSERT INTO {tunings_table_name} (id, name, str1, str2, str3, str4) VALUES ({placeholders})', values
    )


# Strums
strums_table_name = 'strums'
strums_table_starter_query = """
    SELECT
        fingerings.id as fingering_id,
        fingerings.f1 as f1,
        fingerings.f2 as f2,
        fingerings.f3 as f3,
        fingerings.f4 as f4,
        tunings.id as tuning_id,
        tunings.name as tuning_name,
        tunings.str1 as str1,
        tunings.str2 as str2,
        tunings.str3 as str3,
        tunings.str4 as str4
    FROM fingerings
    CROSS JOIN tunings
"""
strums_table_schema = """
        id INTEGER PRIMARY KEY,
        fingering_id TEXT NOT NULL,
        tuning_id TEXT NOT NULL,
        chord_id TEXT,
        abs_note_str TEXT,
        abs_note1 TEXT,
        abs_note2 TEXT,
        abs_note3 TEXT,
        abs_note4 TEXT,
        rel_note_str TEXT,
        rel_note1 TEXT,
        rel_note2 TEXT,
        rel_note3 TEXT,
        rel_note4 TEXT,
        root_note TEXT, 
        chord_type TEXT
"""
cursor.execute(f'CREATE TABLE IF NOT EXISTS {strums_table_name} ({strums_table_schema})')
starter_data = cursor.execute(strums_table_starter_query).fetchall()

for i in range(len(starter_data)):
    placeholders = '?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?'
    values = [
        i, 
        starter_data[i][0], 
        starter_data[i][5],
        ",".join([
            note_add_abs(starter_data[i][7], starter_data[i][1]) if starter_data[i][1] >= 0 else '',
            note_add_abs(starter_data[i][8], starter_data[i][2]) if starter_data[i][2] >= 0 else '',
            note_add_abs(starter_data[i][9], starter_data[i][3]) if starter_data[i][3] >= 0 else '',
            note_add_abs(starter_data[i][10], starter_data[i][4]) if starter_data[i][3] >= 0 else ''
        ]),
        note_add_abs(starter_data[i][7], starter_data[i][1]) if starter_data[i][1] >= 0 else '',
        note_add_abs(starter_data[i][8], starter_data[i][2]) if starter_data[i][2] >= 0 else '',
        note_add_abs(starter_data[i][9], starter_data[i][3]) if starter_data[i][3] >= 0 else '',
        note_add_abs(starter_data[i][10], starter_data[i][4]) if starter_data[i][3] >= 0 else '',
        ",".join(sorted(list(set([x for x in [
            get_rel_note(note_add_abs(starter_data[i][7], starter_data[i][1])) if starter_data[i][1] >= 0 else '',
            get_rel_note(note_add_abs(starter_data[i][8], starter_data[i][2])) if starter_data[i][2] >= 0 else '',
            get_rel_note(note_add_abs(starter_data[i][9], starter_data[i][3])) if starter_data[i][3] >= 0 else '',
            get_rel_note(note_add_abs(starter_data[i][10], starter_data[i][4])) if starter_data[i][3] >= 0 else ''
        ] if x])))),
        get_rel_note(note_add_abs(starter_data[i][7], starter_data[i][1])) if starter_data[i][1] >= 0 else '',
        get_rel_note(note_add_abs(starter_data[i][8], starter_data[i][2])) if starter_data[i][2] >= 0 else '',
        get_rel_note(note_add_abs(starter_data[i][9], starter_data[i][3])) if starter_data[i][3] >= 0 else '',
        get_rel_note(note_add_abs(starter_data[i][10], starter_data[i][4])) if starter_data[i][3] >= 0 else ''
    ]
    chords = cursor.execute('select * from chords').fetchall()
    filtered_chords = [chord for chord in chords if chord[3] == values[8]]
    if filtered_chords:
        for j in filtered_chords:
            new_vals = [filtered_chords[j][0], filtered_chords[j][1], filtered_chords[j][2]]
            cursor.execute(
                f'INSERT INTO {strums_table_name} \
                (id, fingering_id, tuning_id, abs_note_str, abs_note1, abs_note2, abs_note3, abs_note4, rel_note_str, rel_note1, rel_note2, rel_note3, rel_note4, chord_id, root_note, chord_type) \
                VALUES ({placeholders})', values + new_vals
            )
    else:
        new_vals = ['', '', '']
        cursor.execute(
                f'INSERT INTO {strums_table_name} \
                (id, fingering_id, tuning_id, abs_note_str, abs_note1, abs_note2, abs_note3, abs_note4, rel_note_str, rel_note1, rel_note2, rel_note3, rel_note4, chord_id, root_note, chord_type) \
                VALUES ({placeholders})', values + new_vals
            )

conn.commit()
conn.close()