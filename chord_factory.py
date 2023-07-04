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
MAX_FRET = 20
MAX_STRETCH = 10
CHORD_TYPES = [
        # basics
    {
        'type': 'Major', 
        'abbrv': 'M',
        'text_abbrv': '',
        'ints': [0, 4, 7],
        'cat': 'basics'
    },
    {
        'type': 'Minor',
        'abbrv': 'm',
        'text_abbrv': 'm',
        'ints': [0, 3, 7],
        'cat': 'basics'
    },
    # common
    {
        "type": "Major 7th",
        "abbrv": "Maj7",
        'text_abbrv': 'Δ',
        "ints": [0, 4, 7, 11],
        'cat': 'common'
    },
    {
        "type": "Minor 7th",
        "abbrv": "m7",
        'text_abbrv': 'm7',
        "ints": [0, 3, 7, 10],
        'cat': 'common'
    },
    {
        "type": "Dominant 7th",
        "abbrv": "7",
        'text_abbrv': '7',
        "ints": [0, 4, 7, 10],
        'cat': 'common'
    },
    # extensions
    {
        "type": "Dominant 9th",
        "abbrv": "9",
        'text_abbrv': '9',
        "ints": [0, 4, 7, 10, 14],
        'cat': 'extended'
    },
    {
        "type": "Major 9th",
        "abbrv": "Maj9",
        'text_abbrv': 'Δ9',
        "ints": [0, 4, 7, 11, 14],
        'cat': 'extended'
    },
    {
        "type": "Minor 9th",
        "abbrv": "m9",
        'text_abbrv': 'm9',
        "ints": [0, 3, 7, 10, 14],
        'cat': 'extended'
    },
    {
        "type": "Dominant 11th",
        "abbrv": "11",
        'text_abbrv': '11',
        "ints": [0, 4, 7, 10, 14, 17],
        'cat': 'extended'
    },
    {
        "type": "Major 11th",
        "abbrv": "Maj11",
        'text_abbrv': 'Δ11',
        "ints": [0, 4, 7, 11, 14, 17],
        'cat': 'extended'
    },
    {
        "type": "Minor 11th",
        "abbrv": "m11",
        'text_abbrv': 'm11',
        "ints": [0, 3, 7, 10, 14, 17],
        'cat': 'extended'
    },
    {
        "type": "Dominant 13th",
        "abbrv": "13",
        'text_abbrv': '13',
        "ints": [0, 4, 7, 10, 14, 17, 21],
        'cat': 'extended'
    },
    {
        "type": "Major 13th",
        "abbrv": "Maj13",
        'text_abbrv': 'Δ13',
        "ints": [0, 4, 7, 11, 14, 17, 21],
        'cat': 'extended'
    },
    {
        "type": "Minor 13th",
        "abbrv": "m13",
        'text_abbrv': 'm13',
        "ints": [0, 3, 7, 10, 14, 17, 21],
        'cat': 'extended'
    },
    # Altered
    {
        'type': 'Diminished',
        'abbrv': 'dim',
        'text_abbrv': 'dim',
        'ints': [0, 3, 6],
        'cat': 'altered'
    },
    {
        'type': 'Augmented',
        'abbrv': 'aug',
        'text_abbrv': '+',
        'ints': [0, 4, 8],
        'cat': 'altered'
    },
    {
        'type': 'Suspended 2nd',
        'abbrv': 'sus2',
        'text_abbrv': 'sus2',
        'ints': [0, 2, 7],
        'cat': 'altered'
    },
    {
        'type': 'Suspended 4th',
        'abbrv': 'sus4',
        'text_abbrv': 'sus4',
        'ints': [0, 5, 7],
        'cat': 'altered'
    },
    {
        "type": "Dominant 7th Suspended 4th",
        "abbrv": "7sus4",
        'text_abbrv': '7sus4',
        "ints": [0, 5, 7, 10],
        'cat': 'altered'
    },
    {
        "type": "Major 6th",
        "abbrv": "6",
        'text_abbrv': '6',
        "ints": [0, 4, 7, 9],
        'cat': 'altered'
    },
    {
        "type": "Minor 6th",
        "abbrv": "m6",
        'text_abbrv': 'm6',
        "ints": [0, 3, 7, 9],
        'cat': 'altered'
    },
    {
        "type": "Minor Major 7th",
        "abbrv": "mMaj7",
        'text_abbrv': 'mMaj7',
        "ints": [0, 3, 7, 11],
        'cat': 'altered'
    },
    {
        "type": "Half Diminished 7th",
        "abbrv": "m7b5",
        'text_abbrv': 'm7♭5',
        "ints": [0, 3, 6, 10],
        'cat': 'altered'
    },
    {
        "type": "Fully Diminished 7th",
        "abbrv": "dim7",
        'text_abbrv': 'dim7',
        "ints": [0, 3, 6, 9],
        'cat': 'altered'
    },
    {
        "type": "Augmented Major 7th",
        "abbrv": "Maj7s5",
        'text_abbrv': 'Maj7♯5',
        "ints": [0, 4, 8, 11],
        'cat': 'altered'
    },
    {
        "type": "Dominant 7th Augmented 5th",
        "abbrv": "7aug5",
        'text_abbrv': '7♯5',
        "ints": [0, 4, 8, 10],
        'cat': 'altered'
    },
    {
        "type": "Major 7th no 5th",
        "abbrv": "Maj7no5",
        'text_abbrv': 'Maj7(no5)',
        "ints": [0, 4, 11],
        'cat': 'altered'
    },
    {
        "type": "Minor 7th no 5th",
        "abbrv": "m7no5",
        'text_abbrv': 'm7(no5)',
        "ints": [0, 3, 10],
        'cat': 'altered'
    },
    {
        "type": "Dominant 7th no 5th",
        "abbrv": "7no5",
        'text_abbrv': '7(no5)',
        "ints": [0, 4, 10],
        'cat': 'altered'
    },
        # Jazz Variations 1
    {
        "type": 'Major 7th Flat 5th',
        "abbrv": 'Maj7b5',
        "text_abbrv": 'Maj7♭5',
        "ints": [0, 4, 6, 11],
        'cat': 'jazz_variations_1'
    },
    {
        "type": 'Dominant 7th Flat 5th',
        "abbrv": '7b5',
        "text_abbrv": '7♭5',
        "ints": [0, 4, 6, 10],
        'cat': 'jazz_variations_1'
    },
    {
        "type": 'Dominant 7th Sharp 9th',
        "abbrv": '7s9',
        "text_abbrv": '7♯9',
        "ints": [0, 4, 7, 10, 15],
        'cat': 'jazz_variations_1'
    },
    {
        "type": 'Dominant 7th Flat 9th',
        "abbrv": '7b9',
        "text_abbrv": '7♭9',
        "ints": [0, 4, 7, 10, 13],
        'cat': 'jazz_variations_1'
    },
    {
        "type": 'Major 6/9',
        "abbrv": '6_9',
        "text_abbrv": '6/9',
        "ints": [0, 4, 7, 9, 14],
        'cat': 'jazz_variations_1'
    },
    {
        "type": 'Minor 6/9',
        "abbrv": 'm6_9',
        "text_abbrv": 'm6/9',
        "ints": [0, 3, 7, 9, 14],
        'cat': 'jazz_variations_1'
    },
    {
        "type": "Dominant 9th Sharp 11th",
        "abbrv": "9s11",
        "text_abbrv": "9♯11",
        "ints": [0, 4, 7, 10, 14, 18],
        'cat': 'jazz_variations_1'
    },
    {
        "type": 'Minor Major 9th',
        "abbrv": 'mMaj9',
        "text_abbrv": 'mMaj9',
        "ints": [0, 3, 7, 11, 14],
        'cat': 'jazz_variations_1'
    },
    {
        "type": 'Major 7th Sharp 11th',
        "abbrv": 'Maj7s11',
        "text_abbrv": 'Maj7♯11',
        "ints": [0, 4, 7, 11, 18],
        'cat': 'jazz_variations_1'
    },
    {
        "type": 'Dominant 13th Flat 9th',
        "abbrv": '13b9',
        "text_abbrv": '13♭9',
        "ints": [0, 4, 7, 10, 13, 21],
        'cat': 'jazz_variations_1'
    },
    # Jazz Variations 2
    {
        "type": "Dominant 7th Sharp 5th Sharp 9th",
        "abbrv": "7s5s9",
        "text_abbrv": '7♯5♯9',
        "ints": [0, 4, 8, 10, 15],
        'cat': 'jazz_variations_2'
    },
    {
        "type": "Dominant 7th Sharp 11th",
        "abbrv": "7s11",
        "text_abbrv": '7♯11',
        "ints": [0, 4, 7, 10, 18],
        'cat': 'jazz_variations_2'
    },
    {
        "type": "Dominant 7th Flat 5th Flat 9th",
        "abbrv": "7b5b9",
        "text_abbrv": '7♭5♭9',
        "ints": [0, 4, 6, 10, 13],
        'cat': 'jazz_variations_2'
    },
    {
        "type": "Dominant 13th Sharp 11th",
        "abbrv": "13s11",
        "text_abbrv": '13♯11',
        "ints": [0, 4, 7, 10, 14, 18, 21],
        'cat': 'jazz_variations_2'
    },
    {
        "type": "Augmented Minor 7th",
        "abbrv": "Ms7",
        "text_abbrv": '+m7',
        "ints": [0, 3, 8, 10],
        'cat': 'jazz_variations_2'
    },
    {
        "type": "Minor 9th Flat 5th",
        "abbrv": "m9b5",
        "text_abbrv": 'm9♭5',
        "ints": [0, 3, 6, 10, 14],
        'cat': 'jazz_variations_2'
    },
    {
        "type": "Augmented Major 9th",
        "abbrv": "M9s5",
        "text_abbrv": 'Maj9♯5',
        "ints": [0, 4, 8, 11, 14],
        'cat': 'jazz_variations_2'
    },
    {
        "type": "Augmented 7th Flat 9th",
        "abbrv": "7sb9",
        "text_abbrv": '+7♭9',
        "ints": [0, 4, 8, 10, 13],
        'cat': 'jazz_variations_2'
    },
    {
        "type": "Dominant 7th Flat 9th Flat 13th",
        "abbrv": "7b9b13",
        "text_abbrv": '7♭9♭13',
        "ints": [0, 4, 7, 10, 13, 20],
        'cat': 'jazz_variations_2'
    },
    {
        "type": "Dominant 7th Sharp 9th Sharp 11th",
        "abbrv": "7s9s11",
         "text_abbrv": '7♯9♯11',
        "ints": [0, 4, 7, 10, 15, 18],
        'cat': 'jazz_variations_2'
    },
    {
        "type": "Major 9th Sharp 11th",
        "abbrv": "M9s11",
        "text_abbrv": 'Maj9♯11',
        "ints": [0, 4, 7, 11, 14, 18],
        'cat': 'jazz_variations_2'
    },
    {
        "type": "Minor Major 7th Flat 5th",
        "abbrv": "mM7b5",
        "text_abbrv": 'mMaj7♭5',
        "ints": [0, 3, 6, 11],
        'cat': 'jazz_variations_2'
    },
    {
        "type": "dominant_9_flat_13",
        "abbrv": "9b13",
        "text_abbrv": '9♭13',
        "ints": [0, 4, 7, 10, 14, 20],
        'cat': 'jazz_variations_2'
    },
    # Adds 
    {
        "type": "Add Second",
        "abbrv": "add2",
        "text_abbrv": "add2",
        "ints": [0, 2, 4, 7],
        'cat': 'added'
    },
    {
        "type": "Add Fourth",
        "abbrv": "add4",
        "text_abbrv": "add4",
        "ints": [0, 4, 5, 7],
        'cat': 'added'
    },
    {
        "type": "Add Ninth",
        "abbrv": "add9",
        "text_abbrv": "add9",
        "ints": [0, 4, 7, 14],
        'cat': 'added'
    },
    {
        "type": "Minor Add Second",
        "abbrv": "madd2",
        "text_abbrv": "madd2",
        "ints": [0, 2, 3, 7],
        'cat': 'added'
    },
    {
        "type": "Minor Add Fourth",
        "abbrv": "madd4",
        "text_abbrv": "madd4",
        "ints": [0, 3, 5, 7],
        'cat': 'added'
    },
    {
        "type": "Minor Add Ninth",
        "abbrv": "madd9",
        "text_abbrv": "madd9",
        "ints": [0, 3, 7, 14],
        'cat': 'added'
    },
    {
        "type": "Dominant Seventh Add Eleventh",
        "abbrv": "7add11",
        "text_abbrv": "7♯11",
        "ints": [0, 4, 7, 10, 17],
        'cat': 'added'
    },
    {
        "type": "Dominant Seventh Add Thirteenth",
        "abbrv": "7add13",
        "text_abbrv": "7♯13",
        "ints": [0, 4, 7, 10, 21],
        'cat': 'added'
    },
    {
        "type": "Dominant Seventh Add Sixth",
        "abbrv": "7add6",
        "text_abbrv": "7/6",
        "ints": [0, 4, 7, 9, 10],
        'cat': 'added'
    },
    {
        "type": "Major Seventh Add Eleventh",
        "abbrv": "M7add11",
        "text_abbrv": "Maj7♯11",
        "ints": [0, 4, 7, 11, 17],
        'cat': 'added'
    },
    {
        "type": "Major Seventh Add Thirteenth",
        "abbrv": "M7add13",
        "text_abbrv": "Maj7♯13",
        "ints": [0, 4, 7, 11, 21],
        'cat': 'added'
    }
]

# def check_duplicates(lst):
#     seen = {}
#     for chord in lst:
#         # freeze the list into a tuple so it's hashable,
#         # and use frozenset to ignore the order of elements in the lists
#         item = frozenset(chord['ints'])
#         if item in seen:
#             print(f"Duplicate chords: {chord} and {seen[item]}")
#         else:
#             seen[item] = chord

# check_duplicates(CHORD_TYPES) 

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
                fret_stretch = max(zeroless_fingering) - max(0, min(zeroless_fingering)) if zeroless_fingering else 0
                fret_score_alpha = -fret_stretch
                for i in [g, c, e, a]:
                    if i == -1:
                        fret_score_alpha -= 5
                    elif i == 0:
                        fret_score_alpha += 3
                    else:
                        fret_score_alpha -= i
                fret_score_beta = -fret_stretch
                for i in [g, c, e, a]:
                    if i == -1:
                        fret_score_alpha -= 10
                    elif i == 0:
                        fret_score_alpha += 0
                    else:
                        fret_score_alpha -= i
                FINGERINGS += [{
                    'id': counter,
                    'fingering_str': ",".join([str(g), str(c), str(e), str(a)]),
                    'str1': g,
                    'str2': c,
                    'str3': e,
                    'str4': a,
                    'fret_max': max(zeroless_fingering) if zeroless_fingering else 0,
                    'fret_sum': sum(zeroless_fingering) if zeroless_fingering else 0,
                    'fret_stretch': fret_stretch,
                    'mute_count': [g, c, e, a].count(-1),
                    'fret_score_alpha': fret_score_alpha,
                    'fret_score_beta': fret_score_beta
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
conn.row_factory = sqlite3.Row   # This allows dictionaries to be returned from the fetch methods. 
cursor = conn.cursor()

# Notes table
notes_table_name = 'notes'
notes_table_schema = """
    id INTEGER PRIMARY KEY,
    str TEXT NOT NULL UNIQUE
"""
cursor.execute(f'DROP TABLE IF EXISTS {notes_table_name}')
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
    text_abbrv TEXT NOT NULL,
    int_str TEXT NOT NULL,
    cat TEXT NOT NULL
"""
cursor.execute(f'DROP TABLE IF EXISTS {chord_types_table_name}')
cursor.execute(f'CREATE TABLE IF NOT EXISTS {chord_types_table_name} ({chord_types_table_schema})')
for i in range(len(CHORD_TYPES)):
    placeholders = '?, ?, ?, ?, ?, ?'
    values = [
        i, 
        CHORD_TYPES[i]['type'], 
        CHORD_TYPES[i]['abbrv'], 
        CHORD_TYPES[i]['text_abbrv'],
        ','.join([str(x) for x in CHORD_TYPES[i]['ints']]),
        CHORD_TYPES[i]['cat']
    ]
    cursor.execute(f'INSERT INTO {chord_types_table_name} (id, type, abbrv, text_abbrv, int_str, cat) VALUES ({placeholders})', values)

# Chords
chords_table_name = 'chords'
chords_table_schema = """
    id INTEGER PRIMARY KEY,
    root_note_id INTEGER NOT NULL,
    root_note TEXT NOT NULL,
    chord_type_id INTEGER NOT NULL,
    chord_type TEXT NOT NULL,
    rel_notes_str TEXT NOT NULL,
    chord_abbrv TEXT NOT NULL,
    chord_text_abbrv TEXT NOT NULL,
    chord_cat TEXT NOT NULL,
    FOREIGN KEY (root_note_id) REFERENCES notes (id),
    FOREIGN KEY (chord_type_id) REFERENCES chord_types (id)
"""
cursor.execute(f'DROP TABLE IF EXISTS {chords_table_name}')
cursor.execute(f'CREATE TABLE IF NOT EXISTS {chords_table_name} ({chords_table_schema})')
result = cursor.execute(
    'select \
        notes.id as root_note_id, \
        notes.str as root_note, \
        chord_types.id as chord_type_id, \
        chord_types.type as chord_type, \
        chord_types.int_str, \
        chord_types.abbrv as chord_abbrv, \
        chord_types.text_abbrv as chord_text_abbrv, \
        chord_types.cat as chord_cat \
    from notes cross join chord_types order by 1, 2'
    )
data = result.fetchall()
for i in range(len(data)):
    placeholders = '?, ?, ?, ?, ?, ?, ?, ?, ?'
    values = [
        i, 
        data[i][0], 
        data[i][1], 
        data[i][2], 
        data[i][3],
        ','.join(sorted(list(set([i for i in data[i][4].split(',') if i != ''])))), # Dedupe, remove '', sort, join without spaces
        data[i]['chord_abbrv'],
        data[i]['chord_text_abbrv'],
        data[i]['chord_cat']
    ]
    cursor.execute(f'INSERT INTO {chords_table_name} (id, root_note_id, root_note, chord_type_id, chord_type, rel_notes_str, chord_abbrv, chord_text_abbrv, chord_cat) VALUES ({placeholders})', values)


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
        fret_stretch INTEGER NOT NULL,
        mute_count INTEGER NOT NULL,
        fret_score_alpha INTEGER NOT NULL,
        fret_score_beta INTEGER NOT NULL
"""
cursor.execute(f'DROP TABLE IF EXISTS {fingerings_table_name}')
cursor.execute(f'CREATE TABLE IF NOT EXISTS {fingerings_table_name} ({fingerings_table_schema})')
for i in range(len(FINGERINGS)):
    placeholders = '?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?'
    values = [
        i,
        f"{FINGERINGS[i]['str1']},{FINGERINGS[i]['str2']},{FINGERINGS[i]['str3']},{FINGERINGS[i]['str4']}",
        FINGERINGS[i]['str1'],
        FINGERINGS[i]['str2'],
        FINGERINGS[i]['str3'],
        FINGERINGS[i]['str4'],
        FINGERINGS[i]['fret_max'],
        FINGERINGS[i]['fret_sum'],
        FINGERINGS[i]['fret_stretch'],
        FINGERINGS[i]['mute_count'],
        FINGERINGS[i]['fret_score_alpha'],
        FINGERINGS[i]['fret_score_beta']
    ]
    cursor.execute(
        f'INSERT INTO {fingerings_table_name} (id, fingering_str, f1, f2, f3, f4, fret_max, fret_sum, fret_stretch, mute_count, fret_score_alpha, fret_score_beta) VALUES ({placeholders})', values
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
cursor.execute(f'DROP TABLE IF EXISTS {tunings_table_name}')
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
        fingerings.fingering_str as fingering_str,
        fingerings.f1 as f1,
        fingerings.f2 as f2,
        fingerings.f3 as f3,
        fingerings.f4 as f4,
        fret_max,
        fret_sum,
        fret_stretch,
        mute_count,
        fret_score_alpha,
        fret_score_beta,
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
        fingering_str TEXT NOT NULL,
        f1 INTEGER NOT NULL,
        f2 INTEGER NOT NULL,
        f3 INTEGER NOT NULL,
        f4 INTEGER NOT NULL,
        fret_max INTEGER NOT NULL,
        fret_sum INTEGER NOT NULL,
        fret_stretch INTEGER NOT NULL,
        mute_count INTEGER NOT NULL,
        fret_score_alpha INTEGER NOT NULL,
        fret_score_beta INTEGER NOT NULL,
        tuning_name STRING NOT NULL,
        str1 TEXT NOT NULL,
        str2 TEXT NOT NULL,
        str3 TEXT NOT NULL,
        str4 TEXT NOT NULL,
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
        chord_type TEXT,
        chord_abbrv TEXT,
        chord_text_abbrv TEXT,
        chord_int_str TEXT,
        chord_cat TEXT
"""
cursor.execute(f'DROP TABLE IF EXISTS {strums_table_name}')
cursor.execute(f'CREATE TABLE IF NOT EXISTS {strums_table_name} ({strums_table_schema})')
starter_data = cursor.execute(strums_table_starter_query).fetchall()

counter = 0
for row in starter_data:
    print(counter / len(starter_data))
    params = {
        'fingering_id': row['fingering_id'],
        'tuning_id': row['tuning_id'],
        'fingering_str': row['fingering_str'],
        'f1': row['f1'],
        'f2': row['f2'],
        'f3': row['f3'],
        'f4': row['f4'],
        'fret_max': row['fret_max'],
        'fret_sum': row['fret_sum'],
        'fret_stretch': row['fret_stretch'],
        'mute_count': row['mute_count'],
        'fret_score_alpha': row['fret_score_alpha'],
        'fret_score_beta': row['fret_score_beta'],
        'tuning_name': row['tuning_name'],
        'str1': row['str1'],
        'str2': row['str2'],
        'str3': row['str3'],
        'str4': row['str4'],
        'abs_note1': note_add_abs(row['str1'], row['f1']) if row['f1'] >= 0 else '',
        'abs_note2': note_add_abs(row['str2'], row['f2']) if row['f2'] >= 0 else '',
        'abs_note3': note_add_abs(row['str3'], row['f3']) if row['f3'] >= 0 else '',
        'abs_note4': note_add_abs(row['str4'], row['f4']) if row['f4'] >= 0 else '',
    }
    params['abs_note_str'] = ','.join([
        params['abs_note1'], params['abs_note2'], 
        params['abs_note3'], params['abs_note4']
    ])
    params['rel_note1'] = get_rel_note(params['abs_note1'])
    params['rel_note2'] = get_rel_note(params['abs_note2'])
    params['rel_note3'] = get_rel_note(params['abs_note3'])
    params['rel_note4'] = get_rel_note(params['abs_note4'])
    params['rel_note_str'] = ','.join(sorted(list(set([i for i in [
        params['rel_note1'], params['rel_note2'], 
        params['rel_note3'], params['rel_note4']
    ] if i != ''])))) # Dedupe, remove '', sort, join without spaces
    chords = cursor.execute("""
        select 
            c.id as chord_id, c.root_note, c.rel_notes_str, 
            ct.type as chord_type, ct.abbrv as chord_abbrv, ct.text_abbrv as chord_text_abbrv, ct.cat as chord_cat, ct.int_str as chord_int_str
        from chords c join chord_types ct on c.chord_type_id = ct.id
        """
    ).fetchall()
    filtered_chords = [chord for chord in chords if chord['rel_notes_str'] == params['rel_note_str']]
    if filtered_chords:
        for chord in filtered_chords:
            params['id'] = counter
            params['chord_id'] = chord['chord_id']
            params['root_note'] = chord['root_note']
            params['chord_type'] = chord['chord_type']
            params['chord_abbrv'] = chord['chord_abbrv']
            params['chord_text_abbrv'] = chord['chord_text_abbrv']
            params['chord_cat'] = chord['chord_cat']
            placeholders = [':' + str(i) for i in params.keys()]
            strum_query = f"INSERT INTO {strums_table_name} ({', '.join(params.keys())}) VALUES ({', '.join(placeholders)})"
            cursor.execute(strum_query, params)
            counter += 1
    else:
        params['id'] = counter
        params['chord_id'] = ''
        params['root_note'] = ''
        params['chord_type'] = ''
        params['chord_abbrv'] = ''
        params['chord_text_abbrv'] = ''
        params['chord_cat'] = ''
        placeholders = [':' + str(i) for i in params.keys()]
        strum_query = f"INSERT INTO {strums_table_name} ({', '.join(params.keys())}) VALUES ({', '.join(placeholders)})"
        cursor.execute(strum_query, params)
        counter += 1

def create_indices(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    index_queries = [
        "CREATE INDEX IF NOT EXISTS idx_chord_id ON strums(chord_id);",
        "CREATE INDEX IF NOT EXISTS idx_fret_max ON strums(fret_max);",
        "CREATE INDEX IF NOT EXISTS idx_fret_stretch ON strums(fret_stretch);",
        "CREATE INDEX IF NOT EXISTS idx_tuning_name ON strums(tuning_name);",
        "CREATE INDEX IF NOT EXISTS idx_mute_count ON strums(mute_count);",
        "CREATE INDEX IF NOT EXISTS idx_chord_cat ON strums(chord_cat);",
        "CREATE INDEX IF NOT EXISTS idx_root_note ON strums(root_note);"
    ]
    for query in index_queries:
        cursor.execute(query)

create_indices('chords.db')

conn.commit()
conn.close()