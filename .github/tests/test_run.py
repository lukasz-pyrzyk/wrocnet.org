import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
DOCKER_STUB = """#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys

args = sys.argv[1:]
with open(os.environ["DOCKER_CALLS"], "a") as log:
    log.write(json.dumps(args) + "\\n")
scenario = json.loads(os.environ["DOCKER_SCENARIO"])
if args == ["ps", "-aq"]:
    print("\\n".join(scenario.get("containers", {})))
elif args[0] == "inspect":
    print(scenario["containers"][args[-1]])
elif args[0] == "ps" and "publish=4001" in args:
    print("\\n".join(scenario.get("ports", [])))
elif args[0] == "ps":
    print(scenario.get("remaining", ""))
elif args[0] == "build":
    sys.exit(scenario.get("build_exit", 0))
"""


class RunScriptTests(unittest.TestCase):
    def run_script(self, scenario):
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            docker = temp / "docker"
            docker.write_text(DOCKER_STUB)
            docker.chmod(0o755)
            calls_path = temp / "calls.jsonl"
            result = subprocess.run(
                ["sh", str(ROOT / "run.sh"), "--force_polling"],
                env={
                    **os.environ,
                    "PATH": f"{temp}{os.pathsep}{os.environ['PATH']}",
                    "DOCKER_CALLS": str(calls_path),
                    "DOCKER_SCENARIO": json.dumps(scenario),
                },
                capture_output=True,
                text=True,
            )
            calls = [json.loads(line) for line in calls_path.read_text().splitlines()]
            return result, calls

    def test_replaces_legacy_and_labeled_instances_but_not_other_apps(self):
        result, calls = self.run_script({
            "containers": {
                "legacy": "wrocnet-local:old|<no value>|/old-preview",
                "current": "custom-image|true|/wrocnet-local",
                "other": "postgres:17|<no value>|/database",
            },
            "ports": ["legacy", "current"],
        })
        self.assertEqual(result.returncode, 0, result.stderr)
        stops = [call for call in calls if call[0] == "stop"]
        self.assertEqual(stops, [["stop", "legacy"], ["stop", "current"]])
        self.assertFalse(any(call[0] == "rm" for call in calls))
        build_index = next(i for i, call in enumerate(calls) if call[0] == "build")
        self.assertLess(build_index, calls.index(stops[0]))
        self.assertEqual(calls[-1][0], "run")
        self.assertIn("org.wrocnet.local=true", calls[-1])
        self.assertEqual(calls[-1][-1], "--force_polling")

    def test_removes_stopped_named_container_before_start(self):
        result, calls = self.run_script({
            "containers": {"old": "wrocnet-local|<no value>|/wrocnet-local"},
            "remaining": "old",
        })
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(["rm", "old"], calls)
        self.assertLess(calls.index(["rm", "old"]), len(calls) - 1)

    def test_refuses_unrecognized_port_or_name_owners(self):
        for scenario in [
            {"ports": ["foreign"]},
            {"containers": {"foreign": "nginx|<no value>|/wrocnet-local"}},
        ]:
            with self.subTest(scenario=scenario):
                result, calls = self.run_script(scenario)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("leaving it untouched", result.stderr)
                self.assertFalse(any(
                    call[0] in {"build", "stop", "rm", "run"} for call in calls
                ))

    def test_failed_build_preserves_running_preview(self):
        result, calls = self.run_script({
            "containers": {"old": "wrocnet-local:latest|true|/wrocnet-local"},
            "build_exit": 1,
        })
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(any(call[0] in {"stop", "rm", "run"} for call in calls))


if __name__ == "__main__":
    unittest.main()
