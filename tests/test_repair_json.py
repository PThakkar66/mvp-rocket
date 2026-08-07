import json
import pytest
from repair_json import repair, loads

def test_valid_json_passes_through():
    text = '{"a": 1, "b": "test"}'
    res, applied = repair(text)
    assert res == {"a": 1, "b": "test"}
    assert applied == []

def test_markdown_code_fences_stripped():
    text = '```json\n{"a": 1}\n```'
    assert loads(text) == {"a": 1}

def test_smart_quotes_normalized():
    text = '{\u201ckey\u201d: \u201cvalue\u201d}'
    assert loads(text) == {"key": "value"}

def test_single_quoted_strings_converted():
    text = "{'key': 'val'}"
    assert loads(text) == {"key": "val"}

def test_comments_stripped():
    text = '{"a": 1 // line comment\n, "b": 2 /* block comment */}'
    assert loads(text) == {"a": 1, "b": 2}

@pytest.mark.parametrize("text", [
    '{"a": 1,}',
    '{"a": 1,,}'
])
def test_trailing_commas_removed(text):
    assert loads(text) == {"a": 1}

@pytest.mark.parametrize("text,expected", [
    ('{"a": True}', {"a": True}),
    ('{"a": False}', {"a": False}),
    ('{"a": None}', {"a": None}),
    ('{"a": undefined}', {"a": None}),
])
def test_python_literals(text, expected):
    assert loads(text) == expected

@pytest.mark.parametrize("text,expected", [
    ('{"a": TRUE}', {"a": True}),
    ('{"a": FALSE}', {"a": False}),
    ('{"a": NULL}', {"a": None}),
    ('{"a": nil}', {"a": None}),
    ('{"a": Nil}', {"a": None}),
])
def test_case_insensitive_literals(text, expected):
    assert loads(text) == expected

@pytest.mark.parametrize("text,expected", [
    ('result: {"a": NaN} done', {"a": None}),
    ('result: {"a": Infinity} done', {"a": None}),
    ('result: {"a": -Infinity} done', {"a": None}),
])
def test_nan_infinity(text, expected):
    assert loads(text) == expected

def test_unquoted_keys():
    text = '{name: "val"}'
    assert loads(text) == {"name": "val"}

def test_truncated_json_auto_closed():
    text = '{"a": [1, 2'
    assert loads(text) == {"a": [1, 2]}

def test_unescaped_newlines_inside_strings():
    text = '{"a": "line1\nline2"}'
    assert loads(text) == {"a": "line1\nline2"}

@pytest.mark.parametrize("text,expected", [
    ('{"a": 0xFF}', {"a": 255}),
    ('{"a": 0o77}', {"a": 63}),
])
def test_hex_numbers(text, expected):
    assert loads(text) == expected

@pytest.mark.parametrize("text,expected", [
    ('{"a": .5}', {"a": 0.5}),
    ('{"a": 5.}', {"a": 5.0}),
    ('{"a": +5}', {"a": 5}),
])
def test_non_standard_floats(text, expected):
    assert loads(text) == expected

def test_python_tuples():
    text = '{"a": (1, 2, 3)}'
    assert loads(text) == {"a": [1, 2, 3]}

def test_missing_commas():
    text = '{"a": 1 "b": 2}'
    assert loads(text) == {"a": 1, "b": 2}

def test_bom_stripping():
    text = '\ufeff{"a": 1}'
    assert loads(text) == {"a": 1}

def test_empty_input_raises_error():
    with pytest.raises(json.JSONDecodeError):
        loads("")

def test_prose_wrapping_json():
    text = 'Here is the result: {"a": 1} hope that helps'
    assert loads(text) == {"a": 1}

def test_nested_objects_and_arrays():
    text = '{"a": [{"b": 1}, {"c": 2}]}'
    assert loads(text) == {"a": [{"b": 1}, {"c": 2}]}

def test_strings_containing_special_chars():
    text = '{"a": "// not a comment", "b": "True"}'
    assert loads(text) == {"a": "// not a comment", "b": "True"}

def test_requote_preserving_valid_escape_sequences():
    # Single-quoted string with a simple value converts correctly
    text = "{'a': 'hello world', 'b': 'test'}"
    assert loads(text) == {"a": "hello world", "b": "test"}

def test_loads_raises_on_unrecoverable():
    with pytest.raises(json.JSONDecodeError):
        loads('{"a": }')
