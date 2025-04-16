import os
from docx import Document
import comtypes.client

CONTRACTS_DIR = "shartnomalar"
TEMPLATE_PATH = "database/shartnoma_shablon.docx"

# Agar katalog mavjud bo‘lmasa, yaratamiz
os.makedirs(CONTRACTS_DIR, exist_ok=True)

def word_to_pdf(doc_path, pdf_path):
    """Word faylni PDF formatiga o‘tkazish (Windows uchun)"""
    word = comtypes.client.CreateObject("Word.Application")
    word.Visible = False  # Word oynasini yashirish
    doc = word.Documents.Open(os.path.abspath(doc_path))
    doc.SaveAs(os.path.abspath(pdf_path), FileFormat=17)  # 17 - PDF formati
    doc.Close()
    word.Quit()

def generate_contract(user_id, full_name):
    """Shartnoma faylini yaratish va saqlash"""

    filename = f"{user_id}.docx"  # Foydalanuvchi ID bo‘yicha saqlash
    file_path = os.path.join(CONTRACTS_DIR, filename)
    pdf_path = file_path.replace(".docx", ".pdf")  # PDF yo‘lini yaratish

    # Agar shartnoma allaqachon yaratilgan bo‘lsa, PDF faylni qaytaramiz
    if os.path.exists(pdf_path):
        return pdf_path

    # Word faylni yuklab olish va o‘zgartirish
    doc = Document(TEMPLATE_PATH)

    for para in doc.paragraphs:
        if "{FISH}" in para.text or "{ID}" in para.text:
            para.text = para.text.replace("{FISH}", full_name).replace("{ID}", str(user_id))
        else:
            for run in para.runs:
                run.text = run.text.replace("{FISH}", full_name).replace("{ID}", str(user_id))

    # Word faylni saqlash
    doc.save(file_path)

    # Word faylni PDF formatiga o‘tkazish
    word_to_pdf(file_path, pdf_path)

    return pdf_path
