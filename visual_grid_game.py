import random
import tkinter as tk
from agent import SearchAgent  # Import the new Search Agent

# STEP 1.2: Simple Reflex Agent
class SimpleReflexAgent:
    """Agent that acts purely on instinct without memory."""
    def sense_and_act(self, percept):
        wall_ahead = percept['wall_ahead']
        facing = percept['facing']

        left_turns = {'Up': 'Left', 'Left': 'Down', 'Down': 'Right', 'Right': 'Up'}

        if wall_ahead:
            return left_turns[facing]  
        else:
            return facing  

# STEP 1.3: Model-Based Agent
class ModelBasedAgent:
    """Agent with an internal memory state."""
    def __init__(self):
        self.visited_cells = set()
        self.local_x = 0
        self.local_y = 0

    def sense_and_act(self, percept):
        wall_ahead = percept['wall_ahead']
        facing = percept['facing']

        self.visited_cells.add((self.local_x, self.local_y))

        left_turns = {'Up': 'Left', 'Left': 'Down', 'Down': 'Right', 'Right': 'Up'}
        right_turns = {'Up': 'Right', 'Right': 'Down', 'Down': 'Left', 'Left': 'Up'}

        left_dir = left_turns[facing]
        lx, ly = self.local_x, self.local_y
        if left_dir == 'Up': ly += 1
        elif left_dir == 'Down': ly -= 1
        elif left_dir == 'Left': lx -= 1
        elif left_dir == 'Right': lx += 1
        
        left_is_visited = (lx, ly) in self.visited_cells

        if wall_ahead and left_is_visited:
            action = right_turns[facing]  
        elif wall_ahead:
            action = left_turns[facing]   
        else:
            action = facing               

        if action == 'Up': self.local_y += 1
        elif action == 'Down': self.local_y -= 1
        elif action == 'Left': self.local_x -= 1
        elif action == 'Right': self.local_x += 1

        return action


class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, num_traps=3, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]  
        self.facing = 'Up'       

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            self.walls = {(2, 2), (2, 3), (2, 4), (3, 2), (4, 2), (4, 3), (4, 4)}

        self.food_positions = set()
        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            pos_tuple = (fx, fy)
            if pos_tuple != (0, 0) and pos_tuple not in self.walls:
                self.food_positions.add(pos_tuple)

        self.toxic_traps = set()
        while len(self.toxic_traps) < num_traps:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)
            trap_pos = (tx, ty)
            if (
                trap_pos != (0, 0)
                and trap_pos not in self.walls
                and trap_pos not in self.food_positions
            ):
                self.toxic_traps.add(trap_pos)

        self.opponents = []
        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)
            op_pos = [ox, oy]
            if tuple(op_pos) != (0, 0) and tuple(op_pos) not in self.walls and tuple(op_pos) not in self.food_positions:
                self.opponents.append(op_pos)

        self.score = 0
        self.steps = 0
        self.collision = False

    # Updated for Full Observability required by Search Algorithms
    def get_percept(self) -> dict:
        """Returns global state for Search Algorithms."""
        ax, ay = self.agent_pos
        hx, hy = ax, ay

        if self.facing == 'Up': hy += 1
        elif self.facing == 'Down': hy -= 1
        elif self.facing == 'Left': hx -= 1
        elif self.facing == 'Right': hx += 1

        wall_ahead = (hx, hy) in self.walls or hx < 0 or hx >= self.width or hy < 0 or hy >= self.height
        food_here = tuple(self.agent_pos) in self.food_positions

        return {
            'wall_ahead': wall_ahead,
            'food_here': food_here,
            'facing': self.facing,
            'agent_pos': tuple(self.agent_pos),       # Start state for search
            'grid_size': (self.width, self.height),   # Boundaries
            'walls': self.walls.copy(),               # Obstacles
            'all_food': self.food_positions.copy()    # Goal states
        }

    def execute_action(self, action: str):
        self.steps += 1
        self.facing = action  
        new_pos = list(self.agent_pos)

        if action == 'Up':
            new_pos[1] = min(self.height - 1, new_pos[1] + 1)
        elif action == 'Down':
            new_pos[1] = max(0, new_pos[1] - 1)
        elif action == 'Left':
            new_pos[0] = max(0, new_pos[0] - 1)
        elif action == 'Right':
            new_pos[0] = min(self.width - 1, new_pos[0] + 1)

        if tuple(new_pos) in self.walls:
            self.score -= 5
        else:
            self.agent_pos = new_pos

        tuple_pos = tuple(self.agent_pos)
        if tuple_pos in self.food_positions:
            self.food_positions.remove(tuple_pos)
            self.score += 20

        if tuple_pos in self.toxic_traps:
            self.score -= 15

        for op in self.opponents:
            move = random.choice(['Up', 'Down', 'Left', 'Right', 'Stay'])
            if move == 'Up' and op[1] < self.height - 1:
                op[1] += 1
            elif move == 'Down' and op[1] > 0:
                op[1] -= 1
            elif move == 'Left' and op[0] > 0:
                op[0] -= 1
            elif move == 'Right' and op[0] < self.width - 1:
                op[0] += 1

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 100 or self.collision


class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, walls=None):
        self.root = root
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")

        self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food, num_opponents=num_opponents, custom_walls=walls)

        # Initialize the Search Agent. Changed algorithm to 'AStar' as per Step 1.3
        self.agent = SearchAgent(algorithm='AStar')  
        
        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#000066", fg="white")
        self.btn.pack(pady=5)

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")

        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1")

                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text="W", fill="white", font=("Arial", 8, "bold"))

        for tx, ty in self.env.toxic_traps:
            offset = self.cell_size * 0.2
            x1 = tx * self.cell_size + offset
            y1 = (self.env.height - 1 - ty) * self.cell_size + offset
            self.canvas.create_oval(
                x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6,
                fill="#a855f7", outline="#7e22ce"
            )

        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b", outline="#d97706")

        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6, fill="#990000", outline="#7a0000")

        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066", outline="#1e3a8a")

    def run_loop(self):
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():
                percept = self.env.get_percept()
                
                action = self.agent.sense_and_act(percept)
                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}")
                
                self.root.after(300, step)
            else:
                end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}"
                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()

if __name__ == "__main__":
    root = tk.Tk()
    app = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=0)
    root.mainloop()