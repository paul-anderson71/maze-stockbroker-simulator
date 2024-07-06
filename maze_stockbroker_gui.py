import tkinter as tk

EIGHT_DIRS = [
    (-1, -1),
    (-1,  0),
    (-1,  1),
    ( 0, -1),
    ( 0,  0),
    ( 0,  1),
    ( 1, -1),
    ( 1,  0),
    ( 1,  1)
]
FARLOOK = {
    (-2,  0): (-1,  0),
    ( 2,  0): ( 1,  0),
    ( 0, -2): ( 0, -1),
    ( 0,  2): ( 0,  1)
}
STR_MISSING = "?"

def tuple_add(a, b):
    return tuple(a + b for a, b in zip(a, b))

class MazeFrame(tk.Frame):
    def __init__(self, *args):
        super().__init__(*args)
        self.heading = tk.Label(self, text="Maze view")
        self.heading.grid(row=0, column=0, columnspan=5)
        self.grid_stringvars = {
            drdc: tk.StringVar(self, STR_MISSING)
            for drdc in EIGHT_DIRS
        }
        self.grid_stringvars.update({
            drdc: tk.StringVar(self, STR_MISSING)
            for drdc in FARLOOK.keys()
        })
        self.grid_labels = {
            drdc: tk.Label(self, textvariable=stringvar, padx=16, pady=8)
            for drdc, stringvar in self.grid_stringvars.items()
        }
        for drdc, label in self.grid_labels.items():
            r, c = drdc
            label.grid(row=r+3, column=c+2) # row and column must be non-negative
        pass

    def update(self, maze, coord):
        #coord = (0, 0)
        STR_PLAYER = "@"
        STR_WALL = "#"
        STR_EMPTY = "."
        STR_UNKNOWN = " "
        adj_dirs = maze.get_adj(coord)
        for drdc in self.grid_stringvars.keys():
            if drdc == (0, 0):
                self.grid_stringvars[drdc].set(STR_PLAYER)
            elif abs(drdc[0]) == 1 and abs(drdc[1]) == 1:
                self.grid_stringvars[drdc].set(STR_WALL)
            elif abs(drdc[0]) == 2 or abs(drdc[1]) == 2:
                if FARLOOK[drdc] in adj_dirs.keys():
                    vendors = maze.nodes[adj_dirs[FARLOOK[drdc]]].vendors
                    if vendors:
                        self.grid_stringvars[drdc].set("\n".join(vendors))
                    else:
                        self.grid_stringvars[drdc].set(STR_EMPTY)
                else:
                    self.grid_stringvars[drdc].set(STR_UNKNOWN)
            else:
                if drdc in adj_dirs.keys():
                    self.grid_stringvars[drdc].set(STR_EMPTY)
                else:
                    self.grid_stringvars[drdc].set(STR_WALL)

    def move(self, traveler, direction):
        traveler.maybe_move(direction)
        self.update(traveler.maze, traveler.position)
        pass

class StockFrame(tk.Frame):
    def __init__(self, *args):
        super().__init__(*args)
        self.money_text = tk.StringVar(self, STR_MISSING)
        self.portfolio_text = tk.StringVar(self, STR_MISSING)
        self.stockmarket_text = tk.StringVar(self, STR_MISSING)
        self.labels = [None, None, None, None, None]
        self.labels[0] = tk.Label(self, text="Stockmarket")
        self.labels[1] = tk.Label(self, text="Your assets:")
        self.labels[2] = tk.Label(self, textvariable=self.portfolio_text)
        self.labels[3] = tk.Label(self, text="Current stock prices:")
        self.labels[4] = tk.Label(self, textvariable=self.stockmarket_text)
        for label in self.labels:
            label.pack()
        pass
        
    def update(self, portfolio):
        self.portfolio_text.set(str(portfolio))
        self.stockmarket_text.set(str(portfolio.stockmarket))
        pass

class TaskFrame(tk.Frame):
    def __init__(self, *args):
        super().__init__(*args)
        self.task_text = tk.StringVar(self, STR_MISSING)
        self.heading = tk.Label(self, text="Current objective:")
        self.heading.pack()
        self.label = tk.Label(self, textvariable=self.task_text)
        self.label.pack()

    def update(self, task, stock, amount):
        task.maybe_fulfil(stock, amount)
        self.task_text.set(str(task))

class TradeFrame(tk.Frame):
    def __init__(self, *args):
        super().__init__(*args)
        self.buttons = []
        self.stock_frame = None
    
    def set_frame_refs(self, stock_frame, task_frame):
        self.stock_frame = stock_frame
        self.task_frame = task_frame

    def update(self, portfolio, traveler, task):
        for button in self.buttons:
            button.destroy()
        vendors = traveler.maze.nodes[traveler.position].vendors
        for stock in vendors:
            buy = tk.Button(self,
                          text=f"Buy {stock}",
                          command=(lambda: self.trade(portfolio, stock, 1, task)))
            buy.pack()
            self.buttons.append(buy)
            sell = tk.Button(self,
                          text=f"Sell {stock}",
                          command=(lambda:  self.trade(portfolio, stock, -1, task)))
            sell.pack()
            self.buttons.append(sell)

    def trade(self, portfolio, stock, amount, task):
        res = portfolio.maybe_trade(stock, amount)
        if res:
            if self.stock_frame:
                self.stock_frame.update(portfolio)
            if self.task_frame:
                self.task_frame.update(task, stock, amount)

class MainWindow:
    def __init__(self, game):
        root = tk.Tk()
        root.title("Maze Stockbroker Simulator")
        root.bind("q", (lambda _: root.destroy()))
        
        self.game = game
        self.maze_frame = MazeFrame(root)
        self.maze_frame.grid(row=0, column=0)
        self.maze_frame.update(self.game.maze, game.traveler.position)

        root.bind("w", (lambda _: self.maze_move((-1,  0))))
        root.bind("a", (lambda _: self.maze_move(( 0, -1))))
        root.bind("s", (lambda _: self.maze_move(( 1,  0))))
        root.bind("d", (lambda _: self.maze_move(( 0,  1))))

        self.stock_frame = StockFrame(root)
        self.stock_frame.grid(row=1, column=1)
        self.stock_frame.update(self.game.portfolio)

        self.task_frame = TaskFrame(root)
        self.task_frame.grid(row=0, column=1)
        self.task_frame.update(self.game.task, self.game.task.target, 0)

        self.trade_frame = TradeFrame(root)
        self.trade_frame.grid(row=1, column=0)
        self.trade_frame.set_frame_refs(self.stock_frame, self.task_frame)
        self.trade_frame.update(self.game.portfolio, self.game.traveler, self.game.task)
        
        self.help_label = tk.Label(
            root,
            text="Use WASD to move. Find traders to buy/sell.")
        self.help_label.grid(row=2, column=0, columnspan=2)
        
        root.mainloop()

    def maze_move(self, direction):
        self.maze_frame.move(self.game.traveler, direction)
        self.tick()
        self.trade_frame.update(self.game.portfolio, self.game.traveler, self.game.task)

    def tick(self):
        self.game.stockmarket.random_update()
        self.stock_frame.update(self.game.portfolio)
