from __future__ import annotations

from dataclasses import dataclass, field
from queue import Queue
from time import time_ns
from math import inf

from hop_info import HopInfo
from hops_map import HopsMap
from packet import Packet


@dataclass(slots=True, eq=True)
class Node:
    """
    A node struct for the graph.

    Attributes:
        name (str): The name of the node.
        hops_map (dict[str, HopInfo]): A map of hops that represent reachable nodes and how far they are.
        queue (Queue): A Queue object simulating data being sent to the node.
        network (list[Node]): A reference to a shared list of all the nodes in the network.
    """

    name: str
    map: HopsMap = field(hash=False)
    queue: Queue = field(init=False)
    network: dict[str, Node] = field(init=False)

    def __repr__(self):
        return f"<Router {self.name}>" f"\nRouting table:\n{self.map}"

    @classmethod
    def from_links(cls, links: dict[str, list[HopInfo]], /) -> list[Node]:
        """
        Class constructor that builds a list of Nodes from a dictionary.

        The dictionary parameter should be of the form:

        {
            node_1: [hop_info, hop_info ...],

            node_2: [hop_info, hop_info ...],

            ...
        }

        :param links: A Dictionary of node_names to their Hop Information.
        :return: A List of Nodes.
        """
        nodes = []

        for name, hops in links.items():
            node = cls(
                name,
                HopsMap({hop.next_hop: _hop_from(hop.next_hop, hops) for hop in hops}),
            )
            nodes.append(node)

        return nodes

    def with_queue(self, queue: Queue) -> Node:
        """
        Set the queue of the node.

        :param queue: The queue to set.
        :return: The node with the queue set.
        """
        self.queue = queue
        return self

    def with_network(self, network: dict[str, Node]) -> Node:
        """
        Set the network of the node.

        :param network: The network to set.
        :return: The node with the network set.
        """
        self.network = network
        return self

    def normalised(self) -> Node:
        """
        Extends the internal hop_map for nodes which are not directly linked.

        A non-linked node is assigned a distance of infinity.

        :return: The object itself.
        """
        for node in self.neighbours:
            if node.name not in self.map:
                self.map[node.name] = HopInfo(node.name, inf)
        return self

    def and_send(self, destination: Node, /, *, packet: Packet) -> Node:
        """
        Send a packet to a destination node.

        :param destination: The node to and_send the packet to.
        :param packet: The packet to and_send.
        :return: The object itself.
        """
        destination.queue.put(packet)
        return self

    @property
    def dummy_packet(self) -> Packet:
        """
        Generate a sample string to use as a dummy dummy_packet.

        :return: A string to use as a dummy dummy_packet.
        Contains time of creation and the name of the node.
        """
        return Packet(f"Message from: {self.name}.\nTime: {time_ns()}\n", self.map)

    @property
    def neighbours(self) -> list[Node]:
        """
        Get a list of all neighbours of the node.

        :return: A list of all neighbours of the node.
        """
        return [node for node in self.network.values() if self.name != node.name]

    def wait_for_packets(self) -> None:
        """
        Simulate the time it takes for packets to be received.
        The node waits for a packet from each neighbour and keeps on listening.

        :return: None
        """
        while not self.queue.empty():
            packet = self.queue.get()
            print(f"{self.name} received {packet.header}\n")
            self.update_table(packet)

    def send_packets(self, packet: Packet | None = None, /) -> None:
        """
        Simulate the transmission of packets.
        The node sends a packet to each neighbour.

        After sending a packet, the node waits for a packet from each neighbour.

        :param packet: The packet to and_send. Defaults internally to a dummy_packet.
        :return: None
        """
        if packet is None:
            packet = self.dummy_packet

        for neighbour in self.neighbours:
            self.and_send(neighbour, packet=packet)
            print(f"{self.name} sent {packet} to {neighbour.name}")

        self.wait_for_packets()

    def update_table(self, packet: Packet, /) -> None:
        """
        Performs a BellmanFord distributed algorithm to update every link.

        :param packet: A Packet object with the relevant information, including the sender's hop table.
        :return: None
        """
        # self has to be aliased in order to trigger
        # network's __set_attr__ method
        proxy = self
        neighbour_table = packet.content
        edited = False

        for destination in proxy.map:
            current_distance = proxy.distance_to(destination)

            for node in neighbour_table:
                # grab a possible midway point for a shorter distance overall
                midway = proxy.network[node]
                distance_to_midway = proxy.distance_to(node)
                midway_to_node = midway.distance_to(destination)

                # compute the new_distance as the sum of start-midway + midway-destination
                new_distance = distance_to_midway + midway_to_node

                # skip if a node would lead to itself
                # (the algorithm resolves correctly but will display the wrong path)
                if not midway_to_node:
                    continue

                # if a shorter path to the destination is found, update the network
                if new_distance < current_distance:
                    proxy.map[destination] = HopInfo(
                        self.network[destination].map.pass_through(midway.name),
                        new_distance,
                    )

                    print(
                        f"Updated path from {proxy.name} to {destination}\n"
                        f"New best distance: {proxy.map[destination].best_distance}\n"
                    )

                    edited = True

        # reassign self to trigger the network's __set_attr__ method
        self.network[self.name] = proxy

        # repeat the process if a node was updated
        if edited:
            self.send_packets()

    def distance_to(self, node_name: str) -> float:
        """
        Utility method that returns the distance between two nodes.

        :param node_name: the name of the node to compare.
        :return: the distance between the two nodes.
        """
        return self.map.distance_to(node_name)


def _hop_from(_name: str, _hops: list[HopInfo]) -> HopInfo:
    """
    Utility function that finds the first hop which is directly connected to a certain node.

    :param _name: the name of the node to compare.
    :param _hops: a list of hops to iterate through.
    :return:
    """
    for hop in _hops:
        if hop.next_hop == _name:
            return hop
    raise ValueError('The node you are looking for is not in the given list')
