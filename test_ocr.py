
import pytesseract
from PIL import Image

# Tesseract installation path
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# Open invoice image
image = Image.open("sample_invoice.png")

# Extract text using OCR
text = pytesseract.image_to_string(image)

print("INVOICE TEXT")
print("--------------------")
print(text)
