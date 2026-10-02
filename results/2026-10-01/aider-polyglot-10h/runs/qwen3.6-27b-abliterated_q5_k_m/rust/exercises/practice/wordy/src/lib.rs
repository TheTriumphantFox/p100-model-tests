pub fn answer(command: &str) -> Option<i32> {
    if !command.starts_with("What is ") || !command.ends_with('?') {
        return None;
    }

    let body = &command[8..command.len() - 1];
    if body.is_empty() {
        return None;
    }

    let mut tokens = body.split_whitespace().peekable();
    
    let first_token = tokens.next()?;
    let mut result = first_token.parse::<i32>().ok()?;

    while let Some(op) = tokens.next() {
        match op {
            "plus" => {
                let num = tokens.next()?.parse::<i32>().ok()?;
                result += num;
            }
            "minus" => {
                let num = tokens.next()?.parse::<i32>().ok()?;
                result -= num;
            }
            "multiplied" => {
                if tokens.next()? != "by" {
                    return None;
                }
                let num = tokens.next()?.parse::<i32>().ok()?;
                result *= num;
            }
            "divided" => {
                if tokens.next()? != "by" {
                    return None;
                }
                let num = tokens.next()?.parse::<i32>().ok()?;
                result /= num;
            }
            "raised" => {
                if tokens.next()? != "to" {
                    return None;
                }
                if tokens.next()? != "the" {
                    return None;
                }
                let power_str = tokens.next()?;
                // Handle ordinal suffixes like "5th", "3rd", "2nd", "1st"
                let power_digits = power_str.trim_end_matches(|c: char| !c.is_ascii_digit());
                let power = power_digits.parse::<i32>().ok()?;
                if tokens.next()? != "power" {
                    return None;
                }
                result = result.pow(power as u32);
            }
            _ => return None, // Unsupported operation or unexpected token
        }
    }

    Some(result)
}
