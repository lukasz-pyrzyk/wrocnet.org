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
    container_id = args[-1]
    if container_id in scenario.get("inspect_errors", []):
        print("Inspection failed", file=sys.stderr)
        sys.exit(7)
    if ".NetworkSettings.Ports" in args[2]:
        bindings = scenario.get("bindings", {}).get(container_id, {})
        print(" ".join(
            f"{port}:{binding['HostPort']}"
            for port, values in bindings.items() for binding in values
        ))
    else:
        print(scenario["containers"][container_id])
elif args[0] == "ps":
    if scenario.get("presence_error"):
        print("Docker daemon unavailable", file=sys.stderr)
        sys.exit(8)
    print(scenario.get("remaining", ""))
elif args[0] == "build":
    sys.exit(scenario.get("build_exit", 0))
elif args[0] == "stop" and args[-1] in scenario.get("stop_errors", []):
    print("Stop failed", file=sys.stderr)
    sys.exit(9)
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
            {
                "containers": {"foreign": "nginx|<no value>|/web"},
                "bindings": {"foreign": {"80/tcp": [{"HostPort": "4001"}]}},
            },
            {
                "containers": {"foreign": "nginx|<no value>|/web"},
                "bindings": {"foreign": {"80/tcp": [{"HostPort": "35730"}]}},
            },
            {"containers": {"foreign": "nginx|<no value>|/wrocnet-local"}},
        ]:
            with self.subTest(scenario=scenario):
                result, calls = self.run_script(scenario)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("leaving it untouched", result.stderr)
                self.assertFalse(any(
                    call[0] in {"build", "stop", "rm", "run"} for call in calls
                ))

    def test_allows_other_host_ports_and_udp_bindings(self):
        result, calls = self.run_script({
            "containers": {"foreign": "nginx|<no value>|/web"},
            "bindings": {"foreign": {
                "4001/tcp": [{"HostPort": "5000"}],
                "80/udp": [{"HostPort": "4001"}],
            }},
        })
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(any(call[0] == "stop" for call in calls))
        self.assertEqual(calls[-1][0], "run")

    def test_skips_containers_removed_before_inspection_or_stop(self):
        for scenario in [
            {
                "containers": {"gone": "nginx|<no value>|/job"},
                "inspect_errors": ["gone"],
            },
            {
                "containers": {"gone": "wrocnet-local|true|/wrocnet-local"},
                "stop_errors": ["gone"],
            },
        ]:
            with self.subTest(scenario=scenario):
                result, calls = self.run_script(scenario)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("was removed; skipping", result.stderr)
                self.assertEqual(calls[-1][0], "run")

    def test_preserves_errors_for_containers_that_still_exist(self):
        for operation, status, message in [
            ("inspect", 7, "Inspection failed"),
            ("stop", 9, "Stop failed"),
        ]:
            with self.subTest(operation=operation):
                result, calls = self.run_script({
                    "containers": {"existing": "wrocnet-local|true|/wrocnet-local"},
                    f"{operation}_errors": ["existing"],
                    "remaining": "existing",
                })
                self.assertEqual(result.returncode, status)
                self.assertIn(message, result.stderr)
                self.assertFalse(any(call[0] == "run" for call in calls))

    def test_preserves_daemon_errors_when_checking_container_presence(self):
        result, calls = self.run_script({
            "containers": {"existing": "nginx|<no value>|/job"},
            "inspect_errors": ["existing"],
            "presence_error": True,
        })
        self.assertEqual(result.returncode, 8)
        self.assertIn("Docker daemon unavailable", result.stderr)
        self.assertFalse(any(call[0] == "run" for call in calls))

    def test_failed_build_preserves_running_preview(self):
        result, calls = self.run_script({
            "containers": {"old": "wrocnet-local:latest|true|/wrocnet-local"},
            "build_exit": 1,
        })
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(any(call[0] in {"stop", "rm", "run"} for call in calls))


if __name__ == "__main__":
    unittest.main()
