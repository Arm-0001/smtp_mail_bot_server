import asyncio
from aiosmtpd.controller import Controller
from email import message_from_bytes
import random
import string
import subprocess
import re

domain = "coolkids.bio"

# Function to generate a random email and username
def generate_random_email_and_username():
    random_string = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))
    return f"{random_string}@{domain}", f"user_{random_string}"

# Function to find and extract a link matching the specified format
def extract_link_from_text(text):
    # Define a regular expression pattern to match the link format
    link_pattern = r'https://vyper\.io/entries/confirm\?entry_id=[\w\d]+&hash=\d+'
    match = re.search(link_pattern, text)
    if match:
        return match.group(0)
    return None

class MailHandler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        if not address.endswith(f'@{domain}'):
            print(f"Address does not end with @{domain}")
            return '550 not relaying to that domain'
        envelope.rcpt_tos.append(address)
        return '250 OK'
    
    async def handle_DATA(self, server, session, envelope):
        # Extract the sender's email address
        sender_email = envelope.mail_from

        # Extract the recipient's email address
        recipient_email = envelope.rcpt_tos[0] if envelope.rcpt_tos else None

        # Extract the plain text part of the email
        plain_text_part = None
        email_message = message_from_bytes(envelope.content)
        for part in email_message.walk():
            if part.get_content_type() == 'text/plain':
                plain_text_part = part.get_payload(decode=True).decode('utf-8')
                break
        
        if sender_email and recipient_email and plain_text_part:
            # Print email content
            #print("Received email from:", sender_email)
            print("Received email for:", recipient_email)
            #print("Plain text content:")
            #print(plain_text_part)

            # Find a link matching the specified format
            link = extract_link_from_text(plain_text_part)

            if link:
                print("Found link:", link)

                # Run 'clicklink.py' with the link as an argument
                subprocess.run(['python', 'clicklink.py', link])

                print("Successfully ran clicklink.py with the link as an argument.")

        # Finish processing the email
        return '250 Message accepted for delivery'

# Start the email server
controller = Controller(MailHandler(), hostname='192.168.68.107', port=25)
controller.start()
print("Email server started")

# Your existing code to run the email server asynchronously
asyncio.get_event_loop().run_forever()
