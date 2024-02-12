from dotenv import load_dotenv
import unittest
from src.common.utilities import should_include_row_based_on_filters

load_dotenv()


class TestShouldIncludeRow(unittest.TestCase):

    def test_special_keywords(self):
        self.assertTrue(
            should_include_row_based_on_filters(
                "Special Keyword Event", special_keywords=["Special Keyword"]
            )
        )

    def test_player_and_keyword(self):
        self.assertTrue(
            should_include_row_based_on_filters(
                "Player1 Keyword1 Event", players=["Player1"], keywords=["Keyword1"]
            )
        )

    def test_player_no_keyword(self):
        self.assertFalse(
            should_include_row_based_on_filters(
                "Player2 No Keyword Event", players=["Player2"], keywords=["Keyword1"]
            )
        )

    def test_excluded_word(self):
        self.assertFalse(
            should_include_row_based_on_filters(
                "Excluded Word Event", words_to_exclude=["Excluded Word"]
            )
        )

    def test_no_match(self):
        self.assertFalse(
            should_include_row_based_on_filters(
                "No Match Event", players=["Player1"], keywords=["Keyword1"]
            )
        )

    def test_no_filters_provided(self):
        self.assertFalse(should_include_row_based_on_filters("Any Event"))

    def test_player_present_with_excluded_word(self):
        self.assertFalse(
            should_include_row_based_on_filters(
                "Player1 Excluded Word Event",
                players=["Player1"],
                words_to_exclude=["Excluded Word"],
            )
        )

    def test_special_keyword_with_excluded_word(self):
        self.assertTrue(
            should_include_row_based_on_filters(
                "Special Keyword Excluded Word Event",
                special_keywords=["Special Keyword"],
                words_to_exclude=["Excluded Word"],
            )
        )

    def test_player_present_without_keywords_and_excluded_words(self):
        self.assertTrue(
            should_include_row_based_on_filters("Player1 Event", players=["Player1"])
        )

    def test_case_insensitivity(self):
        self.assertTrue(
            should_include_row_based_on_filters(
                "player1 keyword1 event", players=["Player1"], keywords=["Keyword1"]
            )
        )

    def test_real_case_player_with_excluded_word(self):
        players = ["Bol"]
        words_to_exclude = ["FOUL", "Turnover", "Violation", "SUB", "MISS"]
        special_keywords = ["dunk"]
        keywords = ["reverse", "3PT", "shot"]
        self.assertFalse(
            should_include_row_based_on_filters(
                "Bol P.FOUL (P2.T2) (S.Wright)",
                special_keywords=special_keywords,
                players=players,
                words_to_exclude=words_to_exclude,
                keywords=keywords,
            )
        )
        self.assertFalse(
            should_include_row_based_on_filters(
                "Beal 3PT Running Jump Shot (19 PTS) (Allen 4 AST)",
                special_keywords=special_keywords,
                players=players,
                words_to_exclude=words_to_exclude,
                keywords=keywords,
            )
        )
        self.assertFalse(
            should_include_row_based_on_filters(
                "Bol REBOUND (Off:0 Def:3)",
                special_keywords=special_keywords,
                players=players,
                words_to_exclude=words_to_exclude,
                keywords=keywords,
            )
        )
        self.assertFalse(
            should_include_row_based_on_filters(
                "Bol Violation:Defensive Goaltending (S.Wall))",
                special_keywords=special_keywords,
                players=players,
                words_to_exclude=words_to_exclude,
                keywords=keywords,
            )
        )
        self.assertTrue(
            should_include_row_based_on_filters(
                "MISS Beal 2' Running Dunk",
                special_keywords=special_keywords,
                players=players,
                words_to_exclude=words_to_exclude,
                keywords=keywords,
            )
        )
        self.assertTrue(
            should_include_row_based_on_filters(
                "Bol 8' Driving Floating Jump Shot (11 PTS)",
                special_keywords=special_keywords,
                players=players,
                words_to_exclude=words_to_exclude,
                keywords=keywords,
            )
        )
        self.assertTrue(
            should_include_row_based_on_filters(
                "Bol 1' Running Dunk (2 PTS)",
                special_keywords=special_keywords,
                players=players,
                words_to_exclude=words_to_exclude,
                keywords=keywords,
            )
        )
        self.assertTrue(
            should_include_row_based_on_filters(
                "Bol 25' 3PT Jump Shot (5 PTS) (Metu 1 AST)",
                special_keywords=special_keywords,
                players=players,
                words_to_exclude=words_to_exclude,
                keywords=keywords,
            )
        )


if __name__ == "__main__":
    unittest.main()
