pub fn encode(n: u64) -> String {
    if n == 0 {
        return "zero".to_string();
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

    let mut parts = Vec::new();
    let mut n = n;
    let mut scale_index = 0;

    while n > 0 {
        let chunk = n % 1000;
        if chunk > 0 {
            let chunk_str = encode_chunk(chunk);
            let scale_str = scales[scale_index];
            parts.push(format!("{}{}", chunk_str, scale_str));
        }
        n /= 1000;
        scale_index += 1;
    }

    parts.reverse();
    parts.join(" ")
}

fn encode_chunk(mut n: u64) -> String {
    let ones = [
        "",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
        "ten",
        "eleven",
        "twelve",
        "thirteen",
        "fourteen",
        "fifteen",
        "sixteen",
        "seventeen",
        "eighteen",
        "nineteen",
    ];

    let tens = [
        "",
        "",
        "twenty",
        "thirty",
        "forty",
        "fifty",
        "sixty",
        "seventy",
        "eighty",
        "ninety",
    ];

    let mut parts = Vec::new();

    if n >= 100 {
        parts.push(format!("{} hundred", ones[(n / 100) as usize]));
        n %= 100;
    }

    if n > 0 {
        if n < 20 {
            parts.push(ones[n as usize].to_string());
        } else {
            let t = n / 10;
            let o = n % 10;
            if o > 0 {
                parts.push(format!("{}-{}", tens[t as usize], ones[o as usize]));
            } else {
                parts.push(tens[t as usize].to_string());
            }
        }
    }

    parts.join(" ")
}
