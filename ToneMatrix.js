// Question 1

// copy generate_list_of_note from Mission "Musical Diversions"
function generate_list_of_note(letter_name, list_of_interval) {
    /* your answer here */
    const base = letter_name_to_midi_note(letter_name);
    function helper(i, l) {
        return is_null(l)
            ? pair(base + i, null)
            : pair(base + i, helper(i + head(l), tail(l)));
    }
    return helper(0, list_of_interval);
}

const pentatonic_list_of_interval = list(2, 2, 3, 2, 3);

// repeat_pattern from Lecture L2

function repeat_pattern(n, pattern, rune) {
    return n === 0 ? rune : repeat_pattern(n - 1, pattern, pattern(rune));
}

function repeated_scale(note, list_of_interval, n, duration, instrument) {
    // your solution goes here
    if (is_null(list_of_interval) || n < 1) {
        return list(silence_sound(0));
    } else {
        const base = generate_list_of_note(note, list_of_interval);
        const sum = accumulate((x, y) => x + y, 0, list_of_interval);
        const play = repeat_pattern(n - 1, x => append(base, map(y => y + sum, tail(x))), base);
        return map(x => instrument(x, duration), play);
    }
}

play(consecutively(repeated_scale("C4", list(2,1,1,3), 2, 0.5, cello)));
