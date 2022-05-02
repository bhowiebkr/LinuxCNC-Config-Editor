import json
import os
import re

DEBUG = True


class LinuxCNCDocs(object):
    def __init__(self):
        self.data = None
        doc_file_path = os.path.join(os.path.dirname(__file__), "docs.json")
        with open(doc_file_path, "r") as f:
            self.data = json.load(f)

    def get_section_doc(self, section):
        # Try to get the docs from HTML
        html_path = os.path.join(
            os.path.join(os.path.dirname(__file__)), f"{section}.html"
        )
        if os.path.exists(html_path):
            html = None
            with open(html_path) as f:
                html = f.read()

            if html:
                return html

        # Try to get the docs from json
        try:
            docs = self.data[section]["description"]
            return docs
        except KeyError as e:
            if DEBUG:
                print("error:", e)

    def get_variable_docs(self, section, variable):
        try:
            docs = self.data[section]["variables"][variable]
            docs = f"<b>{variable}</b><br>{docs}"
            docs = re.sub(r"([a-z])\. ", r"\g<1>.<br><br>", docs)
            return docs
        except KeyError as e:
            if DEBUG:
                print("Section:", section, "missing:", e)
