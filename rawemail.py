import asyncio
import sqlite3
import os
from aiosmtpd.controller import Controller
from email import message_from_bytes
from email.policy import default
import datetime

# Create database and table if they don't exist or update if structure has changed
def init_database():
    conn = sqlite3.connect("emails.db")
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='emails'")
    table_exists = cursor.fetchone() is not None
    
    if table_exists:
        # Check if columns exist
        cursor.execute("PRAGMA table_info(emails)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add missing columns if needed
        required_columns = ['id', 'timestamp', 'sender', 'recipient', 'subject', 'body', 'raw_content']
        for column in required_columns:
            if column not in columns:
                if column == 'id':
                    cursor.execute(f"ALTER TABLE emails ADD COLUMN {column} INTEGER PRIMARY KEY AUTOINCREMENT")
                else:
                    cursor.execute(f"ALTER TABLE emails ADD COLUMN {column} TEXT")
                print(f"Added missing column '{column}' to emails table")
    else:
        # Create new table with all required columns
        cursor.execute('''
        CREATE TABLE emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            sender TEXT,
            recipient TEXT,
            subject TEXT,
            body TEXT,
            raw_content TEXT
        )
        ''')
        print("Created new emails table")
    
    conn.commit()
    conn.close()

class MailHandler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        # Only accept emails for your domain
        if not address.endswith('@uefnmarket.shop'):
            print(f"Rejected email to {address} - not for our domain")
            return '550 not relaying to that domain'
        envelope.rcpt_tos.append(address)
        return '250 OK'
    
    async def handle_DATA(self, server, session, envelope):
        # Establish a new SQLite connection for this session
        db_connection = sqlite3.connect("emails.db")
        cursor = db_connection.cursor()
        
        # Extract email details
        timestamp = datetime.datetime.now().isoformat()
        sender_email = envelope.mail_from
        recipient_emails = envelope.rcpt_tos
        raw_email_content = envelope.content.decode('utf-8', errors='replace')
        
        # Parse the email
        email_message = message_from_bytes(envelope.content, policy=default)
        subject = email_message.get('Subject', 'No Subject')
        
        # Get email body
        body = ""
        if email_message.is_multipart():
            for part in email_message.iter_parts():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    body = part.get_content()
                    break
        else:
            body = email_message.get_content()
        
        # Log to console
        print("\n" + "="*50)
        print(f"RECEIVED EMAIL AT: {timestamp}")
        print(f"FROM: {sender_email}")
        print(f"TO: {', '.join(recipient_emails)}")
        print(f"SUBJECT: {subject}")
        print("-"*50)
        print("BODY:")
        print(body)
        print("="*50)
        
        # Save to database
        for recipient in recipient_emails:
            cursor.execute(
                "INSERT INTO emails (timestamp, sender, recipient, subject, body, raw_content) VALUES (?, ?, ?, ?, ?, ?)",
                (timestamp, sender_email, recipient, subject, body, raw_email_content)
            )
        
        db_connection.commit()
        db_connection.close()
        
        print(f"Email saved to database for {len(recipient_emails)} recipient(s)")
        return '250 Message accepted for delivery'

# Initialize the database
init_database()

# Start the email server
controller = Controller(MailHandler(), hostname='192.168.68.107', port=25)
controller.start()
print("Email server started. Accepting messages for uefnmarket.shop domain.")

# Run the email server asynchronously
try:
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    print("Server shutting down...")
    controller.stop()
