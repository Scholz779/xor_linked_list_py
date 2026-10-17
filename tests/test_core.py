import unittest

from xor_linked_list_py import XorLinkedList, XorNode


class TestConstruction(unittest.TestCase):
    def test_empty_list_has_zero_length_and_is_falsy(self):
        lst = XorLinkedList()
        self.assertEqual(len(lst), 0)
        self.assertFalse(lst)

    def test_list_with_one_node_is_truthy(self):
        lst = XorLinkedList()
        lst.append(1)
        self.assertEqual(len(lst), 1)
        self.assertTrue(lst)


class TestAppend(unittest.TestCase):
    def test_append_single_node_sets_head_and_tail_same(self):
        lst = XorLinkedList()
        node = lst.append(10)
        self.assertIs(lst._head, node)
        self.assertIs(lst._tail, node)
        self.assertEqual(node.link, 0)

    def test_append_three_nodes_preserves_order_on_forward_walk(self):
        lst = XorLinkedList()
        a = lst.append("a")
        b = lst.append("b")
        c = lst.append("c")
        self.assertEqual([n.value for n in lst], ["a", "b", "c"])
        # The single-node middle link encodes both neighbours.
        self.assertEqual(b.link, id(a) ^ id(c))

    def test_append_then_prepend_interleaves_correctly(self):
        lst = XorLinkedList()
        a = lst.append("a")
        z = lst.prepend("z")
        b = lst.append("b")
        y = lst.prepend("y")
        self.assertEqual([n.value for n in lst], ["y", "z", "a", "b"])
        self.assertIs(lst._head, y)
        self.assertIs(lst._tail, b)


class TestIteration(unittest.TestCase):
    def test_forward_iter_returns_node_objects(self):
        lst = XorLinkedList()
        a = lst.append(1)
        b = lst.append(2)
        self.assertEqual(list(lst), [a, b])

    def test_reversed_walk_gives_reverse_order(self):
        lst = XorLinkedList()
        lst.append(1)
        lst.append(2)
        lst.append(3)
        self.assertEqual([n.value for n in reversed(lst)], [3, 2, 1])

    def test_iterating_empty_list_yields_nothing(self):
        self.assertEqual(list(XorLinkedList()), [])
        self.assertEqual(list(reversed(XorLinkedList())), [])

    def test_single_node_iterates_once_in_both_directions(self):
        lst = XorLinkedList()
        n = lst.append("only")
        self.assertEqual(list(lst), [n])
        self.assertEqual(list(reversed(lst)), [n])


class TestRemove(unittest.TestCase):
    def test_remove_only_node_empties_list(self):
        lst = XorLinkedList()
        node = lst.append(5)
        lst.remove(node)
        self.assertEqual(len(lst), 0)
        self.assertFalse(lst)
        self.assertIsNone(lst._head)
        self.assertIsNone(lst._tail)
        self.assertEqual(node.link, 0)

    def test_remove_head_updates_head_pointer(self):
        lst = XorLinkedList()
        a = lst.append(1)
        b = lst.append(2)
        c = lst.append(3)
        lst.remove(a)
        self.assertIs(lst._head, b)
        self.assertIs(lst._tail, c)
        self.assertEqual([n.value for n in lst], [2, 3])
        self.assertEqual(b.link, id(c))

    def test_remove_tail_updates_tail_pointer(self):
        lst = XorLinkedList()
        a = lst.append(1)
        b = lst.append(2)
        c = lst.append(3)
        lst.remove(c)
        self.assertIs(lst._head, a)
        self.assertIs(lst._tail, b)
        self.assertEqual([n.value for n in lst], [1, 2])
        self.assertEqual(b.link, id(a))

    def test_remove_middle_node_relays_neighbours(self):
        lst = XorLinkedList()
        a = lst.append(1)
        b = lst.append(2)
        c = lst.append(3)
        lst.remove(b)
        self.assertEqual([n.value for n in lst], [1, 3])
        # a and c now point only at each other.
        self.assertEqual(a.link, id(c))
        self.assertEqual(c.link, id(a))
        self.assertIs(lst._head, a)
        self.assertIs(lst._tail, c)

    def test_remove_node_not_in_list_raises_value_error(self):
        lst = XorLinkedList()
        lst.append(1)
        orphan = XorNode(99)
        with self.assertRaises(ValueError):
            lst.remove(orphan)

    def test_remove_from_empty_list_raises_value_error(self):
        lst = XorLinkedList()
        with self.assertRaises(ValueError):
            lst.remove(XorNode(1))

    def test_remove_wrong_type_raises_type_error(self):
        lst = XorLinkedList()
        lst.append(1)
        with self.assertRaises(TypeError):
            lst.remove("not a node")  # type: ignore[arg-type]


class TestEdgeCases(unittest.TestCase):
    def test_values_can_be_falsy_and_still_stored(self):
        lst = XorLinkedList()
        lst.append(0)
        lst.append("")
        lst.append(None)
        self.assertEqual([n.value for n in lst], [0, "", None])

    def test_all_nodes_remain_traversable_after_arbitrary_removals(self):
        lst = XorLinkedList()
        nodes = [lst.append(i) for i in range(5)]  # 0,1,2,3,4
        lst.remove(nodes[2])  # remove middle
        lst.remove(nodes[0])  # remove head
        lst.remove(nodes[4])  # remove tail
        self.assertEqual([n.value for n in lst], [1, 2 + 1])  # [1, 3]
        self.assertEqual([n.value for n in reversed(lst)], [3, 1])

    def test_prepend_then_remove_head_keeps_list_consistent(self):
        lst = XorLinkedList()
        a = lst.append("a")
        z = lst.prepend("z")
        lst.remove(z)
        self.assertEqual([n.value for n in lst], ["a"])
        self.assertIs(lst._head, a)
        self.assertIs(lst._tail, a)
        self.assertEqual(a.link, 0)


if __name__ == "__main__":
    unittest.main()
