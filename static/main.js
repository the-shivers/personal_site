// Declare a variable to hold your data
let data;
console.log('fetching data')
fetch('/data')
.then(response => response.json())
.then(fetchedData => {
    // Store the fetched data
    data = fetchedData;
    console.log('got it!', data)
})
.catch(error => console.error(error));

import ChordBox from './chordbox.js';

const updateButton = document.getElementById('updateButton');
const dataParagraph = document.getElementById('dataParagraph');
const sel = document.getElementById('drawing');
      
function draw(sel, chord, opts) {
    return new ChordBox(sel, opts).draw(chord);
}

const convert = n => n === -1 ? 'x' : n;

function filter_strums(strums_data, filter_dict) {
    let new_list = [];
    for (let i = 0; i < strums_data.length; i++) {
        console.log('filter_dict btw', filter_dict)
        console.log(i, strums_data[i])
        let strum = strums_data[i]
        // if (!(filter_dict['chk' + strum['root_note'].replace('#', 's')])) { // Check if strum root lacks checkmark
        //     continue; // Do not add it to list, skip to next iteration
        // }
        // if (!(filter_dict['ch_' + strum['cat']])) { // Check if chord category lacks checkmark
        //     continue;
        // }
        // if (strum['fret_stretch'] > filter_dict['opt_stretch']) {
        //     continue;
        // }
        // if (strum['fret_max'] > filter_dict['opt_stretch']) {
        //     continue;
        // }
        // if (strum['mute_count'] > 0 && !(filter_dict['opt_enable_mute'])) {
        //     continue;
        // }
        // if (strum['tuning_name'] != filter_dict['opt_tune']) {
        //     continue;
        // }
        new_list.push(strum);
    }
    return new_list
}

function get_filter_dict() {
    return {
        'chkA': document.getElementById('chkA').checked,
        'chkAs': document.getElementById('chkAs').checked,
        'chkB': document.getElementById('chkB').checked,
        'chkC': document.getElementById('chkC').checked,
        'chkCs': document.getElementById('chkCs').checked,
        'chkD': document.getElementById('chkD').checked,
        'chkDs': document.getElementById('chkDs').checked,
        'chkE': document.getElementById('chkE').checked,
        'chkF': document.getElementById('chkF').checked,
        'chkFs': document.getElementById('chkFs').checked,
        'chkG': document.getElementById('chkG').checked,
        'chkGs': document.getElementById('chkGs').checked,

        'ch_basics': document.getElementById('ch_basics').checked,
        'ch_common': document.getElementById('ch_common').checked,
        'ch_extended': document.getElementById('ch_extended').checked,
        'ch_altered': document.getElementById('ch_altered').checked,
        'ch_jazz_variations_1': document.getElementById('ch_jazz_variations_1').checked,
        'ch_jazz_variations_2': document.getElementById('ch_jazz_variations_2').checked,
        'ch_added': document.getElementById('ch_added').checked,

        'opt_fret': document.getElementById('opt_fret').value,
        'opt_stretch': document.getElementById('opt_stretch').value,
        'opt_enable_mute': document.getElementById('opt_enable_mute').checked,
        'opt_tune': document.getElementById('opt_tune').value
    }
}

let myChordBox = new ChordBox();

updateButton.addEventListener('click', () => {
console.log('data', data)
// Check if data has been fetched
if (data) {
    console.log('in if data')
    let filter_dict = get_filter_dict();
    let filtered_data = filter_strums(data, filter_dict);
    console.log('filtering strums')
    // filter data based on inputs
    // Generate a random index
    const randomIndex = Math.floor(Math.random() * filtered_data.length);
    // Get the random row from the data
    const randomRow = filtered_data[randomIndex];
    console.log(randomRow)
    // Update the paragraph with the random row
    dataParagraph.textContent = JSON.stringify([
        randomRow['root_note'], randomRow['chord_type']
    ]);
    sel.innerHTML = ''; // Remove previous content.
    draw(
        sel,
        {
            chord: [
                [4, convert(randomRow['f1']), randomRow['rel_note1']], 
                [3, convert(randomRow['f2']), randomRow['rel_note2']],
                [2, convert(randomRow['f3']), randomRow['rel_note3']], 
                [1, convert(randomRow['f4']), randomRow['rel_note4']]
            ],
            tuning: ['G', 'C', 'E', 'A']
        },
        {
            width: 250,
            height: 400,
            circleRadius: 100,
            numStrings: 4,
            numFrets: 4,
            defaultColor: '#444',
            strokeWidth: 3,
            fretWidth: 3,
            stringWidth: 3,
            labelWeight: 1,
            labelSize: 1,
            fontSize: 28,
            fontWeight: 1,
            fontFamily: ['"Courier Prime"', 'monospace']
        }
    );
} else {
    // If data has not yet been fetched, display an error message
    dataParagraph.textContent = "Data not yet loaded. Please try again in a few seconds.";
}
});