# CoolBits.ai Uptime Monitoring and Alerting System
# ==================================================

import os
import sys
import json
import time
import requests
import psutil
import threading
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import statistics
import logging
from collections import deque
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class AlertLevel(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of metrics to monitor."""

    RESPONSE_TIME = "response_time"
    UPTIME = "uptime"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    ERROR_RATE = "error_rate"
    REQUEST_COUNT = "request_count"


@dataclass
class MetricThreshold:
    """Threshold configuration for metrics."""

    metric_type: MetricType
    warning_threshold: float
    error_threshold: float
    critical_threshold: float
    p95_threshold: Optional[float] = None
    p99_threshold: Optional[float] = None


@dataclass
class Alert:
    """Alert data structure."""

    id: str
    level: AlertLevel
    metric_type: MetricType
    message: str
    value: float
    threshold: float
    timestamp: datetime
    service: str
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class UptimeCheck:
    """Uptime check configuration."""

    name: str
    url: str
    method: str = "GET"
    headers: Dict[str, str] = None
    timeout: int = 10
    expected_status: int = 200
    expected_content: Optional[str] = None
    check_interval: int = 60  # seconds
    enabled: bool = True

    def __post_init__(self):
        if self.headers is None:
            self.headers = {}


class UptimeMonitor:
    """Uptime monitoring system."""

    def __init__(self, config_file: str = "uptime_config.json"):
        self.config_file = config_file
        self.uptime_checks: List[UptimeCheck] = []
        self.metric_thresholds: List[MetricThreshold] = []
        self.alerts: List[Alert] = []
        self.metrics_history: Dict[str, deque] = {}
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Alert handlers
        self.alert_handlers: List[Callable[[Alert], None]] = []

        # Load configuration
        self._load_config()

        # Setup logging
        self._setup_logging()

    def _load_config(self):
        """Load monitoring configuration."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)

                # Load uptime checks
                for check_data in data.get("uptime_checks", []):
                    check = UptimeCheck(**check_data)
                    self.uptime_checks.append(check)

                # Load metric thresholds
                for threshold_data in data.get("metric_thresholds", []):
                    threshold = MetricThreshold(
                        metric_type=MetricType(threshold_data["metric_type"]),
                        warning_threshold=threshold_data["warning_threshold"],
                        error_threshold=threshold_data["error_threshold"],
                        critical_threshold=threshold_data["critical_threshold"],
                        p95_threshold=threshold_data.get("p95_threshold"),
                        p99_threshold=threshold_data.get("p99_threshold"),
                    )
                    self.metric_thresholds.append(threshold)

            except Exception as e:
                print(f"Error loading uptime config: {e}")
                self._create_default_config()
        else:
            self._create_default_config()

    def _create_default_config(self):
        """Create default monitoring configuration."""
        # Default uptime checks
        default_checks = [
            UptimeCheck(
                name="CoolBits.ai Main",
                url="http://localhost:8501/_stcore/health",
                check_interval=30,
            ),
            UptimeCheck(
                name="Admin Console",
                url="http://localhost:8501/admin",
                check_interval=60,
            ),
            UptimeCheck(
                name="API Health",
                url="http://localhost:8501/api/health",
                check_interval=30,
            ),
        ]

        self.uptime_checks.extend(default_checks)

        # Default metric thresholds
        default_thresholds = [
            MetricThreshold(
                metric_type=MetricType.RESPONSE_TIME,
                warning_threshold=1000,  # 1 second
                error_threshold=3000,  # 3 seconds
                critical_threshold=5000,  # 5 seconds
                p95_threshold=2000,  # 2 seconds
            ),
            MetricThreshold(
                metric_type=MetricType.CPU_USAGE,
                warning_threshold=70,  # 70%
                error_threshold=85,  # 85%
                critical_threshold=95,  # 95%
                p95_threshold=80,  # 80%
            ),
            MetricThreshold(
                metric_type=MetricType.MEMORY_USAGE,
                warning_threshold=80,  # 80%
                error_threshold=90,  # 90%
                critical_threshold=95,  # 95%
                p95_threshold=85,  # 85%
            ),
            MetricThreshold(
                metric_type=MetricType.ERROR_RATE,
                warning_threshold=0.01,  # 1%
                error_threshold=0.05,  # 5%
                critical_threshold=0.10,  # 10%
                p95_threshold=0.02,  # 2%
            ),
        ]

        self.metric_thresholds.extend(default_thresholds)

        self._save_config()

    def _save_config(self):
        """Save monitoring configuration."""
        config = {
            "uptime_checks": [asdict(check) for check in self.uptime_checks],
            "metric_thresholds": [
                asdict(threshold) for threshold in self.metric_thresholds
            ],
        }

        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

    def _setup_logging(self):
        """Setup logging for monitoring."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("logs/uptime_monitor.log"),
                logging.StreamHandler(),
            ],
        )

        self.logger = logging.getLogger("uptime_monitor")

    def add_uptime_check(self, check: UptimeCheck):
        """Add new uptime check."""
        self.uptime_checks.append(check)
        self._save_config()

    def add_metric_threshold(self, threshold: MetricThreshold):
        """Add new metric threshold."""
        self.metric_thresholds.append(threshold)
        self._save_config()

    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """Add alert handler."""
        self.alert_handlers.append(handler)

    def _record_metric(
        self, metric_type: MetricType, value: float, service: str = "system"
    ):
        """Record metric value."""
        key = f"{service}_{metric_type.value}"

        if key not in self.metrics_history:
            self.metrics_history[key] = deque(maxlen=1000)  # Keep last 1000 values

        self.metrics_history[key].append({"value": value, "timestamp": datetime.now()})

        # Check thresholds
        self._check_thresholds(metric_type, value, service)

    def _check_thresholds(self, metric_type: MetricType, value: float, service: str):
        """Check metric against thresholds."""
        threshold = next(
            (t for t in self.metric_thresholds if t.metric_type == metric_type), None
        )
        if not threshold:
            return

        alert_level = None
        threshold_value = None

        if value >= threshold.critical_threshold:
            alert_level = AlertLevel.CRITICAL
            threshold_value = threshold.critical_threshold
        elif value >= threshold.error_threshold:
            alert_level = AlertLevel.ERROR
            threshold_value = threshold.error_threshold
        elif value >= threshold.warning_threshold:
            alert_level = AlertLevel.WARNING
            threshold_value = threshold.warning_threshold

        if alert_level:
            self._create_alert(
                alert_level, metric_type, value, threshold_value, service
            )

    def _create_alert(
        self,
        level: AlertLevel,
        metric_type: MetricType,
        value: float,
        threshold: float,
        service: str,
    ):
        """Create new alert."""
        alert_id = f"{service}_{metric_type.value}_{int(time.time())}"

        alert = Alert(
            id=alert_id,
            level=level,
            metric_type=metric_type,
            message=f"{metric_type.value} exceeded {threshold} (current: {value:.2f})",
            value=value,
            threshold=threshold,
            timestamp=datetime.now(),
            service=service,
        )

        self.alerts.append(alert)

        # Send alert to handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Error in alert handler: {e}")

        self.logger.warning(f"Alert created: {alert.message}")

    def _perform_uptime_check(self, check: UptimeCheck) -> Dict:
        """Perform single uptime check."""
        start_time = time.time()

        try:
            response = requests.request(
                method=check.method,
                url=check.url,
                headers=check.headers,
                timeout=check.timeout,
            )

            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            # Check status code
            status_ok = response.status_code == check.expected_status

            # Check content if specified
            content_ok = True
            if check.expected_content:
                content_ok = check.expected_content in response.text

            # Overall check result
            success = status_ok and content_ok

            # Record metrics
            self._record_metric(MetricType.RESPONSE_TIME, response_time, check.name)
            self._record_metric(MetricType.UPTIME, 1.0 if success else 0.0, check.name)

            if not success:
                self._record_metric(MetricType.ERROR_RATE, 1.0, check.name)

            return {
                "success": success,
                "response_time": response_time,
                "status_code": response.status_code,
                "timestamp": datetime.now(),
            }

        except requests.RequestException as e:
            response_time = (time.time() - start_time) * 1000

            self._record_metric(MetricType.RESPONSE_TIME, response_time, check.name)
            self._record_metric(MetricType.UPTIME, 0.0, check.name)
            self._record_metric(MetricType.ERROR_RATE, 1.0, check.name)

            self.logger.error(f"Uptime check failed for {check.name}: {e}")

            return {
                "success": False,
                "response_time": response_time,
                "error": str(e),
                "timestamp": datetime.now(),
            }

    def _collect_system_metrics(self):
        """Collect system metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self._record_metric(MetricType.CPU_USAGE, cpu_percent)

            # Memory usage
            memory = psutil.virtual_memory()
            self._record_metric(MetricType.MEMORY_USAGE, memory.percent)

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100
            self._record_metric(MetricType.DISK_USAGE, disk_percent)

        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")

    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Perform uptime checks
                for check in self.uptime_checks:
                    if check.enabled:
                        self._perform_uptime_check(check)

                # Collect system metrics
                self._collect_system_metrics()

                # Calculate percentiles
                self._calculate_percentiles()

                # Sleep until next check
                time.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error

    def _calculate_percentiles(self):
        """Calculate P95 and P99 percentiles for metrics."""
        for key, values in self.metrics_history.items():
            if len(values) < 10:  # Need at least 10 values
                continue

            metric_values = [v["value"] for v in values]

            # Calculate percentiles
            p95 = statistics.quantiles(metric_values, n=20)[18]  # 95th percentile
            p99 = statistics.quantiles(metric_values, n=100)[98]  # 99th percentile

            # Extract metric type and service from key
            parts = key.split("_", 1)
            service = parts[0] if len(parts) > 1 else "system"
            metric_type_str = parts[1] if len(parts) > 1 else parts[0]

            try:
                metric_type = MetricType(metric_type_str)

                # Check P95 thresholds
                threshold = next(
                    (t for t in self.metric_thresholds if t.metric_type == metric_type),
                    None,
                )
                if (
                    threshold
                    and threshold.p95_threshold
                    and p95 >= threshold.p95_threshold
                ):
                    self._create_alert(
                        AlertLevel.WARNING,
                        metric_type,
                        p95,
                        threshold.p95_threshold,
                        f"{service}_p95",
                    )

                # Check P99 thresholds
                if (
                    threshold
                    and threshold.p99_threshold
                    and p99 >= threshold.p99_threshold
                ):
                    self._create_alert(
                        AlertLevel.ERROR,
                        metric_type,
                        p99,
                        threshold.p99_threshold,
                        f"{service}_p99",
                    )

            except ValueError:
                continue  # Skip unknown metric types

    def start_monitoring(self):
        """Start monitoring."""
        if self.running:
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        self.logger.info("Uptime monitoring started")

    def stop_monitoring(self):
        """Stop monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()

        self.logger.info("Uptime monitoring stopped")

    def get_uptime_stats(self) -> Dict:
        """Get uptime statistics."""
        stats = {}

        for check in self.uptime_checks:
            key = f"{check.name}_uptime"
            if key in self.metrics_history:
                values = list(self.metrics_history[key])
                if values:
                    uptime_percent = (
                        sum(v["value"] for v in values) / len(values)
                    ) * 100
                    stats[check.name] = {
                        "uptime_percent": uptime_percent,
                        "total_checks": len(values),
                        "last_check": (
                            values[-1]["timestamp"].isoformat() if values else None
                        ),
                    }

        return stats

    def get_metrics_summary(self) -> Dict:
        """Get metrics summary."""
        summary = {}

        for key, values in self.metrics_history.items():
            if not values:
                continue

            metric_values = [v["value"] for v in values]

            summary[key] = {
                "count": len(metric_values),
                "min": min(metric_values),
                "max": max(metric_values),
                "avg": statistics.mean(metric_values),
                "p95": (
                    statistics.quantiles(metric_values, n=20)[18]
                    if len(metric_values) >= 10
                    else None
                ),
                "p99": (
                    statistics.quantiles(metric_values, n=100)[98]
                    if len(metric_values) >= 10
                    else None
                ),
                "last_updated": values[-1]["timestamp"].isoformat(),
            }

        return summary

    def get_active_alerts(self) -> List[Alert]:
        """Get active (unresolved) alerts."""
        return [alert for alert in self.alerts if not alert.resolved]

    def resolve_alert(self, alert_id: str):
        """Resolve alert."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                break


class EmailAlertHandler:
    """Email alert handler."""

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_email: str,
        to_emails: List[str],
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_emails = to_emails

    def __call__(self, alert: Alert):
        """Send email alert."""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = ", ".join(self.to_emails)
            msg["Subject"] = (
                f"[{alert.level.value.upper()}] CoolBits.ai Alert: {alert.metric_type.value}"
            )

            body = f"""
Alert Details:
- Level: {alert.level.value.upper()}
- Metric: {alert.metric_type.value}
- Service: {alert.service}
- Value: {alert.value:.2f}
- Threshold: {alert.threshold:.2f}
- Message: {alert.message}
- Timestamp: {alert.timestamp.isoformat()}

Please check the system immediately.
            """

            msg.attach(MimeText(body, "plain"))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.from_email, self.to_emails, text)
            server.quit()

        except Exception as e:
            print(f"Error sending email alert: {e}")


# Global uptime monitor instance
uptime_monitor = UptimeMonitor()


def start_uptime_monitoring():
    """Start global uptime monitoring."""
    uptime_monitor.start_monitoring()


def stop_uptime_monitoring():
    """Stop global uptime monitoring."""
    uptime_monitor.stop_monitoring()


def get_uptime_stats() -> Dict:
    """Get uptime statistics."""
    return uptime_monitor.get_uptime_stats()


def get_metrics_summary() -> Dict:
    """Get metrics summary."""
    return uptime_monitor.get_metrics_summary()


def get_active_alerts() -> List[Alert]:
    """Get active alerts."""
    return uptime_monitor.get_active_alerts()


if __name__ == "__main__":
    print("📊 CoolBits.ai Uptime Monitoring System")
    print("=======================================")

    # Initialize monitor
    monitor = UptimeMonitor()

    # Add email alert handler (example)
    # email_handler = EmailAlertHandler(
    #     smtp_server="smtp.gmail.com",
    #     smtp_port=587,
    #     username="alerts@coolbits.ai",
    #     password="your_password",
    #     from_email="alerts@coolbits.ai",
    #     to_emails=["admin@coolbits.ai"]
    # )
    # monitor.add_alert_handler(email_handler)

    # Start monitoring
    monitor.start_monitoring()

    print("✅ Uptime monitoring started")
    print("📈 Monitoring:")
    for check in monitor.uptime_checks:
        print(f"  - {check.name}: {check.url}")

    print("🎯 Thresholds configured:")
    for threshold in monitor.metric_thresholds:
        print(
            f"  - {threshold.metric_type.value}: W:{threshold.warning_threshold}, E:{threshold.error_threshold}, C:{threshold.critical_threshold}"
        )

    try:
        # Keep running
        while True:
            time.sleep(60)

            # Print stats every minute
            stats = monitor.get_uptime_stats()
            print(f"\n📊 Uptime Stats ({datetime.now().strftime('%H:%M:%S')}):")
            for service, data in stats.items():
                print(f"  {service}: {data['uptime_percent']:.1f}% uptime")

            # Print active alerts
            alerts = monitor.get_active_alerts()
            if alerts:
                print(f"🚨 Active Alerts: {len(alerts)}")
                for alert in alerts[-3:]:  # Show last 3 alerts
                    print(f"  - {alert.level.value.upper()}: {alert.message}")

    except KeyboardInterrupt:
        print("\n🛑 Stopping monitoring...")
        monitor.stop_monitoring()
        print("✅ Monitoring stopped")
