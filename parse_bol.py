"""
File: parse_bol.py
Purpose:
    - Parses raw text extracted from a Bill of Lading PDF (e.g., "065-2024 MBL MEDUP1966175.pdf")
      to extract key shipment details and return a structured JSON object.
      
Target JSON Structure:
{
  "BILL_OF_LADING_No": "MEDUP1966175",
  "SHIPPER": "INTERCROMA SA, Rua Conde D'eu, 800- Bairro Alpino, Phone (47) 3631-4600 - Fax (47) 3631-4604, 89286-691 Sao Bento do Sul - SC - Brazil, CNPJ 005577130001",
  "CONSIGNEE": "MUSCAT WOODEN PALLETS L.L.C., P.O. BOX - 284, AUQADEN 217, SALALAH, SULTANETE OF OMAN, PHONE: +968 23219649, FAX: +968 23219632",
  "Total_Gross_Weight": "50000.000 Kgs",
  "Total_Items": 88,
  "Number_of_Containers": 2,
  "Containers": [
    {
      "container_number": "BEAU5862453",
      "container_size": "40' HIGH CUBE",
      "Seal_Number": "FJ21074021",
      "Description_of_Packages_and_Goods": "44 PALLET of IN 2X40'HC CONTAINERS WITH 88 PALLETS WITH 100,374 CBM OF SAWN TIMBER PALLET AS PER PROFORMA INVOICE 065/2024 DUE: 24BR001928059-7 RUC: 4BR00557713200000000000000001242455 NCM 44071100 COMMERCIAL INVOICE 065/2024 HS CODE: 44071190 FREIGHT PREPAID ABROAD AS PER AGREEMENT WOODEN PACKAGE USED: TREATED/CERTIFIED 44071100 HS Code:440711 Marks and Numbers: MADE IN BRAZIL MUSCAT WOODEN 001/088",
      "Gross_Cargo_Weight": "25,000.000 Kgs"
    },
    {
      "container_number": "BMOU5932452",
      "container_size": "40' HIGH CUBE",
      "Seal_Number": "FJ21154465",
      "Description_of_Packages_and_Goods": "44 PALLET of . 44071100 HS Code:440711 Marks and Numbers: .",
      "Gross_Cargo_Weight": "25,000.000 Kgs"
    }
  ]
}

Role & Relation:
    - This module is used after extracting text (e.g., using pdfplumber) to produce structured data.
    - The returned dictionary is then converted to JSON by the FastAPI endpoint.
Educational Comments:
    - Regex patterns here are tuned to the layout of the provided PDF.
    - Adjustments may be necessary if the raw text extraction changes.
"""

import re

def parse_bol(text: str) -> dict:
    # Normalize text: Convert CRLF to LF and collapse multiple spaces
    text = text.replace('\r\n', '\n').replace('  ', ' ')

    result = {}

    # 1. BILL_OF_LADING_No: Match a "MEDUP" code.
    bol_match = re.search(r'\b(MEDUP\d+)\b', text, re.IGNORECASE)
    result["BILL_OF_LADING_No"] = bol_match.group(1).strip() if bol_match else ""

    # 2. SHIPPER: Capture from "INTERCROMA SA" up to "SHIPPER:" marker.
    shipper_match = re.search(r'INTERCROMA SA([\s\S]*?)SHIPPER:', text, re.IGNORECASE)
    if shipper_match:
        raw_shipper = "INTERCROMA SA" + shipper_match.group(1)
        lines = [line.strip() for line in raw_shipper.split('\n') if line.strip()]
        result["SHIPPER"] = ", ".join(lines)
    else:
        result["SHIPPER"] = ""

    # 3. CONSIGNEE: Capture from "NOTIFY PARTIES :" up to "VESSEL AND VOYAGE NO"
    consignee_match = re.search(r'NOTIFY PARTIES\s*:\s*([\s\S]*?)(?=VESSEL AND VOYAGE NO)', text, re.IGNORECASE)
    if consignee_match:
        lines = [line.strip() for line in consignee_match.group(1).split('\n') if line.strip()]
        result["CONSIGNEE"] = ", ".join(lines)
    else:
        result["CONSIGNEE"] = ""

    # 4. Total_Gross_Weight: e.g., "50000.000 Kgs"
    weight_match = re.search(r'Total Gross Weight\s*:\s*([\d.,]+\s*Kgs)', text, re.IGNORECASE)
    result["Total_Gross_Weight"] = weight_match.group(1).strip() if weight_match else ""

    # 5. Total_Items: e.g., "88"
    items_match = re.search(r'Total Items\s*:\s*(\d+)', text, re.IGNORECASE)
    result["Total_Items"] = int(items_match.group(1)) if items_match else 0

    # 6. Number_of_Containers: from a pattern like "2 x 40' HIGH CUBE"
    container_count_match = re.search(r'(\d+)\s*x\s*40\' HIGH CUBE', text, re.IGNORECASE)
    result["Number_of_Containers"] = int(container_count_match.group(1)) if container_count_match else 0

    # 7. Compute Gross_Cargo_Weight per container.
    container_weight = ""
    if result["Total_Gross_Weight"] and result["Number_of_Containers"]:
        total_weight_str = re.sub(r'[^0-9.]', '', result["Total_Gross_Weight"])
        try:
            total_weight = float(total_weight_str)
            count = result["Number_of_Containers"]
            container_weight = f"{total_weight / count:,.3f} Kgs"
        except Exception:
            container_weight = ""
    # 8. Extract container details.
    containers = []
    container_regex = re.compile(
        r"((?:BEAU|BMOU)\d+)[\s\S]*?Seal Number:\s*(FJ\d+)[\s\S]*?(40' HIGH CUBE)[\s\S]*?(44 PALLET[\s\S]*?)(?=(?:BEAU|BMOU)\d+|$)",
        re.IGNORECASE
    )
    for m in container_regex.finditer(text):
        container_number = m.group(1).strip()
        seal_number = m.group(2).strip()
        container_size = m.group(3).strip()
        description = re.sub(r'\s+', ' ', m.group(4)).strip()
        containers.append({
            "container_number": container_number,
            "container_size": container_size,
            "Seal_Number": seal_number,
            "Description_of_Packages_and_Goods": description,
            "Gross_Cargo_Weight": container_weight,
        })
    result["Containers"] = containers

    return result

if __name__ == "__main__":
    # For testing: read extracted text from a file and print the parsed JSON.
    with open("sample_extracted_text.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()
    import json
    parsed = parse_bol(raw_text)
    print(json.dumps(parsed, indent=2))
