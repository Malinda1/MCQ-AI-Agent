from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import List
from models.mcq_models import MCQ
import os

class PDFGenerator:
    
    @staticmethod
    def _clean_text_for_pdf(text: str) -> str:
        """Clean text specifically for PDF generation"""
        if not text:
            return ""
        
        # Dictionary of character replacements for PDF
        replacements = {
            # Em-dash and en-dash
            '—': '-',
            '–': '-',
            '―': '-',
            
            # Quotes
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            
            # Bullets and special symbols
            '•': '* ',
            '◦': '- ',
            '▪': '* ',
            '▫': '- ',
            '■': '* ',
            '□': '- ',
            
            # Mathematical symbols
            '×': ' x ',
            '÷': ' / ',
            '±': ' +/- ',
            '∑': 'Sum',
            '∏': 'Product',
            '∞': 'infinity',
            '≈': ' ~= ',
            '≤': ' <= ',
            '≥': ' >= ',
            '≠': ' != ',
            
            # Other problematic characters
            '…': '...',
            '™': '(TM)',
            '©': '(C)',
            '®': '(R)',
            
            # Common encoding issues
            'â€™': "'",
            'â€œ': '"',
            'â€': '"',
            'â€"': '-',
            'â€"': '--',
        }
        
        # Apply replacements
        cleaned_text = text
        for old_char, new_char in replacements.items():
            cleaned_text = cleaned_text.replace(old_char, new_char)
        
        # Handle any remaining problematic characters
        # Replace with closest ASCII equivalent or remove
        cleaned_text = ''.join(char if ord(char) < 128 else ' ' for char in cleaned_text)
        
        # Clean up multiple spaces
        cleaned_text = ' '.join(cleaned_text.split())
        
        return cleaned_text
    
    @staticmethod
    def generate_mcq_pdf(mcqs: List[MCQ], filename: str, title: str = "MCQ Assessment") -> str:
        """Generate PDF from MCQs with proper character encoding"""
        
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Clean the title
        clean_title = PDFGenerator._clean_text_for_pdf(title)
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph(clean_title, title_style))
        story.append(Spacer(1, 20))
        
        # MCQs
        for i, mcq in enumerate(mcqs, 1):
            # Clean question text
            clean_question = PDFGenerator._clean_text_for_pdf(mcq.question)
            
            # Question
            question_style = ParagraphStyle(
                'Question',
                parent=styles['Normal'],
                fontSize=12,
                fontName='Helvetica-Bold',
                spaceAfter=10,
                leftIndent=0
            )
            story.append(Paragraph(f"Q{i}. {clean_question}", question_style))
            
            # Options
            option_style = ParagraphStyle(
                'Option',
                parent=styles['Normal'],
                fontSize=11,
                fontName='Helvetica',
                leftIndent=20,
                spaceAfter=3
            )
            
            for j, option in enumerate(mcq.options):
                clean_option_text = PDFGenerator._clean_text_for_pdf(option.text)
                option_text = f"{'ABCD'[j]}. {clean_option_text}"
                
                if option.is_correct:
                    # Use a simple checkmark or indicator for correct answer
                    option_text += " [CORRECT]"
                    # Make correct option bold
                    correct_style = ParagraphStyle(
                        'CorrectOption',
                        parent=option_style,
                        fontName='Helvetica-Bold'
                    )
                    story.append(Paragraph(option_text, correct_style))
                else:
                    story.append(Paragraph(option_text, option_style))
            
            # Explanation
            clean_explanation = PDFGenerator._clean_text_for_pdf(mcq.explanation)
            story.append(Spacer(1, 8))
            
            explanation_style = ParagraphStyle(
                'Explanation',
                parent=styles['Normal'],
                fontSize=10,
                fontName='Helvetica',
                leftIndent=20,
                spaceAfter=15,
                textColor='#444444'
            )
            
            story.append(Paragraph(f"<b>Explanation:</b> {clean_explanation}", explanation_style))
            story.append(Spacer(1, 15))
        
        # Build the PDF
        try:
            doc.build(story)
            return filename
        except Exception as e:
            # If there are still encoding issues, create a fallback version
            print(f"PDF generation error: {e}")
            return PDFGenerator._generate_fallback_pdf(mcqs, filename, clean_title)
    
    @staticmethod
    def _generate_fallback_pdf(mcqs: List[MCQ], filename: str, title: str) -> str:
        """Generate a fallback PDF with extra character cleaning"""
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Simple title
        story.append(Paragraph(title, styles['Title']))
        story.append(Spacer(1, 20))
        
        # Simple MCQ format
        for i, mcq in enumerate(mcqs, 1):
            # Extra aggressive cleaning
            question = ''.join(c if c.isalnum() or c in ' .,?!-()[]{}:;' else ' ' for c in mcq.question)
            story.append(Paragraph(f"Q{i}. {question}", styles['Heading2']))
            
            for j, option in enumerate(mcq.options):
                option_text = ''.join(c if c.isalnum() or c in ' .,?!-()[]{}:;' else ' ' for c in option.text)
                marker = " [CORRECT]" if option.is_correct else ""
                story.append(Paragraph(f"{'ABCD'[j]}. {option_text}{marker}", styles['Normal']))
            
            explanation = ''.join(c if c.isalnum() or c in ' .,?!-()[]{}:;' else ' ' for c in mcq.explanation)
            story.append(Paragraph(f"Explanation: {explanation}", styles['Normal']))
            story.append(Spacer(1, 15))
        
        doc.build(story)
        return filename