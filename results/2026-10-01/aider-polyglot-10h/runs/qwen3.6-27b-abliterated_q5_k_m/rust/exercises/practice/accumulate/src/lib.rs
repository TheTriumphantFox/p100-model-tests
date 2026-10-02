/// What should the type of _function be?
pub fn map<T, U, F>(input: Vec<T>, _function: F) -> Vec<U>
where
    F: FnMut(T) -> U,
{
    let mut result = Vec::with_capacity(input.len());
    let mut func = _function;
    for item in input {
        result.push(func(item));
    }
    result
}
