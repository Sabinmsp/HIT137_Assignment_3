import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np

from image_processor import ImageProcessor


class SpotDifferenceGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Spot The Difference Game")
        self.root.geometry("1200x700")

        self.processor = ImageProcessor()

        self.original_image = None
        self.modified_image = None

        self.original_tk = None
        self.modified_tk = None

        self.score = 0
        self.mistakes = 0
        self.max_mistakes = 3
        self.game_over = False

        self.setup_ui()

    def setup_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        self.load_button = tk.Button(
            top_frame,
            text="Load Image",
            font=("Arial", 14, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=15,
            pady=8,
            command=self.load_image
        )
        self.load_button.grid(row=0, column=0, padx=10)

        self.reveal_button = tk.Button(
            top_frame,
            text="Reveal Remaining",
            font=("Arial", 14, "bold"),
            bg="#2196F3",
            fg="white",
            padx=15,
            pady=8,
            command=self.reveal_remaining
        )
        self.reveal_button.grid(row=0, column=1, padx=10)

        self.reset_button = tk.Button(
            top_frame,
            text="Reset Game",
            font=("Arial", 14, "bold"),
            bg="#FF9800",
            fg="white",
            padx=15,
            pady=8,
            command=self.reset_game
        )
        self.reset_button.grid(row=0, column=2, padx=10)

        self.info_label = tk.Label(
            self.root,
            text="Load an image to start the game",
            font=("Arial", 16, "bold")
        )
        self.info_label.pack(pady=10)

        image_frame = tk.Frame(self.root)
        image_frame.pack()

        left_frame = tk.Frame(image_frame)
        left_frame.grid(row=0, column=0, padx=15)

        right_frame = tk.Frame(image_frame)
        right_frame.grid(row=0, column=1, padx=15)

        tk.Label(
            left_frame,
            text="Original Image",
            font=("Arial", 14, "bold")
        ).pack()

        tk.Label(
            right_frame,
            text="Modified Image",
            font=("Arial", 14, "bold")
        ).pack()

        self.original_canvas = tk.Canvas(
            left_frame,
            width=500,
            height=500,
            bg="lightgray"
        )
        self.original_canvas.pack()

        self.modified_canvas = tk.Canvas(
            right_frame,
            width=500,
            height=500,
            bg="lightgray"
        )
        self.modified_canvas.pack()

        self.original_canvas.bind("<Button-1>", self.check_click)
        self.modified_canvas.bind("<Button-1>", self.check_click)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png *.bmp")
            ]
        )

        if not file_path:
            return

        image = cv2.imread(file_path)

        if image is None:
            messagebox.showerror("Error", "Could not load image")
            return

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = self.processor.resize_keep_ratio(image)

        self.original_image = image.copy()
        self.modified_image = self.processor.generate_differences(image)

        self.score = 0
        self.mistakes = 0
        self.game_over = False

        self.update_status()
        self.display_images()

    def display_images(self):
        original_display = self.original_image.copy()
        modified_display = self.modified_image.copy()

        for diff in self.processor.differences:
            if diff.found:
                cv2.circle(
                    original_display,
                    (diff.x, diff.y),
                    diff.radius + 8,
                    (255, 0, 0),
                    3
                )

                cv2.circle(
                    modified_display,
                    (diff.x, diff.y),
                    diff.radius + 8,
                    (255, 0, 0),
                    3
                )

        self.show_image(original_display, self.original_canvas, "original")
        self.show_image(modified_display, self.modified_canvas, "modified")

    def show_image(self, image, canvas, side):
        h, w = image.shape[:2]

        pil_image = Image.fromarray(image)
        tk_image = ImageTk.PhotoImage(pil_image)

        canvas.delete("all")

        x = (500 - w) // 2
        y = (500 - h) // 2

        canvas.create_image(x, y, anchor=tk.NW, image=tk_image)

        if side == "original":
            self.original_tk = tk_image
        else:
            self.modified_tk = tk_image

    def check_click(self, event):
        if self.game_over:
            return

        if self.original_image is None:
            return

        img_h, img_w = self.original_image.shape[:2]

        offset_x = (500 - img_w) // 2
        offset_y = (500 - img_h) // 2

        click_x = event.x - offset_x
        click_y = event.y - offset_y

        correct_click = False

        for diff in self.processor.differences:
            if diff.found:
                continue

            distance = np.sqrt(
                (click_x - diff.x) ** 2 +
                (click_y - diff.y) ** 2
            )

            if distance <= diff.radius + 15:
                diff.found = True
                self.score += 1
                correct_click = True
                break

        if not correct_click:
            self.mistakes += 1

            if self.mistakes >= self.max_mistakes:
                self.game_over = True
                messagebox.showwarning(
                    "Game Over",
                    "You reached 3 mistakes"
                )

        if self.score == 5:
            self.game_over = True
            messagebox.showinfo(
                "Congratulations",
                "You found all 5 differences!"
            )

        self.update_status()
        self.display_images()

    def reveal_remaining(self):
        if self.original_image is None:
            return

        original_display = self.original_image.copy()
        modified_display = self.modified_image.copy()

        for diff in self.processor.differences:
            if not diff.found:
                cv2.circle(
                    original_display,
                    (diff.x, diff.y),
                    diff.radius + 8,
                    (0, 0, 255),
                    4
                )

                cv2.circle(
                    modified_display,
                    (diff.x, diff.y),
                    diff.radius + 8,
                    (0, 0, 255),
                    4
                )

                diff.found = True

        self.score = 5
        self.game_over = True

        self.update_status()

        self.show_image(original_display, self.original_canvas, "original")
        self.show_image(modified_display, self.modified_canvas, "modified")

    def reset_game(self):
        if self.original_image is None:
            return

        self.modified_image = self.processor.generate_differences(
            self.original_image
        )

        self.score = 0
        self.mistakes = 0
        self.game_over = False

        self.update_status()
        self.display_images()

    def update_status(self):
        remaining = 5 - self.score

        self.info_label.config(
            text=
            f"Score: {self.score}/5    "
            f"Remaining: {remaining}    "
            f"Mistakes: {self.mistakes}/3"
        )
