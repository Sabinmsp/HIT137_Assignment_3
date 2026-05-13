import cv2
import numpy as np
import random
from difference import Difference


class ImageProcessor:
    def __init__(self):
        self.differences = []

    def resize_keep_ratio(self, image, max_width=500, max_height=500):
        h, w = image.shape[:2]
        scale = min(max_width / w, max_height / h)

        new_w = int(w * scale)
        new_h = int(h * scale)

        return cv2.resize(image, (new_w, new_h))

    def is_overlapping(self, x, y, radius):
        for diff in self.differences:
            distance = np.sqrt((x - diff.x) ** 2 + (y - diff.y) ** 2)

            if distance < radius + diff.radius + 40:
                return True

        return False

    def generate_differences(self, image):
        modified = image.copy()
        self.differences = []

        h, w = modified.shape[:2]

        difference_types = [
            "color_change",
            "missing_object",
            "blur_region"
        ]

        while len(self.differences) < 5:
            radius = random.randint(20, 35)

            x = random.randint(radius + 20, w - radius - 20)
            y = random.randint(radius + 20, h - radius - 20)

            if self.is_overlapping(x, y, radius):
                continue

            diff_type = random.choice(difference_types)

            if diff_type == "color_change":
                overlay = modified.copy()

                color = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255)
                )

                cv2.circle(overlay, (x, y), radius, color, -1)
                modified = cv2.addWeighted(overlay, 0.6, modified, 0.4, 0)

            elif diff_type == "missing_object":
                cv2.rectangle(
                    modified,
                    (x - radius, y - radius),
                    (x + radius, y + radius),
                    (255, 255, 255),
                    -1
                )

            elif diff_type == "blur_region":
                x1 = max(0, x - radius)
                y1 = max(0, y - radius)
                x2 = min(w, x + radius)
                y2 = min(h, y + radius)

                region = modified[y1:y2, x1:x2]
                blurred = cv2.GaussianBlur(region, (21, 21), 0)

                modified[y1:y2, x1:x2] = blurred

            self.differences.append(
                Difference(x, y, radius, diff_type)
            )

        return modified
