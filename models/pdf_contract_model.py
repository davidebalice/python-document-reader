import pdfplumber
import re
import logging

def extract_text_from_contract_pdf(file_path):
    contract_data = {
        "supplier": {},
        "customer": {},
        "services": [],
        "total_cost": None,
        "annual_support_cost": None,
        "payment_terms": None,
        "withdrawal_conditions": None
    }
    
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text

            logging.info(f"Processing contract PDF file: {file_path}")
            
            # Stampa il testo per verificare l'estrazione
            print("Testo Estratto:\n", text)

            # Estrazione delle parti
        
            supplier_match = re.search(
                r"between\s+(.+?)\s+with\s+registered\s+office\s+in\s+(.+?)\s+-\s+(.+?)\s*,?\s*VAT\s+number\s+(\d+)",
                text, re.IGNORECASE | re.DOTALL
            )

            customer_match = re.search(
                r"And Customer\s+(.+?)\s+- Address\s+(.+?)\s+- VAT\s+(\d+)",
                text, re.IGNORECASE
            )

            if supplier_match:
                contract_data["supplier"] = {
                    "name": supplier_match.group(1).replace("\n", " ").strip(),
                    "address": supplier_match.group(2).strip(),
                    "city": supplier_match.group(3).strip(),
                    "vat code": supplier_match.group(4).strip()
                }
            else:
                logging.warning("Supplier information not found.")

            if customer_match:
                contract_data["customer"] = {
                    "name": customer_match.group(1).strip(),
                    "address": customer_match.group(2).strip(),
                    "vat code": customer_match.group(3).strip()
                }
            else:
                logging.warning("Customer information not found.")
                
            # Estrazione dei servizi offerti
            services_match = re.search(
                r"1\. SERVICES PROVIDED\s+(.+?)(?=\s+\d+\.)", 
                text, re.DOTALL | re.IGNORECASE
            )
            if services_match:
                contract_data["services"] = [service.strip() for service in services_match.group(1).strip().split("\n") if service.strip()]
            else:
                logging.warning("Services information not found.")
            
            # Estrazione dei costi
            total_cost_match = re.search(
                r"Total cost for the provision of the above services €\s*([\d,.]+)", 
                text
            )
            annual_support_cost_match = re.search(
                r"Annual website support and maintenance service €\s*([\d,.]+)", 
                text
            )
            
            if total_cost_match:
                contract_data["total_cost"] = total_cost_match.group(1).strip()
            else:
                logging.warning("Total cost information not found.")

            if annual_support_cost_match:
                contract_data["annual_support_cost"] = annual_support_cost_match.group(1).strip()
            else:
                logging.warning("Annual support cost information not found.")
                
            # Estrazione dei termini di pagamento
            payment_terms_match = re.search(
                r"3\. PAYMENT METHODS\s+(.+?)(?=\s*4\.)", 
                text, re.DOTALL | re.IGNORECASE
            )
            if payment_terms_match:
                contract_data["payment_terms"] = payment_terms_match.group(1).strip()
            else:
                logging.warning("Payment terms information not found.")
            
            # Estrazione delle condizioni di recesso
            withdrawal_match = re.search(
                r"4\. WITHDRAWAL FROM THE CONTRACT\s+(.+?)(?=Customer)",
                text, re.DOTALL | re.IGNORECASE
            )
            if withdrawal_match:
                contract_data["withdrawal_conditions"] = withdrawal_match.group(1).strip()
            else:
                logging.warning("Withdrawal conditions information not found.")
    
    except Exception as e:
        logging.error(f"Error processing contract PDF {file_path}: {e}")
    
    return contract_data
