from __future__ import annotations
from dataclasses import dataclass

from mountain import Mountain

from typing import TYPE_CHECKING, Union

from data_structures.linked_stack import LinkedStack

# Avoid circular imports for typing.
if TYPE_CHECKING:
    from personality import WalkerPersonality

@dataclass
class TrailSplit:
    """
    A split in the trail.
       ___path_top____
      /               \
    -<                 >-path_follow-
      \__path_bottom__/
    """

    path_top: Trail
    path_bottom: Trail
    path_follow: Trail

    def remove_branch(self) -> TrailStore:
        """Removes the branch, should just leave the remaining following trail."""
        return self.path_follow.store

@dataclass
class TrailSeries:
    """
    A mountain, followed by the rest of the trail

    --mountain--following--

    """

    mountain: Mountain
    following: Trail

    def remove_mountain(self) -> TrailStore:
        """Removes the mountain at the beginning of this series."""
        return self.following.store

    def add_mountain_before(self, mountain: Mountain) -> TrailStore:
        """Adds a mountain in series before the current one."""
        return TrailSeries(mountain, Trail(self))

    def add_empty_branch_before(self) -> TrailStore:
        """Adds an empty branch, where the current trailstore is now the following path."""
        return TrailSplit(Trail(None), Trail(None), Trail(self))

    def add_mountain_after(self, mountain: Mountain) -> TrailStore:
        """Adds a mountain after the current mountain, but before the following trail."""
        return TrailSeries(self.mountain, Trail(TrailSeries(mountain, self.following)))

    def add_empty_branch_after(self) -> TrailStore:
        """Adds an empty branch after the current mountain, but before the following trail."""
        new_branch = Trail(TrailSplit(Trail(None), Trail(None), Trail(None)))
        return TrailSeries(self.mountain, new_branch)

TrailStore = Union[TrailSplit, TrailSeries, None]

@dataclass
class Trail:

    store: TrailStore = None

    def add_mountain_before(self, mountain: Mountain) -> Trail:
        """Adds a mountain before everything currently in the trail."""
        return Trail(TrailSeries(mountain, self))

    def add_empty_branch_before(self) -> Trail:
        """Adds an empty branch before everything currently in the trail."""
        return Trail(TrailSplit(Trail(None), Trail(None), self))

    def follow_path(self, personality: WalkerPersonality) -> None:
        """Follow a path and add mountains according to a personality."""
        stack_path = LinkedStack()
        stack_path.push(self.store)

        while not stack_path.is_empty():

            current_store = stack_path.pop()

            if current_store.__class__.__name__ == "TrailSeries":
                personality.add_mountain(current_store.mountain)
                if current_store.following.store is not None:
                    stack_path.push(current_store.following.store)

            else:
                if current_store is not None:

                    stack_path.push(current_store.path_follow.store)

                    if personality.select_branch(current_store.path_top, current_store.path_bottom):
                        stack_path.push(current_store.path_top.store)
                    else:
                        stack_path.push(current_store.path_bottom.store)

    def collect_all_mountains(self) -> list[Mountain]:
        """Returns a list of all mountains on the trail."""
        raise NotImplementedError()

    def length_k_paths(self, k) -> list[list[Mountain]]: # Input to this should not exceed k > 50, at most 5 branches.
        """
        Returns a list of all paths of containing exactly k mountains.
        Paths are represented as lists of mountains.

        Paths are unique if they take a different branch, even if this results in the same set of mountains.
        """
        raise NotImplementedError()
