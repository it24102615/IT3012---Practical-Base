# agent.py

import random
from collections import deque
import heapq


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ["Up", "Down", "Left", "Right"]

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept["agent_pos"]

        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)


class SearchAgent:
    """Goal-based agent that uses BFS, DFS, or UCS to find food."""

    def __init__(self):
        # Complete sequence of actions to execute
        self.plan = []

        # Select search algorithm
        self.active_algo = "BFS"

    def get_neighbors(self, state, percept):
        """Return valid actions and resulting states from the current state."""

        x, y = state

        actions = [
            ("Up", (x, y + 1)),
            ("Down", (x, y - 1)),
            ("Left", (x - 1, y)),
            ("Right", (x + 1, y)),
        ]

        width, height = percept["grid_size"]
        walls = set(percept["walls"])

        neighbors = []

        for action, new_state in actions:

            nx, ny = new_state

            # Check grid boundaries
            if nx < 0 or nx >= width:
                continue

            if ny < 0 or ny >= height:
                continue

            # Check walls
            if new_state in walls:
                continue

            neighbors.append((action, new_state))

        return neighbors

    def bfs_search(self, start, goals, percept):
        """Breadth-First Search."""

        queue = deque()

        # Store state and path used to reach it
        queue.append((start, []))

        # Reached set prevents repeated states
        reached = {start}

        while queue:

            state, path = queue.popleft()

            # Goal test
            if state in goals:
                return path

            # Expand current state
            for action, new_state in self.get_neighbors(state, percept):

                if new_state not in reached:

                    reached.add(new_state)

                    new_path = path + [action]

                    queue.append((new_state, new_path))

        return []

    def dfs_search(self, start, goals, percept):
        """Depth-First Search."""

        stack = [(start, [])]

        # Reached set prevents repeated states
        reached = {start}

        while stack:

            state, path = stack.pop()

            # Goal test
            if state in goals:
                return path

            # Expand current state
            for action, new_state in self.get_neighbors(state, percept):

                if new_state not in reached:

                    reached.add(new_state)

                    new_path = path + [action]

                    stack.append((new_state, new_path))

        return []

    def ucs_search(self, start, goals, percept):
        """Uniform-Cost Search."""

        frontier = []

        # Counter prevents heap comparison problems when costs are equal
        counter = 0

        # (cost, counter, state, path)
        heapq.heappush(frontier, (0, counter, start, []))

        # Store the cheapest known cost for each state
        reached = {start: 0}

        while frontier:

            cost, _, state, path = heapq.heappop(frontier)

            # Goal test
            if state in goals:
                return path

            # Expand current state
            for action, new_state in self.get_neighbors(state, percept):

                new_cost = cost + 1

                if new_state not in reached or new_cost < reached[new_state]:

                    reached[new_state] = new_cost

                    counter += 1

                    new_path = path + [action]

                    heapq.heappush(frontier, (new_cost, counter, new_state, new_path))

        return []

    def sense_and_act(self, percept):
        """Create a complete plan and execute it one action at a time."""

        # Create a new plan only when the current plan is empty
        if not self.plan:

            # Current position will be supplied by the environment
            start = tuple(percept["agent_pos"])

            # Food locations are the goal states
            goals = set(percept["all_food"])

            # If there is no food left, stay
            if not goals:
                return "Stay"

            # Select the search algorithm
            if self.active_algo == "BFS":

                self.plan = self.bfs_search(start, goals, percept)

            elif self.active_algo == "DFS":

                self.plan = self.dfs_search(start, goals, percept)

            elif self.active_algo == "UCS":

                self.plan = self.ucs_search(start, goals, percept)

        # Execute the next action from the plan
        if self.plan:
            return self.plan.pop(0)

        # No path found
        return "Stay"
