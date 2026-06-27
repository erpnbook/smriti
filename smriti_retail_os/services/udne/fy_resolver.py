import datetime
from typing import Dict

def resolve_fy(dt: datetime.date) -> Dict[str, str]:
    """
    Calculates Indian financial year boundaries (April 1 to March 31).
    Returns short, long, and full FY string representations.
    """
    year = dt.year
    month = dt.month
    
    if month >= 4:
        start_year = year
        end_year = year + 1
    else:
        start_year = year - 1
        end_year = year
        
    start_short = str(start_year)[-2:]
    end_short = str(end_year)[-2:]
    
    return {
        "fy": f"{start_short}-{end_short}",
        "fy_long": f"{start_year}-{end_short}",
        "fy_full": f"{start_year}-{end_year}"
    }
