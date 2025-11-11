"""
Unit tests for the nakeds system.
"""

import unittest
from unittest.mock import Mock, MagicMock
from commands.base_commands.nakeds import CmdNakeds, CmdNakedsHelper, BODY_PARTS, BODY_ORDER


class TestNakedsSystem(unittest.TestCase):
    """Test the nakeds command and helper functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.character = Mock()
        self.character.db = Mock()
        self.character.attributes = Mock()
        self.character.process_pronoun_substitution = Mock(side_effect=lambda x: x)
        
        self.observer = Mock()
        
        self.cmd = CmdNakeds()
        self.cmd.caller = self.character
        self.cmd.msg = Mock()
        
    def test_body_parts_defined(self):
        """Test that body parts are properly defined."""
        self.assertIn("face", BODY_PARTS)
        self.assertIn("chest", BODY_PARTS)
        self.assertIn("lhand", BODY_PARTS)
        self.assertEqual(BODY_PARTS["face"], "face")
        self.assertEqual(BODY_PARTS["lhand"], "left hand")
        
    def test_body_order_complete(self):
        """Test that body order includes all parts."""
        self.assertIn("head", BODY_ORDER)
        self.assertIn("face", BODY_ORDER) 
        self.assertIn("chest", BODY_ORDER)
        self.assertIn("lfoot", BODY_ORDER)
        # Should be in head-to-toe order
        self.assertLess(BODY_ORDER.index("head"), BODY_ORDER.index("chest"))
        self.assertLess(BODY_ORDER.index("chest"), BODY_ORDER.index("lfoot"))
        
    def test_show_all_nakeds_empty(self):
        """Test showing nakeds when none are set."""
        self.character.attributes.has.return_value = False
        self.character.db.nakeds = {}
        
        self.cmd.args = ""
        self.cmd.func()
        
        self.cmd.msg.assert_called_once()
        msg = self.cmd.msg.call_args[0][0]
        self.assertIn("no naked descriptions", msg)
        
    def test_show_all_nakeds_with_data(self):
        """Test showing nakeds with data."""
        nakeds = {
            "face": "A kind face with bright eyes.",
            "chest": "A broad, muscled chest."
        }
        self.character.attributes.has.return_value = True
        self.character.db.nakeds = nakeds
        
        self.cmd.args = ""
        self.cmd.func()
        
        self.cmd.msg.assert_called_once()
        msg = self.cmd.msg.call_args[0][0]
        self.assertIn("Face", msg)
        self.assertIn("Chest", msg)
        self.assertIn("kind face", msg)
        
    def test_set_naked_desc(self):
        """Test setting a naked description."""
        self.character.attributes.has.return_value = False
        self.character.db.nakeds = {}
        
        self.cmd.args = "face is A weathered but kind face."
        self.cmd.func()
        
        # Should have set the description
        expected = {"face": "A weathered but kind face."}
        self.assertEqual(self.character.db.nakeds, expected)
        
        self.cmd.msg.assert_called_once()
        msg = self.cmd.msg.call_args[0][0]
        self.assertIn("Set description", msg)
        
    def test_delete_naked_desc(self):
        """Test deleting a naked description."""
        nakeds = {"face": "A kind face."}
        self.character.attributes.has.return_value = True
        self.character.db.nakeds = nakeds
        
        self.cmd.switches = ["del"]
        self.cmd.args = "face"
        self.cmd.func()
        
        # Should have deleted the description
        self.assertNotIn("face", self.character.db.nakeds)
        
        self.cmd.msg.assert_called_once()
        msg = self.cmd.msg.call_args[0][0]
        self.assertIn("Deleted", msg)
        
    def test_invalid_body_part(self):
        """Test handling invalid body part names."""
        self.cmd.args = "invalidpart is Some description."
        self.cmd.func()
        
        self.cmd.msg.assert_called_once() 
        msg = self.cmd.msg.call_args[0][0]
        self.assertIn("Unknown body part", msg)


class TestNakedsHelper(unittest.TestCase):
    """Test the nakeds helper functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.character = Mock()
        self.character.db = Mock()
        self.character.worn = []
        self.character.process_pronoun_substitution = Mock(side_effect=lambda x: x)
        
        self.observer = Mock()
        
    def test_get_covered_parts_no_clothing(self):
        """Test getting covered parts with no clothing."""
        self.character.worn = []
        
        covered = CmdNakedsHelper.get_covered_body_parts(self.character)
        
        self.assertEqual(len(covered), 0)
        
    def test_get_covered_parts_with_clothing(self):
        """Test getting covered parts with clothing."""
        # Mock clothing items
        shirt = Mock()
        shirt.db.coverage = ["chest", "abdomen"]
        
        pants = Mock() 
        pants.db.coverage = ["groin", "lthigh", "rthigh"]
        
        self.character.worn = [shirt, pants]
        
        covered = CmdNakedsHelper.get_covered_body_parts(self.character)
        
        expected = {"chest", "abdomen", "groin", "lthigh", "rthigh"}
        self.assertEqual(covered, expected)
        
    def test_get_visible_nakeds(self):
        """Test getting visible naked descriptions."""
        # Set up nakeds
        nakeds = {
            "face": "A kind face.",
            "chest": "A broad chest.",
            "lhand": "A scarred hand."
        }
        self.character.db.nakeds = nakeds
        
        # Mock clothing that covers chest
        shirt = Mock()
        shirt.db.coverage = ["chest"]
        self.character.worn = [shirt]
        
        visible = CmdNakedsHelper.get_visible_nakeds(self.character, self.observer)
        
        # Should see face and lhand, but not chest
        expected = {
            "face": "A kind face.",
            "lhand": "A scarred hand."
        }
        self.assertEqual(visible, expected)
        
    def test_format_nakeds_display(self):
        """Test formatting nakeds for display."""
        nakeds = {
            "face": "A kind face.",
            "chest": "A broad chest."
        }
        self.character.db.nakeds = nakeds
        self.character.worn = []  # No clothing
        
        display = CmdNakedsHelper.format_nakeds_display(self.character, self.observer)
        
        # Should have both descriptions in proper order
        self.assertIn("A kind face.", display)
        self.assertIn("A broad chest.", display)
        # Face should come before chest in display order
        face_pos = display.find("A kind face.")
        chest_pos = display.find("A broad chest.")
        self.assertLess(face_pos, chest_pos)


if __name__ == '__main__':
    unittest.main()