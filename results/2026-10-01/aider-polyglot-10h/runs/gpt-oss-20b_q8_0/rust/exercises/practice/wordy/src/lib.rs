pub fn answer(command: &str) -> Option<i32> {
    // Normalize the command: lowercase and trim
    let cmd = command.trim().to_lowercase();

    // The command must start with "what is "
    if !cmd.starts_with("what is ") {
        return None;
    }

    // Remove the leading phrase
    let mut expr = cmd["what is ".len()..].trim();

    // Empty expression is invalid
    if expr.is_empty() {
        return None;
    }

    // Tokenize the expression.
    // We accept numbers (including negative), the words "plus", "minus",
    // "multiplied by", "divided by" and optionally "exponentiated by" when the
    // feature is enabled.
    #[derive(Debug, Clone, Copy)]
    enum Token {
        Number(i32),
        Plus,
        Minus,
        Multiply,
        Divide,
        Exponentiate,
    }

    let mut tokens: Vec<Token> = Vec::new();
    let mut chars = expr.chars().peekable();

    while let Some(&c) = chars.peek() {
        if c.is_whitespace() {
            chars.next();
            continue;
        }

        // Try to parse a number (possibly negative)
        if c.is_ascii_digit() || c == '-' {
            let mut num_str = String::new();
            // Handle negative sign
            if c == '-' {
                num_str.push('-');
                chars.next();
                // After a minus sign we must have a digit
                match chars.peek() {
                    Some(d) if d.is_ascii_digit() => {}
                    _ => return None,
                }
            }
            while let Some(&d) = chars.peek() {
                if d.is_ascii_digit() {
                    num_str.push(d);
                    chars.next();
                } else {
                    break;
                }
            }
            match num_str.parse::<i32>() {
                Ok(n) => tokens.push(Token::Number(n)),
                Err(_) => return None,
            }
            continue;
        }

        // Parse words
        let mut word = String::new();
        while let Some(&d) = chars.peek() {
            if d.is_ascii_alphabetic() {
                word.push(d);
                chars.next();
            } else {
                break;
            }
        }

        match word.as_str() {
            "plus" => tokens.push(Token::Plus),
            "minus" => tokens.push(Token::Minus),
            "multiplied" => {
                // Expect "by"
                let mut by = String::new();
                while let Some(&d) = chars.peek() {
                    if d.is_ascii_alphabetic() {
                        by.push(d);
                        chars.next();
                    } else {
                        break;
                    }
                }
                if by != "by" {
                    return None;
                }
                tokens.push(Token::Multiply);
            }
            "divided" => {
                // Expect "by"
                let mut by = String::new();
                while let Some(&d) = chars.peek() {
                    if d.is_ascii_alphabetic() {
                        by.push(d);
                        chars.next();
                    } else {
                        break;
                    }
                }
                if by != "by" {
                    return None;
                }
                tokens.push(Token::Divide);
            }
            #[cfg(feature = "exponentials")]
            "exponentiated" => {
                // Expect "by"
                let mut by = String::new();
                while let Some(&d) = chars.peek() {
                    if d.is_ascii_alphabetic() {
                        by.push(d);
                        chars.next();
                    } else {
                        break;
                    }
                }
                if by != "by" {
                    return None;
                }
                tokens.push(Token::Exponentiate);
            }
            _ => return None,
        }
    }

    // The token stream must alternate Number, Operator, Number, ...
    if tokens.is_empty() {
        return None;
    }
    if let Token::Number(_) = tokens[0] {
        // ok
    } else {
        return None;
    }

    let mut iter = tokens.into_iter();
    let mut result = match iter.next().unwrap() {
        Token::Number(n) => n,
        _ => unreachable!(),
    };

    while let Some(op) = iter.next() {
        let next_num = match iter.next() {
            Some(Token::Number(n)) => n,
            _ => return None,
        };

        result = match op {
            Token::Plus => result + next_num,
            Token::Minus => result - next_num,
            Token::Multiply => result * next_num,
            Token::Divide => {
                if next_num == 0 {
                    return None;
                }
                result / next_num
            }
            #[cfg(feature = "exponentials")]
            Token::Exponentiate => {
                // Handle negative exponents by returning None
                if next_num < 0 {
                    return None;
                }
                // Use i32::pow; it panics on overflow, so we catch it
                match result.checked_pow(next_num as u32) {
                    Some(v) => v,
                    None => return None,
                }
            }
            // This arm is never reached because `op` is always an operator,
            // but it satisfies the compiler's exhaustiveness check.
            Token::Number(_) => result,
        };
    }

    Some(result)
}
