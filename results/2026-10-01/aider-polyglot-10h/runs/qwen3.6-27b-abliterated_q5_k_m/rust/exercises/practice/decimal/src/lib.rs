/// Type implementing arbitrary-precision decimal arithmetic
pub struct Decimal {
    value: i128,
    scale: u32,
}

impl Decimal {
    pub fn try_from(input: &str) -> Option<Decimal> {
        let input = input.trim();
        if input.is_empty() {
            return None;
        }

        let mut parts = input.splitn(2, '.');
        let int_part = parts.next()?;
        let frac_part = parts.next();

        let (sign, int_str) = if let Some(stripped) = int_part.strip_prefix('-') {
            (-1, stripped)
        } else if let Some(stripped) = int_part.strip_prefix('+') {
            (1, stripped)
        } else {
            (1, int_part)
        };

        if int_str.is_empty() && frac_part.is_none() {
            return None;
        }

        let int_val: i128 = int_str.parse().ok()?;
        
        let (frac_val, scale) = if let Some(frac) = frac_part {
            if frac.is_empty() {
                (0, 0)
            } else {
                let scale = frac.len() as u32;
                let frac_val: i128 = frac.parse().ok()?;
                (frac_val, scale)
            }
        } else {
            (0, 0)
        };

        // Combine integer and fractional parts into a single integer value
        // value = int_val * 10^scale + frac_val
        let multiplier = 10_i128.pow(scale);
        let combined = int_val * multiplier + frac_val;
        
        let final_value = combined * sign as i128;

        Some(Decimal {
            value: final_value,
            scale,
        })
    }

    fn value_at_scale(&self, target_scale: u32) -> i128 {
        if target_scale == self.scale {
            self.value
        } else if target_scale > self.scale {
            let diff = target_scale - self.scale;
            self.value * 10_i128.pow(diff)
        } else {
            let diff = self.scale - target_scale;
            self.value / 10_i128.pow(diff)
        }
    }
}

impl PartialEq for Decimal {
    fn eq(&self, other: &Decimal) -> bool {
        let common_scale = if self.scale > other.scale { self.scale } else { other.scale };
        self.value_at_scale(common_scale) == other.value_at_scale(common_scale)
    }
}

impl Eq for Decimal {}

impl PartialOrd for Decimal {
    fn partial_cmp(&self, other: &Decimal) -> Option<std::cmp::Ordering> {
        let common_scale = if self.scale > other.scale { self.scale } else { other.scale };
        let self_val = self.value_at_scale(common_scale);
        let other_val = other.value_at_scale(common_scale);
        Some(self_val.cmp(&other_val))
    }
}

impl Ord for Decimal {
    fn cmp(&self, other: &Decimal) -> std::cmp::Ordering {
        let common_scale = if self.scale > other.scale { self.scale } else { other.scale };
        let self_val = self.value_at_scale(common_scale);
        let other_val = other.value_at_scale(common_scale);
        self_val.cmp(&other_val)
    }
}

use std::ops::{Add, Sub, Mul};

impl Add for Decimal {
    type Output = Decimal;

    fn add(self, other: Decimal) -> Decimal {
        let common_scale = if self.scale > other.scale { self.scale } else { other.scale };
        let self_val = self.value_at_scale(common_scale);
        let other_val = other.value_at_scale(common_scale);
        Decimal {
            value: self_val + other_val,
            scale: common_scale,
        }
    }
}

impl Sub for Decimal {
    type Output = Decimal;

    fn sub(self, other: Decimal) -> Decimal {
        let common_scale = if self.scale > other.scale { self.scale } else { other.scale };
        let self_val = self.value_at_scale(common_scale);
        let other_val = other.value_at_scale(common_scale);
        Decimal {
            value: self_val - other_val,
            scale: common_scale,
        }
    }
}

impl Mul for Decimal {
    type Output = Decimal;

    fn mul(self, other: Decimal) -> Decimal {
        Decimal {
            value: self.value * other.value,
            scale: self.scale + other.scale,
        }
    }
}
