from __future__ import annotations

from typing import Generic, TypeVar, Iterator
from data_structures.hash_table import LinearProbeTable, FullError
from data_structures.referential_array import ArrayR

K1 = TypeVar('K1')
K2 = TypeVar('K2')
V = TypeVar('V')


class DoubleKeyTable(Generic[K1, K2, V]):
    """
    Double Hash Table.

    Type Arguments:
        - K1:   1st Key Type. In most cases should be string.
                Otherwise `hash1` should be overwritten.
        - K2:   2nd Key Type. In most cases should be string.
                Otherwise `hash2` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """

    # No test case should exceed 1 million entries.
    TABLE_SIZES = [5, 13, 29, 53, 97, 193, 389, 769, 1543, 3079, 6151, 12289, 24593, 49157, 98317, 196613, 393241,
                   786433, 1572869]

    HASH_BASE = 31

    def __init__(self, sizes: list | None = None, internal_sizes: list | None = None) -> None:
        # the top level table is an array
        if sizes is not None:
            self.TABLE_SIZES = sizes
        self.size_index = 0
        self.count = 0
        self.top_level_array: ArrayR[tuple[K1, V]] = ArrayR(self.TABLE_SIZES[self.size_index])

        # the low level table is an instance of LinearProbeTable
        self.internal_sizes = internal_sizes

    def hash1(self, key: K1) -> int:
        """
        Hash the 1st key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """

        value = 0
        a = 31415
        for char in key:
            value = (ord(char) + a * value) % self.table_size
            a = a * self.HASH_BASE % (self.table_size - 1)
        return value

    def hash2(self, key: K2, sub_table: LinearProbeTable[K2, V]) -> int:
        """
        Hash the 2nd key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """

        value = 0
        a = 31415
        for char in key:
            value = (ord(char) + a * value) % sub_table.table_size
            a = a * self.HASH_BASE % (sub_table.table_size - 1)
        return value

    def _linear_probe(self, key1: K1, key2: K2, is_insert: bool) -> tuple[int, int]:
        """
        Find the correct position for this key in the hash table using linear probing.

        :raises KeyError: When the key pair is not in the table, but is_insert is False.
        :raises FullError: When a table is full and cannot be inserted.
        """

        position_top_level = self.hash1(key1)

        # linear probing for top level hash table
        for _ in range(self.table_size):
            if self.top_level_array[position_top_level] is None:
                if is_insert:
                    # create an instance of LinearProbeTable
                    new_probe_table = LinearProbeTable(self.internal_sizes)
                    new_probe_table.hash = lambda k: self.hash2(k, new_probe_table)

                    # add instance and key1
                    self.top_level_array[position_top_level] = (key1, new_probe_table)
                    self.count += 1

                    return position_top_level, new_probe_table.hash(key2)
                else:
                    raise KeyError(key1)

            elif self.top_level_array[position_top_level][0] == key1:
                # key2 is equal to the inner
                position_internal_table = self.top_level_array[position_top_level][1]
                return position_top_level, position_internal_table._linear_probe(key2, is_insert)

            else:
                position_top_level = (position_top_level + 1) % self.table_size

        if is_insert:
            raise FullError("Table is full!")
        else:
            raise KeyError

    def iter_keys(self, key: K1 | None = None) -> Iterator[K1 | K2]:
        """
        key = None:
            Returns an iterator of all top-level keys in hash table
        key = k:
            Returns an iterator of all keys in the bottom-hash-table for k.
        """
        if key is None:
            for item in self.top_level_array:
                if item is not None:
                    yield item[0]

        else:
            for item in self.top_level_array:
                if item is not None and item[0] == key:
                    yield from item[1].keys()

    def keys(self, key: K1 | None = None) -> list[K1]:
        """
        key = None: returns all top-level keys in the table.
        key = x: returns all bottom-level keys for top-level key x.
        """

        if key is None:
            res = []
            for item in self.top_level_array:
                if item is not None:
                    res.append(item[0])
            return res

        else:
            for item in self.top_level_array:
                if item is not None and item[0] == key:
                    return item[1].keys()

    def iter_values(self, key: K1 | None = None) -> Iterator[V]:
        """
        key = None:
            Returns an iterator of all values in hash table
        key = k:
            Returns an iterator of all values in the bottom-hash-table for k.
        """
        if key is None:
            for item in self.top_level_array:
                if item is not None:
                    yield from item[1].values()

        else:
            for item in self.top_level_array:
                if item is not None and item[0] == key:
                    yield from item[1].values()

    def values(self, key: K1 | None = None) -> list[V]:
        """
        key = None: returns all values in the table.
        key = x: returns all values for top-level key x.
        """
        if key is None:
            res = []
            for item in self.top_level_array:
                if item is not None:
                    res += item[1].values()
            return res

        else:
            for item in self.top_level_array:
                if item is not None and item[0] == key:
                    return item[1].values()

    def __contains__(self, key: tuple[K1, K2]) -> bool:
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

    def __getitem__(self, key: tuple[K1, K2]) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        """
        key1_position, key2_position = self._linear_probe(key[0], key[1], False)
        return self.top_level_array[key1_position][key[1]]

    def __setitem__(self, key: tuple[K1, K2], data: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        """
        key1_position, key2_position = self._linear_probe(key[0], key[1], True)

        if self.top_level_array[key1_position][0] == key[0]:
            self.top_level_array[key1_position][1][key[1]] = data

        if len(self) > self.table_size / 2:
            self._rehash()

    def __delitem__(self, key: tuple[K1, K2]) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        """
        key1_position, key2_position = self._linear_probe(key[0], key[1], False)

        # Remove the element
        self.top_level_array[key1_position][1].__delitem__(key[1])

        # Delete key1 only if low level table is empty
        if len(self.top_level_array[key1_position][1]) == 0:
            self.top_level_array[key1_position] = None
            self.count -= 1

            # Start moving over the cluster
            key1_position = (key1_position + 1) % self.table_size
            while self.top_level_array[key1_position] is not None:
                key1, inner_table = self.top_level_array[key1_position]

                # Reinsert
                for inner_item in inner_table.array:
                    if inner_item is not None:
                        key2, value = inner_item
                        self[key1, key2] = value

                key1_position = (key1_position + 1) % self.table_size

    def _rehash(self) -> None:
        """
        Need to resize table and reinsert all values

        :complexity best: O(N*hash(K)) No probing.
        :complexity worst: O(N*hash(K) + N^2*comp(K)) Lots of probing.
        Where N is len(self)
        """
        old_array = self.top_level_array
        self.size_index += 1
        if self.size_index == len(self.TABLE_SIZES):
            return

        # Resize
        self.top_level_array = ArrayR(self.TABLE_SIZES[self.size_index])
        self.count = 0

        # Reinsert top level array
        for item in old_array:
            if item is not None:
                key1, inner_linear_probe_table = item

                # Reinsert inner level array
                for inner_item in inner_linear_probe_table.array:
                    if inner_item is not None:
                        key2, value = inner_item
                        self[key1, key2] = value

    @property
    def table_size(self) -> int:
        """
        Return the current size of the table (different from the length)
        """
        return len(self.top_level_array)

    def __len__(self) -> int:
        """
        Returns number of elements in the hash table
        """
        return self.count

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        result = ""
        for key1 in self.keys():
            for key2 in self.keys(key1):
                result += "(" + str(key1) + "," + str(key2) + "," + str(self[key1, key2]) + ")\n"


# class DoubleHashTableIterator:
#     def __iter__(self):
#         return self
#
#     def __next__(self):
#         if THERE_IS_NEXT_ELEMENT:
#             return NEXT_ELEMENT  # of type SomeElementType
#         else:
#             raise StopIteration
