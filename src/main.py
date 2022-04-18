#!/usr/bin/env python3.10
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager
from pprint import pprint
import sys

from node import Node
from parse_links import parse_links


def main(filename: str = "data.txt") -> int:
    # starting data
    links = parse_links(filename)
    nodes = Node.from_links(links)

    with Manager() as manager:
        # Make a shared memory for every process
        network = manager.dict()

        with ProcessPoolExecutor(max_workers=4) as executor:
            # Make an executor that automatically creates processes, starts and joins them

            for node in nodes:
                # Initialise nodes with their queue and a network reference
                node.with_queue(manager.Queue()).with_network(network)
                network[node.name] = node

            for name, node in network.items():
                # This hack is needed to invoked the __set_attr__ method of the network
                # and pass in updated nodes with all connections in place
                network[name] = node.normalised()

            # Run the processes
            executor.map(Node.send_packets, network.values())

        # Log the final optimised network
        print("Network:")
        pprint(dict(network))

    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise RuntimeError('This file is to be executed with exactly 2 arguments'
                           'The executable name and the file')
    raise SystemExit(main(sys.argv[1]))
