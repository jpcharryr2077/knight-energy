"""
run_all_tests.py
Ejecuta todas las suites de pruebas unitarias.

Uso:
    python tests/run_all_tests.py
"""

import sys, os, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SUITES = [
    "tests.test_board",
    "tests.test_game_state",
    "tests.test_knight",
    "tests.test_heuristic",
    "tests.test_minimax",
]

GREEN = "\033[1;32m"; RED = "\033[1;31m"; RESET = "\033[0m"; CYAN = "\033[1;36m"


def run():
    print("\n" + "═" * 58)
    print("  KNIGHT ENERGY — Suite Completa de Pruebas Unitarias")
    print("═" * 58)

    loader  = unittest.TestLoader()
    full    = unittest.TestSuite()
    totals  = {}

    for module_name in SUITES:
        suite = loader.loadTestsFromName(module_name)
        full.addTests(suite)

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(full)

    print("\n" + "═" * 58)
    ran    = result.testsRun
    errors = len(result.errors)
    fails  = len(result.failures)
    passed = ran - errors - fails
    color  = GREEN if passed == ran else RED

    print(f"  {color}Total : {passed}/{ran} pruebas pasaron{RESET}")
    if errors:
        print(f"  {RED}Errores  : {errors}{RESET}")
    if fails:
        print(f"  {RED}Fallos   : {fails}{RESET}")
    print("═" * 58 + "\n")

    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    run()
