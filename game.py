"""
Tkinter GUI for the Spot The Difference game.

Displays the original and modified images side by side. Only the modified
image responds to player clicks. Tracks a cumulative score across multiple
rounds and a per-image mistake counter (max 3 mistakes before lockout).
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np

from image_processor import ImageProcessor


class SpotDifferenceGame:
    """Main game controller and GUI.

    Coordinates image loading, click validation, scoring, mistake tracking,
    and the reveal feature. Holds an ImageProcessor instance to generate
    and store the current round's Alteration objects.
    """

    DIFFS_PER_ROUND = 5
    MAX_MISTAKES = 3
    CANVAS_SIZE = 500

    def __init__(self, root):
        self.root = root
        self.root.title("Spot The Difference Game")
        self.root.geometry("1200x700")

        self.processor = ImageProcessor()

        # Image state
        self.original_image = None
        self.modified_image = None
        self.original_tk = None
        self.modified_tk = None

        # Game state
        # NOTE: score is cumulative across image loads (per brief).
        # found_this_round resets on each new image and triggers the win.
        self.score = 0
        self.found_this_round = 0
        self.mistakes = 0
        self.game_over = False

        self.setup_ui()

    def setup_ui(self):
        """Build the Tkinter widgets and bind events."""
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        self.load_button = tk.Button(
            top_frame, text="Load Image",
            font=("Arial", 14, "bold"),
            bg="#4CAF50", fg="white", padx=15, pady=8,
            command=self.load_image,
        )
        self.load_button.grid(row=0, column=0, padx=10)

        self.reveal_button = tk.Button(
            top_frame, text="Reveal Remaining",
            font=("Arial", 14, "bold"),
            bg="#2196F3", fg="white", padx=15, pady=8,
            command=self.reveal_remaining,
        )
        self.reveal_button.grid(row=0, column=1, padx=10)

        self.reset_button = tk.Button(
            top_frame, text="Reset Game",
            font=("Arial", 14, "bold"),
            bg="#FF9800", fg="white", padx=15, pady=8,
            command=self.reset_game,
        )
        self.reset_button.grid(row=0, column=2, padx=10)

        self.info_label = tk.Label(
            self.root,
            text="Load an image to start the game",
            font=("Arial", 16, "bold"),
        )
        self.info_label.pack(pady=10)

        image_frame = tk.Frame(self.root)
        image_frame.pack()

        left_frame = tk.Frame(image_frame)
        left_frame.grid(row=0, column=0, padx=15)
        right_frame = tk.Frame(image_frame)
        right_frame.grid(row=0, column=1, padx=15)

        tk.Label(left_frame, text="Original Image",
                 font=("Arial", 14, "bold")).pack()
        tk.Label(right_frame, text="Modified Image",
                 font=("Arial", 14, "bold")).pack()

        self.original_canvas = tk.Canvas(
            left_frame, width=self.CANVAS_SIZE, height=self.CANVAS_SIZE,
            bg="lightgray",
        )
        self.original_canvas.pack()

        self.modified_canvas = tk.Canvas(
            right_frame, width=self.CANVAS_SIZE, height=self.CANVAS_SIZE,
            bg="lightgray",
        )
        self.modified_canvas.pack()

        # Per the brief: only the modified image responds to player clicks.
        # The original is for visual reference only.
        self.modified_canvas.bind("<Button-1>", self.check_click)

    def load_image(self):
        """Open a file dialog, load an image, and start a new round.

        The cumulative score is preserved; only per-round state resets.
        """
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not file_path:
            return

        image = cv2.imread(file_path)
        if image is None:
            messagebox.showerror("Error", "Could not load image")
            return

        # OpenCV loads BGR; convert to RGB for Pillow/Tkinter display
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = self.processor.resize_keep_ratio(image)

        self.original_image = image.copy()
        self.modified_image = self.processor.generate_differences(image)

        # Reset per-round state (mistakes and found-this-round) but
        # KEEP self.score so it accumulates across image loads.
        self.found_this_round = 0
        self.mistakes = 0
        self.game_over = False

        self.update_status()
        self.display_images()

    def display_images(self):
        """Redraw both canvases, circling any differences already found."""
        original_display = self.original_image.copy()
        modified_display = self.modified_image.copy()

        # Draw a red circle on found differences (both images, per brief)
        for diff in self.processor.differences:
            if diff.found:
                cv2.circle(original_display, (diff.x, diff.y),
                           diff.radius + 8, (255, 0, 0), 3)
                cv2.circle(modified_display, (diff.x, diff.y),
                           diff.radius + 8, (255, 0, 0), 3)

        self.show_image(original_display, self.original_canvas, "original")
        self.show_image(modified_display, self.modified_canvas, "modified")

    def show_image(self, image, canvas, side):
        """Render a numpy image onto a Tk canvas, centred."""
        h, w = image.shape[:2]
        pil_image = Image.fromarray(image)
        tk_image = ImageTk.PhotoImage(pil_image)

        canvas.delete("all")

        # Centre the image inside the canvas
        x = (self.CANVAS_SIZE - w) // 2
        y = (self.CANVAS_SIZE - h) // 2
        canvas.create_image(x, y, anchor=tk.NW, image=tk_image)

        # Hold a reference so Tk doesn't garbage-collect the image
        if side == "original":
            self.original_tk = tk_image
        else:
            self.modified_tk = tk_image

    def check_click(self, event):
        """Validate a click on the modified canvas against unfound regions."""
        if self.game_over or self.original_image is None:
            return

        img_h, img_w = self.original_image.shape[:2]

        # Convert canvas coords to image coords by removing the centring offset
        offset_x = (self.CANVAS_SIZE - img_w) // 2
        offset_y = (self.CANVAS_SIZE - img_h) // 2
        click_x = event.x - offset_x
        click_y = event.y - offset_y

        correct_click = False

        # Test the click against each unfound difference with a tolerance
        for diff in self.processor.differences:
            if diff.found:
                continue
            distance = np.sqrt((click_x - diff.x) ** 2
                               + (click_y - diff.y) ** 2)
            if distance <= diff.radius + 15:
                diff.found = True
                self.score += 1               # cumulative
                self.found_this_round += 1    # per-image
                correct_click = True
                break

        if not correct_click:
            self.mistakes += 1
            if self.mistakes >= self.MAX_MISTAKES:
                self.game_over = True
                messagebox.showwarning(
                    "Game Over",
                    f"You reached {self.MAX_MISTAKES} mistakes.\n"
                    f"Differences found this round: "
                    f"{self.found_this_round}/{self.DIFFS_PER_ROUND}.\n"
                    "Load a new image to continue."
                )

        # Win condition: all 5 found in the current round
        if self.found_this_round == self.DIFFS_PER_ROUND:
            self.game_over = True
            messagebox.showinfo(
                "Congratulations",
                f"You found all {self.DIFFS_PER_ROUND} differences!\n"
                "Load another image to keep playing."
            )

        self.update_status()
        self.display_images()

    def reveal_remaining(self):
        """Mark every unfound difference with a blue circle on both images."""
        if self.original_image is None:
            return

        original_display = self.original_image.copy()
        modified_display = self.modified_image.copy()

        for diff in self.processor.differences:
            if not diff.found:
                cv2.circle(original_display, (diff.x, diff.y),
                           diff.radius + 8, (0, 0, 255), 4)
                cv2.circle(modified_display, (diff.x, diff.y),
                           diff.radius + 8, (0, 0, 255), 4)
                diff.found = True

        # All differences in this round are now revealed
        self.found_this_round = self.DIFFS_PER_ROUND
        self.game_over = True

        self.update_status()
        self.show_image(original_display, self.original_canvas, "original")
        self.show_image(modified_display, self.modified_canvas, "modified")

    def reset_game(self):
        """Reset everything including cumulative score and regenerate diffs."""
        if self.original_image is None:
            return

        self.modified_image = self.processor.generate_differences(
            self.original_image
        )
        self.score = 0
        self.found_this_round = 0
        self.mistakes = 0
        self.game_over = False

        self.update_status()
        self.display_images()

    def update_status(self):
        """Refresh the info label with cumulative score and round state."""
        remaining = self.DIFFS_PER_ROUND - self.found_this_round
        self.info_label.config(
            text=(
                f"Total Score: {self.score}    "
                f"This Round: {self.found_this_round}/{self.DIFFS_PER_ROUND}    "
                f"Remaining: {remaining}    "
                f"Mistakes: {self.mistakes}/{self.MAX_MISTAKES}"
            )
        )