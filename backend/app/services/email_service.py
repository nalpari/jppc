"""Email service for sending notifications."""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

import aiosmtplib
from jinja2 import Environment, PackageLoader, select_autoescape

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


@dataclass
class EmailMessage:
    """Email message structure."""

    to: list[str]
    subject: str
    html_body: str
    text_body: str | None = None
    cc: list[str] | None = None
    bcc: list[str] | None = None


class EmailService:
    """Service for sending email notifications."""

    def __init__(self):
        self._jinja_env = Environment(
            loader=PackageLoader("app", "templates/email"),
            autoescape=select_autoescape(["html", "xml"]),
        )
        self._jinja_env.filters["format_datetime"] = self._format_datetime
        self._jinja_env.filters["format_currency"] = self._format_currency
        self._jinja_env.filters["format_percentage"] = self._format_percentage

    @staticmethod
    def _format_datetime(value: datetime | str | None) -> str:
        """Format datetime for display."""
        if not value:
            return "-"
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        return value.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _format_currency(value: float | None, currency: str = "¥") -> str:
        """Format currency for display."""
        if value is None:
            return "-"
        return f"{currency}{value:,.2f}"

    @staticmethod
    def _format_percentage(value: float | None) -> str:
        """Format percentage for display."""
        if value is None:
            return "-"
        sign = "+" if value > 0 else ""
        return f"{sign}{value:.1f}%"

    async def send_email(self, message: EmailMessage) -> bool:
        """Send an email message.

        Args:
            message: Email message to send

        Returns:
            True if sent successfully, False otherwise
        """
        if not settings.smtp_host:
            logger.warning("SMTP not configured, skipping email")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = message.subject
            msg["From"] = settings.smtp_from
            msg["To"] = ", ".join(message.to)

            if message.cc:
                msg["Cc"] = ", ".join(message.cc)

            # Add text body
            if message.text_body:
                msg.attach(MIMEText(message.text_body, "plain", "utf-8"))

            # Add HTML body
            msg.attach(MIMEText(message.html_body, "html", "utf-8"))

            # Send email
            await aiosmtplib.send(
                msg,
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_user,
                password=settings.smtp_password,
                use_tls=settings.smtp_port == 465,
                start_tls=settings.smtp_port == 587,
            )

            logger.info(f"Email sent to {message.to}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def render_template(
        self, template_name: str, context: dict[str, Any]
    ) -> tuple[str, str]:
        """Render an email template.

        Args:
            template_name: Name of the template file (without extension)
            context: Template context variables

        Returns:
            Tuple of (html_content, text_content)
        """
        # Render HTML
        html_template = self._jinja_env.get_template(f"{template_name}.html")
        html_content = html_template.render(**context)

        # Try to render text version
        try:
            text_template = self._jinja_env.get_template(f"{template_name}.txt")
            text_content = text_template.render(**context)
        except Exception:
            # Fall back to stripping HTML
            text_content = self._html_to_text(html_content)

        return html_content, text_content

    @staticmethod
    def _html_to_text(html: str) -> str:
        """Simple HTML to text conversion."""
        import re

        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", html)
        # Decode HTML entities
        text = text.replace("&nbsp;", " ")
        text = text.replace("&amp;", "&")
        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")
        # Clean up whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    async def send_crawl_failure_alert(
        self,
        recipients: list[str],
        company_name: str,
        error_message: str,
        crawl_time: datetime,
        job_id: str | None = None,
    ) -> bool:
        """Send a crawl failure alert.

        Args:
            recipients: List of email addresses
            company_name: Name of the company that failed
            error_message: Error message
            crawl_time: Time of the failed crawl
            job_id: Optional job ID

        Returns:
            True if sent successfully
        """
        context = {
            "company_name": company_name,
            "error_message": error_message,
            "crawl_time": crawl_time,
            "job_id": job_id,
        }

        html_body, text_body = self.render_template("crawl_failure", context)

        message = EmailMessage(
            to=recipients,
            subject=f"[JPPC Alert] Crawl Failed: {company_name}",
            html_body=html_body,
            text_body=text_body,
        )

        return await self.send_email(message)

    async def send_price_change_alert(
        self,
        recipients: list[str],
        company_name: str,
        changes: list[dict[str, Any]],
        crawl_time: datetime,
    ) -> bool:
        """Send a price change alert.

        Args:
            recipients: List of email addresses
            company_name: Company name
            changes: List of price changes
            crawl_time: Time of the crawl

        Returns:
            True if sent successfully
        """
        context = {
            "company_name": company_name,
            "changes": changes,
            "crawl_time": crawl_time,
            "change_count": len(changes),
        }

        html_body, text_body = self.render_template("price_change", context)

        message = EmailMessage(
            to=recipients,
            subject=f"[JPPC Alert] Price Change Detected: {company_name}",
            html_body=html_body,
            text_body=text_body,
        )

        return await self.send_email(message)

    async def send_weekly_report(
        self,
        recipients: list[str],
        report_data: dict[str, Any],
    ) -> bool:
        """Send a weekly summary report.

        Args:
            recipients: List of email addresses
            report_data: Report data including:
                - period_start: Start of reporting period
                - period_end: End of reporting period
                - companies: List of company summaries
                - crawl_stats: Crawl statistics
                - price_changes: Price changes during period

        Returns:
            True if sent successfully
        """
        html_body, text_body = self.render_template("weekly_report", report_data)

        period_end = report_data.get("period_end", datetime.utcnow())
        if isinstance(period_end, str):
            period_end = datetime.fromisoformat(period_end)

        message = EmailMessage(
            to=recipients,
            subject=f"[JPPC] Weekly Report - {period_end.strftime('%Y-%m-%d')}",
            html_body=html_body,
            text_body=text_body,
        )

        return await self.send_email(message)


# Global service instance
email_service = EmailService()
