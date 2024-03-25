import ast
import textwrap
from pathlib import Path
import ast_comments

source_path = Path("anki_connect.py")
dest_path = Path("anki_connect.python.md")
code_header = """\
<details>
<summary><i>Example:</i></summary>

```py"""
code_footer = """\
```
</details>
"""
def show_info(functionNode):
    docstring = ast.get_docstring(functionNode)
    if not docstring:
        return
    func = functionNode.name
    args = ", ".join(arg.arg for arg in functionNode.args.args)
    writeln()
    writeln(f"`{func}({args})`\n")
    #docstring = textwrap.indent(docstring, "    ")
    #docstring = "*" + docstring[1:]
    docstring = docstring.replace("Example::", code_header)
    writeln(docstring)
    writeln(code_footer)

def writeln(s=""):
    f.write(s + "\n")

with source_path.open('r', encoding="utf-8") as f:
    tree = ast_comments.parse(f.read())
docstring = ast.get_docstring(tree)

with dest_path.open("w", encoding="utf-8") as f:
    #writeln(docstring)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            show_info(node)
        elif isinstance(node, ast_comments.Comment):
            writeln("##" + node.value)

from github import Github, Auth

# using an access token
auth = Auth.Token("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")

# First create a Github instance:

# Public Web Github
g = Github(auth=auth)

# Find your repository and path of README.md
repo = g.get_user().get_repo("misc")
file = repo.get_contents("anki/anki_connect.python.md")

# content = file.decoded_content.decode()
# for line in content.splitlines():
#     print(line)

# The new contents of your README.md
with dest_path.open("r", encoding="utf-8") as f:
    content = f.read()
repo.update_file(file.path, "more tests", content, file.sha)

g.close()