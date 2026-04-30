import unittest
from app.analysis.legacy.similarity import normalize_feature_map, min_max_normalize_rows, euclidean_distance, similarity_score, nearest_neighbors

class TestSimilarity(unittest.TestCase):
    def test_normalize_feature_map(self):
        self.assertEqual(normalize_feature_map({"goals": None, "shots": 10}), {"goals": 0.0, "shots": 10.0})

    def test_min_max_normalize_rows(self):
        rows = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
        normalized = min_max_normalize_rows(rows)
        self.assertEqual(normalized[0]["a"], 0.0)
        self.assertEqual(normalized[1]["a"], 1.0)

    def test_euclidean_distance(self):
        a = {"x": 1, "y": 2}
        b = {"x": 1, "y": 5}
        self.assertEqual(euclidean_distance(a,b), 3.0)

    def test_similarity_score(self):
        self.assertEqual(similarity_score(0.5), 50.0)

    def test_nearest_neighbors(self):
        vectors = {
            "A": {"x": 1, "y": 2},
            "B": {"x": 2, "y": 3},
            "C": {"x": 3, "y": 1}
        }
        neighbors = nearest_neighbors("A", vectors, limit=2)
        self.assertEqual(len(neighbors), 2)

if __name__ == "__main__":
    unittest.main()
