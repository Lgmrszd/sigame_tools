from xml.dom.minidom import Element, Text


def get_text(el: Element) -> str:
    if len(el.childNodes) == 0:
        return ""
    text: Text = el.childNodes[0]
    return text.data
