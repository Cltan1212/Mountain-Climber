from __future__ import annotations
from typing import Generic, TypeVar
from data_structures.referential_array import ArrayR
from data_structures.linked_stack import LinkedStack

K = TypeVar("K")
V = TypeVar("V")


class InfiniteHashTable(Generic[K, V]):
    """
    Infinite Hash Table.

    Type Arguments:
        - K:    Key Type. In most cases should be string.
                Otherwise `hash` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """
    TABLE_SIZE = 27

    def __init__(self) -> None:
        self.table = ArrayR(self.TABLE_SIZE)
        self.level = 0
        self.count = 0

    def hash(self, key: K) -> int:
        if self.level < len(key):
            return ord(key[self.level]) % (self.TABLE_SIZE - 1)
        return self.TABLE_SIZE - 1

    def __getitem__(self, key: K) -> V:
        """
        Get the value at a certain key
        :raises KeyError: when the key doesn't exist.
        """
        current = self.table
        location = self.get_location(key)
        for index in location:
            current = current[index][1]
        return current

    def __setitem__(self, key: K, value: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        """

        self.level = 0
        pos = self.hash(key)
        current_table = self.table

        while current_table[pos] is not None:

            self.level += 1
            current_table.count += 1
            if not isinstance(current_table[pos][1], ArrayR):
                new_table = ArrayR(self.TABLE_SIZE)
                new_table[self.hash(current_table[pos][0])] = current_table[pos]
                new_table.count += 1
                current_table[pos] = key[:self.level], new_table

            current_table = current_table[pos][1]
            pos = self.hash(key)

        current_table[pos] = key, value
        self.count += 1
        current_table.count += 1

    def __delitem__(self, key: K) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        """

        self.level = 0
        current_table = self.table
        tables = LinkedStack()
        pos = self.hash(key)

        while current_table[pos][0] != key:
            current_table.count -= 1
            tables.push(current_table)
            current_table = current_table[pos][1]
            self.level += 1
            pos = self.hash(key)

        current_table[pos] = None
        current_table.count -= 1

        item = None
        for i in range(len(current_table)):
            if current_table[i] is not None:
                item = current_table[i]
                break
        while current_table.count == 1 and not tables.is_empty():
            current_table = tables.pop()
            self.level -= 1
            current_table[self.hash(item[0])] = item

        self.count -= 1

    def __len__(self):
        return self.count

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        return "/".join([str(lst) for lst in self.table])

    def get_location(self, key):
        """
        Get the sequence of positions required to access this key.

        :raises KeyError: when the key doesn't exist.
        """

        self.level = 0
        temp = []
        current_table = self.table
        pos = self.hash(key)

        while current_table[pos] is not None and current_table[pos][0] is not key:
            temp.append(pos)
            self.level += 1
            current_table = current_table[pos][1]
            pos = self.hash(key)
            if isinstance(current_table, int):
                raise KeyError

        temp.append(pos)
        self.level = 0
        return temp

    def __contains__(self, key: K) -> bool:
        """
        Checks to see if the given key is in the Hash Table

        :complexity: See linear probe.
        """
        try:
            _ = self[key]
        except KeyError:
            return False
        else:
            return True