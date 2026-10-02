use std::str::SplitWhitespace;

pub fn answer(command: &str) -> Option<i32> {
    // Split the command into words
    let mut words: Vec<&str> = command.split_whitespace().collect();

    // Check if we have at least "What is X?" format
    if words.len() < 3 || words[0] != "What" || words[1] != "is" {
        return None;
    }

    // Parse the first number
    let mut current = parse_number(words[2])?;

    // Process operations (starting from index 3)
    let mut i = 3;
    while i < words.len() - 1 {
        let op = words[i];
        let next_num = parse_number(words[i + 1])?;

        current = match op {
            "plus" => current + next_num,
            "minus" => current - next_num,
            "multiplied" => current * next_num,
            "divided" => current / next_num,
            _ => return None, // Unsupported operation
        };

        i += 2;
    }

    Some(current)
}

fn parse_number(word: &str) -> Option<i32> {
    word.parse().ok()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_numbers() {
        assert_eq!(answer("What is 5?"), Some(5));
        assert_eq!(answer("What is 0?"), Some(0));
        assert_eq!(answer("What is -3?"), Some(-3));
    }

    #[test]
    fn test_addition() {
        assert_eq!(answer("What is 5 plus 13?"), Some(18));
        assert_eq!(answer("What is -1 plus 1?"), Some(0));
        assert_eq!(answer("What is 100 plus 200?"), Some(300));
    }

    #[test]
    fn test_subtraction() {
        assert_eq!(answer("What is 7 minus 5?"), Some(2));
        assert_eq!(answer("What is 10 minus -5?"), Some(15));
    }

    #[test]
    fn test_multiplication() {
        assert_eq!(answer("What is 6 multiplied by 4?"), Some(24));
        assert_eq!(answer("What is -3 multiplied by 2?"), Some(-6));
    }

    #[test]
    fn test_division() {
        assert_eq!(answer("What is 25 divided by 5?"), Some(5));
        assert_eq!(answer("What is 10 divided by 2?"), Some(5));
    }

    #[test]
    fn test_multiple_operations() {
        assert_eq!(answer("What is 5 plus 13 plus 6?"), Some(24));
        assert_eq!(answer("What is 3 plus 2 multiplied by 3?"), Some(15));
        assert_eq!(answer("What is 10 minus 5 minus 2?"), Some(3));
    }

    #[test]
    fn test_errors() {
        assert_eq!(answer("What is 52 cubed?"), None);
        assert_eq!(answer("Who is the President of the United States"), None);
        assert_eq!(answer("What is 1 plus plus 2?"), None);
        assert_eq!(answer("What is plus 5?"), None);
    }
}
