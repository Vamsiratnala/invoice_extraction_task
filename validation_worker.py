import re
from datetime import datetime



def check_compliance(data: dict) -> dict:
    """
    data = {
        "Product Code": str,
        "Product Name / Type": str,
        "Quantity": str,
        "Address": str,
        "MRP": str (optional)
    }
    """

    report = {"status": "PASS", "errors": []}

    # 1. Mandatory fields
    if not data.get("Product Code"):
        report["errors"].append("Missing Product Code")
    if not data.get("Product Name / Type"):
        report["errors"].append("Missing Product Name")
    if not data.get("Address") or data["Address"].strip().upper() in ["N/A", ""]:
        report["errors"].append("Invalid Address")

    # 2. Quantity format
    qty = data.get("Quantity", "")
    valid_units = ["Set", "Pair", "Unit", "Pieces", "Pcs"]
    if qty:
        match = re.match(r"^\s*(\d+)\s*([A-Za-z]+)\s*$", qty)
        if not match:
            report["errors"].append("Invalid Quantity format")
        else:
            number, unit = match.groups()
            if unit not in valid_units:
                report["errors"].append(f"Invalid unit '{unit}' in Quantity")
    else:
        report["errors"].append("Missing Quantity")

    # 3. Address validation
    Address = data.get("Address", "")
    if Address:
        lines = [line.strip() for line in re.split(r"[,|\n]", Address) if line.strip()]
        if len(lines) < 2:
            report["errors"].append("Address must have at least 2 lines")
        if not re.search(r"\b\d{6}\b", Address):  # Indian pincode format
            report["errors"].append("Address must contain a valid pincode")

    # Final status
    if report["errors"]:
        report["status"] = "FAIL"

    return report


invoice_data = {'Product Code': '', 'Product Name / Type': 'Neck Tie', 'Quantity': '1 Set', 'Address': 'Aditya Birla Lifestyle Brands Limited. on + 118/110/1, Building 2, 4 tan Ay Mes Yemalur Post, Bengaluru,Karnataka - 560 037.', 'MRP': 3999.0}
result = check_compliance(invoice_data)
print(result)