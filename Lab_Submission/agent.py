# agent.py
import random
from collections import deque
import heapq

class SearchAgent:
    """An agent that uses uninformed search algorithms (BFS, DFS, UCS) to find paths to food."""

    def __init__(self, algorithm='bfs'):
        self.algorithm = algorithm
        self.plan = []  # Holds the sequence of actions to execute
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If the plan is empty, generate a new plan using the selected algorithm
        if not self.plan:
            if self.algorithm == 'bfs':
                self.plan = self.bfs_search(percept)
            elif self.algorithm == 'dfs':
                self.plan = self.dfs_search(percept)
            elif self.algorithm == 'ucs':
                self.plan = self.ucs_search(percept)
            
            # Fallback if no path is found (e.g., trapped or no food left)
            if not self.plan:
                return 'Stay'

        # Execute the next step in the plan
        return self.plan.pop(0)

    def get_successors(self, x, y, grid_size, walls):
        """Generates valid next states (moves) from the current position."""
        width, height = grid_size
        successors = []
        moves = {'Up': (0, 1), 'Down': (0, -1), 'Left': (-1, 0), 'Right': (1, 0)}
        
        for action, (dx, dy) in moves.items():
            nx, ny = x + dx, y + dy
            # Check boundaries and walls
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls:
                successors.append((action, (nx, ny), 1)) # 1 is the uniform step cost
        return successors

    def bfs_search(self, percept):
        """Breadth-First Search: Finds the shortest path in terms of steps."""
        start = percept['agent_pos']
        grid_size = percept['grid_size']
        walls = percept['walls']
        all_food = percept['all_food']

        if not all_food:
            return []

        # Queue stores tuples of (current_position, path_of_actions)
        queue = deque([(start, [])])
        visited = set([start])

        while queue:
            current, path = queue.popleft()

            # Goal test
            if current in all_food:
                return path

            for action, next_state, _ in self.get_successors(current[0], current[1], grid_size, walls):
                if next_state not in visited:
                    visited.add(next_state)
                    queue.append((next_state, path + [action]))
        return []

    def dfs_search(self, percept):
        """Depth-First Search: Explores as deep as possible before backtracking."""
        start = percept['agent_pos']
        grid_size = percept['grid_size']
        walls = percept['walls']
        all_food = percept['all_food']

        if not all_food:
            return []

        # Stack stores tuples of (current_position, path_of_actions)
        stack = [(start, [])]
        visited = set()

        while stack:
            current, path = stack.pop()

            # Goal test
            if current in all_food:
                return path

            if current not in visited:
                visited.add(current)
                for action, next_state, _ in self.get_successors(current[0], current[1], grid_size, walls):
                    if next_state not in visited:
                        stack.append((next_state, path + [action]))
        return []

    def ucs_search(self, percept):
        """Uniform Cost Search: Expands the lowest cost path first."""
        start = percept['agent_pos']
        grid_size = percept['grid_size']
        walls = percept['walls']
        all_food = percept['all_food']

        if not all_food:
            return []

        # Priority Queue stores tuples of (cumulative_cost, current_position, path_of_actions)
        pq = [(0, start, [])]
        visited = set()

        while pq:
            cost, current, path = heapq.heappop(pq)

            if current in visited:
                continue
            visited.add(current)

            # Goal test
            if current in all_food:
                return path

            for action, next_state, step_cost in self.get_successors(current[0], current[1], grid_size, walls):
                if next_state not in visited:
                    heapq.heappush(pq, (cost + step_cost, next_state, path + [action]))
        return []