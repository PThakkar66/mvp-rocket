import pytest
from json_to_schema import infer, merge, finalize, emit_zod, emit_pydantic, emit_jsonschema, emit_typescript, Config

def test_infer_null():
    assert infer(None, Config()) == {"kind": "null"}

def test_infer_bool():
    assert infer(True, Config()) == {"kind": "bool"}

def test_infer_int():
    assert infer(1, Config()) == {"kind": "int"}

def test_infer_float():
    assert infer(1.5, Config()) == {"kind": "float"}

def test_infer_string():
    res = infer("hello", Config())
    assert res["kind"] == "string"

def test_infer_empty_list():
    assert infer([], Config()) == {"kind": "array", "item": None}

def test_infer_list_of_ints():
    assert infer([1, 2], Config()) == {"kind": "array", "item": {"kind": "int"}}

def test_infer_simple_object():
    res = infer({"a": 1, "b": "two"}, Config())
    assert res["kind"] == "object"
    assert "a" in res["props"]
    assert "b" in res["props"]
    assert res["required"] == {"a", "b"}

@pytest.mark.parametrize("val,fmt", [
    ("123e4567-e89b-12d3-a456-426614174000", "uuid"),
    ("test@example.com", "email"),
    ("https://example.com", "url"),
    ("2023-10-01T12:00:00Z", "datetime"),
    ("2023-10-01", "date"),
])
def test_format_detection(val, fmt):
    res = infer(val, Config())
    assert res["format"] == fmt

def test_format_detection_disabled():
    res = infer("test@example.com", Config(formats=False))
    assert res["format"] is None

def test_merging_same_type():
    a = {"kind": "int"}
    b = {"kind": "int"}
    assert merge(a, b, Config()) == {"kind": "int"}

def test_merging_int_float():
    a = {"kind": "int"}
    b = {"kind": "float"}
    assert merge(a, b, Config()) == {"kind": "float"}

def test_merging_null_string():
    a = {"kind": "null"}
    b = {"kind": "string", "format": None, "values": {"x"}}
    res = merge(a, b, Config())
    assert res["kind"] == "string"
    assert res.get("nullable") is True

def test_object_merge_required_only_if_in_both():
    a = infer({"a": 1, "b": 2}, Config())
    b = infer({"a": 3, "c": 4}, Config())
    res = merge(a, b, Config())
    assert res["required"] == {"a"}

def test_different_types_union():
    a = {"kind": "int"}
    b = {"kind": "string"}
    res = merge(a, b, Config())
    assert res["kind"] == "union"
    assert a in res["options"]
    assert b in res["options"]

def test_enum_inference():
    res = infer("val1", Config(enum_threshold=10))
    res = merge(res, infer("val2", Config(enum_threshold=10)), Config(enum_threshold=10))
    assert res["values"] == {"val1", "val2"}
    finalize(res)
    assert "values" not in res
    assert res["enum_values"] == ["val1", "val2"]

def test_enum_over_threshold():
    c = Config(enum_threshold=1)
    res = infer("val1", c)
    res = merge(res, infer("val2", c), c)
    assert res["values"] is None

def test_enum_disabled():
    res = infer("val1", Config(enum_threshold=0))
    assert "values" not in res

def test_emit_zod():
    cfg = Config()
    # Merge two samples to produce nullable and optional fields
    node1 = infer({"a": 1, "b": "str", "c": "hello"}, cfg)
    node2 = infer({"a": 2, "b": "str", "c": None}, cfg)
    node = merge(node1, node2, cfg)
    finalize(node)
    out = emit_zod(node, "MyModel", loose=False)
    assert "z.object" in out
    assert "z.number().int()" in out
    assert ".nullable()" in out

def test_emit_zod_enum():
    node = infer("val", Config())
    finalize(node)
    out = emit_zod(node, "MyEnum", loose=False)
    assert "z.literal(" in out or "z.enum([" in out

def test_emit_pydantic():
    node = infer({"class": "reserved", "myField": 1, "date_val": "2023-10-01"}, Config())
    out = emit_pydantic(node, "MyModel", loose=False)
    assert "class MyModel(BaseModel):" in out
    assert "_class: str" in out
    assert "my_field: int" in out
    assert "from datetime import date" in out

def test_emit_jsonschema():
    node = infer({"a": 1, "b": "str", "c": None}, Config())
    node = merge(node, infer({"a": 2}, Config()), Config())
    out = emit_jsonschema(node, "MyModel", loose=False)
    assert "$schema" in out
    assert '"type": "object"' in out
    assert '"properties"' in out
    assert '"required"' in out
    assert '["string", "null"]' in out or '"null"' in out

def test_emit_typescript():
    node = infer({"a": [1, 2], "b": "str"}, Config())
    out = emit_typescript(node, "MyModel", loose=False)
    assert "export interface MyModel {" in out
    assert "a: number[];" in out or "a: (number)[];" in out
    assert "b: string;" in out

def test_edge_cases_deeply_nested():
    config = Config()
    res = infer({"a": "val"}, config, depth=51)
    assert res["kind"] == "unknown"

def test_edge_cases_empty_object():
    res = infer({}, Config())
    out = emit_zod(res, "Empty", loose=False)
    assert "z.record" in out or "z.object({})" in out

def test_edge_cases_primitive_top_level():
    res = infer("hello", Config())
    out = emit_typescript(res, "Root", loose=False)
    assert "export type Root = string;" in out or "export type Root = \"hello\";" in out

def test_max_array_samples():
    res = infer([1, 2, 3, 4, 5], Config(max_samples=2))
    assert res["kind"] == "array"
    assert res["item"]["kind"] == "int"
