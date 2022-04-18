from __future__ import annotations

from typing import Generic, TypeVar

from hop_info import HopInfo


# Key type
_KT = TypeVar("_KT", bound=str)
# Value type
_VT = TypeVar("_VT", bound=HopInfo)


class HopsMap(dict, Generic[_KT, _VT]):
    """
    Thin wrapper around a dictionary that represents destination nodes
    and the most convenient hops to reach those destinations.
    """
    def distance_to(self, node_name: _KT) -> float:
        """
        Forwards the best destination to reach a node.
        Here for the sake of readability and syntactic sugar.

        :param node_name: Name of the node to compare.
        :return: The current best distance to reach that node.
        """
        return self[node_name].best_distance

    def pass_through(self, node_name: _KT) -> str:
        """
        Forwards which path is the best to reach a node.
        Here for the sake of readability and syntactic sugar.

        :param node_name: Name of the node to compare.
        :return: The current best path to reach that node.
        """
        return self[node_name].next_hop
