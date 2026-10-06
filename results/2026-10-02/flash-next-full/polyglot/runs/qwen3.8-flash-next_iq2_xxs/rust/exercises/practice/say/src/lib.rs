pub fn encode(n: u64) -> String {
    if n == 0 {
        return "zero".to_string();
    }

    let scales = [
        "", "thousand", "million", "billion", "trillion", "quadrillion", "quintillion",
    ];

    let mut parts: Vec<String> = Vec::new();
    let mut remaining = n;
    let mut scale_index = 0;

    while remaining > 0 {
        let chunk = remaining % 1000;
        remaining /= 1000;

        if chunk != 0 {
            let chunk_str = encode_chunk(chunk);
            let scale_str = scales[scale_index];
            if scale_str.is_empty() {
                parts.push(chunk_str);
            } else {
                parts.push(format!("{} {}", chunk_str, scale_str));
            }
        }
        scale_index += 1;
    }

    parts.reverse();
    parts.join(" ")
}

fn encode_chunk(n: u64) -> String {
    let units = [
        "", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
        "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
        "eighteen", "nineteen",
    ];
    let tens = [
        "", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety",
    ];

    let mut parts: Vec<String> = Vec::new();

    let hundreds = n / 100;
    let remainder = n % 100;

    if hundreds > 0 {
        parts.push(format!("{} hundred", units[hundreds as usize]));
    }

    if remainder > 0 {
        if remainder < 20 {
            parts.push(units[remainder as usize].to_string());
        } else {
            let ten = tens[(remainder / 10) as usize];
            let unit = units[(remainder % 10) as usize];
            if unit.is_empty() {
                parts.push(ten.to_string());
            } else {
                parts.push(format!("{}-{}", ten, unit));
            }
        }
    }

    parts.join(" ")
}
