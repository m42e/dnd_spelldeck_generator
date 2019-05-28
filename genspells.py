import contextlib
import json
import os
import re
import sys
import argparse

import jinja2
from jinja2 import Template

latex_jinja_env = jinja2.Environment(
    block_start_string="\BLOCK{",
    block_end_string="}",
    variable_start_string="\VAR{",
    variable_end_string="}",
    comment_start_string="\#{",
    comment_end_string="}",
    line_statement_prefix="%%",
    line_comment_prefix="%#",
    trim_blocks=True,
    autoescape=False,
    loader=jinja2.FileSystemLoader(os.path.abspath("templates/")),
)


def latex_format(text):
    text = re.sub(r"\*(?! )(([^*])*?)(?! )\*", "\\\\textbf{\\1}", text)
    text = re.sub(
        r"(\s|\()([0-9]*W(?:4|6|8|10|12|20)(?:\s*\+[0-9]+)?)", r"\1\\textbf{\2}", text
    )
    text = re.sub(r"([0-9]+)\sm", r"\1~m", text)
    return text


def create_cards(spells):
    cards = []
    template = latex_jinja_env.get_template("spellcard.tex.jinja")
    for spell, s in spells.items():
        s["text"] = latex_format(s["text"])
        if "text_card" in s:
            s["text_card"] = latex_format(s["text_card"])
        cards.append(template.render(title=spell, **s))
    return cards


def write_spells(args, spells):
    if args.characterclass != "":
        fn = args.characterclass
    else:
        fn = "All"

    cards = create_cards(spells)
    cardcount = len(cards)

    # create empty cards
    for i in range(10):
        cards.append("")

    spell_text = []
    pagetemplate = latex_jinja_env.get_template("spellpage.tex.jinja")
    for offset in range(0, cardcount, 10):
        data = {"c": cards[offset : offset + 9]}
        spell_text.append(pagetemplate.render(**data))

    with open("{}.tex".format(fn), "w+") as of:
        of.write(
            latex_jinja_env.get_template("spelldeck.tex.jinja").render(
                content="".join(spell_text)
            )
        )


def read_spells(args):
    spells = dict()
    for f in args.spellfile:
        spells.update(json.load(f))

    if args.characterclass != "":
        spells = dict(
            filter(lambda x: args.characterclass in x[1]["classes"], spells.items())
        )

    spells = dict(sorted(spells.items(), key=lambda x: x[1]["level"]))
    return spells


def parse_args():
    parser = argparse.ArgumentParser(
        description="Simple tool to create LaTeX spellcards from json data"
    )
    parser.add_argument(
        "--spellfile",
        type=argparse.FileType(),
        default=["spells_german/spells.json"],
        nargs="+",
    )
    parser.add_argument("--characterclass", "-cc", default="", nargs="?")
    return parser.parse_args()


def main():
    args = parse_args()
    spells = read_spells(args)
    write_spells(args, spells)


if __name__ == "__main__":
    main()
