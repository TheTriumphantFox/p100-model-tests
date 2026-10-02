use std::fmt;
use std::ops::{Add, Sub, Mul};

/// Type implementing arbitrary-precision decimal arithmetic
pub struct Decimal {
    // We store the decimal as an integer scaled by 10^scale.
    // e.g., 12.34 is stored as 1234 with scale 2.
    // Using i128 allows for large numbers and negative values.
    value: i128,
    scale: usize,
}

impl Decimal {
    pub fn try_from(input: &str) -> Option<Decimal> {
        let input = input.trim();
        if input.is_empty() {
            return None;
        }

        let mut sign: i128 = 1;
        let mut start = 0;

        if input.starts_with('-') {
            sign = -1;
            start = 1;
        } else if input.starts_with('+') {
            start = 1;
        }

        let digits_str = &input[start..];
        
        if digits_str.is_empty() {
            return None;
        }

        let dot_pos = digits_str.find('.');
        
        let (int_str, frac_str) = match dot_pos {
            Some(pos) => (&digits_str[..pos], &digits_str[pos+1..]),
            None => (digits_str, ""),
        };

        if int_str.is_empty() && frac_str.is_empty() {
            return None;
        }

        // Parse integer part
        let int_part: i128 = match int_str.parse() {
            Ok(v) => v,
            Err(_) => return None,
        };

        // Parse fractional part
        let mut frac_part: i128 = 0;
        let mut frac_len: usize = 0;

        if !frac_str.is_empty() {
            // Remove trailing zeros for canonical representation
            let trimmed_frac = frac_str.trim_end_matches('0');
            if !trimmed_frac.is_empty() {
                frac_part = match trimmed_frac.parse::<i128>() {
                    Ok(v) => v,
                    Err(_) => return None,
                };
                frac_len = trimmed_frac.len();
            }
        }

        // Combine into a single scaled value
        // Value = sign * (int_part * 10^frac_len + frac_part)
        // We need to align scales. The resulting scale will be frac_len.
        
        let int_scaled = int_part * 10i128.pow(frac_len as u32);
        let total_value = sign * (int_scaled + frac_part);

        // Normalize zero
        if total_value == 0 {
            return Some(Decimal {
                value: 0,
                scale: 0,
            });
        }

        Some(Decimal {
            value: total_value,
            scale: frac_len,
        })
    }
}

impl PartialEq for Decimal {
    fn eq(&self, other: &Self) -> bool {
        if self.scale != other.scale {
            // Align scales to compare
            let scale_diff = (self.scale as i64 - other.scale as i64).abs() as u32;
            let self_scaled = if self.scale > other.scale {
                self.value * 10i128.pow(scale_diff)
            } else {
                self.value
            };
            let other_scaled = if other.scale > self.scale {
                other.value * 10i128.pow(scale_diff)
            } else {
                other.value
            };
            self_scaled == other_scaled
        } else {
            self.value == other.value
        }
    }
}

impl Eq for Decimal {}

impl PartialOrd for Decimal {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        if self.scale != other.scale {
            let scale_diff = (self.scale as i64 - other.scale as i64).abs() as u32;
            let self_scaled = if self.scale > other.scale {
                self.value * 10i128.pow(scale_diff)
            } else {
                self.value
            };
            let other_scaled = if other.scale > self.scale {
                other.value * 10i128.pow(scale_diff)
            } else {
                other.value
            };
            self_scaled.partial_cmp(&other_scaled)
        } else {
            self.value.partial_cmp(&other.value)
        }
    }
}

impl Add for Decimal {
    type Output = Self;

    fn add(self, other: Self) -> Self {
        // Find common scale
        let max_scale = std::cmp::max(self.scale, other.scale);
        
        let self_scaled = if self.scale < max_scale {
            self.value * 10i128.pow((max_scale - self.scale) as u32)
        } else {
            self.value
        };
        
        let other_scaled = if other.scale < max_scale {
            other.value * 10i128.pow((max_scale - other.scale) as u32)
        } else {
            other.value
        };
        
        let result_value = self_scaled + other_scaled;
        
        // Normalize trailing zeros if possible to reduce scale
        let mut final_scale = max_scale;
        let mut final_value = result_value;
        
        while final_scale > 0 && final_value % 10 == 0 {
            final_value /= 10;
            final_scale -= 1;
        }
        
        // Handle zero
        if final_value == 0 {
            return Decimal {
                value: 0,
                scale: 0,
            };
        }

        Decimal {
            value: final_value,
            scale: final_scale,
        }
    }
}

impl Sub for Decimal {
    type Output = Self;

    fn sub(self, other: Self) -> Self {
        self.add(Decimal {
            value: -other.value,
            scale: other.scale,
        })
    }
}

impl Mul for Decimal {
    type Output = Self;

    fn mul(self, other: Self) -> Self {
        let result_value = self.value * other.value;
        let result_scale = self.scale + other.scale;
        
        // Normalize trailing zeros
        let mut final_scale = result_scale;
        let mut final_value = result_value;
        
        while final_scale > 0 && final_value % 10 == 0 {
            final_value /= 10;
            final_scale -= 1;
        }
        
        // Handle zero
        if final_value == 0 {
            return Decimal {
                value: 0,
                scale: 0,
            };
        }

        Decimal {
            value: final_value,
            scale: final_scale,
        }
    }
}

impl fmt::Display for Decimal {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        if self.value == 0 {
            return write!(f, "0");
        }

        if self.value < 0 {
            write!(f, "-")?;
        }
        
        let abs_value = self.value.abs();
        
        if self.scale == 0 {
            write!(f, "{}", abs_value)
        } else {
            let abs_str = abs_value.to_string();
            let len = abs_str.len();
            
            if len <= self.scale {
                // Need leading zeros after decimal point
                write!(f, "0.")?;
                for _ in 0..(self.scale - len) {
                    write!(f, "0")?;
                }
                write!(f, "{}", abs_str)
            } else {
                // Split into integer and fractional parts
                let int_part = &abs_str[..len - self.scale];
                let frac_part = &abs_str[len - self.scale..];
                write!(f, "{}.{}", int_part, frac_part)
            }
        }
    }
}
