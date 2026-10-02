pub fn translate(input: &str) -> String {
    input
        .split_whitespace()
        .map(|word| {
            let chars: Vec<char> = word.chars().collect();
            if chars.is_empty() {
                return String::new();
            }

            // Rule 1: Starts with vowel sound
            // Vowels: a, e, i, o, u
            // Special cases: xr, yt
            if is_vowel_sound(&chars) {
                return format!("{}ay", word);
            }

            // Find the split point for consonant cluster
            // Rule 3: qu
            // Rule 4: y acting as vowel
            // Rule 2: standard consonants
            
            let mut split_index = 0;
            while split_index < chars.len() {
                let c = chars[split_index];
                if is_vowel(c) {
                    // Rule 3: if 'u' follows 'q', it's part of the consonant cluster
                    if c == 'u' && split_index > 0 && chars[split_index - 1] == 'q' {
                        split_index += 1;
                        continue;
                    }
                    break;
                }
                
                // Rule 4: 'y' acts as a vowel if it's not the first letter
                if c == 'y' && split_index > 0 {
                    break;
                }
                
                split_index += 1;
            }

            let prefix: String = chars[..split_index].iter().collect();
            let suffix: String = chars[split_index..].iter().collect();
            format!("{}{}ay", suffix, prefix)
        })
        .collect::<Vec<String>>()
        .join(" ")
}

fn is_vowel(c: char) -> bool {
    matches!(c, 'a' | 'e' | 'i' | 'o' | 'u')
}

fn is_vowel_sound(chars: &[char]) -> bool {
    if chars.is_empty() {
        return false;
    }
    
    // Check for standard vowel start
    if is_vowel(chars[0]) {
        return true;
    }
    
    // Check for xr or yt start
    if chars.len() >= 2 {
        let start: String = chars[..2].iter().collect();
        if start == "xr" || start == "yt" {
            return true;
        }
    }
    
    false
}
