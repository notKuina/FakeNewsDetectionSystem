import unittest
from detection_module import preprocess_text, predict_news

class TestFakeNewsDetection(unittest.TestCase):
    
    def test_preprocess_text(self):
        raw = "Breaking: Trump WINS election!!!"
        expected_keywords = ["breaking", "trump", "wins", "election"]
        cleaned = preprocess_text(raw)
        for word in expected_keywords:
            self.assertIn(word, cleaned)

    def test_predict_news_real(self):
        title = "NASA confirms water on the moon"
        text = "NASA scientists announced today that water molecules are present on the sunlit surface of the moon."
        result, confidence = predict_news(title, text)
        self.assertIn(result, ['Real', 'Fake'])
        self.assertGreater(confidence, 0.0)

    def test_predict_news_empty(self):
        result, confidence = predict_news("", "")
        self.assertEqual(result, 'unknown')
        self.assertEqual(confidence, 0.0)

if __name__ == '__main__':
    unittest.main()
