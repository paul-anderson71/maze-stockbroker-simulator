import maze_stockbroker_classes as ms_classes
import maze_stockbroker_gui as ms_gui

MAZE_WIDTH = 6
MAZE_HEIGHT = 6
INITIAL_STOCKS = {
    "FOO": 10000,
    "BAR": 10000,
    "BAZ": 10000,
    "QUZ": 10000
}
INITIAL_MONEY = 100000

if __name__ == "__main__":
    game = ms_classes.Game(MAZE_WIDTH, MAZE_HEIGHT, INITIAL_STOCKS, INITIAL_MONEY)
    gui = ms_gui.MainWindow(game)
