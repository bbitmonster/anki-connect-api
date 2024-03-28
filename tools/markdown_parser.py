import mistletoe
from mistletoe.span_token import InlineCode, RawText, Link, LineBreak
from mistletoe.span_token import Emphasis, Strong
from mistletoe.block_token import Quote, ThematicBreak, Heading, Paragraph
from mistletoe.block_token import HtmlBlock, List, ListItem, Document, CodeFence
from mistletoe.markdown_renderer import BlankLine, MarkdownRenderer


def traverse(t, level=0):
    """Recursively traverses a mistletoe AST and returns the content as
    Markdown. Used here as a kind of beautifier for the Markdown text."""

    match t:
        case RawText():
            return t.content
        case BlankLine():
            return "\n"
        case LineBreak():
            return " "
            # return "\n"
        case ThematicBreak():
            return "---\n"
    sub = "".join(traverse(child, level+1) for child in t.children)
    match t:
        case Heading():
            return f"{t.level * '#'} {sub}\n"
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
                t.indentation * " "
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
            print("unknown AST type:", str(type(t)))
            return ""


def beautify(text):
    with MarkdownRenderer():
        return traverse(mistletoe.Document(text))
