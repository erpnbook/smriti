import re
from typing import List, Tuple, Optional

class CompiledTemplate:
    def __init__(self, template_str: str):
        self.template_str = template_str
        self.parts: List[Tuple[str, str]] = []
        self.counter_padding: Optional[int] = None
        self._compile()

    def _compile(self):
        pattern = r"(\{[^}]+\})"
        raw_parts = re.split(pattern, self.template_str)
        
        for part in raw_parts:
            if not part:
                continue
            if part.startswith("{") and part.endswith("}"):
                token = part[1:-1]
                if token.startswith("counter"):
                    if ":" in token:
                        try:
                            self.counter_padding = int(token.split(":")[1])
                        except ValueError:
                            self.counter_padding = 0
                    else:
                        self.counter_padding = 0
                    self.parts.append(("counter", token))
                else:
                    self.parts.append(("variable", token))
            else:
                self.parts.append(("literal", part))

    def render(self, context: dict, counter_val: int) -> str:
        """Evaluates compiled tokens against the resolved context dictionary."""
        rendered = []
        for ptype, val in self.parts:
            if ptype == "literal":
                rendered.append(val)
            elif ptype == "counter":
                if self.counter_padding:
                    rendered.append(str(counter_val).zfill(self.counter_padding))
                else:
                    rendered.append(str(counter_val))
            elif ptype == "variable":
                rendered.append(str(context.get(val, "")))
        return "".join(rendered)
