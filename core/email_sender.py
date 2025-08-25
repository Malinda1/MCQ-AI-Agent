import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment
import base64
from utils.logger import logger
from config.settings import settings
from datetime import datetime

class EmailSender:
    def __init__(self):
        self.sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    
    def send_mcq_pdf(self, recipient_email: str, pdf_path: str, recipient_name: str = None, subject: str = None):
        """Send MCQ PDF via email with improved deliverability"""
        try:
            # More personalized subject line
            if not subject:
                subject = f"Your MCQ Assessment Results - {datetime.now().strftime('%B %d, %Y')}"
            
            # Create personalized HTML content
            html_content = self._create_html_content(recipient_name or "Student")
            
            message = Mail(
                from_email=('malindap288@gmail.com', 'MCQ Assessment System'),
                to_emails=recipient_email,
                subject=subject,
                html_content=html_content
            )
            
            # Add PDF attachment
            with open(pdf_path, 'rb') as f:
                data = f.read()
                encoded = base64.b64encode(data).decode()
            
            attachment = Attachment(
                file_content=encoded,
                file_type='application/pdf',
                file_name='MCQ_Assessment_Results.pdf',
                disposition='attachment'
            )
            message.attachment = attachment
            
            response = self.sg.send(message)
            logger.info(f"Email sent successfully to {recipient_email}, Status: {response.status_code}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {recipient_email}: {e}")
            return False
    
    def _create_html_content(self, recipient_name: str) -> str:
        """Create rich HTML content for better deliverability"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Your MCQ Assessment Results</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; margin-bottom: 30px;">
                <h1 style="color: #2c3e50; margin-bottom: 20px; text-align: center;">MCQ Assessment System</h1>
                <hr style="border: none; height: 2px; background-color: #3498db; margin: 20px 0;">
            </div>
            
            <div style="background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #2980b9; margin-bottom: 20px;">Dear {recipient_name},</h2>
                
                <p style="font-size: 16px; margin-bottom: 20px;">
                    Thank you for completing your MCQ assessment! We're pleased to provide you with your results.
                </p>
                
                <div style="background-color: #e8f6f3; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #27ae60;">
                    <h3 style="color: #27ae60; margin-top: 0;">📄 Your Assessment Results</h3>
                    <p style="margin-bottom: 0;">Your detailed MCQ assessment results are attached as a PDF document. This includes:</p>
                    <ul style="margin-top: 10px;">
                        <li>Your score and performance analysis</li>
                        <li>Question-by-question breakdown</li>
                        <li>Areas for improvement</li>
                        <li>Recommended study materials</li>
                    </ul>
                </div>
                
                <p style="font-size: 16px; margin: 20px 0;">
                    If you have any questions about your results or need additional support, please don't hesitate to contact our support team.
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="mailto:malindaall999@gmail.com" style="background-color: #3498db; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; display: inline-block;">Contact Support</a>
                </div>
                
                <hr style="border: none; height: 1px; background-color: #eee; margin: 30px 0;">
                
                <p style="font-size: 14px; color: #7f8c8d; text-align: center;">
                    Best regards,<br>
                    <strong>The MCQ Assessment Team</strong>
                </p>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 30px; text-align: center;">
                <p style="font-size: 12px; color: #95a5a6; margin-bottom: 10px;">
                    This is an automated message from MCQ Assessment System.<br>
                    If you no longer wish to receive these emails, you can 
                    <a href="mailto:malindaall999@gmail.com" style="color: #3498db;">contact us here</a>.
                </p>
                <p style="font-size: 11px; color: #bdc3c7; margin: 0;">
                    © {datetime.now().year} MCQ Assessment System. All rights reserved.
                </p>
            </div>
        </body>
        </html>
        """