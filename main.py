"""
Entry point for the Spot The Difference game.

Creates the Tk root window, instantiates the SpotDifferenceGame controller,
and starts the Tk event loop.
"""

import tkinter as tk
from game import SpotDifferenceGame


def main():
    """Launch the game."""
    root = tk.Tk()
    SpotDifferenceGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()