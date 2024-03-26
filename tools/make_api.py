import re
import textwrap
import json
from pathlib import Path

import black
import mistletoe
from mistletoe.markdown_renderer import MarkdownRenderer, BlankLine
from mistletoe.span_token import InlineCode, RawText, Link, LineBreak, Emphasis, Strong
from mistletoe.block_token import (Quote, ThematicBreak, Heading, Paragraph, CodeFence, 
                                   HtmlBlock, List, ListItem, Document)

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
    result part."""
    
    mode = 0
    doc = ""
    request = ""
    result = ""
    for line in lines_gen:
        # look for start of next function definition
        if line.strip().startswith("###"):
            # send the line back to the generator, so the caller can take care of it
            lines_gen.send(line) 
            # we are done with this block
            break
        s = line.strip()
        match(mode):
            case 0:
                if s == "<details>":
                    mode = 1
                else:
                    doc += line
            case 1:
                if re.search(REQUEST_SEARCH, s):
                    mode = 2
            case 2:
                if s.startswith("```json"):
                    mode = 3
            case 3:
                if s.startswith("```"):
                    mode = 4
                else:
                    request += line
            case 4:
                if re.search(RESULT_SEARCH, s):
                    mode = 5
                elif re.search(REQUEST_SEARCH, s):
                    print("another request")
            case 5:
                if s.startswith("```json"):
                    mode = 6
            case 6:
                if s.startswith("```"):
                    mode = 7
                else:
                    result += line
            case 7:
                if re.search(RESULT_SEARCH, s):
                    print(func_name, "another result")
                elif re.search(REQUEST_SEARCH, s):
                    print(func_name, "another request")

    return doc, request, result


def make_func(func_name, doc, request, result):
    with MarkdownRenderer() as renderer:
        document = mistletoe.Document(doc)
    doc = traverse(document)
    doc = " " + doc.strip()[1:] # remove the list asterisk

    doc = doc.replace("`null`", "`None`")
    doc = doc.replace("`true`", "`True`")
    doc = doc.replace("`false`", "`False`")
    doc = textwrap.dedent(doc)

    # process sample request 
    try:
        d = json.loads(request)
    except:
        print(func_name)
        print(repr(request))
        raise
    invoke_args = [f'"{func_name}"']
    example_args = ""
    func_args = []
    if "params" in d:
        for arg, value in d["params"].items():
            invoke_args.append(f"{arg}={arg}")
            func_args.append(f"{arg}: {type(value).__name__}")
        example_args = ", ".join((f"{v!r}" for k,v in d["params"].items()))
    invoke_args_str = ", ".join(invoke_args)
    func_args_str = ", ".join(func_args)

    # process sample result
    try:
        d = json.loads(result)
    except:
        print(func_name)
        print(result)
        raise
    if d["result"] is None:
        return_type = "None"
    else:
        return_type = type(d["result"]).__name__

    func_def = f"def {func_name}({func_args_str}) -> {return_type}:"

    # use black to format and beautify the example invokation
    example = black.format_str(f"{func_name}({example_args})", mode=black.Mode())
    lines = example.splitlines()
    # add doctest delimiters to the code
    example = "        >>> " + lines[0] + "\n"
    for line in lines[1:]:
        example += "        ... " + line+ "\n"
    example = example.rstrip()

    example_return_value = black.format_str(repr(d["result"]), mode=black.Mode())
    example_return_value = textwrap.indent(example_return_value, "        ").rstrip()

    code = f'    return invoke({invoke_args_str})'

    if func_name in replace_data:
        func_def, code = replace_data[func_name]

    if "\\" in doc or "\\" in example or "\\" in example_return_value:
        prefix = '    r"""'
    else:
        prefix = '    """'
    p = []
    for line in doc.splitlines():
        p.append(
            textwrap.fill(
                line, 
                width=90, 
                break_long_words=False, 
                initial_indent=prefix, 
                subsequent_indent="    "
            )
        )
        prefix = '    '
    doc = "\n".join(p)

    # write every part of the function to the .py file
    fout.write(CODE_TEMPLATE.format(**locals()))


def writeln(s):
    fout.write(s + "\n")


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
    fout.write(HEADER +"\n")
    # ignore everything till the first thematic break
    for line in lines_gen:
        if line.strip().startswith("---"):
            break
    # look for lines of interest
    for line in lines_gen:
        if line.startswith("### "):
            fout.write("# " + line[4: ] + "\n")
        elif line.startswith("#### "):
            func_name = line[5:].strip().replace("`", "")
            doc, request, result = split_to_chunks(lines_gen, func_name)
            make_func(func_name, doc, request, result)
