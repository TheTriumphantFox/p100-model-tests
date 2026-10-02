pub fn encode(n: u64) -> String {
    if n == 0 {
        return "zero".to_string();
    }

    let units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
        "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen",
        "eighteen", "nineteen",
    ];
    let tens = [
        "", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety",
    ];

    fn encode_chunk(n: u64, units: &[&str], tens: &[&str]) -> String {
        if n == 0 {
            return String::new();
        }
        let mut parts = Vec::new();
        let hundreds = n / 100;
        let remainder = n % 100;

        if hundreds > 0 {
            parts.push(units[hundreds as usize]);
            parts.push("hundred");
        }

        if remainder > 0 {
            if remainder < 20 {
                parts.push(units[remainder as usize]);
            } else {
                let ten = remainder / 10;
                let unit = remainder % 10;
                if unit > 0 {
                    parts.push(&format!("{}-{}", tens[ten as usize], units[unit as usize]));
                } else {
                    parts.push(tens[ten as usize]);
                }
            }
        }

        parts.join(" ")
    }

    let scales = [
        "",
        " thousand",
        " million",
        " billion",
        " trillion",
        " quadrillion",
        " quintillion",
    ];
    let mut result = String::new();
    let mut current_n = n;
    let mut scale_index = 0;

    while current_n > 0 {
        let chunk = current_n % 1000;
        if chunk > 0 {
            let chunk_str = encode_chunk(chunk, &units, &tens);
            let scale_str = scales[scale_index];
            if !result.is_empty() {
                result = format!("{}{} {}", chunk_str, scale_str, result);
            } else {
                result = format!("{}{}", chunk_str, scale_str);
            }
        }
        current_n /= 1000;
        scale_index += 1;
    }

    result.trim().to_string()
}
