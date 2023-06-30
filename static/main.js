import ChordBox from './chordbox.js';

// Now you can use ChordBox in this file. For illustration:
let myChordBox = new ChordBox();

const sel = document.getElementById('drawing');
      
function draw(sel, chord, opts) {
    return new ChordBox(sel, opts).draw(chord);
}

// 7 string
draw(
sel,
{
    chord: [[1, 2], [2, 1], [3, 2], [4, 0], [5, 'x'], [6, 'x'], [7, 1]],
    tuning: ['B', 'E', 'A', 'D', 'G', 'B', 'E']
},
{ numStrings: 7 }
);

// Stretch chord
draw(
sel,
{
    chord: [[3, 3], [4, 5], [5, 7], [6, 'x']],
    position: 5,
    barres: [{ fromString: 6, toString: 1, fret: 1 }]
},
{ height: 140, numFrets: 8, strokeColor: '#8a8' }
);

// Big
draw(
'#drawing2',
{
    chord: [[1, 2, 2], [2, 1, 1], [3, 2, 3], [4, 0], [5, 'x'], [6, 'x']]
},
{ width: 180, height: 220, defaultColor: '#745' }
);

// Bass
draw(
'#drawing2',
{
    chord: [[1, 3, 'F#'], [2, 3, 'D'], [3, 3, 'A'], [4, 3]],
    tuning: ['G', 'C', 'E', 'A']
},
{
    width: 180,
    height: 220,
    numStrings: 4,
    defaultColor: '#37a',
    strokeWidth: 2,
    fretWidth: 2,
    fontWeight: 'normal'
}
);