
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate

import pytesseract
from PIL import Image,ImageOps


import re
import json

# Point directly to the installed binary
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")


class ExtractionWorker:
    def __init__(self, model: str = "llama-3.1-8b-instant"):
        # Initialize Groq LLM
        self.llm = ChatGroq(groq_api_key=groq_api_key, model=model)

        # Prompt template for extraction
        self.prompt = ChatPromptTemplate.from_template(
    """
    You are an invoice extraction assistant, strictly match the feilds only if it is present in the text, otherwise leave it blank.   
    Extract all available information from the given raw invoice text, including:
     Parse the following fields:
   - **Product Code** (e.g., `RNPC524983222`, `MAW25304B2`)
   - **Product Name / Type** (e.g., "Neck Tie", "BOTTOM")
   - **Quantity** (e.g., "1 Set", "1 Unit")
   - **Address** (manufacturer/distributor address)
   - **MRP** (optional)

    Your response must be ONLY a valid JSON object containing all extracted fields.
    Do not include any explanation, heading, or extra text.
    The output must start with '{{' and end with '}}'.

    Raw invoice text:
    {text}
    """
)


    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from images using Tesseract OCR."""
        image = Image.open(image_path)
        image = ImageOps.exif_transpose(image)   # Correct orientation using EXIF data
        text = pytesseract.image_to_string(image)
        print("✅ Extracted Raw Text from Image:")
        print(text)
        return text.strip()

    def extract_invoice(self, text: str) -> str:
        
        chain = self.prompt | self.llm
        result = chain.invoke({"text": text})
        
        #using regex to extract JSON object from the response

        match = re.search(r"\{.*\}", result.content, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json_str  # Return as string, not parsed
        else:
            print("❌ No JSON object found in LLM output.")
            return ""


def run_extraction_pipeline(file_path: str):

    worker = ExtractionWorker()

    ext = os.path.splitext(file_path)[-1].lower()

    if ext in [".png", ".jpg", ".jpeg"]:
        raw_text = worker.extract_text_from_image(file_path) 
    else:
        raise ValueError(f"❌ Unsupported file type: {ext}")

    structured_invoice = worker.extract_invoice(raw_text)
    structured_invoice = json.loads(structured_invoice) if structured_invoice else {}

    print("✅ Extracted Invoice JSON:")
    print(structured_invoice)
    print(type(structured_invoice))
    return structured_invoice


# -------------------------
# Run if main
# -------------------------
if __name__ == "__main__":
    run_extraction_pipeline("IMG_7142.jpeg")  # Change file as needed

"""
{
    "VendorDetails": {
        "Name": "Borcele Bank",
        "Address": "123 Anywhere St., Any City"
    },
    "InvoiceNumber": "01234",
    "InvoiceDate": "11.02.2030",
    "DueDate": "11.03.2030",
    "TotalAmount": 440,
    "LineItems": [
        {
            "Description": "Brand consultation",
            "UnitPrice": 100,
            "Quantity": 1,
            "Total": 100
        },
        {
            "Description": "logo design",
            "UnitPrice": 100,
            "Quantity": 1,
            "Total": 100
        },
        {
            "Description": "Website design",
            "UnitPrice": 100,
            "Quantity": 1,
            "Total": 100
        },
        {
            "Description": "Social media templates",
            "UnitPrice": 100,
            "Quantity": 1,
            "Total": 100
        },
        {
            "Description": "Brand photography",
            "UnitPrice": 100,
            "Quantity": 1,
            "Total": 100
        },
        {
            "Description": "Brand guide",
            "UnitPrice": 100,
            "Quantity": 1,
            "Total": 100
        }
    ],
    "TaxDetails": {
        "TaxRate": 10,
        "TaxAmount": 40
    },
    "PaymentTerms": "SUBTOTAL $400.00, Tax 10%, TOTAL $440.00"
}
"""
