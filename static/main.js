import ChordBox from './chordbox.js';

// Declare a variable to hold your data
let data;
fetch('/data')
.then(response => response.json())
.then(fetchedData => {
    // Store the fetched data
    data = fetchedData;
})
.catch(error => console.error(error));

const updateButton = document.getElementById('updateButton');
const dataParagraph = document.getElementById('dataParagraph');
const sel = document.getElementById('drawing');
      
function draw(sel, chord, opts) {
    return new ChordBox(sel, opts).draw(chord);
}

const convert = n => n === -1 ? 'x' : n;

let myChordBox = new ChordBox();

updateButton.addEventListener('click', () => {
// Check if data has been fetched
if (data) {
    // Generate a random index
    const randomIndex = Math.floor(Math.random() * data.length);
    // Get the random row from the data
    const randomRow = data[randomIndex];
    console.log(randomRow)
    // Update the paragraph with the random row
    dataParagraph.textContent = JSON.stringify([randomRow,
        [1, randomRow[19], randomRow[5]], 
        [2, randomRow[20], randomRow[6]],
        [3, randomRow[21], randomRow[7]], 
        [4, randomRow[22], randomRow[8]]
    ]);
    draw(
        sel,
        {
            chord: [
                [4, convert(randomRow[19]), randomRow[5]], 
                [3, convert(randomRow[20]), randomRow[6]],
                [2, convert(randomRow[21]), randomRow[7]], 
                [1, convert(randomRow[22]), randomRow[8]]
            ],
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
} else {
    // If data has not yet been fetched, display an error message
    dataParagraph.textContent = "Data not yet loaded. Please try again in a few seconds.";
}
});

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
sel,
{
    chord: [[1, 2, 2], [2, 1, 1], [3, 2, 3], [4, 0], [5, 'x'], [6, 'x']]
},
{ width: 180, height: 220, defaultColor: '#745' }
);

// Bass
draw(
sel,
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
