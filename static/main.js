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

var vf = new Vex.Flow.Factory({renderer: {elementId: 'output', height: 700, width: 400}});
var score = vf.EasyScore();
var system = vf.System({x:30, y:10, spaceBetweenStaves:10, width:100});

var notes = [
  score.notes('C#5/1', {stem: 'up'}),
  score.notes('C#4/1', {stem: 'down'}),
  score.notes('C#3/1', {clef: 'bass', stem: 'up'}),
  score.notes('C#2/1', {clef: 'bass', stem: 'down'})
];

system.addStave({
  voices: [
    score.voice(notes[0]),
    score.voice(notes[1])
  ]
}).addClef('treble');

system.addStave({
  voices: [
    score.voice(notes[2]),
    score.voice(notes[3])
  ]
}).addClef('bass');

system.addConnector()

// Change the color of the first note
notes[0][0].note_heads.forEach(function(note_head) {
  note_head.setStyle({fillStyle: 'red', strokeStyle: 'red'});
});

vf.draw();
      
function draw(sel, chord, opts) {
    return new ChordBox(sel, opts).draw(chord);
}

const convert = n => n === -1 ? 'x' : n;

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

function get_disallowed_str(filter_dict, my_str = 'roots') {
    let my_list = []
    if (my_str === 'roots') {
        for (const [key, value] of Object.entries(filter_dict)) {
            console.log(`${key}: ${value}`);
            if (key.slice(0, 3) === 'chk' && !(value)) {
                my_list.push(key.replace('chk', ''))
            }
        }
    } else {
        for (const [key, value] of Object.entries(filter_dict)) {
            console.log(`${key}: ${value}`);
            if (key.slice(0, 3) === 'ch_' && !(value)) {
                console.log('we did it')
                my_list.push(key.replace('ch_', ''))
            }
        }
    }
    return my_list.join(',')
}

function filter_dict_to_query_params(filter_dict) {
    return {
        'fret_max': filter_dict['opt_fret'],
        'fret_stretch': filter_dict['opt_stretch'],
        'tuning_name': filter_dict['opt_tune'],
        'mutes': filter_dict['opt_enable_mute'].toString(),
        'disallowed_roots': get_disallowed_str(filter_dict, 'roots'),
        'disallowed_types': get_disallowed_str(filter_dict, 'types')
    }
}

let myChordBox = new ChordBox();

updateButton.addEventListener('click', async () => {
    try {
        let filter_dict = get_filter_dict();
        let query_params = filter_dict_to_query_params(filter_dict);
        // Below is magic code to remove keys with '' values.
        //let query_params_2 = Object.entries(query_params).reduce((acc, [k, v]) => v ? {...acc, [k]:v} : acc , {})
        let query_params_2 = query_params
        var param_str = Object.keys(query_params_2).map(function(key) {
            return key + '=' + query_params_2[key];
          }).join('&');
        // let param_str = new URLSearchParams(query_params).toString();
        console.log('filter dict', filter_dict)
        console.log('query params', query_params)
        console.log('query params2', query_params_2)
        console.log(param_str)
        
        const response = await fetch(`/data?${param_str.replace('#','s')}`); 
        const data = await response.json(); 
      
        if(data) {
            console.log('data', data)
            const randomIndex = Math.floor(Math.random() * data.length);
            const randomRow = data[randomIndex];
            console.log(randomRow)
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
                    defaultColor: '#130400',
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
        // your error handling code. 
        }
    } catch (error) {
        dataParagraph.textContent = "Data not yet loaded. Please try again in a few seconds.";
        console.log(error);
    }
});