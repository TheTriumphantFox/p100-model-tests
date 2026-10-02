package protein

import "errors"

var (
	ErrStop          = errors.New("stop codon")
	ErrInvalidBase   = errors.New("invalid codon")
)

func FromRNA(rna string) ([]string, error) {
	var proteins []string
	for i := 0; i < len(rna); i += 3 {
		codon := rna[i:min(i+3, len(rna))]
		protein, err := FromCodon(codon)
		if err != nil {
			if err == ErrStop {
				break
			}
			return nil, err
		}
		proteins = append(proteins, protein)
	}
	return proteins, nil
}

func FromCodon(codon string) (string, error) {
	switch codon {
	case "AUG":
		return "Methionine", nil
	case "UUU", "UUC":
		return "Phenylalanine", nil
	case "UUA", "UUG":
		return "Leucine", nil
	case "UCU", "UCC", "UCA", "UCG":
		return "Serine", nil
	case "UAU", "UAC":
		return "Tyrosine", nil
	case "UGU", "UGC":
		return "Cysteine", nil
	case "UGG":
		return "Tryptophan", nil
	case "UAA", "UAG", "UGA":
		return "", ErrStop
	default:
		return "", ErrInvalidBase
	}
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
