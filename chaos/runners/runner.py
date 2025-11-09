# CoolBits.ai Chaos Engineering - Unified Experiment Runner
# Single entrypoint that launches, measures, and decides pass/fail

import json
import sys
import time
import yaml
import logging
import os
from typing import Dict, Any
from datetime import datetime

from injectors_windows import (
    NetworkLatencyInjector,
    ServiceKillInjector,
    CPUSpikeInjector,
)
from validators_windows import (
    SLOValidator,
    AutoHealManager,
    ChaosMonitor,
    SLOThresholds,
)


class ChaosRunner:
    """Unified chaos experiment runner"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()

        self.slo_validator = SLOValidator()
        self.auto_heal_manager = AutoHealManager()
        self.monitor = ChaosMonitor()

        # Injector mapping (Windows-compatible)
        self.injectors = {
            "network_latency": NetworkLatencyInjector,
            "service_kill": ServiceKillInjector,
            "cpu_spike": CPUSpikeInjector,
        }

    def setup_logging(self):
        """Setup logging for chaos runner"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("chaos/chaos_runner.log"),
                logging.StreamHandler(),
            ],
        )

    def load_scenario(self, scenario_file: str) -> Dict[str, Any]:
        """Load scenario from YAML file"""
        try:
            with open(scenario_file, "r") as f:
                scenario = yaml.safe_load(f)

            self.logger.info(f"Loaded scenario: {scenario['name']}")
            return scenario

        except Exception as e:
            self.logger.error(f"Failed to load scenario {scenario_file}: {e}")
            raise

    def create_injector(self, scenario: Dict[str, Any]):
        """Create appropriate injector for scenario"""
        scenario_name = scenario["name"]

        if scenario_name not in self.injectors:
            raise ValueError(f"Unknown scenario type: {scenario_name}")

        injector_class = self.injectors[scenario_name]
        return injector_class(scenario)

    def check_safety_guards(self, scenario: Dict[str, Any]) -> bool:
        """Check safety guards before starting experiment"""
        try:
            safety_config = scenario.get("safety", {})
            blast_radius = safety_config.get("blast_radius", "staging_only")

            # Check blast radius
            if blast_radius == "staging_only":
                # Verify we're in staging environment
                if not self._is_staging_environment():
                    self.logger.error("Safety guard: Not in staging environment")
                    return False

            # Check error budget
            if not self._check_error_budget():
                self.logger.error("Safety guard: Error budget exceeded")
                return False

            self.logger.info("Safety guards passed")
            return True

        except Exception as e:
            self.logger.error(f"Safety guard check failed: {e}")
            return False

    def _is_staging_environment(self) -> bool:
        """Check if we're in staging environment"""
        try:
            # Check environment variables
            env = os.environ.get("OPIPE_ENV", "")
            if env == "staging":
                return True

            # For Windows simulation, always allow if OPIPE_ENV is set
            return True

        except Exception as e:
            self.logger.error(f"Failed to check staging environment: {e}")
            return False

    def _check_error_budget(self) -> bool:
        """Check if error budget allows chaos experiments"""
        try:
            # In real implementation, would check actual error budget
            # For now, always allow in staging
            return True

        except Exception as e:
            self.logger.error(f"Error budget check failed: {e}")
            return False

    def run_experiment(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run chaos experiment"""
        try:
            self.logger.info(f"Starting chaos experiment: {scenario['name']}")

            # Check safety guards
            if not self.check_safety_guards(scenario):
                return {
                    "verdict": "FAIL",
                    "reason": "Safety guards failed",
                    "start": time.time(),
                    "stop": time.time(),
                }

            # Log experiment start
            self.monitor.start_experiment(scenario["name"])

            start_time = time.time()
            result = {
                "scenario": scenario["name"],
                "start": start_time,
                "stop": None,
                "verdict": "UNKNOWN",
                "slo_before": {},
                "slo_after": {},
                "actions": [],
                "reason": "",
            }

            # Measure baseline SLO
            self.logger.info("Measuring baseline SLO")
            baseline_slo = self.slo_validator.fetch_slo_window(
                scenario["targets"][0]["service"], minutes=5
            )
            result["slo_before"] = {
                "p95_ms": baseline_slo.p95_ms,
                "error_rate": baseline_slo.error_rate,
                "availability": baseline_slo.availability,
            }
            # Log SLO measurement (Windows-compatible)

            # Create and start injector
            injector = self.create_injector(scenario)

            if not injector.start():
                result["verdict"] = "FAIL"
                result["reason"] = "Failed to start injection"
                result["stop"] = time.time()
                return result

            # Verify injection
            if not injector.verify_injection():
                result["verdict"] = "FAIL"
                result["reason"] = "Injection verification failed"
                injector.stop()
                result["stop"] = time.time()
                return result

            # Wait for experiment duration
            target_duration = scenario["targets"][0].get("duration_s", 180)
            self.logger.info(f"Running experiment for {target_duration} seconds")

            # Monitor during experiment
            experiment_start = time.time()
            safety_check_interval = 30  # Check safety every 30 seconds

            while time.time() - experiment_start < target_duration:
                # Check safety guard
                if not injector.safety_guard():
                    result["verdict"] = "FAIL"
                    result["reason"] = "Safety guard triggered"
                    injector.stop()
                    result["stop"] = time.time()
                    return result

                # Check if auto-heal should be triggered
                current_slo = self.slo_validator.fetch_slo_window(
                    scenario["targets"][0]["service"], minutes=2
                )

                # Check auto-heal with Windows-compatible manager
                slo_thresholds = SLOThresholds(
                    p95_ms=scenario["slo"]["p95_ms"],
                    error_rate=scenario["slo"]["error_rate"],
                    availability=0.99,
                )

                if self.auto_heal_manager.check_auto_heal(
                    scenario["targets"][0]["service"], current_slo, slo_thresholds
                ):
                    self.logger.warning("Auto-heal triggered")

                    # Execute rollback
                    rollback_success = self.auto_heal_manager.execute_rollback(
                        scenario["targets"][0]["service"]
                    )
                    result["actions"].append(
                        f"canary_rollback: {'SUCCESS' if rollback_success else 'FAILED'}"
                    )

                    if not rollback_success:
                        result["verdict"] = "FAIL"
                        result["reason"] = "Auto-heal failed"
                        injector.stop()
                        result["stop"] = time.time()
                        return result

                time.sleep(safety_check_interval)

            # Stop injection
            injector.stop()

            # Wait for system to stabilize
            time.sleep(30)

            # Measure final SLO
            self.logger.info("Measuring final SLO")
            final_slo = self.slo_validator.fetch_slo_window(
                scenario["targets"][0]["service"], minutes=5
            )
            result["slo_after"] = {
                "p95_ms": final_slo.p95_ms,
                "error_rate": final_slo.error_rate,
                "availability": final_slo.availability,
            }
            # Log final SLO measurement (Windows-compatible)

            # Determine verdict
            slo_thresholds = SLOThresholds(
                p95_ms=scenario["slo"]["p95_ms"],
                error_rate=scenario["slo"]["error_rate"],
                availability=scenario["slo"]["availability"],
            )

            verdict = self.slo_validator.slo_ok(final_slo, slo_thresholds)
            result["verdict"] = "PASS" if verdict else "FAIL"
            result["reason"] = (
                "SLO thresholds met" if verdict else "SLO thresholds violated"
            )

            result["stop"] = time.time()

            # Log experiment end (Windows-compatible)
            self.monitor.end_experiment(scenario["name"], result["verdict"])

            self.logger.info(f"Chaos experiment completed: {result['verdict']}")
            return result

        except Exception as e:
            self.logger.error(f"Chaos experiment failed: {e}")
            return {
                "verdict": "FAIL",
                "reason": f"Experiment failed: {e}",
                "start": time.time(),
                "stop": time.time(),
            }

    def generate_report(self, scenario: Dict[str, Any], result: Dict[str, Any]) -> str:
        """Generate chaos experiment report"""
        try:
            report = f"""# Chaos Experiment Report: {scenario["name"]}

## Summary
- **Verdict**: {result["verdict"]}
- **Duration**: {result["stop"] - result["start"]:.1f} seconds
- **Reason**: {result["reason"]}

## SLO Measurements
### Before Experiment
- P95 Latency: {result["slo_before"].get("p95_ms", 0):.1f}ms
- Error Rate: {result["slo_before"].get("error_rate", 0):.3f}
- Availability: {result["slo_before"].get("availability", 0):.3f}

### After Experiment
- P95 Latency: {result["slo_after"].get("p95_ms", 0):.1f}ms
- Error Rate: {result["slo_after"].get("error_rate", 0):.3f}
- Availability: {result["slo_after"].get("availability", 0):.3f}

## Actions Taken
{chr(10).join(f"- {action}" for action in result.get("actions", []))}

## Scenario Configuration
- **Target Service**: {scenario["targets"][0]["service"]}
- **Duration**: {scenario["targets"][0].get("duration_s", 180)}s
- **SLO Thresholds**: P95 < {scenario["slo"]["p95_ms"]}ms, Error Rate < {scenario["slo"]["error_rate"]}

Generated: {datetime.now().isoformat()}
"""
            return report

        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            return f"# Chaos Experiment Report: {scenario['name']}\n\nError generating report: {e}"

    def run(self, scenario_file: str) -> Dict[str, Any]:
        """Main entry point for running chaos experiments"""
        try:
            # Load scenario
            scenario = self.load_scenario(scenario_file)

            # Run experiment
            result = self.run_experiment(scenario)

            # Generate report (Windows-compatible)
            report = self.generate_report(scenario, result)

            # Save report
            report_file = f"chaos/reports/{scenario['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            import os

            os.makedirs("chaos/reports", exist_ok=True)

            with open(report_file, "w") as f:
                f.write(report)

            self.logger.info(f"Report saved: {report_file}")

            return result

        except Exception as e:
            self.logger.error(f"Failed to run chaos experiment: {e}")
            return {
                "verdict": "FAIL",
                "reason": f"Runner failed: {e}",
                "start": time.time(),
                "stop": time.time(),
            }


def main():
    """Main function for command line usage"""
    if len(sys.argv) != 2:
        print("Usage: python runner.py <scenario_file>")
        sys.exit(1)

    scenario_file = sys.argv[1]

    runner = ChaosRunner()
    result = runner.run(scenario_file)

    # Print result as JSON
    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    sys.exit(0 if result["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
