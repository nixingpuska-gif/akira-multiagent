import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main():
    from core.tools.creator import ToolCreator
    from core.tools.library import ToolLibrary, ToolSpec
    from core.tools.validator import ToolValidator

    td = tempfile.mkdtemp(prefix="akira_tools_")
    creator = ToolCreator()
    validator = ToolValidator()

    spec = ToolSpec(
        name="my_tool",
        description="Do something simple.",
        args_schema={"arg1": {"type": "string"}},
        code="print('ok')\n",
        tags=["demo"],
    )
    assert validator.is_valid(spec)

    bad_name = ToolSpec(
        name="bad tool",
        description="x",
        args_schema={},
        code="print('x')",
    )
    assert not validator.is_valid(bad_name)

    no_schema = ToolSpec(
        name="noschema",
        description="x",
        args_schema=None,
        code="print('x')",
    )
    assert not validator.is_valid(no_schema)

    empty_code = ToolSpec(
        name="emptycode",
        description="x",
        args_schema={},
        code="",
    )
    assert not validator.is_valid(empty_code)

    stub_spec = creator.build_spec(
        name="demo_tool",
        description="Demo tool.",
        args_schema={"a": {"type": "int"}},
        tags=["demo"],
    )
    stub = creator.create_stub(stub_spec)
    stub.encode("ascii")
    assert "def demo_tool" in stub
    assert "NotImplementedError" in stub

    lib = ToolLibrary(td)
    spec.code = stub
    lib.add(spec)
    names = lib.list_names()
    assert "my_tool" in names
    loaded = lib.get("my_tool")
    assert loaded is not None
    assert loaded.name == "my_tool"
    assert loaded.args_schema.get("arg1")


if __name__ == "__main__":
    main()
