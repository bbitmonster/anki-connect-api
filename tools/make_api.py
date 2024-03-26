import re
import textwrap
import json
from pathlib import Path

import black
import mistletoe
from mistletoe.span_token import InlineCode, RawText, Link, LineBreak, Emphasis, Strong
from mistletoe.block_token import Quote, ThematicBreak, Heading, Paragraph, CodeFence
from mistletoe.block_token import HtmlBlock, List, ListItem, Document
from mistletoe.markdown_renderer import BlankLine, MarkdownRenderer

REQUEST_SEARCH = re.compile("^<summary><i>Sample.* request.*</i></summary>")
RESULT_SEARCH = re.compile("^<summary><i>Sample.* result.*</i></summary>")

HEADER = '''\
__version__ = '24.2.26.0'

import json
from urllib.request import urlopen, Request


def invoke(action, **params):
    requestJson = json.dumps({
        'action': action, 
        'params': params, 
        'version': 6
    }).encode('utf-8')
    response = json.load(urlopen(Request('http://127.0.0.1:8765', requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']

'''

CODE_TEMPLATE = '''\
{func_def}
{doc}
    
    Example::
{example}
{example_return_value}
    """
{code}

'''
replace_data = {
    "storeMediaFile": (
        "def storeMediaFile(filename: str, *, data=None, path: str=None, url=None, deleteExisting: bool=True) -> str:",
    """\
    if data is not None:
        return invoke("storeMediaFile", filename=filename, data=data, deleteExisting=deleteExisting)
    elif path is not None:
        return invoke("storeMediaFile", filename=filename, path=str(path), deleteExisting=deleteExisting)
    elif url is not None:
        return invoke("storeMediaFile", filename=filename, url=url, deleteExisting=deleteExisting)
    else:
        raise Exception("one argument of data, path or url must be supplied")"""
    ),
    "getIntervals": (
        "def getIntervals(cards: list, complete: bool=False) -> list:",
        '    return invoke("getIntervals", cards=cards, complete=complete)'
    )
}


def traverse(t, level=0):
    """Recursively traverses a mistletoe AST and returns the content as Markdown. Used here as 
    a kind of beautifier for the Markdown text."""
    match t:
        case RawText():
            return t.content
        case BlankLine():
            return "\n"
        case LineBreak():
            return " "
            #return "\n"
        case ThematicBreak():
            return "---\n"
    sub = "".join(traverse(child, level+1) for child in t.children)
    match t:
        case Heading():
            return f"{t.level*"#"} {sub}\n"
        case Link():
            return f"[{sub}]({t.target})"
        case Emphasis():
            return t.delimiter + sub + t.delimiter
        case Strong():
            return 2 * t.delimiter + sub + 2 * t.delimiter
        case List():
            return sub
        case ListItem():
            first_indent = (
                " " * t.indentation
                + t.leader 
                + (t.prepend - len(t.leader) - t.indentation) * " "
            )
            next_indent = " " * len(first_indent)
            lines = sub.splitlines()
            res = first_indent + lines[0] + "\n"
            for line in lines[1:]:
                if line.strip() == "":
                    res += "\n"
                else:
                    res += next_indent + line + "\n"
            return res
        case Paragraph():
            return sub + "\n"
        case HtmlBlock():
            return sub + "\n"
        case CodeFence():
            return f"```{t.language}\n{sub}```\n"
        case Document():
            return sub
        case InlineCode():
            return t.delimiter + sub + t.delimiter
        case Quote():
            s = ""
            for line in sub.splitlines():
                s += f"> {line}\n"
            return s
        case _:
            print(str(type(t)))
            return ""
        

def split_to_chunks(lines_gen, func_name):
    """Simple state machine to split the text into the docstring, sample request and sample
    result parts."""

    state = 0
    doc = ""
    request = ""
    result = ""
    requests = []
    results = []
    for line in lines_gen:
        s = line.strip()
        match state:
            case 0:
                if s == "<details>":
                    state = 1
                else:
                    doc += line
            case 1:
                if re.search(REQUEST_SEARCH, s):
                    state = 2
            case 2:
                if s == "```json":
                    state = 3
            case 3:
                if s == "```":
                    requests.append(request)
                    request = ""
                    state = 4
                else:
                    request += line
            case 4:
                if re.search(RESULT_SEARCH, s):
                    state = 5
            case 5:
                if s == "```json":
                    state = 6
            case 6:
                if s == "```":
                    results.append(result)
                    result = ""
                    state = 7
                else:
                    result += line
            case 7:
                if re.search(REQUEST_SEARCH, s):
                    state = 2
                elif re.search(RESULT_SEARCH, s):
                    state = 5
                # wait for start of next function definition
                elif line.strip().startswith("###"):
                    # send the line back to the generator, so the caller can take care of it
                    lines_gen.send(line) 
                    # we are done with this block
                    break
    return doc, requests, results


def make_func(func_name, doc, requests, results):
    if len(requests) > 1:
        print(func_name, len(requests), "requests")
    if len(results) > 1:
        print(func_name, len(results), "results")

    with MarkdownRenderer():
        doc = traverse(mistletoe.Document(doc))
    doc = " " + doc.strip()[1:] # remove the list asterisk
    doc = doc.replace("`null`", "`None`")
    doc = doc.replace("`true`", "`True`")
    doc = doc.replace("`false`", "`False`")
    doc = textwrap.dedent(doc)

    request = requests[0]
    # process sample request 
    data = json.loads(request)
    invoke_args = [f'"{func_name}"']
    example_args = ""
    func_args = []
    if "params" in data:
        for arg, value in data["params"].items():
            invoke_args.append(f"{arg}={arg}")
            func_args.append(f"{arg}: {type(value).__name__}")
        example_args = ", ".join((f"{v!r}" for k,v in data["params"].items()))
    invoke_args_str = ", ".join(invoke_args)
    func_args_str = ", ".join(func_args)

    result = results[0]
    # process sample result
    data = json.loads(result)
    if data["result"] is None:
        return_type = "None"
    else:
        return_type = type(data["result"]).__name__

    func_def = f"def {func_name}({func_args_str}) -> {return_type}:"

    # use black to format and beautify the example invokation
    example = black.format_str(f"{func_name}({example_args})", mode=black.Mode())
    # add doctest delimiters to the code
    lines = example.splitlines()
    example = "        >>> " + lines[0] + "\n"
    for line in lines[1:]:
        example += "        ... " + line+ "\n"
    example = example.rstrip()

    example_return_value = black.format_str(repr(data["result"]), mode=black.Mode())
    example_return_value = textwrap.indent(example_return_value, "        ").rstrip()

    code = f'    return invoke({invoke_args_str})'

    if func_name in replace_data:
        func_def, code = replace_data[func_name]

    if "\\" in doc or "\\" in example or "\\" in example_return_value:
        initial_indent = '    r"""'
    else:
        initial_indent = '    """'
    p = []
    for line in doc.splitlines():
        p.append(
            textwrap.fill(
                line, 
                width=90, 
                break_long_words=False, 
                initial_indent=initial_indent, 
                subsequent_indent="    "
            )
        )
        initial_indent = '    '
    doc = "\n".join(p)

    # write every part of the function to the .py file
    fout.write(CODE_TEMPLATE.format(**locals()))


def line_generator(file):
    """Make a file a generator for lines, so we can send() back lines"""
    for line in file:
        line = yield line
        while line is not None:
            yield
            line = yield line
            
script_dir = Path(__file__).absolute().parent
source_file_path = script_dir / "anki_connect.md"
out_file_path = script_dir.parent / "anki_connect.py"

with (source_file_path.open('r', encoding="utf-8") as fin,
      out_file_path.open('w', encoding="utf-8") as fout):
    lines_gen = line_generator(fin)
    fout.write(HEADER)
    # ignore everything till the first thematic break
    for line in lines_gen:
        if line.strip().startswith("---"):
            break
    # look for lines of interest
    for line in lines_gen:
        if line.startswith("### "):
            # new section heading
            fout.write("# " + line[4:] + "\n")
        elif line.startswith("#### "):
            # new function
            func_name = line[5:].strip().replace("`", "")
            doc, requests, results = split_to_chunks(lines_gen, func_name)
            make_func(func_name, doc, requests, results)
        else:
            if line != "\n":
                print("ignored line:", repr(line))