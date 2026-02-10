"""
Alert Integrations for Kill Switch System
Supports Slack, Email, PagerDuty, and webhook notifications.
"""

import asyncio
import json
import logging
import smtplib
import ssl
from dataclasses import dataclass
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class AlertMessage:
    """Standardized alert message format."""
    title: str
    description: str
    severity: str  # info, warning, critical
    timestamp: datetime
    source: str
    metadata: Dict[str, Any]
    actions: List[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.actions is None:
            self.actions = []


class SlackNotifier:
    """Slack webhook notification handler."""
    
    def __init__(self, webhook_url: str, channel: str = None, username: str = "Kill Switch"):
        self.webhook_url = webhook_url
        self.channel = channel
        self.username = username
        self._last_alert_time: Dict[str, datetime] = {}
        self._cooldown_seconds = 300  # 5 min default cooldown
    
    def _get_color(self, severity: str) -> str:
        """Get Slack color code for severity."""
        colors = {
            "info": "#36a64f",      # Green
            "warning": "#ff9900",   # Orange
            "critical": "#ff0000",  # Red
            "emergency": "#990000"  # Dark red
        }
        return colors.get(severity, "#cccccc")
    
    def _get_emoji(self, severity: str) -> str:
        """Get emoji for severity."""
        emojis = {
            "info": "ℹ️",
            "warning": "⚠️",
            "critical": "🚨",
            "emergency": "🆘"
        }
        return emojis.get(severity, "📋")
    
    def _check_cooldown(self, alert_key: str) -> bool:
        """Check if alert is within cooldown period."""
        now = datetime.now()
        last_time = self._last_alert_time.get(alert_key)
        
        if last_time is None:
            return True
        
        elapsed = (now - last_time).total_seconds()
        return elapsed > self._cooldown_seconds
    
    async def send(self, message: AlertMessage, alert_key: str = None) -> bool:
        """Send alert to Slack."""
        if alert_key and not self._check_cooldown(alert_key):
            logger.debug(f"Alert {alert_key} suppressed due to cooldown")
            return False
        
        emoji = self._get_emoji(message.severity)
        color = self._get_color(message.severity)
        
        # Build attachment fields from metadata
        fields = []
        for key, value in message.metadata.items():
            if isinstance(value, (int, float, str)):
                fields.append({
                    "title": key.replace("_", " ").title(),
                    "value": str(value),
                    "short": len(str(value)) < 20
                })
        
        # Add action buttons if provided
        actions = []
        for action in message.actions:
            actions.append({
                "type": "button",
                "text": action.get("text", "Action"),
                "url": action.get("url", "#"),
                "style": action.get("style", "default")
            })
        
        payload = {
            "username": self.username,
            "icon_emoji": emoji,
            "attachments": [{
                "color": color,
                "title": f"{emoji} {message.title}",
                "text": message.description,
                "fields": fields,
                "footer": f"Source: {message.source}",
                "ts": message.timestamp.timestamp(),
                "actions": actions if actions else None
            }]
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        if alert_key:
                            self._last_alert_time[alert_key] = datetime.now()
                        logger.info(f"Slack alert sent: {message.title}")
                        return True
                    else:
                        text = await response.text()
                        logger.error(f"Slack alert failed: {response.status} - {text}")
                        return False
        except asyncio.TimeoutError:
            logger.error("Slack alert timeout")
            return False
        except Exception as e:
            logger.error(f"Slack alert error: {e}")
            return False


class EmailNotifier:
    """Email notification handler."""
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_address: str,
        to_addresses: List[str],
        use_tls: bool = True
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_address = from_address
        self.to_addresses = to_addresses
        self.use_tls = use_tls
        self._last_alert_time: Dict[str, datetime] = {}
        self._cooldown_seconds = 300
    
    def _check_cooldown(self, alert_key: str) -> bool:
        """Check if alert is within cooldown period."""
        now = datetime.now()
        last_time = self._last_alert_time.get(alert_key)
        
        if last_time is None:
            return True
        
        elapsed = (now - last_time).total_seconds()
        return elapsed > self._cooldown_seconds
    
    def _build_html_body(self, message: AlertMessage) -> str:
        """Build HTML email body."""
        colors = {
            "info": "#36a64f",
            "warning": "#ff9900",
            "critical": "#ff0000",
            "emergency": "#990000"
        }
        color = colors.get(message.severity, "#cccccc")
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="border-left: 5px solid {color}; padding-left: 15px;">
                <h2 style="color: {color};">{message.title}</h2>
                <p style="font-size: 16px;">{message.description}</p>
                
                <h3>Details:</h3>
                <table style="border-collapse: collapse; width: 100%;">
        """
        
        for key, value in message.metadata.items():
            html += f"""
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">
                            {key.replace("_", " ").title()}
                        </td>
                        <td style="padding: 8px; border: 1px solid #ddd;">
                            {value}
                        </td>
                    </tr>
            """
        
        html += f"""
                </table>
                
                <p style="margin-top: 20px; color: #666; font-size: 12px;">
                    Source: {message.source}<br>
                    Time: {message.timestamp.isoformat()}
                </p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    async def send(self, message: AlertMessage, alert_key: str = None) -> bool:
        """Send email alert."""
        if alert_key and not self._check_cooldown(alert_key):
            logger.debug(f"Email alert {alert_key} suppressed due to cooldown")
            return False
        
        try:
            # Build message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[Kill Switch] {message.severity.upper()}: {message.title}"
            msg['From'] = self.from_address
            msg['To'] = ", ".join(self.to_addresses)
            
            # HTML body
            html_body = self._build_html_body(message)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send via SMTP in executor to not block
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._send_smtp, msg)
            
            if alert_key:
                self._last_alert_time[alert_key] = datetime.now()
            
            logger.info(f"Email alert sent: {message.title}")
            return True
            
        except Exception as e:
            logger.error(f"Email alert error: {e}")
            return False
    
    def _send_smtp(self, msg: MIMEMultipart):
        """Synchronous SMTP send."""
        context = ssl.create_default_context() if self.use_tls else None
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            if self.use_tls:
                server.starttls(context=context)
            server.login(self.username, self.password)
            server.sendmail(
                self.from_address,
                self.to_addresses,
                msg.as_string()
            )


class PagerDutyNotifier:
    """PagerDuty incident creation handler."""
    
    INTEGRATION_URL = "https://events.pagerduty.com/v2/enqueue"
    
    def __init__(self, integration_key: str, service_id: str = None):
        self.integration_key = integration_key
        self.service_id = service_id
        self._incident_cache: Dict[str, str] = {}  # alert_key -> incident_id
    
    def _get_severity(self, severity: str) -> str:
        """Map severity to PagerDuty severity."""
        mapping = {
            "info": "info",
            "warning": "warning",
            "critical": "critical",
            "emergency": "critical"
        }
        return mapping.get(severity, "warning")
    
    async def send(self, message: AlertMessage, alert_key: str = None) -> bool:
        """Create or update PagerDuty incident."""
        if message.severity not in ["critical", "emergency"]:
            # Only create incidents for critical/emergency
            return True
        
        payload = {
            "routing_key": self.integration_key,
            "event_action": "trigger",
            "dedup_key": alert_key or message.title,
            "payload": {
                "summary": message.title,
                "severity": self._get_severity(message.severity),
                "source": message.source,
                "component": "Kill Switch System",
                "group": "Trading System",
                "class": "Circuit Breaker",
                "custom_details": message.metadata
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.INTEGRATION_URL,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status in [200, 202]:
                        data = await response.json()
                        if alert_key:
                            self._incident_cache[alert_key] = data.get('dedup_key')
                        logger.info(f"PagerDuty incident created: {message.title}")
                        return True
                    else:
                        text = await response.text()
                        logger.error(f"PagerDuty alert failed: {response.status} - {text}")
                        return False
        except Exception as e:
            logger.error(f"PagerDuty alert error: {e}")
            return False
    
    async def resolve(self, alert_key: str) -> bool:
        """Resolve a PagerDuty incident."""
        if alert_key not in self._incident_cache:
            return False
        
        payload = {
            "routing_key": self.integration_key,
            "event_action": "resolve",
            "dedup_key": self._incident_cache[alert_key]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.INTEGRATION_URL,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status in [200, 202]:
                        del self._incident_cache[alert_key]
                        logger.info(f"PagerDuty incident resolved: {alert_key}")
                        return True
                    return False
        except Exception as e:
            logger.error(f"PagerDuty resolve error: {e}")
            return False


class WebhookNotifier:
    """Generic webhook notifier for custom integrations."""
    
    def __init__(self, webhook_url: str, headers: Dict[str, str] = None):
        self.webhook_url = webhook_url
        self.headers = headers or {}
        self._last_alert_time: Dict[str, datetime] = {}
        self._cooldown_seconds = 60
    
    def _check_cooldown(self, alert_key: str) -> bool:
        """Check if alert is within cooldown period."""
        now = datetime.now()
        last_time = self._last_alert_time.get(alert_key)
        
        if last_time is None:
            return True
        
        elapsed = (now - last_time).total_seconds()
        return elapsed > self._cooldown_seconds
    
    async def send(self, message: AlertMessage, alert_key: str = None) -> bool:
        """Send webhook notification."""
        if alert_key and not self._check_cooldown(alert_key):
            return False
        
        payload = {
            "title": message.title,
            "description": message.description,
            "severity": message.severity,
            "timestamp": message.timestamp.isoformat(),
            "source": message.source,
            "metadata": message.metadata
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status < 400:
                        if alert_key:
                            self._last_alert_time[alert_key] = datetime.now()
                        logger.info(f"Webhook alert sent: {message.title}")
                        return True
                    else:
                        text = await response.text()
                        logger.error(f"Webhook alert failed: {response.status} - {text}")
                        return False
        except Exception as e:
            logger.error(f"Webhook alert error: {e}")
            return False


class AlertManager:
    """Centralized alert manager coordinating multiple notification channels."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.notifiers: List[Any] = []
        self._setup_notifiers()
    
    def _setup_notifiers(self):
        """Initialize notifiers based on configuration."""
        # Slack
        slack_config = self.config.get('slack', {})
        if slack_config.get('webhook_url'):
            self.notifiers.append(SlackNotifier(
                webhook_url=slack_config['webhook_url'],
                channel=slack_config.get('channel'),
                username=slack_config.get('username', 'Kill Switch')
            ))
        
        # Email
        email_config = self.config.get('email', {})
        if email_config.get('enabled'):
            self.notifiers.append(EmailNotifier(
                smtp_server=email_config['smtp_server'],
                smtp_port=email_config['smtp_port'],
                username=email_config['username'],
                password=email_config['password'],
                from_address=email_config['from_address'],
                to_addresses=email_config['to_addresses'],
                use_tls=email_config.get('use_tls', True)
            ))
        
        # PagerDuty
        pagerduty_config = self.config.get('pagerduty', {})
        if pagerduty_config.get('integration_key'):
            self.notifiers.append(PagerDutyNotifier(
                integration_key=pagerduty_config['integration_key'],
                service_id=pagerduty_config.get('service_id')
            ))
        
        # Custom webhooks
        for webhook_config in self.config.get('webhooks', []):
            self.notifiers.append(WebhookNotifier(
                webhook_url=webhook_config['url'],
                headers=webhook_config.get('headers', {})
            ))
    
    async def send_alert(
        self,
        title: str,
        description: str,
        severity: str,
        source: str,
        metadata: Dict[str, Any] = None,
        actions: List[Dict[str, str]] = None,
        alert_key: str = None
    ) -> Dict[str, bool]:
        """Send alert through all configured channels."""
        message = AlertMessage(
            title=title,
            description=description,
            severity=severity,
            timestamp=datetime.now(),
            source=source,
            metadata=metadata or {},
            actions=actions
        )
        
        results = {}
        
        # Send to all notifiers concurrently
        tasks = []
        for notifier in self.notifiers:
            task = asyncio.create_task(
                self._send_with_error_handling(notifier, message, alert_key)
            )
            tasks.append((notifier.__class__.__name__, task))
        
        for name, task in tasks:
            try:
                result = await task
                results[name] = result
            except Exception as e:
                logger.error(f"Notifier {name} failed: {e}")
                results[name] = False
        
        return results
    
    async def _send_with_error_handling(self, notifier, message, alert_key) -> bool:
        """Send alert with error handling."""
        try:
            return await notifier.send(message, alert_key)
        except Exception as e:
            logger.error(f"Alert send failed: {e}")
            return False
    
    async def resolve_incident(self, alert_key: str):
        """Resolve an incident across all notifiers that support it."""
        for notifier in self.notifiers:
            if hasattr(notifier, 'resolve'):
                try:
                    await notifier.resolve(alert_key)
                except Exception as e:
                    logger.error(f"Resolve failed for {notifier}: {e}")


# Convenience functions for kill switch integration

async def send_kill_switch_alert(
    level: str,
    reason: str,
    strategy_id: Optional[str],
    threshold: float,
    actual_value: float,
    initiator: Optional[str],
    alert_manager: AlertManager
):
    """Send standardized kill switch alert."""
    
    severity_map = {
        "STRATEGY_HALT": "warning",
        "STRATEGY_CLOSE": "warning",
        "PORTFOLIO_SOFT": "critical",
        "PORTFOLIO_HARD": "critical",
        "EMERGENCY": "emergency"
    }
    
    severity = severity_map.get(level, "warning")
    
    title = f"Kill Switch: {level}"
    if strategy_id:
        title += f" ({strategy_id})"
    
    description = f"Kill switch triggered due to {reason}"
    
    metadata = {
        "level": level,
        "reason": reason,
        "strategy_id": strategy_id or "N/A",
        "threshold": threshold,
        "actual_value": actual_value,
        "initiator": initiator or "SYSTEM"
    }
    
    actions = []
    if level in ["PORTFOLIO_HARD", "EMERGENCY"]:
        actions.append({
            "text": "View Dashboard",
            "url": "https://your-dashboard.com/kill-switch",
            "style": "primary"
        })
    
    alert_key = f"{level}_{strategy_id or 'portfolio'}"
    
    await alert_manager.send_alert(
        title=title,
        description=description,
        severity=severity,
        source="KillSwitchSystem",
        metadata=metadata,
        actions=actions,
        alert_key=alert_key
    )


if __name__ == "__main__":
    # Example usage
    async def test_alerts():
        config = {
            'slack': {
                'webhook_url': 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
            }
        }
        
        manager = AlertManager(config)
        
        await manager.send_alert(
            title="Test Alert",
            description="This is a test alert from the kill switch system",
            severity="warning",
            source="test",
            metadata={"test": True, "value": 123}
        )
    
    asyncio.run(test_alerts())
