from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import datetime

@dataclass(frozen=True)
class GenerationContext:
    company: str
    branch: Optional[str] = None
    store: Optional[str] = None
    terminal_id: Optional[str] = None
    user: Optional[str] = None
    department: Optional[str] = None
    transaction_date: Optional[datetime.date] = None
    extra_context: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        res = {
            "company": self.company,
            "branch": self.branch,
            "store": self.store,
            "terminal_id": self.terminal_id,
            "user": self.user,
            "department": self.department,
            "transaction_date": self.transaction_date or datetime.date.today()
        }
        if self.extra_context:
            res.update(self.extra_context)
        return res

@dataclass(frozen=True)
class UDNEResult:
    identity: str
    display_number: str
    rule: str
    version: int
    counter: int
    context: Dict[str, Any]
    reservation: Optional[str] = None
    generated_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    duration_ms: float = 0.0
