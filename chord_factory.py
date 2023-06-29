import sqlite3

# constants
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
NOTES_LEN = len(NOTES)
NOTES_DICT = dict(zip(NOTES, range(NOTES_LEN)))
OCTAVES = 8
ABS_NOTES = [note + str(i) for i in range(1, 1 + OCTAVES) for note in NOTES]
ABS_NOTES_LEN = len(ABS_NOTES)
ABS_NOTES_DICT = dict(zip(ABS_NOTES, range(ABS_NOTES_LEN)))

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
    return abs_note[:-1]

# def fingering_to_notes(fingering, tuning):
#     return [note_add_abs(tuning[i], fingering[i]) for i in range(len(fingering))]

# chord types
chord_types = {
    'major': {
        'abbrv': '',
        'ints': [0, 4, 7]
    },
    'minor': {
        'abbrv': 'm',
        'ints': [0, 3, 7]
    },
    'minor7': {
        'abbrv': 'm7',
        'ints': [0, 3, 7, 10]
    },
    '7': {
        'abbrv': '7',
        'ints': [0, 4, 7, 10]
    },
    'major7': {
        'abbrv': 'M7',
        'ints': [0, 4, 7, 11]
    }
}

# generation
chords = []
counter = 0
for note in NOTES:
    for chord_type, chord_details in chord_types.items():
        chord_notes = []
        for i in chord_details['ints']:
            chord_notes += [note_add_rel(note, i)]
        chords += [{
            'id': counter,
            'name': note + chord_details['abbrv'],
            'root': note,
            'type': chord_type,
            'notes': chord_notes,
            'notes_str': ','.join(chord_notes)
        }]
        counter += 1

# SQLite
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

table_schema = """
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    root TEXT NOT NULL,
    type TEXT NOT NULL,
    notes TEXT NOT NULL
"""
cursor.execute(f'CREATE TABLE IF NOT EXISTS my_table ({table_schema})')

# Remove array for SQLITE
chord_data = [{key : val for key, val in sub.items() if key != 'notes'} for sub in chords]

for row in chord_data:
    placeholders = ', '.join(['?' for _ in row])
    values = list(row.values())
    cursor.execute(f'INSERT INTO my_table VALUES ({placeholders})', values)

conn.commit()
conn.close()


# # scoring
# scored_chords = chords.copy()

# strum = ['G3', 'C4', 'E4', 'C5']
# rel_strum = [get_rel_note(i) for i in strum]

# for i in range(len(scored_chords)):
#     scored_chords[i]['len'] = len(scored_chords[i]['notes'])
#     scored_chords[i]['score'] = len(scored_chords[i]['notes']) - len(set(scored_chords[i]['notes']) - set(rel_strum))
#     scored_chords[i]['q'] = scored_chords[i]['score'] / scored_chords[i]['len']

# sorted_scored_chords = sorted(scored_chords, key=lambda x: x['q'], reverse=True)

# # tunings
# tunings = {
#     'high_g': ['G4', 'C4', 'E4', 'A4'],
#     'low_g': ['G3', 'C4', 'E4', 'A4'],
#     'baritone': ['D3', 'G3', 'B3', 'E4']
# }

# fingering_to_notes([0, 0, 0, 3], tunings['low_g'])