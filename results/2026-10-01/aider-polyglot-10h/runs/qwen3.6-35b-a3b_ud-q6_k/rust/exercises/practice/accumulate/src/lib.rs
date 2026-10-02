pub fn accumulate<T, U>(input: Vec<T>, operation: impl FnMut(T) -> U) -> Vec<U> {
    let mut output = Vec::with_capacity(input.len());
    let mut operation = operation;
    for item in input {
        output.push(operation(item));
    }
    output
}
