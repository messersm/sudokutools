from unittest import TestCase

from sudokutools.notation import decode, encode


RNCN_3x3 = (
    ("r1c1", "r1c2", "r1c3", "r1c4", "r1c5", "r1c6", "r1c7", "r1c8", "r1c9"),
    ("r2c1", "r2c2", "r2c3", "r2c4", "r2c5", "r2c6", "r2c7", "r2c8", "r2c9"),
    ("r3c1", "r3c2", "r3c3", "r3c4", "r3c5", "r3c6", "r3c7", "r3c8", "r3c9"),
    ("r4c1", "r4c2", "r4c3", "r4c4", "r4c5", "r4c6", "r4c7", "r4c8", "r4c9"),
    ("r5c1", "r5c2", "r5c3", "r5c4", "r5c5", "r5c6", "r5c7", "r5c8", "r5c9"),
    ("r6c1", "r6c2", "r6c3", "r6c4", "r6c5", "r6c6", "r6c7", "r6c8", "r6c9"),
    ("r7c1", "r7c2", "r7c3", "r7c4", "r7c5", "r7c6", "r7c7", "r7c8", "r7c9"),
    ("r8c1", "r8c2", "r8c3", "r8c4", "r8c5", "r8c6", "r8c7", "r8c8", "r8c9"),
    ("r9c1", "r9c2", "r9c3", "r9c4", "r9c5", "r9c6", "r9c7", "r9c8", "r9c9")
)

BNPN_3x3 = (
    ("b1p1", "b1p2", "b1p3", "b2p1", "b2p2", "b2p3", "b3p1", "b3p2", "b3p3"),
    ("b1p4", "b1p5", "b1p6", "b2p4", "b2p5", "b2p6", "b3p4", "b3p5", "b3p6"),
    ("b1p7", "b1p8", "b1p9", "b2p7", "b2p8", "b2p9", "b3p7", "b3p8", "b3p9"),
    ("b4p1", "b4p2", "b4p3", "b5p1", "b5p2", "b5p3", "b6p1", "b6p2", "b6p3"),
    ("b4p4", "b4p5", "b4p6", "b5p4", "b5p5", "b5p6", "b6p4", "b6p5", "b6p6"),
    ("b4p7", "b4p8", "b4p9", "b5p7", "b5p8", "b5p9", "b6p7", "b6p8", "b6p9"),
    ("b7p1", "b7p2", "b7p3", "b8p1", "b8p2", "b8p3", "b9p1", "b9p2", "b9p3"),
    ("b7p4", "b7p5", "b7p6", "b8p4", "b8p5", "b8p6", "b9p4", "b9p5", "b9p6"),
    ("b7p7", "b7p8", "b7p9", "b8p7", "b8p8", "b8p9", "b9p7", "b9p8", "b9p9"),
)


class EncodeTests(TestCase):
    def test_numbers_are_sorted(self):
        """Coordinates are always shown in a sorted order."""
        self.assertEqual("r1c12", encode(((0, 0), (0, 1))))
        self.assertEqual("r1c12", encode(((0, 1), (0, 0))))
        self.assertEqual("r12c1", encode(((0, 0), (1, 0))))
        self.assertEqual("r12c1", encode(((1, 0), (0, 0))))

    def test_groups_are_sorted(self):
        """Groups are sorted by the numbers of rows or boxes."""
        self.assertEqual("r1c1,r10c10", encode(
            ((0, 0), (9, 9)), width=2, height=5, use_boxes=False))
        self.assertEqual("r1c1,r10c10", encode(
            ((9, 9), (0, 0)), width=2, height=5, use_boxes=False))
        self.assertEqual("b1p1,b10p10", encode(
            ((0, 0), (9, 9)), width=2, height=5, use_boxes=True))
        self.assertEqual("b1p1,b10p10", encode(
            ((9, 9), (0, 0)), width=2, height=5, use_boxes=True))

    def test_default_number_sep(self):
        """Numbers > 9 are separated using the default separator."""
        self.assertEqual("r1c1,12", encode(((0, 0), (0, 11)), width=4, height=4))

    def test_custom_number_sep(self):
        """Numbers are separated by a custom separator."""
        self.assertEqual(
            "r1c1.2,r9c9", encode(((0, 0), (0, 1), (8, 8)), nsep="."))

    def test_default_group_sep(self):
        """Groups of coordinates are separated using the default separator."""
        self.assertEqual("r1c1,r9c9", encode(((0, 0), (8, 8))))

    def test_custom_group_sep(self):
        """Groups of coordinates are separated using a custom separator."""
        self.assertEqual(
            "r1c12, r9c9", encode(((0, 0), (0, 1), (8, 8)), sep=", "))

    def test_invalid_coordinates(self):
        """Using invalid coordinates raises a ValueError."""
        self.assertRaises(ValueError, encode, ((0, 9), ))
        self.assertRaises(ValueError, encode, ((9, 0), ))
        self.assertRaises(ValueError, encode, ((-1, 0), ))
        self.assertRaises(ValueError, encode, ((0, -1), ))

    def test_invalid_dimensions(self):
        """Using invalid values for width or height raises a ValueError."""
        self.assertRaises(ValueError, encode, ((0, 0), ), width=0)
        self.assertRaises(ValueError, encode, ((0, 0), ), width=1.2)
        self.assertRaises(ValueError, encode, ((0, 0), ), height=0)
        self.assertRaises(ValueError, encode, ((0, 0), ), height=1.2)
        self.assertEqual("r1c1", encode(((0, 0), ), width=1.0))

    def test_use_boxes(self):
        """The default use_boxes argument works as expected."""
        self.assertEqual("r1c1,r2c2", encode(((0, 0), (1, 1)), use_boxes=False))
        self.assertEqual("b1p15", encode(((0, 0), (1, 1)), use_boxes=True))
        self.assertEqual("b1p15", encode(((0, 0), (1, 1)), use_boxes=None))

        self.assertEqual("r1c34", encode(((0, 2), (0, 3)), use_boxes=False))
        self.assertEqual("b1p3,b2p1", encode(((0, 2), (0, 3)), use_boxes=True))
        self.assertEqual("r1c34", encode(((0, 2), (0, 3)), use_boxes=None))

    def test_width_influences_boxes(self):
        """Changing the width influences the box notation."""
        self.assertEqual("b1p3", encode(((0, 2), ), width=3, use_boxes=True))
        self.assertEqual("b2p1", encode(((0, 2), ), width=2, use_boxes=True))

    def test_height_influences_boxes(self):
        """Changing the height influences the box notation."""
        self.assertEqual("b1p7", encode(((2, 0), ), height=3, use_boxes=True))
        self.assertEqual("b3p1", encode(((2, 0), ), height=2, use_boxes=True))

    def test_encode_rncn_3x3(self):
        """rncn encoding works for 3x3 sudokus."""
        for row, columns in enumerate(RNCN_3x3):
            for col, coords in enumerate(columns):
                self.assertEqual(coords, encode(
                    ((row, col), ), width=3, height=3, use_boxes=False))

    def test_encode_bnpn_3x3(self):
        """bnpn encoding works for 3x3 sudokus."""
        for row, columns in enumerate(BNPN_3x3):
            for col, coords in enumerate(columns):
                self.assertEqual(coords, encode(
                    ((row, col), ), width=3, height=3, use_boxes=True))


class DecodeTests(TestCase):
    def test_split_groups(self):
        self.assertEqual(((0, 0), (0, 1), (8, 8)), decode("r1c12,r9c9"))
        self.assertEqual(((0, 0), (0, 1), (9, 9)), decode(
            "r1c1,2,r10c10", width=2, height=5))

    def test_decode_rncn_3x3(self):
        """rncn decoding works for 3x3 sudokus."""
        for row, columns in enumerate(RNCN_3x3):
            for col, coords in enumerate(columns):
                self.assertEqual(
                    ((row, col), ), decode(coords, width=3, height=3))

    def test_decode_bnpn_3x3(self):
        """bnpn decoding works for 3x3 sudokus."""
        for row, columns in enumerate(BNPN_3x3):
            for col, coords in enumerate(columns):
                self.assertEqual(
                    ((row, col), ), decode(coords, width=3, height=3))
