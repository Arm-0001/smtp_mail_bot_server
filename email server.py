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

# Ensure a directory exists to save QR codes
os.makedirs("qr_codes", exist_ok=True)

# Database initialization function
def initialize_database():
    db_connection = sqlite3.connect("emails.db")
    cursor = db_connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS emails (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sender_email TEXT,
                        recipient_email TEXT,
                        plain_text_content TEXT,
                        qr_code_path TEXT,
                        raw_email_content TEXT,
                        received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''')
    db_connection.commit()
    db_connection.close()

# Initialize the database
initialize_database()

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
        html_content = None

        for part in email_message.iter_parts():
            # Extract plain text part of the email
            if part.get_content_type() == 'text/plain':
                plain_text_part = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
            # Extract HTML part of the email
            elif part.get_content_type() == 'text/html':
                html_content = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
            # Check if there's an image attachment (QR code)
            elif part.get_content_type().startswith('image/') and part.get_filename():
                # Generate a unique filename and save the QR code
                qr_code_filename = f"qr_{recipient_email}_{int(time.time())}.png"
                qr_code_path = os.path.join("qr_codes", qr_code_filename)
                with open(qr_code_path, "wb") as qr_code_file:
                    qr_code_file.write(part.get_payload(decode=True))

        # If HTML content exists, look for the specific embedded QR code image
        item_name = "unknown_item"
        if html_content:
            html_content = html.unescape(html_content)
            # Find all images in the HTML and select the one within the specified div
            qr_code_matches = re.findall(r'<div class="element-1015412"[^>]*>.*?<img[^>]+src="(https?://[^"]+)"', html_content, re.DOTALL)
            item_match = re.search(r'Grattis! Du har vunnit!!!\s*(.*?)\s*', html_content, re.IGNORECASE)
            if item_match:
                item_name = item_match.group(1).strip().replace(" ", "_").lower()
                # Remove invalid filename characters
                valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
                item_name = ''.join(c for c in item_name if c in valid_chars)
            for qr_code_url in qr_code_matches:
                parsed_url = urlparse(qr_code_url)
                if "scratcher.io" in parsed_url.netloc:
                    # Attempt to download the QR code image
                    try:
                        response = requests.get(qr_code_url, stream=True)
                        if response.status_code == 200:
                            timestamp = int(time.time())
                            qr_code_filename = f"{item_name}_{timestamp}.png"
                            qr_code_path = os.path.join("qr_codes", qr_code_filename)
                            with open(qr_code_path, "wb") as qr_code_file:
                                for chunk in response.iter_content(1024):
                                    qr_code_file.write(chunk)
                            print(f"QR Code saved at: {qr_code_path}")
                    except Exception as e:
                        print(f"Failed to download QR code from {qr_code_url}: {e}")

        # Decode any HTML entities in the plain text content for Swedish characters
        if plain_text_part:
            plain_text_part = html.unescape(plain_text_part)
        
            # Updated regex patterns to handle different formats
            item_match = re.search(r'Grattis! Du har vunnit!!!\s*(.*?)\s*', plain_text_part, re.IGNORECASE)

            # Structure extracted info
            item = item_match.group(1).strip() if item_match else "N/A"

            # Save email content and QR code path to SQLite3 database
            cursor.execute('''INSERT INTO emails (sender_email, recipient_email, plain_text_content, qr_code_path, raw_email_content)
                              VALUES (?, ?, ?, ?, ?)''', 
                           (sender_email, recipient_email, plain_text_part, qr_code_path, raw_email_content))
            db_connection.commit()

            # Display extracted information
            print(f"Email saved to database for recipient: {recipient_email}")
            print(f"Extracted Offer Details:")
            print(f"- Item: {item}")
            if qr_code_path:
                print(f"QR Code saved at: {qr_code_path}")
        
        # Close the SQLite connection for this session
        db_connection.close()
        return '250 Message accepted for delivery'

# Start the email server
controller = Controller(MailHandler(), hostname='192.168.68.107', port=25)
controller.start()
print("Email server started")

# Run the email server asynchronously
asyncio.get_event_loop().run_forever()
