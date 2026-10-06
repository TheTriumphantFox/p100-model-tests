package ledger

import (
	"errors"
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
	if len(entries) == 0 {
		if _, err := FormatLedger(currency, "en-US", []Entry{{Date: "2014-01-01", Description: "", Change: 0}}); err != nil {
			return "", err
		}
	}

	// Validate locale
	if locale != "nl-NL" && locale != "en-US" {
		return "", errors.New("")
	}

	// Validate currency
	if currency != "EUR" && currency != "USD" {
		return "", errors.New("")
	}

	// Validate entries
	for _, entry := range entries {
		if len(entry.Date) != 10 {
			return "", errors.New("")
		}
		if entry.Date[4] != '-' || entry.Date[7] != '-' {
			return "", errors.New("")
		}
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

	// Build header
	var header string
	if locale == "nl-NL" {
		header = "Datum" + strings.Repeat(" ", 10-len("Datum")) + " | " +
			"Omschrijving" + strings.Repeat(" ", 25-len("Omschrijving")) + " | " + "Verandering" + "\n"
	} else {
		header = "Date" + strings.Repeat(" ", 10-len("Date")) + " | " +
			"Description" + strings.Repeat(" ", 25-len("Description")) + " | " + "Change" + "\n"
	}

	var s strings.Builder
	s.WriteString(header)

	for _, entry := range entriesCopy {
		// Format date
		var d string
		if locale == "nl-NL" {
			d = entry.Date[8:10] + "-" + entry.Date[5:7] + "-" + entry.Date[0:4]
		} else {
			d = entry.Date[5:7] + "/" + entry.Date[8:10] + "/" + entry.Date[0:4]
		}

		// Format description
		de := entry.Description
		if len(de) > 25 {
			de = de[:22] + "..."
		} else {
			de = de + strings.Repeat(" ", 25-len(de))
		}

		// Format amount
		negative := false
		cents := entry.Change
		if cents < 0 {
			cents = cents * -1
			negative = true
		}
		centsStr := strconv.Itoa(cents)
		switch len(centsStr) {
		case 1:
			centsStr = "00" + centsStr
		case 2:
			centsStr = "0" + centsStr
		}
		rest := centsStr[:len(centsStr)-2]
		var parts []string
		for len(rest) > 3 {
			parts = append(parts, rest[len(rest)-3:])
			rest = rest[:len(rest)-3]
		}
		if len(rest) > 0 {
			parts = append(parts, rest)
		}
		var a strings.Builder
		if locale == "nl-NL" {
			if negative {
				a.WriteString("-")
			} else {
				a.WriteString(" ")
			}
			if currency == "EUR" {
				a.WriteString("€")
			} else {
				a.WriteString("$")
			}
			a.WriteString(" ")
			for i := len(parts) - 1; i >= 0; i-- {
				a.WriteString(parts[i])
				if i > 0 {
					a.WriteString(".")
				}
			}
			a.WriteString(".")
			a.WriteString(centsStr[len(centsStr)-2:])
		} else {
			if negative {
				a.WriteString("(")
			}
			if currency == "EUR" {
				a.WriteString("€")
			} else {
				a.WriteString("$")
			}
			for i := len(parts) - 1; i >= 0; i-- {
				a.WriteString(parts[i])
				if i > 0 {
					a.WriteString(",")
				}
			}
			a.WriteString(".")
			a.WriteString(centsStr[len(centsStr)-2:])
			if negative {
				a.WriteString(")")
			} else {
				a.WriteString(" ")
			}
		}

		al := 0
		for range a.String() {
			al++
		}
		s.WriteString(d + strings.Repeat(" ", 10-len(d)) + " | " + de + " | " +
			strings.Repeat(" ", 13-al) + a.String() + "\n")
	}

	return s.String(), nil
}
