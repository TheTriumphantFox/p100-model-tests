pub fn map<T, U, F>(input: Vec<T>, function: F) -> Vec<U>
where
    F: Fn(T) -> U,
{
    let mut result = Vec::with_capacity(input.len());
    for item in input {
        result.push(function(item));
    }
    result
}
