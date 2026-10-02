package ledger

import (
	"errors"
	"fmt"
	"sort"
	"strconv"
	"strings"
	"unicode/utf8"
)

type Entry struct {
	Date        string // "Y-m-d"
	Description string
	Change      int // in cents
}

// Refactoring Log:
// 1. Removed manual entry copying and complex bubble-sort-like sorting logic.
// 2. Implemented sort.Slice for stable, clear sorting by Date, Description, and Change.
// 3. Extracted date validation and formatting into formatDate helper.
// 4. Extracted description truncation/padding into formatDescription helper.
// 5. Extracted amount formatting into formatAmount helper, handling locale-specific rules.
// 6. Removed concurrent processing (goroutines/channels) in favor of simple sequential processing for clarity and reliability.
// 7. Cleaned up header generation.
// 8. Improved error handling to return specific errors instead of empty strings.
// 9. Fixed trailing newline issue by joining lines with \n instead of appending \n to each line.
// 10. Fixed amount padding to use rune count for correct visual alignment with multi-byte characters like €.

func FormatLedger(currency string, locale string, entries []Entry) (string, error) {
	if locale != "en-US" && locale != "nl-NL" {
		return "", errors.New("invalid locale")
	}
	if currency != "USD" && currency != "EUR" {
		return "", errors.New("invalid currency")
	}

	// Create a copy to avoid modifying the original slice
	entriesCopy := make([]Entry, len(entries))
	copy(entriesCopy, entries)

	// Sort entries by Date, then Description, then Change
	sort.Slice(entriesCopy, func(i, j int) bool {
		if entriesCopy[i].Date != entriesCopy[j].Date {
			return entriesCopy[i].Date < entriesCopy[j].Date
		}
		if entriesCopy[i].Description != entriesCopy[j].Description {
			return entriesCopy[i].Description < entriesCopy[j].Description
		}
		return entriesCopy[i].Change < entriesCopy[j].Change
	})

	var lines []string

	// Header
	if locale == "en-US" {
		lines = append(lines, "Date       | Description               | Change       ")
	} else {
		lines = append(lines, "Datum      | Omschrijving              | Verandering  ")
	}

	for _, entry := range entriesCopy {
		dateStr, err := formatDate(entry.Date, locale)
		if err != nil {
			return "", err
		}
		descStr := formatDescription(entry.Description)
		amountStr, err := formatAmount(entry.Change, currency, locale)
		if err != nil {
			return "", err
		}

		lines = append(lines, fmt.Sprintf("%s | %s | %s", dateStr, descStr, amountStr))
	}

	return strings.Join(lines, "\n"), nil
}

func formatDate(date string, locale string) (string, error) {
	if len(date) != 10 {
		return "", errors.New("invalid date format")
	}
	// Expected format: YYYY-MM-DD
	if date[4] != '-' || date[7] != '-' {
		return "", errors.New("invalid date format")
	}

	year := date[0:4]
	month := date[5:7]
	day := date[8:10]

	if locale == "en-US" {
		return fmt.Sprintf("%s/%s/%s", month, day, year), nil
	}
	// nl-NL
	return fmt.Sprintf("%s-%s-%s", day, month, year), nil
}

func formatDescription(desc string) string {
	if len(desc) > 25 {
		return desc[:22] + "..."
	}
	return desc + strings.Repeat(" ", 25-len(desc))
}

func formatAmount(cents int, currency string, locale string) (string, error) {
	negative := cents < 0
	if negative {
		cents = -cents
	}

	// Split into dollars and cents
	dollars := cents / 100
	centsPart := cents % 100

	// Format dollars with thousands separators
	dollarsStr := strconv.Itoa(dollars)
	var parts []string
	for len(dollarsStr) > 3 {
		parts = append(parts, dollarsStr[len(dollarsStr)-3:])
		dollarsStr = dollarsStr[:len(dollarsStr)-3]
	}
	if len(dollarsStr) > 0 {
		parts = append(parts, dollarsStr)
	}

	var formattedDollars string
	if locale == "en-US" {
		for i := len(parts) - 1; i >= 0; i-- {
			if i == len(parts)-1 {
				formattedDollars = parts[i]
			} else {
				formattedDollars += "," + parts[i]
			}
		}
	} else { // nl-NL
		for i := len(parts) - 1; i >= 0; i-- {
			if i == len(parts)-1 {
				formattedDollars = parts[i]
			} else {
				formattedDollars += "." + parts[i]
			}
		}
	}

	// Format cents
	centsStr := fmt.Sprintf("%02d", centsPart)

	// Determine currency symbol
	var symbol string
	if currency == "USD" {
		symbol = "$"
	} else if currency == "EUR" {
		symbol = "€"
	} else {
		return "", errors.New("invalid currency")
	}

	var amountStr string
	if locale == "en-US" {
		if negative {
			amountStr = fmt.Sprintf("(%s%s.%s)", symbol, formattedDollars, centsStr)
		} else {
			amountStr = fmt.Sprintf("%s%s.%s", symbol, formattedDollars, centsStr)
		}
	} else { // nl-NL
		if negative {
			amountStr = fmt.Sprintf("%s %s,%s-", symbol, formattedDollars, centsStr)
		} else {
			amountStr = fmt.Sprintf("%s %s,%s", symbol, formattedDollars, centsStr)
		}
	}

	// Pad to 13 characters (runes)
	runeCount := utf8.RuneCountInString(amountStr)
	if runeCount < 13 {
		amountStr = strings.Repeat(" ", 13-runeCount) + amountStr
	}

	return amountStr, nil
}
