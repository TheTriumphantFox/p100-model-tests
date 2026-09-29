"""Objective coding tasks for the local-model benchmark.

The prompts are shown to models.  Checker source is deliberately kept out of
those prompts and is executed only after a model returns a solution.
"""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Task:
    slug: str
    title: str
    prompt: str
    entrypoint: str
    checker_source: str
    test_count: int


def _function_checker(function_name: str, cases: list) -> str:
    """Create trusted checker source for ordinary function tasks."""
    return f'''\
import copy


def check(module):
    function = getattr(module, {function_name!r})
    cases = {cases!r}
    passed = 0
    failures = []
    for number, (args, kwargs, expected) in enumerate(cases, 1):
        try:
            actual = function(*copy.deepcopy(args), **copy.deepcopy(kwargs))
            if actual == expected:
                passed += 1
            elif len(failures) < 3:
                failures.append({{"case": number, "expected": repr(expected), "actual": repr(actual)}})
        except BaseException as exc:
            if len(failures) < 3:
                failures.append({{"case": number, "error": f"{{type(exc).__name__}}: {{exc}}"}})
    return {{"passed": passed, "total": len(cases), "failures": failures}}
'''


def _lru_checker() -> str:
    return r'''
def check(module):
    passed = 0
    total = 0
    failures = []

    def expect(name, actual, expected):
        nonlocal passed, total
        total += 1
        if actual == expected:
            passed += 1
        elif len(failures) < 3:
            failures.append({"case": name, "expected": repr(expected), "actual": repr(actual)})

    try:
        cache = module.LRUCache(2)
        expect("empty lookup", cache.get("missing"), -1)
        cache.put("a", 1)
        cache.put("b", 2)
        expect("first lookup", cache.get("a"), 1)
        cache.put("c", 3)
        expect("least recently used evicted", cache.get("b"), -1)
        expect("recent key retained", cache.get("c"), 3)
        cache.put("d", 4)
        expect("next least recently used evicted", cache.get("a"), -1)
        expect("d retained", cache.get("d"), 4)
        cache.put("c", 30)
        expect("update existing", cache.get("c"), 30)

        one = module.LRUCache(1)
        one.put(10, "x")
        one.put(20, "y")
        expect("capacity one", one.get(10), -1)
        expect("capacity one current", one.get(20), "y")
    except BaseException as exc:
        if len(failures) < 3:
            failures.append({"case": "construction or operation", "error": f"{type(exc).__name__}: {exc}"})

    return {"passed": passed, "total": total, "failures": failures}
'''


TASKS: List[Task] = [
    Task(
        slug="merge-intervals",
        title="Merge overlapping intervals",
        entrypoint="merge_intervals",
        prompt="""Implement `merge_intervals(intervals)`.

`intervals` is a list of two-item lists containing inclusive integer ranges.
Return a new list sorted by start value in which overlapping or touching ranges
are merged.  Do not mutate the input.  Empty input returns an empty list.
Use only the Python standard library.  Define exactly the requested function
and keep the module safe to import.""",
        checker_source=_function_checker(
            "merge_intervals",
            [
                (([[1, 3], [2, 6], [8, 10], [9, 12]],), {}, [[1, 6], [8, 12]]),
                (([[1, 4], [4, 5]],), {}, [[1, 5]]),
                (([],), {}, []),
                (([[5, 7], [1, 2], [2, 5]],), {}, [[1, 7]]),
                (([[-5, -2], [-10, -6], [-6, 0]],), {}, [[-10, 0]]),
                (([[3, 3], [1, 1], [2, 2]],), {}, [[1, 1], [2, 2], [3, 3]]),
            ],
        ),
        test_count=6,
    ),
    Task(
        slug="top-k-frequent",
        title="Top-k frequent values",
        entrypoint="top_k_frequent",
        prompt="""Implement `top_k_frequent(values, k)`.

Return the `k` most frequent integers in `values`.  Sort primarily by
frequency descending; break ties by integer value ascending.  The result must
contain each value once.  Inputs satisfy 1 <= k <= number of distinct values.
Do not mutate the input and use only the standard library.""",
        checker_source=_function_checker(
            "top_k_frequent",
            [
                (([1, 1, 1, 2, 2, 3], 2), {}, [1, 2]),
                (([4, 4, -1, -1, 2, 2, 3], 3), {}, [-1, 2, 4]),
                (([5, 4, 3, 2, 1], 3), {}, [1, 2, 3]),
                (([7, 7, 8, 8, 8, 9], 1), {}, [8]),
                (([0, 0, -2, -2, -2, 4], 2), {}, [-2, 0]),
                (([10, 10, 9, 9, 8, 8], 2), {}, [8, 9]),
            ],
        ),
        test_count=6,
    ),
    Task(
        slug="shortest-grid-path",
        title="Shortest path through a grid",
        entrypoint="shortest_grid_path",
        prompt="""Implement `shortest_grid_path(grid)`.

`grid` is a non-empty rectangular list of strings.  `S` is the start, `T` is
the target, `.` is open space, and `#` is a wall.  Return the minimum number
of four-direction moves from S to T, or -1 when T cannot be reached.  There is
exactly one S and one T.  Do not mutate the grid and use only the standard
library.""",
        checker_source=_function_checker(
            "shortest_grid_path",
            [
                ((["S..", ".#.", "..T"],), {}, 4),
                ((["S#T"],), {}, -1),
                ((["S.", ".T"],), {}, 2),
                ((["S...", "####", "...T"],), {}, -1),
                ((["S....", ".###.", "...#T"],), {}, 6),
                ((["S#.", ".#T", "..."],), {}, 5),
            ],
        ),
        test_count=6,
    ),
    Task(
        slug="flatten-dict",
        title="Flatten nested dictionaries",
        entrypoint="flatten_dict",
        prompt="""Implement `flatten_dict(data, parent_key='', sep='.')`.

Recursively flatten nested dictionaries into a new dictionary.  Join nested
keys with `sep`; preserve non-dictionary values, including lists, unchanged.
If `parent_key` is non-empty, prepend it to every emitted key.  An empty
nested dictionary emits no key.  Do not mutate `data`.  Use only the standard
library.""",
        checker_source=_function_checker(
            "flatten_dict",
            [
                (({"a": {"b": 1, "c": 2}, "d": 3},), {}, {"a.b": 1, "a.c": 2, "d": 3}),
                (({"user": {"name": "Ada", "tags": ["a", "b"]}},), {"parent_key": "record"}, {"record.user.name": "Ada", "record.user.tags": ["a", "b"]}),
                (({},), {}, {}),
                (({"a": {}, "b": {"c": {}}},), {}, {}),
                (({"x": {"y": {"z": False}}, "n": None},), {}, {"x.y.z": False, "n": None}),
                (({"a": {"b": 1}},), {"sep": "/"}, {"a/b": 1}),
            ],
        ),
        test_count=6,
    ),
    Task(
        slug="parse-duration",
        title="Parse compact durations",
        entrypoint="parse_duration",
        prompt="""Implement `parse_duration(text)`.

Parse a duration such as `2h 5m 9s` and return its total number of seconds as
an integer.  Supported units are days (`d`), hours (`h`), minutes (`m`), and
seconds (`s`), in any order, with optional whitespace between components.
Components are non-negative integers and each unit appears at most once.
Inputs in the benchmark are valid; you do not need to design an error API.
Use only the standard library.""",
        checker_source=_function_checker(
            "parse_duration",
            [
                (("2h 5m 9s",), {}, 7509),
                (("1d",), {}, 86400),
                (("  3m   4s ",), {}, 184),
                (("45s",), {}, 45),
                (("2d 1h 0m 5s",), {}, 176405),
                (("5h 2s",), {}, 18002),
            ],
        ),
        test_count=6,
    ),
    Task(
        slug="minimum-window",
        title="Minimum covering substring",
        entrypoint="minimum_window",
        prompt="""Implement `minimum_window(text, required)`.

Return the shortest contiguous substring of `text` containing every character
in `required` with at least the same multiplicity.  Matching is case-sensitive.
If several windows have the same shortest length, return the leftmost one.  If
no window exists, return the empty string.  Use only the standard library.""",
        checker_source=_function_checker(
            "minimum_window",
            [
                (("ADOBECODEBANC", "ABC"), {}, "BANC"),
                (("a", "a"), {}, "a"),
                (("a", "aa"), {}, ""),
                (("ab", "b"), {}, "b"),
                (("aaabdabcefaecbef", "abc"), {}, "abc"),
                (("xyyzyzyx", "xyz"), {}, "zyx"),
            ],
        ),
        test_count=6,
    ),
    Task(
        slug="evaluate-rpn",
        title="Evaluate reverse Polish notation",
        entrypoint="evaluate_rpn",
        prompt="""Implement `evaluate_rpn(tokens)`.

Evaluate a valid reverse-Polish expression represented by a list of tokens.
Tokens are integers or the operators `+`, `-`, `*`, `/`.  Division truncates
 toward zero (not toward negative infinity).  Return an integer.  Inputs are
valid and every intermediate result fits in ordinary Python integers.  Use
only the standard library.""",
        checker_source=_function_checker(
            "evaluate_rpn",
            [
                ((["2", "1", "+", "3", "*"],), {}, 9),
                ((["4", "13", "5", "/", "+"],), {}, 6),
                ((["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"],), {}, 22),
                ((["7", "2", "/"],), {}, 3),
                ((["-7", "2", "/"],), {}, -3),
                ((["5", "1", "2", "+", "4", "*", "+", "3", "-"],), {}, 50),
            ],
        ),
        test_count=6,
    ),
    Task(
        slug="lru-cache",
        title="Implement an LRU cache",
        entrypoint="LRUCache",
        prompt="""Implement a class named `LRUCache` with this API:

- `LRUCache(capacity)` creates a cache with a positive integer capacity.
- `get(key)` returns the stored value, or `-1` when absent.  A hit makes the
  key most recently used.
- `put(key, value)` inserts or replaces a value and makes the key most recently
  used.  When over capacity, evict the least recently used key.

Use only the standard library.  Define the requested class at module scope and
keep the module safe to import.""",
        checker_source=_lru_checker(),
        test_count=9,
    ),
]


TASK_BY_SLUG = {task.slug: task for task in TASKS}
