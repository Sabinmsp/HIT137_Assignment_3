# Spot The Difference Game

HIT137 Group Assignment 3 — Semester 1, 2026
Charles Darwin University

A Tkinter desktop game that loads an image, programmatically introduces five
hidden differences using OpenCV, and lets the player find them by clicking.

## Group: DAN/EXT 24

| Name                                 | File(s) Edited       | Contribution                                                                 |
|--------------------------------------|----------------------|------------------------------------------------------------------------------|
| Sabin Man Singh Pradhan (s401417)    | `game.py`            | Tkinter GUI: layout, click binding to modified canvas only, cumulative score, win logic, reveal and reset buttons, status updates |
| Nishant Shrestha (s400342)           | `main.py`            | Application entry point, Tk root window setup, launch sequence, fixed syntax error |
| Karan Pandey (s403497)               | `alterations.py`     | OOP refactor: Alteration base class with three subclasses (ColorShift, Blur, Patch), inheritance and polymorphism |
| Sabraham Shrestha (s404389)          | `image_processor.py` | Image resizing, non-overlapping region generation, polymorphic alteration dispatch |

GitHub repository: https://github.com/Sabinmsp/HIT137_Assignment_3

## Features

- Side-by-side display of original and modified images
- Three distinct alteration types implemented with OpenCV:
  - **Colour Shift** — partial colour blend over a circular region
  - **Blur** — Gaussian blur applied to a square region
  - **Patch** — clone-stamp replacement using a nearby image patch
- Exactly five non-overlapping differences generated at random positions
- Only the modified (right) image responds to clicks
- Cumulative score across image loads, per-round counter for the win check
- Maximum three mistakes per round with a clear lockout prompt
- "Reveal Remaining" button marks unfound differences in blue
- "Reset Game" button regenerates the same image with new differences

## Object-Oriented Design

The codebase is organised into four classes across three modules:

- `Alteration` (base class, `alterations.py`) — defines the common interface
  `apply(image)` and shared state (`x`, `y`, `radius`, `found`).
- `ColorShiftAlteration`, `BlurAlteration`, `PatchAlteration` — three subclasses
  that inherit from `Alteration` and each override `apply()` polymorphically.
- `ImageProcessor` (`image_processor.py`) — generates non-overlapping alterations
  and calls them polymorphically through the shared `apply()` method.
- `SpotDifferenceGame` (`game.py`) — Tkinter GUI controller; holds an
  `ImageProcessor` instance (class composition) and manages game state.

This structure demonstrates encapsulation, constructors, methods, class
interaction, **inheritance**, and **polymorphism** as required by the brief.

## Requirements

- Python 3.9 or newer
- Tk 8.6 or newer (bundled with most modern Python installs)
- Packages listed in `requirements.txt` (`numpy`, `opencv-python`, `Pillow`)

## How to Run

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

On macOS, avoid `/usr/bin/python3` if it uses Tk 8.5. Install a modern Python
from python.org or via Homebrew.

## Files

```
main.py              # Entry point — Nishant
game.py              # SpotDifferenceGame class (Tkinter GUI) — Sabin
image_processor.py   # ImageProcessor class — Sabraham
alterations.py       # Alteration base class + 3 subclasses — Karan
requirements.txt     # Python dependencies
github_link.txt      # Group repository URL
README.md            # This file
```
