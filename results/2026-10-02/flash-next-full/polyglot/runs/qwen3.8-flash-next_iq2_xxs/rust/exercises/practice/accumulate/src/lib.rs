/// What should the type of _function be?
pub fn map<F, T, U>(input: Vec<T>, _function: F) -> Vec<U>
where
    F: Fn(T) -> U,
{
    let mut result = Vec::new();
    for item in input {
        result.push(_function(item));
    }
    result
}
