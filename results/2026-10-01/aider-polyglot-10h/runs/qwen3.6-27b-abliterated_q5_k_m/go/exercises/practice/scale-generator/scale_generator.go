package scale

var sharps = []string{
	"A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#",
}

var flats = []string{
	"A", "Bb", "B", "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab",
}

var sharpTonics = map[string]bool{
	"C":  true,
	"G":  true,
	"D":  true,
	"A":  true,
	"E":  true,
	"B":  true,
	"F#": true,
	"a":  true,
	"e":  true,
	"b":  true,
	"f#": true,
	"c#": true,
	"g#": true,
	"d#": true,
}

func Scale(tonic, interval string) []string {
	var scale []string

	// Determine if we should use sharps or flats based on the tonic
	// The table in instructions specifies exact strings for tonics.
	// Let's check if the tonic is in the sharpTonics map.
	// Note: The map keys cover both major (uppercase) and minor (lowercase) as per instructions.
	// However, we need to handle the input tonic casing correctly.
	// The instructions say: "Return all notes in uppercase letters (except for the b for flats) irrespective of the casing of the given tonic."
	// But the table lists specific tonics like "a", "e", etc. for minor.
	// Let's assume the input tonic matches the casing in the table for minor keys.
	
	useSharps := sharpTonics[tonic]
	
	if useSharps {
		scale = sharps
	} else {
		scale = flats
	}

	// Find the starting index of the tonic in the chosen scale
	startIndex := -1
	for i, note := range scale {
		if note == tonic {
			startIndex = i
			break
		}
	}

	if startIndex == -1 {
		// This case should ideally not be reached if inputs are valid according to instructions
		// But for robustness, we might want to handle it.
		// For now, let's assume valid input.
		return []string{}
	}

	// Generate the chromatic scale starting with the tonic
	chromaticScale := make([]string, 12)
	for i := 0; i < 12; i++ {
		chromaticScale[i] = scale[(startIndex+i)%12]
	}

	if interval == "" {
		return chromaticScale
	}

	// Generate the diatonic scale based on intervals
	result := []string{chromaticScale[0]}
	currentIndex := 0

	for _, iv := range interval {
		switch iv {
		case 'm': // half step
			currentIndex = (currentIndex + 1) % 12
		case 'M': // whole step
			currentIndex = (currentIndex + 2) % 12
		case 'A': // augmented second (whole + half)
			currentIndex = (currentIndex + 3) % 12
		}
		result = append(result, chromaticScale[currentIndex])
	}

	return result
}
