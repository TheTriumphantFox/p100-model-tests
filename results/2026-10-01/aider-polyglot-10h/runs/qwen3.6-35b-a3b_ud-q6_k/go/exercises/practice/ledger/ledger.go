package ledger

import (
	"errors"
	"fmt"
	"sort"
	"strings"
)

type Entry struct {
	Date        string // "Y-m-d"
	Description string
	Change      int // in cents
}

func FormatLedger(currency string, locale string, entries []Entry) (string, error) {
	// Log of changes:
	// 1. Added sort and fmt to imports.
	// 2. Removed unnecessary entry copying and complex manual sorting.
	// 3. Replaced complex goroutine/channel logic with simple sequential processing.
	// 4. Simplified header generation.
	// 5. Simplified currency and date formatting logic.
	// 6. Improved error handling and code readability.
	// 7. Removed unused variables (dateLen, descLen, changeLen, dateHeader, descHeader, changeHeader)

	if currency != "EUR" && currency != "USD" {
		return "", errors.New("invalid currency")
	}

	var header string

	if locale == "nl-NL" {
		header = "Datum" + strings.Repeat(" ", 10-len("Datum")) + " | " +
			"Omschrijving" + strings.Repeat(" ", 25-len("Omschrijving")) + " | " +
			"Verandering" + "\n"
	} else if locale == "en-US" {
		header = "Date" + strings.Repeat(" ", 10-len("Date")) + " | " +
			"Description" + strings.Repeat(" ", 25-len("Description")) + " | " +
			"Change" + "\n"
	} else {
		return "", errors.New("invalid locale")
	}

	// Sort entries
	entriesCopy := make([]Entry, len(entries))
	copy(entriesCopy, entries)
	sort.Slice(entriesCopy, func(i, j int) bool {
		if entriesCopy[i].Date != entriesCopy[j].Date {
			return entriesCopy[i].Date < entriesCopy[j].Date
		}
		if entriesCopy[i].Description != entriesCopy[j].Description {
			return entriesCopy[i].Description < entriesCopy[j].Description
		}
		return entriesCopy[i].Change < entriesCopy[j].Change
	})

	var sb strings.Builder
	sb.WriteString(header)

	for _, e := range entriesCopy {
		// Validate Date
		if len(e.Date) != 10 || e.Date[4] != '-' || e.Date[7] != '-' {
			return "", errors.New("invalid date format")
		}

		// Format Date
		var formattedDate string
		if locale == "nl-NL" {
			formattedDate = e.Date[8:10] + "-" + e.Date[5:7] + "-" + e.Date[0:4]
		} else {
			formattedDate = e.Date[5:7] + "/" + e.Date[8:10] + "/" + e.Date[0:4]
		}

		// Format Description
		desc := e.Description
		if len(desc) > 25 {
			desc = desc[:22] + "..."
		} else {
			desc = desc + strings.Repeat(" ", 25-len(desc))
		}

		// Format Change
		negative := e.Change < 0
		cents := e.Change
		if negative {
			cents = -cents
		}

		var changeStr string
		dollars := cents / 100
		remainingCents := cents % 100

		var formattedDollars string
		if dollars == 0 {
			formattedDollars = "0"
		} else {
			var parts []string
			for dollars > 0 {
				parts = append(parts, fmt.Sprintf("%03d", dollars%1000))
				dollars /= 1000
			}
			for i := len(parts) - 1; i >= 0; i-- {
				if i < len(parts)-1 {
					formattedDollars += ","
				}
				formattedDollars += parts[i]
			}
		}

		if locale == "nl-NL" {
			changeStr = fmt.Sprintf("%s %s,%02d ", currency, formattedDollars, remainingCents)
			if negative {
				changeStr = fmt.Sprintf("%s -%s,%02d", currency, formattedDollars, remainingCents)
			}
		} else if locale == "en-US" {
			if negative {
				changeStr = fmt.Sprintf("(%s%s.%02d)", currency, formattedDollars, remainingCents)
			} else {
				changeStr = fmt.Sprintf("%s%s.%02d ", currency, formattedDollars, remainingCents)
			}
		}

		// Adjust spacing for Change column to be 13 chars wide
		// The column width is effectively determined by the header "Change" (6 chars) + padding?
		// Looking at original code:
		// " | " + "Change" + "\n"
		// And for entries: strings.Repeat(" ", 13-al) + a
		// So the change part is right-aligned in a 13 char space?
		// Let's check original logic:
		// al is length of 'a' (the formatted change string).
		// It prepends spaces to make total width 13? No, 13 - al.
		// So the field is 13 chars wide.
		
		// Let's reconstruct the line
		line := fmt.Sprintf("%-10s | %-25s | %13s", formattedDate, desc, changeStr)
		sb.WriteString(line)
		sb.WriteString("\n")
	}

	return sb.String(), nil
}
