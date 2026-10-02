pub fn encode(n: u64) -> String {
    if n == 0 {
        return "zero".to_string();
    }

    let small_numbers = [
        "", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
        "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
        "eighteen", "nineteen",
    ];

    let tens = [
        "", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety",
    ];

    let scales = ["", " thousand", " million", " billion", " trillion", " quadrillion", " quintillion"];

    fn encode_chunk(n: u64, small_numbers: &[&str], tens: &[&str]) -> String {
        let mut parts = Vec::new();
        if n >= 100 {
            parts.push(small_numbers[(n / 100) as usize]);
            parts.push(" hundred");
        }
        let remainder = n % 100;
        if remainder >= 20 {
            parts.push(tens[(remainder / 10) as usize]);
            if remainder % 10 > 0 {
                parts.push("-");
                parts.push(&small_numbers[(remainder % 10) as usize]);
            }
        } else if remainder > 0 {
            parts.push(small_numbers[remainder as usize]);
        }
        parts.join("")
    }

    let mut parts = Vec::new();
    let mut scale_idx = 0;
    let mut remaining = n;

    while remaining > 0 {
        let chunk = remaining % 1000;
        remaining /= 1000;

        if chunk > 0 {
            let chunk_str = encode_chunk(chunk, &small_numbers, &tens);
            let scale = scales[scale_idx];
            parts.push(format!("{}{}", chunk_str, scale));
        }
        scale_idx += 1;
    }

    parts.reverse();
    parts.join(" ")
}
