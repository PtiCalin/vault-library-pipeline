from pathlib import Path
import unittest

from library_pipeline import cli


def _base_cfg() -> dict:
    return {
        "type_keywords": {
            "REVIEW": ["systematic review"],
            "SURVEY": ["survey"],
            "PAPER": [],
        },
        "domain_keywords": {
            "COMPUTE": [
                {
                    "term": "machine learning",
                    "aliases": ["ml"],
                    "weight": 1.2,
                    "concepts": ["ml"],
                }
            ],
            "FORMAL": ["statistics"],
            "META": [],
        },
        "classification": {
            "field_weights": {
                "title": 3.0,
                "filename": 2.0,
                "first_page": 1.5,
                "abstract": 1.2,
            },
            "fuzzy": {
                "enabled": True,
                "threshold": 0.88,
                "partial_threshold": 0.92,
                "fuzzy_boost": 0.7,
            },
            "secondary_domains": {
                "max_count": 3,
                "min_relative_score": 0.35,
            },
            "concept_tags": {
                "min_count": 1,
                "fallback": "general",
            },
        },
    }


class ClassificationAccuracyTests(unittest.TestCase):
    def test_iterate_keyword_entries_supports_legacy_and_rich(self):
        legacy_entries = cli.iterate_keyword_entries(["machine learning"])
        rich_entries = cli.iterate_keyword_entries(
            [{"term": "machine learning", "weight": 2.0, "aliases": ["ml"], "concepts": ["ml"]}]
        )

        self.assertEqual(legacy_entries[0]["term"], "machine learning")
        self.assertEqual(legacy_entries[0]["weight"], 1.0)
        self.assertEqual(rich_entries[0]["weight"], 2.0)
        self.assertEqual(rich_entries[0]["aliases"], ["ml"])

    def test_fuzzy_matching_handles_typo(self):
        cfg = _base_cfg()
        sources = {
            "title": "systmatic review of recommendation systems",
            "filename": "",
            "first_page": "",
            "abstract": "",
        }

        doc_type, ranked = cli.infer_type_with_ranking(sources, cfg)

        self.assertEqual(doc_type, "REVIEW")
        self.assertGreater(ranked[0]["score"], 0)

    def test_primary_and_secondary_domains_are_ranked(self):
        cfg = _base_cfg()
        sources = {
            "title": "machine learning and statistics for recommender systems",
            "filename": "",
            "first_page": "",
            "abstract": "",
        }

        primary, secondary, ranked = cli.infer_primary_and_secondary_domains(sources, cfg)

        self.assertEqual(primary, "COMPUTE")
        self.assertIn("FORMAL", secondary)
        self.assertLessEqual(len(secondary), 3)
        self.assertGreaterEqual(ranked[0]["score"], ranked[1]["score"])

    def test_concept_tags_always_have_at_least_one_value(self):
        cfg = _base_cfg()
        concept_tags = cli.build_concept_tags(
            "", ranked_type=[], ranked_domains=[], cfg=cfg
        )

        self.assertTrue(concept_tags)
        self.assertEqual(concept_tags[0], "general")

    def test_build_classification_sources_uses_multiple_fields(self):
        metadata = {
            "title": "AI systems",
            "first_page_text": "ml pipeline",
            "abstract": "statistics",
        }
        sources = cli.build_classification_sources(Path("sample.pdf"), metadata)

        self.assertEqual(sources["title"], "ai systems")
        self.assertEqual(sources["filename"], "sample")
        self.assertEqual(sources["first_page"], "ml pipeline")
        self.assertEqual(sources["abstract"], "statistics")


if __name__ == "__main__":
    unittest.main()
