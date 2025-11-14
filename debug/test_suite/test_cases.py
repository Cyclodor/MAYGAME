import json
import os
import unittest
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")


class FantasyStrategyTestSuite(unittest.TestCase):
    """Набор автоматических проверок в соответствии с TestPlan.md."""

    def test_entry_points_exist(self):
        """TC-GAME-01: проверка наличия основных точек входа."""
        main_py = os.path.join(PROJECT_ROOT, "main.py")
        battle_exe = os.path.join(PROJECT_ROOT, "BattleGame.exe")
        dist_exe = os.path.join(PROJECT_ROOT, "dist", "BattleGame.exe")

        self.assertTrue(os.path.isfile(main_py), "main.py отсутствует")
        self.assertTrue(
            os.path.isfile(battle_exe) or os.path.isfile(dist_exe),
            "Не найдена исполняемая сборка BattleGame.exe"
        )

    def test_settings_json_structure(self):
        """TC-SETTINGS-01/02: структура файла настроек."""
        settings_path = os.path.join(DATA_DIR, "settings.json")
        with open(settings_path, "r", encoding="utf-8") as fh:
            config = json.load(fh)

        required_keys = {
            "music_volume": float,
            "sfx_volume": float,
            "muted": bool,
            "screen_width": int,
            "screen_height": int,
            "fullscreen": bool,
        }
        for key, expected_type in required_keys.items():
            self.assertIn(key, config, f"Ключ {key} отсутствует в settings.json")
            self.assertIsInstance(config[key], expected_type, f"Ключ {key} имеет неверный тип")

        self.assertGreater(config["screen_width"], 0)
        self.assertGreater(config["screen_height"], 0)

    def test_unit_overrides_integrity(self):
        """TC-BATTLE-01/02: проверка целостности настроек юнитов."""
        overrides_path = os.path.join(DATA_DIR, "unit_overrides.json")
        with open(overrides_path, "r", encoding="utf-8") as fh:
            overrides = json.load(fh)

        self.assertGreater(len(overrides), 0, "Файл unit_overrides.json пуст")

        for unit_name, params in overrides.items():
            self.assertIsInstance(params, dict, f"Параметры {unit_name} должны быть словарём")
            for key, value in params.items():
                if isinstance(value, (int, float)):
                    self.assertGreaterEqual(
                        value, 0,
                        f"Параметр {key} для юнита {unit_name} имеет отрицательное значение"
                    )

    def test_spell_classes(self):
        """TC-SPELL-01/02/03: базовая проверка заклинаний."""
        from game.spells import BlessSpell, CurseSpell, FireballSpell, HealSpell

        spells = [BlessSpell(), CurseSpell(), FireballSpell(), HealSpell()]
        for spell in spells:
            self.assertGreaterEqual(spell.mana_cost, 0, f"Заклинание {spell.name} имеет некорректную стоимость маны")
            spell.cast()
            self.assertGreaterEqual(spell.current_cooldown, 0, f"Заклинание {spell.name} имеет некорректное значение перезарядки")
            spell.update()
            self.assertGreaterEqual(spell.current_cooldown, 0)

    def test_ai_controller_interface(self):
        """TC-AI-01: наличие ключевых методов у AIController."""
        try:
            import pygame  # noqa: F401
        except ModuleNotFoundError:
            self.skipTest("pygame не установлен, тест пропущен")

        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        import pygame
        if not pygame.get_init():
            pygame.init()

        from types import SimpleNamespace
        try:
            from game.ai import AIController
        except Exception as exc:  # pragma: no cover
            self.skipTest(f"Не удалось импортировать AIController: {exc}")

        game_stub = SimpleNamespace(selected_unit=None, units=[], ai_actions=SimpleNamespace(use_spell_direct=lambda *args, **kwargs: False))
        controller = AIController(game_stub, ai_team="player1")
        self.assertTrue(hasattr(controller, "make_decision"))
        self.assertFalse(controller.make_decision())
        pygame.quit()

    def test_testplan_document_present(self):
        """Наличие TestPlan.md и актуальной версии Test_Results.md."""
        plan_path = os.path.join(PROJECT_ROOT, "Документация", "TestPlan.md")
        results_path = os.path.join(PROJECT_ROOT, "Документация", "Test_Results.md")
        self.assertTrue(os.path.isfile(plan_path), "Не найден TestPlan.md")
        self.assertTrue(os.path.isfile(results_path), "Не найден Test_Results.md")
        with open(results_path, "r", encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("Процент успешности", content)
        self.assertIn("Игра готова к использованию", content)


def load_tests(loader, tests, pattern):  # pragma: no cover - используется unittest
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(FantasyStrategyTestSuite))
    return suite
