
import unittest
from unittest.mock import patch
from bot import *

class TestOxxxymironBot(unittest.TestCase):
    @patch('bot.requests.get')
    def test_get_news_successful(self, mock_get):
        mock_get.return_value.json.return_value = {
            'articles': [
                {'title': 'Новость 1'},
                {'title': 'Новость 2'},
                {'title': 'Новость 3'}
            ]
        }

        result = get_news()

        expected_result = 'Новость 1\nНовость 2\nНовость 3\n'
        self.assertEqual(result, expected_result)

    def test_get_news_negative(self):
        @patch('mymodule.requests.get')
        def test_get_news_no_articles(self, mock_get):
            mock_get.return_value.json.return_value = {
                'articles': []
            }

            result = get_news()

            expected_result = 'К сожалению, за последний месяц про Мирона нет новостей :('
            self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
