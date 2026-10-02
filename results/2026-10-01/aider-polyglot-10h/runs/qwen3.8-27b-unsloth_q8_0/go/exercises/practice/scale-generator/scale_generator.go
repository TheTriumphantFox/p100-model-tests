package scale

import (
	"strings"
	"unicode"
)

var chromaticSharp = []string{
	"A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#",
}

var chromaticFlat = []string{
	"A", "Bb", "B", "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab",
}

var sharpTonics = map[string]bool{
	"G":  true,
	"D":  true,
	"A":  true,
	"E":  true,
	"B":  true,
	"F#": true,
	"e":  true,
	"b":  true,
	"f#": true,
	"c#": true,
	"g#": true,
	"d#": true,
}

var flatTonics = map[string]bool{
	"F":  true,
	"Bb": true,
	"Eb": true,
	"Ab": true,
	"Db": true,
	"Gb": true,
	"d":  true,
	"g":  true,
	"c":  true,
	"f":  true,
	"bb": true,
	"eb": true,
}

func Scale(tonic, interval string) []string {
	normalizedTonic := normalizeTonic(tonic)

	useFlats := false
	if flatTonics[normalizedTonic] {
		useFlats = true
	} else if sharpTonics[normalizedTonic] {
		useFlats = false
	} else {
		// Natural keys C and a
		// "C" and "a" are natural.
		// The instructions say: "Note that by common music theory convention the natural notes "C" and "a" follow the sharps scale when ascending and the flats scale when descending. For the scope of this exercise the scale is only ascending."
		// So for ascending scales (which is what we are generating), C and a use sharps.
		useFlats = false
	}

	var chromatic []string
	if useFlats {
		chromatic = chromaticFlat
	} else {
		chromatic = chromaticSharp
	}

	// Find the index of the tonic in the chosen chromatic scale
	tonicIndex := -1
	for i, note := range chromatic {
		if note == normalizedTonic {
			tonicIndex = i
			break
		}
	}

	if tonicIndex == -1 {
		return []string{}
	}

	if interval == "" {
		// Chromatic scale
		result := make([]string, 12)
		for i := 0; i < 12; i++ {
			result[i] = chromatic[(tonicIndex+i)%12]
		}
		return result
	}

	// Diatonic scale
	result := []string{chromatic[tonicIndex]}
	currentIndex := tonicIndex
	for _, step := range interval {
		switch step {
		case 'm':
			currentIndex = (currentIndex + 1) % 12
		case 'M':
			currentIndex = (currentIndex + 2) % 12
		case 'A':
			currentIndex = (currentIndex + 3) % 12
		}
		result = append(result, chromatic[currentIndex])
	}
	return result
}

func normalizeTonic(tonic string) string {
	if tonic == "" {
		return ""
	}

	// Replace unicode sharp with #
	tonic = strings.ReplaceAll(tonic, "♯", "#")
	// Replace unicode flat with b
	tonic = strings.ReplaceAll(tonic, "♭", "b")

	// Handle casing
	// If the tonic is a single letter, it's a natural note.
	// Major keys are uppercase, minor keys are lowercase.
	// However, the chromatic scale notes are always uppercase in our internal representation.
	// The key signature maps use specific casings (e.g. "G" for major, "g" for minor).
	// We need to preserve the case of the first letter to distinguish between major and minor for natural notes.
	// For sharps/flats, the first letter is uppercase in the key signature maps (e.g. "F#", "Bb").
	
	// If it's a single character
	if len(tonic) == 1 {
		// It's a natural note.
		// We keep the case as is, because "C" (major) and "c" (minor) are different keys.
		// But wait, the chromatic scale is the same. The difference is only in which enharmonic equivalents are used.
		// The maps sharpTonics and flatTonics contain both "C" and "c" (implicitly, by not being in the other map? No, they are explicitly listed or not).
		// Actually, "C" is not in sharpTonics or flatTonics. It falls to the else branch.
		// "c" is in flatTonics.
		// So we must preserve the case.
		return tonic
	}

	// If it's two characters, it's a sharp or flat.
	// The first character is the note name, the second is the accidental.
	// In the key signature maps, these are uppercase (e.g. "F#", "Bb").
	// So we uppercase the first character.
	first := string(unicode.ToUpper(rune(tonic[0])))
	return first + tonic[1:]
}
