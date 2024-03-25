import ast
import json
import textwrap
from pathlib import Path
import ast_comments

import jsbeautifier

opts = jsbeautifier.default_options()
opts.indent_size = 4

python_code_header = """\
<details>
<summary><i>Example:</i></summary>

```python"""
python_code_footer = """
    ```
    </details>

"""
json_code_header = """\
    <details>
    <summary><i>Sample request:</i></summary>

    ```json
"""
json_code_footer = """
    ```
    </details>

"""

json_result_header = """\
    <details>
    <summary><i>Sample result:</i></summary>

    ```json
"""
json_result_footer = """
    ```
    </details>

"""

def return_args(*args):
    return args

def write_python_func(functionNode):
    docstring = ast.get_docstring(functionNode)
    if not docstring:
        return ""
    func = functionNode.name
    args = ", ".join(arg.arg for arg in functionNode.args.args)
    fp.write(f"##### `{func}({args})`\n\n")
    docstring = docstring.replace("Example::", python_code_header)
    docstring = textwrap.indent(docstring, "    ")
    docstring = "*" + docstring[1:]
    fp.write(docstring)
    fp.write(python_code_footer)

def write_json_func(functionNode):
    docstring = ast.get_docstring(functionNode)
    if not docstring:
        return ""
    func = functionNode.name
    description, example = docstring.split("Example::")
    description = textwrap.indent(description, "    ")
    description = "*" + description[1:]

    arg_names = [arg.arg for arg in functionNode.args.args]
    lines = example.splitlines()
    call_str = ""
    for i, line in enumerate(lines):
        if line.strip() == "":
            continue
        if not (line.startswith("    >>> ") or line.startswith("    ... ")):
            break
        call_str += line[8:] + "\n"
    result_str = ""
    for line in lines[i:]:
        result_str += line + "\n"
    result = eval(result_str)
    call_dict = {
        "action": func,
        "version": 6,
    }
    if len(arg_names):
        call_str = call_str.replace(func, "return_args", 1)
        args = eval(call_str, {"return_args": return_args})
        try:
            call_dict["params"] = {k: args[i] for i, k in enumerate(arg_names) if i < len(args)}
        except:
            print(func)
            print(arg_names)
            print(args)
            raise
    json_args_str = jsbeautifier.beautify(json.dumps(call_dict), opts)

    result_dict = {
        "result": result,
        "error": None
    }
    json_result_str = jsbeautifier.beautify(json.dumps(result_dict), opts)

    fj.write(f"##### `{func}`\n\n")
    fj.write(description)
    fj.write(json_code_header)
    fj.write(textwrap.indent(json_args_str, "    "))
    fj.write(json_code_footer)
    fj.write(json_result_header)
    fj.write(textwrap.indent(json_result_str, "    "))
    fj.write(json_result_footer)

with Path("anki_connect.py").open('r', encoding="utf-8") as file:
    tree = ast_comments.parse(file.read())

with Path("anki_connect.header.md").open('r', encoding="utf-8") as file:
    header = file.read()

with (
    Path("anki_connect.python.md").open("w", encoding="utf-8") as fp,
    Path("anki_connect.json.md").open("w", encoding="utf-8") as fj,
    ):
    fp.write(header)
    fj.write(header)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            write_python_func(node)
            write_json_func(node)
        elif isinstance(node, ast_comments.Comment):
            fp.write("##" + node.value + "\n\n")
            fj.write("##" + node.value + "\n\n")

