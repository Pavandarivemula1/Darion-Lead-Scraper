import pandas as pd
from typing import List
from src.models import Lead
from src.utils.logger import get_logger

logger = get_logger(__name__)

class DataExporter:
    @staticmethod
    def _prepare_data(leads: List[Lead]) -> List[dict]:
        data = []
        for l in leads:
            row = l.model_dump()
            row["social_links"] = ", ".join(row.get("social_links", []))
            if hasattr(row.get("priority", ""), 'value'):
                row["priority"] = row.get("priority").value
            data.append(row)
        return data

    @staticmethod
    def export_csv(leads: List[Lead], filename: str = "leads_export.csv"):
        if not leads:
            logger.warning("No leads to export.")
            return
            
        df = pd.DataFrame(DataExporter._prepare_data(leads))
        df = df.sort_values(by="score", ascending=False)
        df.to_csv(filename, index=False)
        logger.info(f"Exported {len(leads)} leads to {filename}")
        
    @staticmethod
    def export_excel(leads: List[Lead], filename: str = "leads_export.xlsx"):
        if not leads:
            logger.warning("No leads to export.")
            return
            
        df = pd.DataFrame(DataExporter._prepare_data(leads))
        df = df.sort_values(by="score", ascending=False)
        df.to_excel(filename, index=False)
        logger.info(f"Exported {len(leads)} leads to {filename}")
