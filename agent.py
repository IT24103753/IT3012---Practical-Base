# agent.py
import random
from collections import deque
import heapq
import math  # Step 1.1: Added for Euclidean distance calculation

class SearchAgent:
    """An agent that uses uninformed (BFS, DFS, UCS) and informed (A*) search algorithms to find paths to food."""

    def __init__(self, algorithm='astar'):
        self.algorithm = algorithm
        self.plan = []  # Holds the sequence of actions to execute
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    # STEP 1.1: Heuristic Functions
    def manhattan_distance(self, pos, goal):
        """Calculates h(n) = |x1 - x2| + |y1 - y2|"""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        """Calculates h(n) = sqrt((x1 - x2)^2 + (y1 - y2)^2)"""
        return math.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)

    # STEP 1.2: A* Search Algorithm
    def astar_search(self, start_pos, goal_pos, walls, grid_size, heuristic_type='manhattan'):
        pq = []
        reached_states = set()

        # Calculate initial heuristic
        if heuristic_type == 'manhattan':
            h_start = self.manhattan_distance(start_pos, goal_pos)
        else:
            h_start = self.euclidean_distance(start_pos, goal_pos)

        f_start = 0 + h_start
        # Priority Queue stores tuples of (f_cost, g_cost, current_position, path_taken)
        heapq.heappush(pq, (f_start, 0, start_pos, []))

        while pq:
            f_cost, g_cost, current_pos, path_taken = heapq.heappop(pq)

            if current_pos == goal_pos:
                return path_taken

            if current_pos in reached_states:
                continue
            reached_states.add(current_pos)

            for action, next_state, step_cost in self.get_successors(current_pos[0], current_pos[1], grid_size, walls):
                if next_state not in reached_states:
                    g_new = g_cost + step_cost
                    
                    if heuristic_type == 'manhattan':
                        h_new = self.manhattan_distance(next_state, goal_pos)
                    else:
                        h_new = self.euclidean_distance(next_state, goal_pos)

                    f_new = g_new + h_new
                    heapq.heappush(pq, (f_new, g_new, next_state, path_taken + [action]))

        return []

    # STEP 1.3: Updated Decision Loop
    def sense_and_act(self, percept: dict) -> str:
        # If the plan is empty, generate a new plan using the selected algorithm
        if not self.plan:
            algo = self.algorithm.lower()
            if algo == 'bfs':
                self.plan = self.bfs_search(percept)
            elif algo == 'dfs':
                self.plan = self.dfs_search(percept)
            elif algo == 'ucs':
                self.plan = self.ucs_search(percept)
            elif algo == 'astar':
                all_food = percept.get('all_food', set())
                if all_food:
                    start_pos = percept['agent_pos']
                    # Find nearest food target using Manhattan distance
                    closest_food = min(all_food, key=lambda f: self.manhattan_distance(start_pos, f))
                    self.plan = self.astar_search(
                        start_pos=start_pos,
                        goal_pos=closest_food,
                        walls=percept['walls'],
                        grid_size=percept['grid_size']
                    )

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
                successors.append((action, (nx, ny), 1))  # 1 is the uniform step cost
        return successors

    def bfs_search(self, percept):
        """Breadth-First Search: Finds the shortest path in terms of steps."""
        start = percept['agent_pos']
        grid_size = percept['grid_size']
        walls = percept['walls']
        all_food = percept['all_food']

        if not all_food:
            return []

        queue = deque([(start, [])])
        visited = set([start])

        while queue:
            current, path = queue.popleft()

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

        stack = [(start, [])]
        visited = set()

        while stack:
            current, path = stack.pop()

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

        pq = [(0, start, [])]
        visited = set()

        while pq:
            cost, current, path = heapq.heappop(pq)

            if current in visited:
                continue
            visited.add(current)

            if current in all_food:
                return path

            for action, next_state, step_cost in self.get_successors(current[0], current[1], grid_size, walls):
                if next_state not in visited:
                    heapq.heappush(pq, (cost + step_cost, next_state, path + [action]))
        return []