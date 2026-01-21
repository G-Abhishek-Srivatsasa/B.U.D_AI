import imaplib
import email
from email.header import decode_header

def get_unread_emails(username, password, limit=5):
    """
    Fetches the last N unread emails from Gmail.
    Returns: A list of strings (Sender - Subject).
    """
    if not username or not password or "YOUR_EMAIL" in username:
        return ["Error: Email credentials are not set in main.py."]

    try:
        # 1. Connect to Gmail
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(username, password)
        
        # 2. Select Inbox
        mail.select("inbox")

        # 3. Search for Unread Emails
        status, messages = mail.search(None, "UNSEEN")
        email_ids = messages[0].split()

        if not email_ids:
            return ["No new unread emails."]

        # 4. Fetch latest N emails
        results = []
        # Get the latest IDs (reversed)
        latest_ids = email_ids[-limit:]
        
        for e_id in reversed(latest_ids):
            _, msg_data = mail.fetch(e_id, "(RFC822)")
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Decode Subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                        
                    # Decode Sender
                    from_ = msg.get("From")
                    
                    results.append(f"From: {from_} | Subject: {subject}")

        mail.close()
        mail.logout()
        return results

    except Exception as e:
        print(f"Mail Error: {e}")
        return [f"Error checking email: {e}"]
