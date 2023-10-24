import unittest

# from unittest.mock import patch, Mock
from src.magicmath.magicmath import MagicMath


class TestMagicMath(unittest.TestCase):
    """Test the magicmath class."""

    def test_constructor(self):
        """Test class constructor."""
        MagicMath()
