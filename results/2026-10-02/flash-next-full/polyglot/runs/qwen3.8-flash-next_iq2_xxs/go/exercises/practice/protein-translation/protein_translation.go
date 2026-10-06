package protein

import (
	"errors"
)

var ErrStop = errors.New("stop codon encountered")
var ErrInvalidBase = errors.New("invalid RNA")

var codonTable = map[string]string{
	"AUG": "Methionine",
	"UUU": "Phenylalanine",
	"UUC": "Phenylalanine",
	"UUA": "Leucine",
	"UUG": "Leucine",
	"UCU": "Serine",
	"UCC": "Serine",
	"UCA": "Serine",
	"UCG": "Serine",
	"UAU": "Tyrosine",
	"UAC": "Tyrosine",
	"UGU": "Cysteine",
	"UGC": "Cysteine",
	"UGG": "Tryptophan",
	"UAA": "STOP",
	"UAG": "STOP",
	"UGA": "STOP",
}

func FromCodon(codon string) (string, error) {
	if protein, ok := codonTable[codon]; ok {
		if protein == "STOP" {
			return "", ErrStop
		}
		return protein, nil
	}
	return "", ErrInvalidBase
}

func FromRNA(rna string) ([]string, error) {
	var proteins []string
	for i := 0; i < len(rna); i += 3 {
		if i+3 > len(rna) {
			return proteins, ErrInvalidBase
		}
		codon := rna[i : i+3]
		protein, err := FromCodon(codon)
		if err != nil {
			if err == ErrStop {
				return proteins, nil
			}
			return proteins, err
		}
		proteins = append(proteins, protein)
	}
	return proteins, nil
}
