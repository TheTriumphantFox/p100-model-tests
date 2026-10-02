package ledger

import (
	"errors"
	"fmt"
	"sort"
	"strconv"
	"strings"
)

type Entry struct {
	Date        string // "Y-m-d"
	Description string
	Change      int // in cents
}

func FormatLedger(currency string, locale string, entries []Entry) (string, error) {
	// Validate locale
	var header string
	if locale == "nl-NL" {
		header = "Datum      | Omschrijving              | Verandering\n"
	} else if locale == "en-US" {
		header = "Date       | Description               | Change\n"
	} else {
		return "", errors.New("unknown locale")
	}

	// Validate currency
	var currencySymbol string
	if currency == "EUR" {
		currencySymbol = "€"
	} else if currency == "USD" {
		currencySymbol = "$"
	} else {
		return "", errors.New("unknown currency")
	}

	// Sort entries
	sortedEntries := make([]Entry, len(entries))
	copy(sortedEntries, entries)
	sort.Slice(sortedEntries, func(i, j int) bool {
		ei, ej := sortedEntries[i], sortedEntries[j]
		if ei.Date != ej.Date {
			return ei.Date < ej.Date
		}
		if ei.Description != ej.Description {
			return ei.Description < ej.Description
		}
		return ei.Change < ej.Change
	})

	var sb strings.Builder
	sb.WriteString(header)

	for _, entry := range sortedEntries {
		// Validate date format
		if len(entry.Date) != 10 || entry.Date[4] != '-' || entry.Date[7] != '-' {
			return "", errors.New("invalid date format")
		}

		// Format date
		var dateStr string
		if locale == "nl-NL" {
			dateStr = fmt.Sprintf("%s-%s-%s", entry.Date[8:10], entry.Date[5:7], entry.Date[0:4])
		} else {
			dateStr = fmt.Sprintf("%s/%s/%s", entry.Date[5:7], entry.Date[8:10], entry.Date[0:4])
		}

		// Format description
		desc := entry.Description
		if len(desc) > 25 {
			desc = desc[:22] + "..."
		}
		descPadded := fmt.Sprintf("%-25s", desc)

		// Format change
		changeStr := formatChange(entry.Change, currencySymbol, locale)
		changePadded := fmt.Sprintf("%13s", changeStr)

		sb.WriteString(fmt.Sprintf("%s | %s | %s\n", dateStr, descPadded, changePadded))
	}

	return sb.String(), nil
}

func formatChange(change int, currencySymbol string, locale string) string {
	negative := change < 0
	if negative {
		change = -change
	}

	cents := change % 100
	dollars := change / 100

	centsStr := fmt.Sprintf("%02d", cents)
	dollarsStr := strconv.Itoa(dollars)

	// Add thousands separators
	var parts []string
	for i := len(dollarsStr); i > 0; i -= 3 {
		if i < 3 {
			parts = append([]string{dollarsStr[:i]}, parts...)
		} else {
			parts = append([]string{dollarsStr[i-3:i]}, parts...)
		}
	}

	var formattedDollars string
	if locale == "nl-NL" {
		formattedDollars = strings.Join(parts, ".")
	} else {
		formattedDollars = strings.Join(parts, ",")
	}

	var result string
	if locale == "nl-NL" {
		if negative {
			result = fmt.Sprintf("%s %s,%s-", currencySymbol, formattedDollars, centsStr)
		} else {
			result = fmt.Sprintf("%s %s,%s ", currencySymbol, formattedDollars, centsStr)
		}
	} else {
		if negative {
			result = fmt.Sprintf("(%s%s.%s)", currencySymbol, formattedDollars, centsStr)
		} else {
			result = fmt.Sprintf("%s%s.%s ", currencySymbol, formattedDollars, centsStr)
		}
	}

	return result
}
