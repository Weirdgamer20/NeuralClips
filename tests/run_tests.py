"""NeuralClips Standalone Test Runner using Python Standard Library."""

import inspect
import os
import sys
import time
import traceback

# Ensure workspace root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def run_all_tests():
    tests_dir = os.path.join(BASE_DIR, "tests")
    test_files = [
        f for f in sorted(os.listdir(tests_dir))
        if f.startswith("test_") and f.endswith(".py")
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    start_time = time.time()

    print(f"\nDiscovered {len(test_files)} test files in {tests_dir}\n" + "=" * 60)

    for tf in test_files:
        module_name = f"tests.{tf[:-3]}"
        try:
            # Reload / import module
            if module_name in sys.modules:
                del sys.modules[module_name]
            mod = __import__(module_name, fromlist=["*"])
        except Exception as e:
            print(f"[FAIL IMPORT] {module_name}: {e}")
            traceback.print_exc()
            failed_tests += 1
            continue

        # Find test functions
        test_funcs = [
            (name, func) for name, func in inspect.getmembers(mod, inspect.isfunction)
            if name.startswith("test_")
        ]

        print(f"[{tf}] Running {len(test_funcs)} tests...")
        for name, func in test_funcs:
            total_tests += 1
            t0 = time.time()
            try:
                func()
                elapsed = time.time() - t0
                print(f"  [PASS] {name} ({elapsed:.3f}s)")
                passed_tests += 1
            except Exception as e:
                elapsed = time.time() - t0
                print(f"  [FAIL] {name} ({elapsed:.3f}s): {e}")
                traceback.print_exc()
                failed_tests += 1

    total_time = time.time() - start_time
    print("=" * 60)
    print(f"Results: {passed_tests} PASSED, {failed_tests} FAILED in {total_time:.2f}s")
    print("=" * 60 + "\n")

    if failed_tests > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
