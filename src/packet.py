from __future__ import annotations

from dataclasses import dataclass

from hops_map import HopsMap


@dataclass
class Packet:
    """
    Struct-like class for packets.
    Holds an header, a payload and some parameters.

    For this assignment, only the content of the payload is relevant.
    However, it could easily be extended to hold more information and options.

    Attributes:
        header (str): The header of the packet.
        content (HopsMap): The payload of the packet.
        params (list[str]): The parameters of the packet.
    """
    header: str
    content: HopsMap
    params: list[str] | None = None
