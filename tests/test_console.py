"""Проверка: ошибки пользователя не останавливают главное меню"""
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from application.music_service import MusicService
from infrastructure.json_repository import JsonMusicRepository
from infrastructure.xml_repository import XmlMusicRepository
from presentation.console import ConsoleApp


class ConsoleTests(unittest.TestCase):
    def run_actions(self, actions):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            app = ConsoleApp(MusicService(), JsonMusicRepository(root / 'data.json'),
                             XmlMusicRepository(root / 'data.xml'))
            output = io.StringIO()
            with patch('builtins.input', side_effect=actions), redirect_stdout(output):
                app.run()
            return output.getvalue()

    def test_bad_integer_then_exit_normally(self):
        output = self.run_actions(['4', 'Test', 'не число', '0'])
        self.assertIn('Ошибка ввода', output)
        self.assertIn('Программа завершена', output)

    def test_custom_exception_then_good_action(self):
        output = self.run_actions(['2', '   ', '2', 'Кино', '0'])
        self.assertIn('Ошибка:', output)
        self.assertIn('Добавлен исполнитель #1', output)

    def test_missing_file_then_menu_continues(self):
        output = self.run_actions(['11', '1', '0'])
        self.assertIn('Файл не найден', output)
        self.assertIn('Каталог пуст', output)


if __name__ == '__main__':
    unittest.main()
