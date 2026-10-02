//
// This is only a SKELETON file for the 'Pig Latin' exercise. It's been provided as a
// convenience to get you started writing code faster.
//

export const translate = (text) => {
  return text.split(' ').map(word => {
    // Rule 1: Starts with vowel sound (vowel, xr, yt)
    if (/^([aeiou]|xr|yt)/.test(word)) {
      return word + 'ay';
    }

    // Rule 3: Starts with consonants followed by 'qu'
    // This needs to be checked before Rule 2 because 'qu' acts as a unit.
    // The regex matches any leading consonants (including none) followed by 'qu'.
    const quMatch = word.match(/^([^aeiou]*qu)(.*)/);
    if (quMatch) {
      return quMatch[2] + quMatch[1] + 'ay';
    }

    // Rule 4: Starts with consonants followed by 'y'
    // 'y' acts as a vowel here if it's not the first letter.
    // The regex matches leading consonants (excluding y) followed by y.
    const yMatch = word.match(/^([^aeiouy]+)(y.*)/);
    if (yMatch) {
      return yMatch[2] + yMatch[1] + 'ay';
    }

    // Rule 2: Starts with one or more consonants
    const consonantMatch = word.match(/^([^aeiou]+)(.*)/);
    if (consonantMatch) {
      return consonantMatch[2] + consonantMatch[1] + 'ay';
    }

    // Fallback (should technically be covered by Rule 1 if it starts with a vowel)
    return word + 'ay';
  }).join(' ');
};
