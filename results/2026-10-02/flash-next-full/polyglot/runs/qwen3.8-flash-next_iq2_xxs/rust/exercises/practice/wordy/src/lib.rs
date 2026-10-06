pub fn answer(command: &str) -> Option<i32> {
    // Check basic format
    if !command.starts_with("What is ") || !command.ends_with('?') {
        return None;
    }

    // Extract the expression part, removing "What is " and "?"
    let expr = &command[8..command.len() - 1];
    
    // Tokenize
    let mut tokens: Vec<String> = Vec::new();
    let mut current_token = String::new();
    let mut prev_was_space = true; // Handle leading spaces if any, though slice starts after "What is "
    
    // Simple tokenizer: split by spaces, but keep "multiplied by" and "divided by" as single tokens if they appear as separate words?
    // Actually, the problem says "multiplied by" and "divided by". 
    // Let's just split by whitespace first, then merge "multiplied" + "by" and "divided" + "by".
    let raw_tokens: Vec<&str> = expr.split_whitespace().collect();
    
    if raw_tokens.is_empty() {
        return None;
    }

    let mut i = 0;
    while i < raw_tokens.len() {
        let token = raw_tokens[i];
        if token == "multiplied" && i + 1 < raw_tokens.len() && raw_tokens[i + 1] == "by" {
            tokens.push("multiplied by".to_string());
            i += 2;
        } else if token == "divided" && i + 1 < raw_tokens.len() && raw_tokens[i + 1] == "by" {
            tokens.push("divided by".to_string());
            i += 2;
        } else {
            tokens.push(token.to_string());
            i += 1;
        }
    }

    if tokens.is_empty() {
        return None;
    }

    // Validate and Parse
    // Expecting: Number (Operator Number)*
    // Tokens should alternate: Number, Operator, Number, Operator...
    
    let mut result: Option<i32> = None;
    let mut expecting_number = true;

    for token in &tokens {
        if expecting_number {
            // Parse number
            match token.parse::<i32>() {
                Ok(val) => {
                    if result.is_none() {
                        result = Some(val);
                    } else {
                        // Should have been handled by operator logic if we were evaluating immediately, 
                        // but we are validating structure first. 
                        // Actually, let's just validate structure first, then evaluate.
                        // Or evaluate on the fly.
                        // Let's stick to validation first.
                    }
                    // If we are evaluating on the fly, we need to know the previous result.
                    // Let's just validate structure first.
                }
                Err(_) => return None, // Invalid number token
            }
            expecting_number = false;
        } else {
            // Expecting operator
            match token.as_str() {
                "plus" | "minus" | "multiplied by" | "divided by" => {
                    // Valid operator
                }
                _ => return None, // Invalid token in operator position
            }
            expecting_number = true;
        }
    }

    // Check if we ended expecting a number (i.e., last token was an operator)
    if expecting_number {
        return None;
    }

    // Re-evaluate with actual calculation
    // We can re-parse or just do it in one pass. 
    // Let's do a second pass for evaluation since we validated structure.
    
    let mut iter = tokens.iter();
    let first_token = iter.next()?;
    let mut current_val: i32 = first_token.parse().ok()?;

    while let Some(op_token) = iter.next() {
        // Next token should be a number
        if let Some(num_token) = iter.next() {
            let num: i32 = num_token.parse().ok()?;
            match op_token.as_str() {
                "plus" => current_val += num,
                "minus" => current_val -= num,
                "multiplied by" => current_val *= num,
                "divided by" => {
                    if num == 0 {
                        return None; // Division by zero? Not specified, but usually invalid. 
                        // The prompt doesn't specify division by zero handling, but standard math rules apply.
                        // However, the prompt says "evaluate... ignoring typical order of operations".
                        // Let's assume valid inputs for valid syntax. If num is 0, it's a valid syntax but math error.
                        // The prompt says "The parser should reject... Word problems with invalid syntax".
                        // Division by zero is a math error, not necessarily syntax. 
                        // But if we return None for invalid syntax, what about div by 0?
                        // Let's assume the test cases don't have div by 0 or expect a specific behavior.
                        // Standard behavior for "evaluate" might be panic or error. 
                        // Let's just do the math. If num is 0, integer division in Rust panics.
                        // Let's check if num is 0.
                        if num == 0 {
                             return None; // Or panic? Let's return None to be safe as "invalid"
                        }
                    }
                    current_val /= num;
                }
                _ => return None, // Should have been caught in validation
            }
        } else {
            // Operator without following number
            return None;
        }
    }

    Some(current_val)
}
