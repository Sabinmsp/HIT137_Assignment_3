"""
Image processing module for the Spot The Difference game.

The ImageProcessor class handles image resizing and is responsible for
generating exactly five non-overlapping differences on a copy of the
original image. It uses polymorphism: each chosen Alteration subclass
defines its own apply() behaviour, but ImageProcessor calls them through
the shared Alteration interface.
"""

import cv2
import numpy as np
import random

from alterations import (
    ColorShiftAlteration,
    BlurAlteration,
    PatchAlteration,
)


class ImageProcessor:
    """Generates non-overlapping image differences using polymorphic alterations.

    Attributes:
        differences (list[Alteration]): The five Alteration instances created
            for the current image. Each tracks its own position, radius, and
            found state.
    """

    # Available alteration subclasses. Adding a new one is as simple as
    # appending its class here -- the rest of the code uses them
    # polymorphically through the Alteration interface.
    ALTERATION_TYPES = [
        ColorShiftAlteration,
        BlurAlteration,
        PatchAlteration,
    ]

    def __init__(self):
        self.differences = []

    def resize_keep_ratio(self, image, max_width=500, max_height=500):
        """Resize image to fit within max_width x max_height, preserving ratio."""
        h, w = image.shape[:2]
        scale = min(max_width / w, max_height / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        return cv2.resize(image, (new_w, new_h))

    def is_overlapping(self, x, y, radius):
        """Return True if a region at (x, y, radius) overlaps any existing one.

        A 40 px buffer is added so even near-touching circles are rejected.
        """
        for diff in self.differences:
            distance = np.sqrt((x - diff.x) ** 2 + (y - diff.y) ** 2)
            if distance < radius + diff.radius + 40:
                return True
        return False

    def generate_differences(self, image):
        """Generate exactly 5 non-overlapping random alterations on a copy.

        Each iteration: pick a random position and radius, reject if it
        overlaps an existing region, otherwise pick a random Alteration
        subclass and apply it. Returns the modified image.
        """
        modified = image.copy()
        self.differences = []
        h, w = modified.shape[:2]

        # Loop until we have 5 non-overlapping alterations
        while len(self.differences) < 5:
            radius = random.randint(20, 35)
            # Keep the circle fully inside the image (with margin)
            x = random.randint(radius + 20, w - radius - 20)
            y = random.randint(radius + 20, h - radius - 20)

            if self.is_overlapping(x, y, radius):
                continue

            # Random subclass selection -- polymorphism in action
            AlterationClass = random.choice(self.ALTERATION_TYPES)
            alteration = AlterationClass(x, y, radius)

            # Polymorphic call: each subclass implements apply() differently
            modified = alteration.apply(modified)

            self.differences.append(alteration)

        return modified
