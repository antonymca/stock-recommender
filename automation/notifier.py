import os
import json
import smtplib
import ssl
import requests
from email.mime.text import MIMEText


def send_slack(text: str):
    url = os.getenv("SLACK_WEBHOOK_URL")
    if not url:
        return
    try:
        requests.post(url, json={"text": text}, timeout=10)
    except Exception:
        pass


def send_email(subject: str, html: str):
    user = os.getenv("SMTP_USER")
    pwd = os.getenv("SMTP_PASS")
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    to = os.getenv("EMAIL_TO")
    if not all([user, pwd, host, port, to]):
        return
    msg = MIMEText(html, "html")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to
    try:
        with smtplib.SMTP(host, port) as s:
            s.starttls(context=ssl.create_default_context())
            s.login(user, pwd)
            s.sendmail(user, [to], msg.as_string())
    except Exception:
        pass


def send_telegram(text: str):
    token = os.getenv("TG_BOT_TOKEN")
    chat = os.getenv("TG_CHAT_ID")
    if not token or not chat:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat, "text": text},
            timeout=10,
        )
    except Exception:
        pass


def notify(title: str, payload: dict):
    text = f"*{title}*\n```{json.dumps(payload, indent=2)}```"
    html = f"<h3>{title}</h3><pre>{json.dumps(payload, indent=2)}</pre>"
    send_slack(text)
    send_email(title, html)
    send_telegram(f"{title}\n{json.dumps(payload, indent=2)}")
