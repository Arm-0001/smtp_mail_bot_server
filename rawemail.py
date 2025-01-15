import asyncio
import sqlite3
import html
import re
import os
import time
import requests
from aiosmtpd.controller import Controller
from email import message_from_bytes
from email.policy import default
from urllib.parse import urlparse
import string

domain = "pandabuyspreads.com"

class MailHandler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        if not address.endswith(f'@{domain}'):
            print(f"Address does not end with @{domain}")
            return '550 not relaying to that domain'
        envelope.rcpt_tos.append(address)
        return '250 OK'
    
    async def handle_DATA(self, server, session, envelope):
        # Establish a new SQLite connection for this session
        db_connection = sqlite3.connect("emails.db")
        cursor = db_connection.cursor()
        
        # Extract the sender's email address
        sender_email = envelope.mail_from
        recipient_email = envelope.rcpt_tos[0] if envelope.rcpt_tos else None
        plain_text_part = None
        qr_code_path = None  # To store the path of the saved QR code

        # Extract email content
        email_message = message_from_bytes(envelope.content, policy=default)
        raw_email_content = envelope.content.decode('utf-8', errors='replace')
        # Display extracted information
        print(f"Email saved to database for recipient: {recipient_email}")
        print(f"Extracted Offer Details: {email_message}")
        
        # Close the SQLite connection for this session
        db_connection.close()
        return '250 Message accepted for delivery'

# Start the email server
controller = Controller(MailHandler(), hostname='192.168.68.107', port=25)
controller.start()
print("Email server started")

# Run the email server asynchronously
asyncio.get_event_loop().run_forever()
