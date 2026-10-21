# xor_linked_list_py

A doubly linked list whose nodes store a single integer pointer field, computed as the XOR of their two neighbours' `id()` values. Exports `XorLinkedList` and `XorNode`.

```python
from xor_linked_list_py import XorLinkedList

lst = XorLinkedList()
lst.append("a")
lst.append("b")
lst.prepend("z")
print([n.value for n in lst])          # ['z', 'a', 'b']
print([n.value for n in reversed(lst)]) # ['b', 'a', 'z']
lst.remove(next(iter(lst)))            # removes the 'z' node
```

## Why

A classic doubly linked list stores two pointers per node (`prev`, `next`). An XOR linked list folds both into one field: `link = id(prev) XOR id(next)`. Given a node and one neighbour you recover the other by XOR-ing out the known side, so the list remains walkable in both directions from a starting edge pair. The trade-off is that traversal always needs a "previous" node in hand — you cannot jump to an arbitrary node's neighbour from the node alone.

This implementation applies the XOR trick to `id()` of Python node objects. `id()` is a stable object identity for as long as the object is alive, and the list holds strong references to every node it contains, so every address encoded in a `link` field is always live. `ctypes` (standard library) resolves an address back to its object. The saving is one pointer field per node; the cost is the indirection on traversal.

## Edge you will hit

The list rejects duplicate node identity — adding the same `XorNode` object twice, or a node already in another list, is not supported. The XOR scheme is only decodable while every node appears at most once, so `remove()` raises `ValueError` if it detects the same node twice during its walk. If you want the same *value* in two places, create two `XorNode` objects (which is what `append`/`prepend` do for you).

Removing a node you did not obtain from the list (an orphan) raises `ValueError`. The list cannot verify membership without walking, so this is checked at `remove()` time rather than at insert time.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

