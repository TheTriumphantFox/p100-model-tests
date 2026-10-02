package scale

import (
	"strings"
)

var sharpScale = []string{
	"A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#",
}

var flatScale = []string{
	"A", "Bb", "B", "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab",
}

var flatTonics = map[string]bool{
	"F":   true,
	"Bb":  true,
	"Eb":  true,
	"Ab":  true,
	"Db":  true,
	"Gb":  true,
	"d":   true,
	"g":   true,
	"c":   true,
	"f":   true,
	"bb":  true,
	"eb":  true,
}

func Scale(tonic, interval string) []string {
	var scale []string
	if interval == "" {
		// Chromatic scale
		scale = chromaticScale(tonic)
	} else {
		// Diatonic scale
		scale = diatonicScale(tonic, interval)
	}
	return scale
}

func chromaticScale(tonic string) []string {
	useFlats := flatTonics[strings.ToLower(tonic)]
	var baseScale []string
	if useFlats {
		baseScale = flatScale
	} else {
		baseScale = sharpScale
	}

	// Find start index
	startIndex := -1
	for i, note := range baseScale {
		if strings.EqualFold(note, tonic) {
			startIndex = i
			break
		}
	}

	if startIndex == -1 {
		return nil
	}

	result := make([]string, 12)
	for i := 0; i < 12; i++ {
		result[i] = baseScale[(startIndex+i)%12]
	}
	return result
}

func diatonicScale(tonic, intervals string) []string {
	chromatic := chromaticScale(tonic)
	result := []string{chromatic[0]}
	currentIndex := 0

	for _, interval := range intervals {
		switch interval {
		case 'm':
			currentIndex++
		case 'M':
			currentIndex += 2
		case 'A':
			currentIndex += 3
		}
		result = append(result, chromatic[currentIndex%12])
	}
	return result
}
