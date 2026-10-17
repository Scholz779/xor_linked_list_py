"""XOR doubly linked list.

Each node stores a single integer field, ``link``:
    link = (address(prev) if prev else 0) XOR (address(next) if next else 0)

Given a node and its neighbour you recover the other neighbour, which lets the
list be walked in either direction from a starting edge pair. The XOR itself is
just integer arithmetic on ``id()`` results; because zero denotes "no node",
the identity ``(0 XOR a) == a`` preserves the non-neighbour side.

A pointer (``XorNode``) is a first-class Python object, so a node stays alive
as long as the list holds it. The list is therefore traversable for as long as
it exists. The memory saving is the one pointer field per node instead of two.

Key naming decision: ``XorNode`` (matching the project prefix) rather than
``Node``. In a library intended for import into unfamiliar code, unique
prefixes make grepping and autocomplete unambiguous. The README documents
both exported names.
"""

from __future__ import annotations

from typing import Dict, Iterator, Optional


class XorNode:
    """A node carrying a ``value`` plus a single XOR-encoded ``link``.

    ``link`` equals ``(id(prev) or 0) XOR (id(next) or 0)``. It is raw
    integer state; mutating it directly from outside the list corrupts the
    list. It is exposed as a plain attribute so the list implementation can
    read/write it cheaply; callers should treat it as opaque.
    """

    __slots__ = ("value", "link")

    def __init__(self, value: object = None, link: int = 0) -> None:
        self.value = value
        # XOR of neighbours' ids; 0 means "no node" on that side.
        self.link = link

    def __repr__(self) -> str:
        return f"XorNode(value={self.value!r}, link={self.link!r})"


class XorLinkedList:
    """Doubly linked list whose nodes use a single XOR-encoded pointer field.

    Interpretation chosen (stated plainly because the brief is ambiguous):
    the XOR trick is applied to ``id()`` of node objects. The list is
    reference-stable, which means nodes never need to be re-addressed — a
    benefit a compacting collector would erase. We trade that benefit for an
    implementation that runs on the stock CPython interpreter with zero
    third-party dependencies.

    Operations provided: ``append`` (insert at tail), ``prepend`` (insert at
    head), ``remove`` (delete a specific node), forward and reverse
    iteration, ``len``, and truth-testing. The list rejects duplicate node
    identity because the XOR scheme needs each node present at most once to
    stay decodable.
    """

    __slots__ = ("_head", "_tail", "_size", "_nodes")

    def __init__(self) -> None:
        self._head: Optional[XorNode] = None
        self._tail: Optional[XorNode] = None
        self._size: int = 0
        self._nodes: Dict[int, XorNode] = {}

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return self._size > 0

    def __iter__(self) -> Iterator[XorNode]:
        # Walk using the neighbour invariant: from a node A whose neighbour on
        # one side is B, the other neighbour is A.link XOR id(B).
        prev: Optional[XorNode] = None
        cur: Optional[XorNode] = self._head
        while cur is not None:
            yield cur
            nxt_id = cur.link ^ (id(prev) if prev is not None else 0)
            nxt: Optional[XorNode] = None
            if nxt_id != 0:
                nxt = self._nodes.get(nxt_id)
            prev, cur = cur, nxt

    def __reversed__(self) -> Iterator[XorNode]:
        prev: Optional[XorNode] = None
        cur: Optional[XorNode] = self._tail
        while cur is not None:
            yield cur
            nxt_id = cur.link ^ (id(prev) if prev is not None else 0)
            nxt: Optional[XorNode] = None
            if nxt_id != 0:
                nxt = self._nodes.get(nxt_id)
            prev, cur = cur, nxt

    def append(self, value: object) -> XorNode:
        """Insert ``value`` at the tail and return the new node."""
        node = XorNode(value)
        if self._head is None:
            self._head = self._tail = node
        else:
            assert self._tail is not None
            tail = self._tail
            node.link = id(tail)
            tail.link ^= id(node)
            self._tail = node
        self._size += 1
        self._nodes[id(node)] = node
        return node

    def prepend(self, value: object) -> XorNode:
        """Insert ``value`` at the head and return the new node."""
        node = XorNode(value)
        if self._head is None:
            self._head = self._tail = node
        else:
            head = self._head
            node.link = id(head)
            head.link ^= id(node)
            self._head = node
        self._size += 1
        self._nodes[id(node)] = node
        return node

    def remove(self, node: XorNode) -> None:
        """Delete ``node`` from the list.

        Raises ``ValueError`` if ``node`` is not in the list, or is in the
        list more than once. The duplicate check is structural: the XOR
        scheme only stays decodable while every node appears at most once,
        so we enforce that invariant rather than silently corrupting links.
        """
        if not isinstance(node, XorNode):
            raise TypeError("remove() expects an XorNode")
        if self._size == 0:
            raise ValueError("node not in list")

        # Single-node fast path keeps the general logic free of special cases.
        if self._size == 1:
            if self._head is not node:
                raise ValueError("node not in list")
            self._head = None
            self._tail = None
            self._size = 0
            self._nodes.pop(id(node), None)
            node.link = 0
            return

        # General case: locate node by forward walk, remembering both
        # neighbours.
        prev: Optional[XorNode] = None
        cur: Optional[XorNode] = self._head
        found_prev: Optional[XorNode] = None
        found_next: Optional[XorNode] = None
        seen = 0
        while cur is not None:
            nxt_id = cur.link ^ (id(prev) if prev is not None else 0)
            nxt: Optional[XorNode] = None
            if nxt_id != 0:
                nxt = self._nodes.get(nxt_id)
            if cur is node:
                found_prev = prev
                found_next = nxt
                seen += 1
                if seen > 1:
                    raise ValueError("node appears more than once")
            prev, cur = cur, nxt

        if seen == 0:
            raise ValueError("node not in list")

        assert found_prev is not None or found_next is not None

        if found_prev is not None:
            found_prev.link ^= id(node) ^ (id(found_next) if found_next is not None else 0)
        if found_next is not None:
            found_next.link ^= id(node) ^ (id(found_prev) if found_prev is not None else 0)

        if node is self._head:
            self._head = found_next
        if node is self._tail:
            self._tail = found_prev

        self._size -= 1
        self._nodes.pop(id(node), None)
        node.link = 0
