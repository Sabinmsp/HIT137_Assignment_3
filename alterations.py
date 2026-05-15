"""
Alteration classes for the Spot The Difference game.

This module defines a base Alteration class and three concrete subclasses
that each implement a different visual modification to an image region.
The classes demonstrate inheritance (all subclasses extend Alteration) and
polymorphism (each subclass overrides the apply() method with its own
behaviour while sharing a common interface).
"""

import cv2
import numpy as np
import random


class Alteration:
    """Base class for all image alterations.

    Stores the location and radius of a difference region and tracks whether
    the player has found it. Subclasses must override the apply() method to
    define how the region is visually modified.

    Attributes:
        x (int): X-coordinate of the alteration centre (image pixels).
        y (int): Y-coordinate of the alteration centre (image pixels).
        radius (int): Radius of the alteration region in pixels.
        found (bool): True once the player has correctly clicked this region.
    """

    def __init__(self, x, y, radius):
        # Encapsulated state for this alteration instance
        self.x = x
        self.y = y
        self.radius = radius
        self.found = False

    def apply(self, image):
        """Apply this alteration to the given image.

        This is the polymorphic entry point. Each subclass overrides this
        method to perform its own type of visual change. The base class
        raises NotImplementedError to enforce override.

        Args:
            image (np.ndarray): RGB image to modify (modified in place
                or returned).

        Returns:
            np.ndarray: The modified image.
        """
        raise NotImplementedError("Subclasses must implement apply()")

    @property
    def diff_type(self):
        """Human-readable name of this alteration type."""
        return self.__class__.__name__


class ColorShiftAlteration(Alteration):
    """Shifts the colour of a circular region by blending a random colour.

    The blend is partial (50/50) so the change is noticeable on careful
    inspection but not glaringly obvious, as required by the brief.
    """

    def apply(self, image):
        overlay = image.copy()
        # Pick a random RGB colour for the overlay circle
        colour = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )
        cv2.circle(overlay, (self.x, self.y), self.radius, colour, -1)
        # 50/50 blend keeps underlying texture visible
        return cv2.addWeighted(overlay, 0.5, image, 0.5, 0)


class BlurAlteration(Alteration):
    """Applies a Gaussian blur to a square region around (x, y).

    The blurred area subtly removes detail without changing colour,
    making it findable but not obvious.
    """

    def apply(self, image):
        h, w = image.shape[:2]
        # Clamp the region so we never index outside the image bounds
        x1 = max(0, self.x - self.radius)
        y1 = max(0, self.y - self.radius)
        x2 = min(w, self.x + self.radius)
        y2 = min(h, self.y + self.radius)

        region = image[y1:y2, x1:x2]
        image[y1:y2, x1:x2] = cv2.GaussianBlur(region, (21, 21), 0)
        return image


class PatchAlteration(Alteration):
    """Replaces a region with a nearby patch of the image (clone-stamp style).

    This is much subtler than overlaying a solid colour rectangle: the
    replacement blends in with the surrounding image, but careful comparison
    against the original reveals that an object or detail is missing.
    """

    def apply(self, image):
        h, w = image.shape[:2]
        r = self.radius

        # Choose a source patch offset from the target location
        # Offsets are clamped so the source rectangle stays inside the image
        sx = max(0, min(w - 2 * r, self.x + 60))
        sy = max(0, min(h - 2 * r, self.y + 60))

        patch = image[sy:sy + 2 * r, sx:sx + 2 * r].copy()

        # Make sure the destination rectangle is also in bounds
        dy1 = max(0, self.y - r)
        dx1 = max(0, self.x - r)
        dy2 = dy1 + patch.shape[0]
        dx2 = dx1 + patch.shape[1]

        # Only paste if the destination rectangle fits
        if dy2 <= h and dx2 <= w:
            image[dy1:dy2, dx1:dx2] = patch
        return image
