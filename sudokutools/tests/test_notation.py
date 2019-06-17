from unittest import TestCase

from sudokutools.notation import encode


class EncodeTests(TestCase):
    def test_order(self):
        """Coordinates are always shown in a sorted order."""
        self.assertEqual("r1c12", encode(((0, 0), (0, 1))))
        self.assertEqual("r1c12", encode(((0, 1), (0, 0))))
        self.assertEqual("r12c1", encode(((0, 0), (1, 0))))
        self.assertEqual("r12c1", encode(((1, 0), (0, 0))))

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

