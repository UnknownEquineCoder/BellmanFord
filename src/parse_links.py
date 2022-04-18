from __future__ import annotations

from pprint import pprint

from hop_info import HopInfo


def parse_links(filename: str, /) -> dict[str, list[HopInfo]]:
    """
    Utility function that reads from a file and returns a temporary structure.

    This structure has to be used in conjunction with the Node.from_links class method.

    :param filename: The name of the file to read from.
    :return: A dictionary with the key being the name of the node and the value being a list of HopInfo objects.
    """
    matrices = {}

    with open(filename) as source:
        for line in source:
            match line.strip().split(" "):
                # Pattern matching makes this very intuitive.
                case name, *links if links:
                    matrix = [HopInfo(name, 0.0)] + [
                        HopInfo.parse_str(link) for link in links
                    ]

                    matrices[name] = matrix
                # Ignore any line that doesn't match the pattern.
                case _:
                    pass

    return matrices
