pub fn translate(input: &str) -> String {
    input
        .split_whitespace()
        .map(translate_word)
        .collect::<Vec<String>>()
        .join(" ")
}

fn is_vowel(c: char) -> bool {
    matches!(c, 'a' | 'e' | 'i' | 'o' | 'u')
}

fn translate_word(word: &str) -> String {
    let chars: Vec<char> = word.chars().collect();
    let len = chars.len();

    if len == 0 {
        return String::new();
    }

    // Rule 1: Starts with a vowel, "xr", or "yt"
    if is_vowel(chars[0]) || word.starts_with("xr") || word.starts_with("yt") {
        return format!("{}ay", word);
    }

    // Find the split point
    // We look for the first vowel, or 'y' (if not at start), or "qu"
    let mut split_index = 0;
    let mut found_qu = false;
    
    for i in 0..len {
        let c = chars[i];
        
        // Check for "qu"
        if c == 'q' && i + 1 < len && chars[i + 1] == 'u' {
            // Move up to and including "qu"
            split_index = i + 2;
            found_qu = true;
            break;
        }
        
        // Check for vowel
        if is_vowel(c) {
            split_index = i;
            break;
        }
        
        // Check for 'y' (Rule 4: consonants followed by 'y')
        // 'y' is treated as a vowel if it's not the first character
        if c == 'y' && i > 0 {
            split_index = i;
            break;
        }
        
        // If we reach the end without finding a vowel, 'y', or 'qu',
        // the whole word is consonants (unlikely in English but safe)
        if i == len - 1 {
            split_index = len;
        }
    }
    
    // If we found "qu", we already set split_index to include it.
    // Otherwise, split_index points to the first vowel or 'y'.
    
    let prefix: String = chars[..split_index].iter().collect();
    let suffix: String = chars[split_index..].iter().collect();
    
    format!("{}{}ay", suffix, prefix)
}
