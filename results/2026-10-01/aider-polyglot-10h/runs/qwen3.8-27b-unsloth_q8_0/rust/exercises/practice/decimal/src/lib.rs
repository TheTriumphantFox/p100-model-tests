use std::cmp::Ordering;
use std::ops::{Add, Mul, Sub};

/// Type implementing arbitrary-precision decimal arithmetic
#[derive(Debug, Clone, Copy)]
pub struct Decimal {
    // The unscaled value. The actual value is value / 10^scale
    value: i128,
    // The number of digits after the decimal point
    scale: u32,
}

impl Decimal {
    pub fn try_from(input: &str) -> Option<Decimal> {
        let input = input.trim();
        if input.is_empty() {
            return None;
        }

        let (sign, digits) = if let Some(rest) = input.strip_prefix('-') {
            (-1i128, rest)
        } else if let Some(rest) = input.strip_prefix('+') {
            (1i128, rest)
        } else {
            (1i128, input)
        };

        let (int_part, frac_part) = match digits.find('.') {
            Some(pos) => (&digits[..pos], &digits[pos + 1..]),
            None => (digits, ""),
        };

        if int_part.is_empty() && frac_part.is_empty() {
            return None;
        }

        // Check for valid digits
        if !int_part.is_empty() && !int_part.chars().all(|c| c.is_ascii_digit()) {
            return None;
        }
        if !frac_part.is_empty() && !frac_part.chars().all(|c| c.is_ascii_digit()) {
            return None;
        }

        let scale = frac_part.len() as u32;
        
        // Combine integer and fractional parts into a single integer string
        let combined = if int_part.is_empty() {
            frac_part.to_string()
        } else if frac_part.is_empty() {
            int_part.to_string()
        } else {
            format!("{}{}", int_part, frac_part)
        };

        // Remove leading zeros for parsing, but keep at least one digit
        let combined_trimmed = combined.trim_start_matches('0');
        let value_str = if combined_trimmed.is_empty() {
            "0".to_string()
        } else {
            combined_trimmed.to_string()
        };

        let value: i128 = value_str.parse().ok()?;

        Some(Decimal {
            value: value * sign,
            scale,
        })
    }

    fn normalize(&self) -> (i128, u32) {
        let mut value = self.value;
        let mut scale = self.scale;

        while scale > 0 && value % 10 == 0 {
            value /= 10;
            scale -= 1;
        }

        (value, scale)
    }
}

impl PartialEq for Decimal {
    fn eq(&self, other: &Self) -> bool {
        let (v1, s1) = self.normalize();
        let (v2, s2) = other.normalize();

        if s1 == s2 {
            v1 == v2
        } else if s1 > s2 {
            v1 == v2 * 10i128.pow(s1 - s2)
        } else {
            v2 == v1 * 10i128.pow(s2 - s1)
        }
    }
}

impl Eq for Decimal {}

impl PartialOrd for Decimal {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl Ord for Decimal {
    fn cmp(&self, other: &Self) -> Ordering {
        let (v1, s1) = self.normalize();
        let (v2, s2) = other.normalize();

        if s1 == s2 {
            v1.cmp(&v2)
        } else if s1 > s2 {
            v1.cmp(&(v2 * 10i128.pow(s1 - s2)))
        } else {
            (v1 * 10i128.pow(s2 - s1)).cmp(&v2)
        }
    }
}

impl Add for Decimal {
    type Output = Decimal;

    fn add(self, rhs: Self) -> Self::Output {
        let (v1, s1) = self.normalize();
        let (v2, s2) = rhs.normalize();

        if s1 == s2 {
            Decimal {
                value: v1 + v2,
                scale: s1,
            }
        } else if s1 > s2 {
            Decimal {
                value: v1 + v2 * 10i128.pow(s1 - s2),
                scale: s1,
            }
        } else {
            Decimal {
                value: v1 * 10i128.pow(s2 - s1) + v2,
                scale: s2,
            }
        }
    }
}

impl Sub for Decimal {
    type Output = Decimal;

    fn sub(self, rhs: Self) -> Self::Output {
        let (v1, s1) = self.normalize();
        let (v2, s2) = rhs.normalize();

        if s1 == s2 {
            Decimal {
                value: v1 - v2,
                scale: s1,
            }
        } else if s1 > s2 {
            Decimal {
                value: v1 - v2 * 10i128.pow(s1 - s2),
                scale: s1,
            }
        } else {
            Decimal {
                value: v1 * 10i128.pow(s2 - s1) - v2,
                scale: s2,
            }
        }
    }
}

impl Mul for Decimal {
    type Output = Decimal;

    fn mul(self, rhs: Self) -> Self::Output {
        let (v1, s1) = self.normalize();
        let (v2, s2) = rhs.normalize();

        Decimal {
            value: v1 * v2,
            scale: s1 + s2,
        }
    }
}
