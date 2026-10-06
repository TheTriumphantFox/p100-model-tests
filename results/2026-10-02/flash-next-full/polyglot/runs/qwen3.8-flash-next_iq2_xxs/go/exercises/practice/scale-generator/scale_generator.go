package scale

import (
	"strings"
)

// Scale returns the scale of notes starting with the given tonic and following the given intervals.
func Scale(tonic, interval string) []string {
	// Define the chromatic scales
	sharps := []string{"A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"}
	flats := []string{"A", "Bb", "B", "C", "Db", "D", "Eb", "E", "F", "G", "Ab", "A"}

	// Determine if we should use sharps or flats based on the tonic
	// Sharps tonics: C, G, D, A, E, B, F# (Major) and a, e, b, f#, c#, g#, d# (Minor)
	// Flats tonics: F, Bb, Eb, Ab, Db, Gb (Major) and d, g, c, f, bb, eb (Minor)
	// Note: The problem states "For the scope of this exercise the scale is only ascending."
	// And "For the given tonic, determine if the scale is to be returned with flats or sharps."
	// Based on the table:
	// Sharps: C, G, D, A, E, B, F#, a, e, b, f#, c#, g#, d#
	// Flats: F, Bb, Eb, Ab, Db, Gb, d, g, c, f, bb, eb
	
	// Normalize tonic for comparison
	t := strings.ToUpper(tonic)
	// Handle specific cases for flats notation in input (e.g. "Bb", "Eb")
	// The input tonic might be like "C", "a", "F#", "Bb", etc.
	// We need to map the input tonic to the starting index in the appropriate scale array.
	
	// List of tonics that use sharps notation
	sharpsTonics := map[string]bool{
		"C": true, "G": true, "D": true, "A": true, "E": true, "B": true, "F#": true,
		"A": true, "E": true, "B": true, "F#": true, "C#": true, "G#": true, "D#": true,
	}
	// List of tonics that use flats notation
	flatsTonics := map[string]bool{
		"F": true, "BB": true, "EB": true, "AB": true, "DB": true, "GB": true,
		"D": true, "G": true, "C": true, "F": true, "BB": true, "EB": true,
	}
	
	// Check if the tonic is in the sharps list or flats list
	// Note: The table in the prompt uses lowercase for minor keys (e.g. 'a', 'e').
	// The input tonic might be "C", "a", "F#", "Bb".
	// Let's normalize the input tonic to match the keys in our scales.
	// The scales arrays use "A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#" for sharps
	// and "A", "Bb", "B", "C", "Db", "D", "Eb", "E", "F", "G", "Ab", "A" for flats.
	
	// Determine which scale to use
	// If the tonic is in the sharps list, use sharps. If in flats list, use flats.
	// Note: 'C' and 'a' are in both lists in the table description but the prompt says:
	// "Note that by common music theory convention the natural notes "C" and "a" follow the sharps scale when ascending and the flats scale when descending. For the scope of this exercise the scale is only ascending."
	// This implies for ascending scales, C and a use sharps.
	
	// Let's check the input tonic against the known tonics.
	// We need to find the index of the tonic in the chosen scale.
	
	// Normalize input tonic to match the format in the scales (e.g. "Bb" vs "bb")
	// The input tonic might be "C", "a", "F#", "Bb".
	// Let's convert the input tonic to the format used in the scales arrays.
	// Sharps scale notes: A, A#, B, C, C#, D, D#, E, F, F#, G, G#
	// Flats scale notes: A, Bb, B, C, Db, D, Eb, E, F, G, Ab, A
	
	// Check if tonic is in sharps tonics list
	isSharps := false
	isFlats := false
	
	// Check sharps tonics
	for _, s := range sharpsTonics {
		if strings.EqualFold(tonic, s) {
			isSharps = true
			break
		}
	}
	// Check flats tonics
	for _, f := range flatsTonics {
		if strings.EqualFold(tonic, f) {
			isFlats = true
			break
		}
	}
	
	// If both are false, default to sharps? Or error?
	// The prompt implies the tonic will be one of the listed ones.
	// Let's assume if it's not explicitly in flats list, use sharps.
	// Actually, let's just pick the scale based on the tonic.
	// If the tonic is in the flats list, use flats. Otherwise use sharps.
	// But wait, the table lists specific tonics.
	// Let's just check if the tonic matches any of the flat tonics.
	// If yes, use flats. If no, use sharps.
	
	// Let's refine the logic.
	// If the tonic is one of the flat tonics, use the flats scale.
	// Otherwise, use the sharps scale.
	
	// Let's check if the tonic is in the flats list
	// We need to compare the input tonic with the notes in the flats scale.
	// The input tonic might be "C", "a", "F#", "Bb".
	// Let's normalize the input tonic to the format in the scales.
	// e.g. "Bb" -> "Bb", "bb"