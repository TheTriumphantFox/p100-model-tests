pub fn answer(command: &str) -> Option<i32> {
    let trimmed = command.trim();
    let prefix = "What is ";
    if !trimmed.starts_with(prefix) {
        return None;
    }
    let rest = &trimmed[prefix.len()..];
    if !rest.ends_with('?') {
        return None;
    }
    let expr = &rest[..rest.len() - 1];
    
    let tokens: Vec<&str> = expr.split_whitespace().collect();
    if tokens.is_empty() {
        return None;
    }

    let mut iter = tokens.iter();
    
    // Parse first number
    let first_num_str = iter.next()?;
    let mut current = parse_number(first_num_str)?;

    while let Some(op_str) = iter.next() {
        let op = match *op_str {
            "plus" => Some(0),
            "minus" => Some(1),
            "multiplied" => Some(2),
            "divided" => Some(3),
            _ => None,
        };
        
        let op_code = op?;
        
        // Handle multi-word operators
        if op_code == 2 || op_code == 3 {
            let next_token = iter.next()?;
            if *next_token != "by" {
                return None;
            }
        }

        let num_str = iter.next()?;
        let num = parse_number(num_str)?;

        current = match op_code {
            0 => current + num,
            1 => current - num,
            2 => current * num,
            3 => {
                if num == 0 {
                    return None;
                }
                current / num
            }
            _ => return None,
        };
    }

    Some(current)
}

fn parse_number(s: &str) -> Option<i32> {
    s.parse::<i32>().ok()
}
