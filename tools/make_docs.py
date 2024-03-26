import ast
import json
from textwrap import indent, dedent
from pathlib import Path

import ast_comments
import jsbeautifier

opts = jsbeautifier.default_options()
opts.indent_size = 4

HEADER = """
<!-- This file is auto-generated from <anki_connect.py>, do not edit it by hand. -->

"""

CODE_TEMPLATE = """\
<details>
<summary><i>{desc}:</i></summary>

```{lang}
{code}
```
</details>

"""

def return_args(*args):
    return args

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
    desc, example = docstring.split("Example::")
    desc = desc.replace("`None`", "`null`")
    desc = desc.replace("`True`", "`true`")
    desc = desc.replace("`False`", "`false`")
    desc = indent(desc, "    ")
    desc = "*" + desc[1:]

    lines = example.splitlines()
    request_str = ""
    for i, line in enumerate(lines):
        if line.strip() == "":
            continue
        if not (line.startswith("    >>> ") or line.startswith("    ... ")):
            break
        request_str += line[8:] + "\n"
    result_str = "".join(line + "\n" for line in lines[i:])
    result_values = eval(result_str)

    request = {"action": func_name, "version": 6}
    result = {"result": result_values, "error": None}
    if len(args):
        request_str = request_str.replace(func_name, "return_args", 1)
        request_values = eval(request_str, {"return_args": return_args})
        request["params"] = {
            k: request_values[i] 
            for i, k in enumerate(args) if i < len(request_values)
        }
    request_json = jsbeautifier.beautify(json.dumps(request), opts)
    result_json = jsbeautifier.beautify(json.dumps(result), opts)

    fout.write(f"#### `{func_name}`\n\n")
    fout.write(desc)
    s = CODE_TEMPLATE.format(desc="Sample request", lang="json", code=request_json)
    s += CODE_TEMPLATE.format(desc="Sample result", lang="json", code=result_json)
    fout.write(indent(s, "    "))


script_dir = Path(__file__).absolute().parent

with open(script_dir.parent / "anki_connect.py", 'r', encoding="utf-8") as file:
    tree = ast_comments.parse(file.read())

with open(script_dir / "anki_connect.header.md", 'r', encoding="utf-8") as file:
    header = file.read()

jobs = (
    (script_dir.parent / "docs" / "anki_connect.python.md", write_python_func),
    (script_dir.parent / "docs" / "anki_connect.json.md", write_json_func),
    
)
for filename, write_func in jobs:
    with open(filename, "w", encoding="utf-8") as fout:
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
                fout.write("##" + node.value + "\n\n")

