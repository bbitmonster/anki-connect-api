import re
import textwrap
import json
from pathlib import Path

import black

import markdown_parser

black_mode = black.Mode(line_length=80)
REQUEST_SEARCH = re.compile("^<summary><i>Sample.* request.*</i></summary>")
RESULT_SEARCH = re.compile("^<summary><i>Sample.* result.*</i></summary>")

HEADER = r'''\
__version__ = '24.2.26.0'

import json
import urllib.request

URL = 'http://127.0.0.1:8765'

def invoke(action: str, **params):
    requestJson = json.dumps({
        'action': action, 
        'version': 6,
        'params': params
    }).encode('utf-8')
    response = json.load(
        urllib.request.urlopen(urllib.request.Request(URL, requestJson))
    )
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
{examples}
    """
{func_code}

'''

exceptional_funcs = {}
func_def = "def storeMediaFile(filename: str, *, data: str=None, path: str=None, url: str=None, deleteExisting: bool=True) -> str:"
func_examples = '''\
        >>> storeMediaFile("_hello.txt", data="SGVsbG8sIHdvcmxkIQ==")
        "_hello.txt"

        >>> storeMediaFile("_hello.txt", path="/path/to/file")
        "_hello.txt"

        >>> storeMediaFile("_hello.txt", url="https://url.to.file")
        "_hello.txt"'''
func_code = """\
    if data is not None:
        return invoke("storeMediaFile", filename=filename, data=data, deleteExisting=deleteExisting)
    elif path is not None:
        return invoke("storeMediaFile", filename=filename, path=str(path), deleteExisting=deleteExisting)
    elif url is not None:
        return invoke("storeMediaFile", filename=filename, url=url, deleteExisting=deleteExisting)
    else:
        raise Exception("one argument of data, path or url must be supplied")"""
exceptional_funcs["storeMediaFile"] = (func_def, func_examples, func_code)

func_def = "def getIntervals(cards: list, complete: bool=False) -> list:"
func_examples = '''\
        >>> getIntervals([1502298033753, 1502298036657])
        [-14400, 3]

        >>> getIntervals([1502298033753, 1502298036657], True)
        [
            [-120, -180, -240, -300, -360, -14400],
            [-120, -180, -240, -300, -360, -14400, 1, 3]
        ]'''
func_code = '    return invoke("getIntervals", cards=cards, complete=complete)'
exceptional_funcs["getIntervals"] = (func_def, func_examples, func_code)


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

    doc = markdown_parser.beautify(doc)
    doc = " " + doc.strip()[1:] # remove the list asterisk
    doc = doc.replace("`null`", "`None`")
    doc = doc.replace("`true`", "`True`")
    doc = doc.replace("`false`", "`False`")
    doc = textwrap.dedent(doc)

    examples = []
    for i in range(len(requests)):
        request = requests[i]
        result = results[i]

        # process sample request 
        try:
            data = json.loads(request)
        except:
            print(func_name)
            raise
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

        # process sample result
        try:
            data = json.loads(result)
        except:
            print(func_name)
            raise
        if data["result"] is None:
            return_type = "None"
        else:
            return_type = type(data["result"]).__name__

        # use black to format and beautify the example invokation
        example = black.format_str(f"{func_name}({example_args})", mode=black_mode)
        # add doctest delimiters to the code
        lines = example.splitlines()
        example = ">>> " + lines[0] + "\n"
        for line in lines[1:]:
            example += "... " + line+ "\n"
        if data["result"] is not None:
            example += black.format_str(repr(data["result"]), mode=black_mode)
        example = textwrap.indent(example, "        ").rstrip()
        examples.append(example)
    examples = "\n\n".join(examples)

    if func_name in exceptional_funcs:
        func_def, examples, func_code = exceptional_funcs[func_name]
    else:
        func_def = f"def {func_name}({func_args_str}) -> {return_type}:"
        func_code = f'    return invoke({invoke_args_str})'

    if "\\" in doc or "\\" in example:
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
    fout.write(
        CODE_TEMPLATE.format(
            func_def=func_def,
            doc=doc,
            examples=examples,
            func_code=func_code,
        )
    )


def line_generator(file):
    """Make a file a generator for lines, so we can send() back lines"""
    for line in file:
        line = yield line
        while line is not None:
            yield
            line = yield line
            
script_dir = Path(__file__).absolute().parent
source_file_path = script_dir / "anki_connect.md"
out_file_path = script_dir.parent / "anki_connect_api.py"

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