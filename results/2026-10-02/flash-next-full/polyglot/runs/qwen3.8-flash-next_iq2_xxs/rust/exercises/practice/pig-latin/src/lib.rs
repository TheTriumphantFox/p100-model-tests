pub fn translate(input: &str) -> String {
    input
        .split_whitespace()
        .map(|word| translate_word(word))
        .collect::<Vec<String>>()
        .join(" ")
}

fn translate_word(word: &str) -> String {
    // Rule 1: Starts with vowel sound or "xr" or "yt"
    if starts_with_vowel_sound(word) {
        return format!("{}ay", word);
    }

    let chars: Vec<char> = word.chars().collect();
    if chars.is_empty() {
        return String::from(word);
    }

    // Find the split index
    let mut split_index = 0;
    let mut found_vowel = false;

    // Iterate through the word to find the first vowel sound boundary
    // We start from 0 because we need to check if the first char is part of a qu cluster or just a consonant
    for i in 0..chars.len() {
        let c = chars[i];

        // Check for "qu" rule (Rule 3)
        // If we see 'q' and next is 'u', we split after 'u'
        if c == 'q' && i + 1 < chars.len() && chars[i + 1] == 'u' {
            split_index = i + 2; // Move up to and including 'u'
            found_vowel = true;
            break;
        }

        // Check for 'y' rule (Rule 4)
        // If 'y' follows consonants, it acts as a vowel.
        // Note: if 'y' is the first char, it's a consonant sound (handled by starts_with_vowel_sound returning false for 'y' unless followed by 't')
        // Actually, if 'y' is at index 0, it's a consonant. If it's later, it's a vowel.
        // So if we encounter 'y' at index i > 0, we split at i.
        if c == 'y' && i > 0 {
            split_index = i; // Move consonants before 'y' to end. 'y' stays at start.
            found_vowel = true;
            break;
        }

        // Check for standard vowels
        if is_vowel(c) {
            split_index = i;
            found_vowel = true;
            break;
        }
    }

    if !found_vowel {
        // No vowel found? Treat whole word as consonant cluster? 
        // Or just append ay? 
        // If no vowel, it's all consonants. Move all to end? 
        // Usually words have vowels. If not, just append ay.
        return format!("{}ay", word);
    }

    // Split the word
    let prefix: String = chars[..split_index].iter().collect();
    let suffix: String = chars[split_index..].iter().collect();
    
    format!("{}{}ay", suffix, prefix)
}

fn is_vowel(c: char) -> bool {
    matches!(c.to_ascii_lowercase(), 'a' | 'e' | 'i' | 'o' | 'u')
}

fn starts_with_vowel_sound(word: &str) -> bool {
    if word.is_empty() {
        return false;
    }
    let first_char = word.chars().next().unwrap().to_ascii_lowercase();
    
    // Check simple vowels
    if is_vowel(first_char) {
        return true;
    }
    
    // Check "xr" or "yt"
    if word.len() >= 2 {
        let second_char = word.chars().nth(1).unwrap().to_ascii_lowercase();
        if first_char == 'x' && second_char == 'r' {
            return true;
        }
        if first_char == 'y' && second_char == 't' {
            return true;
        }
    }
    
    false
}
