import ast
import json
from textwrap import indent, dedent
from pathlib import Path

import ast_comments
import jsbeautifier
import markdown_parser

opts = jsbeautifier.default_options()
opts.indent_size = 4
opts.wrap_line_length = 100

HEADER = """
<!-- This file is auto-generated from <anki_connect_api.py>, do not edit it by hand. -->

"""

CODE_TEMPLATE = """\
<details>
<summary><i>{desc}:</i></summary>

```{lang}
{code}
```
</details>

"""


def return_args(*args, **kwargs):
    return (args, kwargs)


def write_python_func(fout, func_name, args, docstring):
    args = ", ".join(args)
    desc, example = docstring.split("Example::")
    desc = indent(desc, "    ")
    desc = "*" + desc[1:]
    example = dedent(example).strip()
    fout.write(f"#### `{func_name}({args})`\n")
    fout.write(desc)
    s = CODE_TEMPLATE.format(desc="Example", lang="python", code=example)
    fout.write(indent(s, "    "))


def write_json_func(fout, func_name, args, docstring):
    desc, example = docstring.split("Example::\n")
    desc = desc.replace("`None`", "`null`")
    desc = desc.replace("`True`", "`true`")
    desc = desc.replace("`False`", "`false`")
    desc = indent(desc, "    ")
    desc = "*" + desc[1:]

    request_str = ""
    result_str = ""
    for line in example.rstrip().splitlines():
        if line.strip() == "":
            break
        if line.startswith("    >>> ") or line.startswith("    ... "):
            request_str += line[8:] + "\n"
        else:
            result_str += line[4:] + "\n"

    if result_str:
        result_values = eval(result_str)
    else:
        result_values = None

    request = {"action": func_name, "version": 6}
    result = {"result": result_values, "error": None}
    if len(args):
        request_str = request_str.replace(func_name, "return_args", 1)
        request_args, request_kwargs = eval(request_str, {"return_args": return_args})
        request["params"] = {
            k: request_args[i] for i, k in enumerate(args) if i < len(request_args)
        }
        for k, v in request_kwargs.items():
            request["params"][k] = v

    request_json = jsbeautifier.beautify(json.dumps(request), opts)
    result_json = jsbeautifier.beautify(json.dumps(result), opts)

    # request_json = json.dumps(request, indent=4)
    # result_json = json.dumps(result, indent=4)

    fout.write(f"#### `{func_name}`\n\n")
    fout.write(desc)
    s = CODE_TEMPLATE.format(desc="Sample request", lang="json", code=request_json)
    s += CODE_TEMPLATE.format(desc="Sample result", lang="json", code=result_json)
    fout.write(indent(s, "    "))


script_dir = Path(__file__).absolute().parent

with open(script_dir.parent / "anki_connect_api.py", 'r') as file:
    tree = ast_comments.parse(file.read())


jobs = (
    (
        script_dir.parent / "docs" / "anki_connect.python.md",
        script_dir / "header.python.md",
        write_python_func
    ), (
        script_dir.parent / "docs" / "anki_connect.json.md",
        script_dir / "header.json.md",
        write_json_func
    ),

)

for out_filepath, header_filepath, write_func in jobs:
    with out_filepath.open("w") as fout:
        with header_filepath.open('r') as file:
            header = file.read()
        fout.write(HEADER)
        fout.write(header)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                if not docstring:
                    continue
                func_name = node.name
                args = [arg.arg for arg in node.args.args]
                write_func(fout, func_name, args, docstring)
            elif isinstance(node, ast_comments.Comment):
                fout.write("---\n\n##" + node.value + "\n\n")
    with out_filepath.open("r") as file:
        unformatted = file.read()
    formatted = markdown_parser.beautify(unformatted)
    with out_filepath.open("w") as file:
        file.write(formatted)

with open(script_dir / "original.README.md", 'r') as file:
    unformatted = file.read()
formatted = markdown_parser.beautify(unformatted)
with open(script_dir / "formatted.README.md", 'w') as file:
    file.write(formatted)
