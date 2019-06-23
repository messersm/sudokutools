from unittest import TestCase

from sudokutools.coordinates import the_box, the_column, the_part, the_row

BOXES_3x3 = (
    (0, 0, 0, 1, 1, 1, 2, 2, 2),
    (0, 0, 0, 1, 1, 1, 2, 2, 2),
    (0, 0, 0, 1, 1, 1, 2, 2, 2),
    (3, 3, 3, 4, 4, 4, 5, 5, 5),
    (3, 3, 3, 4, 4, 4, 5, 5, 5),
    (3, 3, 3, 4, 4, 4, 5, 5, 5),
    (6, 6, 6, 7, 7, 7, 8, 8, 8),
    (6, 6, 6, 7, 7, 7, 8, 8, 8),
    (6, 6, 6, 7, 7, 7, 8, 8, 8)
)

BOXES_5x2 = (
    (0, 0, 0, 0, 0, 1, 1, 1, 1, 1),
    (0, 0, 0, 0, 0, 1, 1, 1, 1, 1),
    (2, 2, 2, 2, 2, 3, 3, 3, 3, 3),
    (2, 2, 2, 2, 2, 3, 3, 3, 3, 3),
    (4, 4, 4, 4, 4, 5, 5, 5, 5, 5),
    (4, 4, 4, 4, 4, 5, 5, 5, 5, 5),
    (6, 6, 6, 6, 6, 7, 7, 7, 7, 7),
    (6, 6, 6, 6, 6, 7, 7, 7, 7, 7),
    (8, 8, 8, 8, 8, 9, 9, 9, 9, 9),
    (8, 8, 8, 8, 8, 9, 9, 9, 9, 9)
)

PARTS_3x3 = (
    (0, 1, 2, 0, 1, 2, 0, 1, 2),
    (3, 4, 5, 3, 4, 5, 3, 4, 5),
    (6, 7, 8, 6, 7, 8, 6, 7, 8),
    (0, 1, 2, 0, 1, 2, 0, 1, 2),
    (3, 4, 5, 3, 4, 5, 3, 4, 5),
    (6, 7, 8, 6, 7, 8, 6, 7, 8),
    (0, 1, 2, 0, 1, 2, 0, 1, 2),
    (3, 4, 5, 3, 4, 5, 3, 4, 5),
    (6, 7, 8, 6, 7, 8, 6, 7, 8)
)

PARTS_5x2 = (
    (0, 1, 2, 3, 4, 0, 1, 2, 3, 4),
    (5, 6, 7, 8, 9, 5, 6, 7, 8, 9),
    (0, 1, 2, 3, 4, 0, 1, 2, 3, 4),
    (5, 6, 7, 8, 9, 5, 6, 7, 8, 9),
    (0, 1, 2, 3, 4, 0, 1, 2, 3, 4),
    (5, 6, 7, 8, 9, 5, 6, 7, 8, 9),
    (0, 1, 2, 3, 4, 0, 1, 2, 3, 4),
    (5, 6, 7, 8, 9, 5, 6, 7, 8, 9),
    (0, 1, 2, 3, 4, 0, 1, 2, 3, 4),
    (5, 6, 7, 8, 9, 5, 6, 7, 8, 9)
)


class BoxTests(TestCase):
    def test_the_box(self):
        for example, width, height in ((BOXES_3x3, 3, 3), (BOXES_5x2, 5, 2)):
            boxes = [[] for i in range(len(example))]

            for row, columns in enumerate(example):
                for col, box in enumerate(columns):
                    boxes[box].append((row, col))

            for box, coords in enumerate(boxes):
                self.assertEqual(
                    coords, the_box(box, width=width, height=height))


class PartTests(TestCase):
    def test_the_part(self):
        for example, width, height in ((PARTS_3x3, 3, 3), (PARTS_5x2, 5, 2)):
            parts = [[] for i in range(len(example))]

            for row, columns in enumerate(example):
                for col, part in enumerate(columns):
                    parts[part].append((row, col))

            for part, coords in enumerate(parts):
                self.assertEqual(
                    coords, the_part(part, width=width, height=height))

