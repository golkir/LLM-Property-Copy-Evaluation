import html
from html.parser import HTMLParser
from typing import Annotated
from pydantic import BeforeValidator


class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return "".join(self.fed)


def strip_html_tags(value: str) -> str:
    if not value or not isinstance(value, str):
        return value
    stripper = HTMLStripper()
    stripper.feed(value)
    clean_text = stripper.get_data()
    return html.unescape(clean_text).strip()


CleanedHTMLString = Annotated[str, BeforeValidator(strip_html_tags)]
