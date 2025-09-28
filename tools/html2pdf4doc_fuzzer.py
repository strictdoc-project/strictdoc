import argparse
import datetime
import os.path
import random
import shutil
from subprocess import CalledProcessError, CompletedProcess, TimeoutExpired, run
from typing import List

from faker import Faker
from lxml import etree, html

from strictdoc.helpers.timing import measure_performance


def mutate_and_print(path_to_input_file) -> bool:
    assert os.path.isfile(path_to_input_file), path_to_input_file

    text = open(path_to_input_file, encoding="utf-8").read()

    # Parse HTML into DOM
    tree = html.fromstring(text)

    # Pick a random element
    elems = tree.xpath("//p | //td")
    if elems:
        for _ in range(10):
            node = random.choice(elems)

            print("Mutating node:", node.tag)  # noqa: T201

            n_sentences = random.randint(1, 100)

            fake = Faker()
            extra_text = fake.text(max_nb_chars=10 * n_sentences)

            node.text = extra_text

    # Serialize back to HTML
    mutated_html = etree.tostring(tree, pretty_print=False, method="html", encoding="unicode")

    # Save next to input file
    out_file = path_to_input_file + ".mut.html"
    out_file_pdf = path_to_input_file + ".mut.html.pdf"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(mutated_html)

    print("Wrote mutated file:", out_file)  # noqa: T201

    paths_to_print = [
        (out_file, out_file_pdf)
    ]

    cmd: List[str] = ["html2pdf4doc", "print", "--strict"]

    for path_to_print_ in paths_to_print:
        cmd.append(path_to_print_[0])
        cmd.append(path_to_print_[1])

    with measure_performance(
        "PDFPrintDriver: printing HTML to PDF using HTML2PDF and Chrome Driver"
    ):
        try:
            _: CompletedProcess[bytes] = run(
                cmd,
                capture_output=False,
                check=True,
            )
        except CalledProcessError:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            error_file = f"{out_file}.{timestamp}.html"
            shutil.copy(out_file, error_file)
            print(f"Saved failed mutated HTML as: {error_file}")  # noqa: T201
            return False
        except TimeoutExpired:
            raise TimeoutError from None
    return True

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("input_file", type=str, help="TODO")
    args = parser.parse_args()

    path_to_input_file = args.input_file

    success_count, failure_count = 0, 0
    for i in range(1, 100):
        print(f"--- Printing cycle #{i} — So far: 🟢{success_count} / 🔴{failure_count} ---")  # noqa: T201
        success = mutate_and_print(path_to_input_file)
        if success:
            success_count += 1
        else:
            failure_count += 1


if __name__ == "__main__":
    main()
