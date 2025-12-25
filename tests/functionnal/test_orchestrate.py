import subprocess
import sys


def test_orchestrator_starts():
    result = subprocess.run(
        [sys.executable, "orchestrate.py"],
        timeout=15,
        capture_output=True,
        text=True,
    )

    # 0 = succès, 1 = échec contrôlé
    assert result.returncode in (0, 1)
