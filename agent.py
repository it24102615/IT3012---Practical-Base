# agent.py

import random
from collections import deque
import heapq
import math


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
    """Goal-based agent that uses BFS, DFS, UCS, or A* to find food."""

    def __init__(self):
        # Complete sequence of actions to execute
        self.plan = []

        # Select search algorithm
        self.active_algo = "AStar"

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

    def manhattan_distance(self, pos, goal):
        """Calculate Manhattan distance between two positions."""

        x1, y1 = pos
        x2, y2 = goal

        return abs(x1 - x2) + abs(y1 - y2)

    def euclidean_distance(self, pos, goal):
        """Calculate Euclidean distance between two positions."""

        x1, y1 = pos
        x2, y2 = goal

        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def astar_search(
        self, start_pos, goal_pos, walls, grid_size, heuristic_type="manhattan"
    ):
        """A* Search using f(n) = g(n) + h(n)."""

        print("A* Search Started")
        print("Start:", start_pos)
        print("Goal:", goal_pos)

        frontier = []

        reached_states = set()

        # Starting node
        g_cost = 0

        if heuristic_type == "manhattan":
            h_cost = self.manhattan_distance(start_pos, goal_pos)
        else:
            h_cost = self.euclidean_distance(start_pos, goal_pos)

        f_cost = g_cost + h_cost

        heapq.heappush(frontier, (f_cost, g_cost, start_pos, []))

        width, height = grid_size
        walls = set(walls)

        while frontier:

            f_cost, g_cost, current_pos, path_taken = heapq.heappop(frontier)

            # Goal test
            if current_pos == goal_pos:
                return path_taken

            # Do not expand an already reached state
            if current_pos in reached_states:
                continue

            reached_states.add(current_pos)

            x, y = current_pos

            actions = [
                ("Up", (x, y + 1)),
                ("Down", (x, y - 1)),
                ("Left", (x - 1, y)),
                ("Right", (x + 1, y)),
            ]

            for action, new_pos in actions:

                nx, ny = new_pos

                # Check grid boundaries
                if nx < 0 or nx >= width:
                    continue

                if ny < 0 or ny >= height:
                    continue

                # Check walls
                if new_pos in walls:
                    continue

                # Check reached states
                if new_pos in reached_states:
                    continue

                # Calculate g(n)
                new_g_cost = g_cost + 1

                # Calculate h(n)
                if heuristic_type == "manhattan":
                    new_h_cost = self.manhattan_distance(new_pos, goal_pos)
                else:
                    new_h_cost = self.euclidean_distance(new_pos, goal_pos)

                # Calculate f(n)
                new_f_cost = new_g_cost + new_h_cost

                new_path = path_taken + [action]

                heapq.heappush(frontier, (new_f_cost, new_g_cost, new_pos, new_path))

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

            elif self.active_algo == "AStar":

                # Select the closest food as the goal
                goal_pos = min(
                    goals, key=lambda food: self.manhattan_distance(start, food)
                )

                self.plan = self.astar_search(
                    start,
                    goal_pos,
                    percept["walls"],
                    percept["grid_size"],
                    heuristic_type="manhattan",
                )

        # Execute the next action from the plan
        if self.plan:
            return self.plan.pop(0)

        # No path found
        return "Stay"
