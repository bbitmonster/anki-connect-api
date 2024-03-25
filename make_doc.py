import ast
import textwrap
from pathlib import Path
import ast_comments

source_path = Path("anki_connect.py")
dest_path = Path("anki_connect.python.md")
code_header = """\
<details>
<summary><i>Example:</i></summary>

```python"""
code_footer = """\
```
</details>
"""
def show_info(functionNode):
    docstring = ast.get_docstring(functionNode)
    if not docstring:
        return ""
    func = functionNode.name
    args = ", ".join(arg.arg for arg in functionNode.args.args)
    writeln()
    writeln(f"# `{func}({args})`\n")
    docstring = docstring.replace("Example::", code_header)
    docstring = textwrap.indent(docstring, "    ")
    docstring = "*" + docstring[1:]
    writeln(docstring)
    writeln(textwrap.indent(code_footer, "    ")
)

def writeln(s=""):
    f.write(s + "\n")

with source_path.open('r', encoding="utf-8") as f:
    tree = ast_comments.parse(f.read())

with Path("anki_connect.header.md").open('r', encoding="utf-8") as f:
    header = f.read()

with dest_path.open("w", encoding="utf-8") as f:
    f.write(header)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            show_info(node)
        elif isinstance(node, ast_comments.Comment):
            writeln("##" + node.value)

