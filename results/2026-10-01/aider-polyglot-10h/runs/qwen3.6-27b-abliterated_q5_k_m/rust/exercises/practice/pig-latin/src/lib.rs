pub fn translate(input: &str) -> String {
    input
        .split_whitespace()
        .map(translate_word)
        .collect::<Vec<_>>()
        .join(" ")
}

fn translate_word(word: &str) -> String {
    let chars: Vec<char> = word.chars().collect();
    let len = chars.len();

    // Rule 1: Starts with vowel sound
    // Vowels: a, e, i, o, u
    // Special starts: xr, yt
    if is_vowel(chars[0]) || word.starts_with("xr") || word.starts_with("yt") {
        return format!("{}ay", word);
    }

    // Find the split point for consonant cluster
    // We need to handle 'qu' as a unit (Rule 3) and 'y' as a vowel after consonants (Rule 4)
    
    let mut i = 0;
    while i < len {
        let c = chars[i];
        
        // If we hit a vowel, the consonant cluster ends before this index
        if is_vowel(c) {
            break;
        }
        
        // Rule 4: 'y' acts as a vowel if it's not the first letter
        if c == 'y' && i > 0 {
            break;
        }
        
        // Rule 3: 'qu' acts as a consonant unit. 
        // If we see 'q' followed by 'u', we include both in the consonant cluster.
        if c == 'q' && i + 1 < len && chars[i + 1] == 'u' {
            i += 2;
            continue;
        }
        
        i += 1;
    }
    
    // i is now the index where the vowel sound starts (or end of string)
    // The consonant cluster is word[..i]
    // The rest is word[i..]
    
    let prefix: String = chars[..i].iter().collect();
    let suffix: String = chars[i..].iter().collect();
    
    format!("{}{}ay", suffix, prefix)
}

fn is_vowel(c: char) -> bool {
    matches!(c, 'a' | 'e' | 'i' | 'o' | 'u')
}
