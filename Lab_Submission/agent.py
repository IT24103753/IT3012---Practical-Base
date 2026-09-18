import random
import math
from collections import deque
import heapq

class SearchAgent:
    """An agent that uses uninformed search algorithms (BFS, DFS, UCS) and informed search (A*) to find paths to food."""

    def __init__(self, algorithm='bfs'):
        self.algorithm = algorithm
        self.plan = []  # Holds the sequence of actions to execute
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

        # Step 1.1: Testing Checkpoint
        print(f"Testing Checkpoint - Manhattan: (0, 0) to (3, 4) -> {self.manhattan_distance((0, 0), (3, 4))}")
        print(f"Testing Checkpoint - Euclidean: (0, 0) to (3, 4) -> {self.euclidean_distance((0, 0), (3, 4))}")

    # Step 1.1: Implementing the Heuristic Functions
    def manhattan_distance(self, pos, goal):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        return math.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)

    # Step 1.2: Implementing A* Search
    def astar_search(self, start_pos, goal_pos, walls, grid_size, heuristic_type='manhattan'):
        pq = []
        reached_states = set()

        if heuristic_type == 'manhattan':
            h_cost = self.manhattan_distance(start_pos, goal_pos)
        else:
            h_cost = self.euclidean_distance(start_pos, goal_pos)

        g_cost = 0
        f_cost = g_cost + h_cost

        # Push the initial state: (f_cost, g_cost, current_pos, path_taken)
        heapq.heappush(pq, (f_cost, g_cost, start_pos, []))

        while pq:
            current_f, current_g, current_pos, path_taken = heapq.heappop(pq)

            if current_pos == goal_pos:
                return path_taken

            if current_pos in reached_states:
                continue

            reached_states.add(current_pos)

            for action, next_state, step_cost in self.get_successors(current_pos[0], current_pos[1], grid_size, walls):
                if next_state not in reached_states:
                    new_g = current_g + step_cost
                    
                    if heuristic_type == 'manhattan':
                        new_h = self.manhattan_distance(next_state, goal_pos)
                    else:
                        new_h = self.euclidean_distance(next_state, goal_pos)
                        
                    new_f = new_g + new_h
                    heapq.heappush(pq, (new_f, new_g, next_state, path_taken + [action]))

        return []

    def sense_and_act(self, percept: dict) -> str:
        # If the plan is empty, generate a new plan using the selected algorithm
        if not self.plan:
            if self.algorithm == 'bfs':
                self.plan = self.bfs_search(percept)
            elif self.algorithm == 'dfs':
                self.plan = self.dfs_search(percept)
            elif self.algorithm == 'ucs':
                self.plan = self.ucs_search(percept)
            # Step 1.3: Integrating A* into the Agent's Decision Loop
            elif self.algorithm == 'AStar':
                start_pos = percept['agent_pos']
                grid_size = percept['grid_size']
                walls = percept['walls']
                all_food = percept['all_food']

                if all_food:
                    # Find the closest food item to act as the goal_pos
                    closest_food = min(all_food, key=lambda f: self.manhattan_distance(start_pos, f))
                    self.plan = self.astar_search(start_pos, closest_food, walls, grid_size, 'manhattan')
            
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