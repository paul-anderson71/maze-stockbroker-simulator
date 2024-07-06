import random

# Tuple here is row, col
DIR_NONE  = ( 0,  0)
DIR_LEFT  = ( 0, -1)
DIR_RIGHT = ( 0,  1)
DIR_UP    = (-1,  0)
DIR_DOWN  = ( 1,  0)
DIR_ALL = [DIR_LEFT, DIR_RIGHT, DIR_UP, DIR_DOWN]
INVALID_COORD = (-1, -1)

def tuple_add(a, b):
    return tuple(i + j for i, j in zip(a, b))

class MazeNode:
    def __init__(self):
        self.parent = DIR_NONE
        self.vendors = set()

class Maze:
    def __init__(self, width, height):
        self.nodes = dict()
        self.root = None
        self.width = width
        self.height = height
        for r in range(height):
            for c in range(width):
                self.nodes[(r, c)] = MazeNode()
                if c > 0:
                    self.nodes[(r, c)].parent = DIR_LEFT
                elif r > 0:
                    self.nodes[(r, c)].parent = DIR_UP
                else:
                    self.nodes[(r, c)].parent = DIR_NONE
                    self.root = (r, c)
        assert len(self.nodes) == width * height
        assert self.root != None
        assert INVALID_COORD not in self.nodes.keys()
        self._shuffle()
        pass

    def _shuffle(self):
        for _ in range(self.width * self.height * 5):
            self._step_root()
        pass
    
    def _step_root(self):
        assert len(self.nodes) > 1
        new_root = (-1, -1)
        while not self.valid_coord(new_root):
            drdc = random.choice(DIR_ALL)
            new_root = tuple_add(self.root, drdc)
        self.nodes[self.root].parent = drdc
        self.nodes[new_root].parent = DIR_NONE
        self.root = new_root
        pass

    def valid_coord(self, coord):
        return coord in self.nodes.keys()

    def _is_adj(self, a, b):
        if (a not in self.nodes.keys()) or (b not in self.nodes.keys()):
            return False
        return (
            tuple_add(self.nodes[a].parent, a) == b
        or
            tuple_add(self.nodes[b].parent, b) == a
        )

    def get_adj(self, coord):
        return {
            drdc: tuple_add(coord, drdc)
            for drdc in DIR_ALL
            if self._is_adj(coord, tuple_add(coord, drdc))
        }

    def add_vendor(self, vendor):
        self.nodes[self.random_position()].vendors.add(vendor)
        pass

    def random_position(self):
        return random.choice(list(self.nodes.keys()))

    def __str__(self):
        result = []
        STR_WALL = "#"
        STR_EMPTY = "."
        STR_VENDOR = "$"
        result.append(STR_WALL * ((2 * self.width) + 1)) # top wall
        result.append("\n")
        for r in range(self.height):
            result.append(STR_WALL) # left wall
            for c in range(self.width):
                if self.nodes[(r, c)].vendors:
                    result.append(STR_VENDOR)
                else:
                    result.append(STR_EMPTY)
                if DIR_RIGHT in self.get_adj((r, c)).keys():
                    result.append(STR_EMPTY)
                else:
                    result.append(STR_WALL)
            result.append("\n" + STR_WALL) # left wall
            for c in range(self.width):
                if DIR_DOWN in self.get_adj((r, c)).keys():
                    result.append(STR_EMPTY)
                else:
                    result.append(STR_WALL)
                result.append(STR_WALL)
            result.append("\n")
        return "".join(result)

class Traveler:
    def __init__(self, maze):
        self.maze = maze
        self.position = maze.random_position()

    def maybe_move(self, direction):
        adj_coords = self.maze.get_adj(self.position)
        if direction in adj_coords:
            self.position = adj_coords[direction]
            return True
        else:
            return False

    def can_trade(self, stock_name):
        return (stock_name in self.maze.nodes[self.position].vendors)

class Stockmarket:
    def __init__(self, initial_stocks):
        self.stocks = initial_stocks.copy()
        pass

    def random_update(self):
        SIGMA = 0.025 # about 95% of changes will be within 2*SIGMA
        self.stocks = {
            stock: max(0, int(random.gauss(1, SIGMA) * price))
            for stock, price in self.stocks.items()
        }
        pass
        
    def __str__(self):
        return "\n".join(
            f"{stock}: {price/100:.2f}"
            for stock, price in self.stocks.items()
        )

class Portfolio:
    def __init__(self, stockmarket, initial_money):
        self.stockmarket = stockmarket
        self.money = initial_money
        self.shares = {
            name: 0
            for name in stockmarket.stocks.keys()
        }
        pass

    def maybe_trade(self, name, amount): # positive amount = buying
        if amount + self.shares.get(name, 0) < 0:
            return False # Can't sell shares you don't have
        share_cost = self.stockmarket.stocks[name] * amount
        if self.money - share_cost < 0:
            return False # Can't buy shares you can't afford
        self.shares[name] = self.shares.get(name, 0) + amount
        self.money = self.money - share_cost
        return True

    def __str__(self):
        result = []
        result.append(f"${self.money/100:.2f}")
        for name, amount in self.shares.items():
            result.append(f"{amount} share(s) of {name}")
        return "\n".join(result)

class Task:
    def __init__(self, stock_names):
        self.stock_names = list(stock_names)
        self.is_buy = False
        self.target = self.stock_names[0]
        self.new_task()
        
    def new_task(self):
        self.is_buy = random.choice([True, False])
        self.target = random.choice(self.stock_names)

    def maybe_fulfil(self, name, amount):
        if name == self.target and amount != 0:
            # positive amount = buying
            if (amount > 0) == self.is_buy:
                self.new_task()
                return True
        return False

    def __str__(self):
        result = []
        if self.is_buy:
            result.append("Buy")
        else:
            result.append("Sell")
        result.append(self.target)
        return " ".join(result)

class Game:
    def __init__(self, maze_width, maze_height, initial_stocks, initial_money):
        self.maze = Maze(maze_width, maze_height)
        for stock in initial_stocks.keys():
            self.maze.add_vendor(stock)
        self.traveler = Traveler(self.maze)
        self.stockmarket = Stockmarket(initial_stocks)
        self.portfolio = Portfolio(self.stockmarket, initial_money)
        self.task = Task(initial_stocks.keys())
