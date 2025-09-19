from extraction_worker import run_extraction_pipeline
from validation_worker import check_compliance
def main_function(file_path:str):
    structured_invoice = run_extraction_pipeline(file_path)
    print("Structured Invoice:", structured_invoice)
    compliance_report = check_compliance(structured_invoice)
    print("Compliance Report:", compliance_report)
    merged = structured_invoice | compliance_report
    print("Clothing Tag OCR & Compliance Checker result:",merged)

    
main_function("IMG_7141.jpeg")