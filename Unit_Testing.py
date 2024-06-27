import unittest
from utils.exchange_rate_analyzer import ExchangeRateAnalyzer
from unittest.mock import patch
import pandas as pd


class TestExchangeRateAnalyzer(unittest.TestCase):

    def setUp(self):
        self.api_key = "23a56d651d65db49fee83eb1"
        self.base_currency = "AUD"
        self.target_currency = "NZD"
        self.analyzer = ExchangeRateAnalyzer(self.api_key, self.base_currency, self.target_currency)

    @patch('utils.exchange_rate_analyzer.requests.get')
    def test_fetch_exchange_rates_success(self, mock_get):
        mock_response = {
            "result": "success",
            "conversion_rates": {
                "NZD": 1.07
            }
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        rates = self.analyzer.fetch_exchange_rates()
        self.assertTrue("NZD" in rates.values())

    @patch('utils.exchange_rate_analyzer.requests.get')
    def test_fetch_exchange_rates_failure(self, mock_get):
        mock_get.return_value.status_code = 403
        rates = self.analyzer.fetch_exchange_rates()
        self.assertEqual(rates, {})

    def test_preprocess_data(self):
        df = pd.DataFrame({
            "Date": ["2023-06-01", "2023-06-02"],
            "Exchange Rate": [1.05, None]
        })
        df = self.analyzer.preprocess_data(df)
        self.assertTrue(df.isna().sum().sum() == 0)

    def test_get_statistics(self):
        df = pd.DataFrame({
            "Date": ["2023-06-01", "2023-06-02", "2023-06-03"],
            "Exchange Rate": [1.05, 1.07, 1.06]
        })
        df = self.analyzer.preprocess_data(df)
        best_rate, worst_rate, average_rate, highest_daily_change, lowest_daily_change = self.analyzer.get_statistics(
            df)
        self.assertEqual(best_rate, 1.07)
        self.assertEqual(worst_rate, 1.05)
        self.assertAlmostEqual(average_rate, 1.06)
        self.assertAlmostEqual(highest_daily_change, 0.02)
        self.assertAlmostEqual(lowest_daily_change, -0.01)


if __name__ == '__main__':
    unittest.main()
