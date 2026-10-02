pub fn answer(command: &str) -> Option<i32> {
    if !command.starts_with("What is ") || !command.ends_with('?') {
        return None;
    }

    let mut parts = command[8..command.len() - 1].trim().split_whitespace().peekable();

    let mut result = match parts.next() {
        Some(num_str) => num_str.parse::<i32>().ok()?,
        None => return None,
    };

    while let Some(op) = parts.next() {
        match op {
            "plus" => {
                let operand = parts.next()?.parse::<i32>().ok()?;
                result = result + operand;
            }
            "minus" => {
                let operand = parts.next()?.parse::<i32>().ok()?;
                result = result - operand;
            }
            "multiplied" => {
                if parts.next() != Some("by") {
                    return None;
                }
                let operand = parts.next()?.parse::<i32>().ok()?;
                result = result * operand;
            }
            "divided" => {
                if parts.next() != Some("by") {
                    return None;
                }
                let operand = parts.next()?.parse::<i32>().ok()?;
                result = result / operand;
            }
            "raised" => {
                if parts.next() != Some("to") {
                    return None;
                }
                if parts.next() != Some("the") {
                    return None;
                }
                if parts.next() != Some("power") {
                    return None;
                }
                if parts.next() != Some("of") {
                    return None;
                }
                let exponent = parts.next()?.parse::<i32>().ok()?;
                result = result.pow(exponent as u32);
            }
            _ => return None,
        }
    }

    Some(result)
}
