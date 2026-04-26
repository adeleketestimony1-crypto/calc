from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Optional

@dataclass
class CalcState:
    display: str = "0"
    expression: str = ""
    history: str = ""
    phase: str = "idle"
    operator: Optional[str] = None
    operand1: Optional[Decimal] = None
    operand2: Optional[Decimal] = None
    fresh: bool = True

class CalculatorEngine:
    def __init__(self):
        self._s = CalcState()

    def digit(self, d):
        s = self._s
        if s.phase == "error": return s
        if s.fresh or s.phase in ("idle","result"):
            self._s = CalcState(display="0" if d=="0" else d, phase="entering2" if s.operator else "entering1", operator=s.operator, operand1=s.operand1, operand2=s.operand2, fresh=False, history=s.history)
        else:
            if len(s.display.replace("-","").replace(".","")) >= 12: return s
            self._s = CalcState(**{**s.__dict__, "display": s.display if s.display!="0" else "" + d if s.display=="0" else s.display+d})
            self._s = CalcState(**{**s.__dict__, "display": d if s.display=="0" else s.display+d})
        return self._s

    def decimal(self):
        s = self._s
        if s.phase == "error": return s
        if s.fresh or s.phase in ("idle","result"):
            self._s = CalcState(display="0.", phase="entering2" if s.operator else "entering1", operator=s.operator, operand1=s.operand1, fresh=False, history=s.history)
        elif "." not in s.display:
            self._s = CalcState(**{**s.__dict__, "display": s.display+"."})
        return self._s

    def operator(self, op):
        s = self._s
        if s.phase == "error": return s
        current = self._parse(s.display)
        if s.phase == "entering2":
            result = self._compute(s.operand1, s.operator, current)
            if result is None: return self._set_error("Division by zero")
            fmt = self._format(result)
            self._s = CalcState(display=fmt, expression=f"{fmt} {op}", phase="op_set", operator=op, operand1=result, fresh=True, history=s.history)
        else:
            op1 = current if s.phase != "op_set" else s.operand1
            self._s = CalcState(display=self._format(op1), expression=f"{self._format(op1)} {op}", phase="op_set", operator=op, operand1=op1, fresh=True, history=s.history)
        return self._s

    def equals(self):
        s = self._s
        if s.phase == "error": return s
        current = self._parse(s.display)
        if s.phase == "result":
            if not s.operator or s.operand2 is None: return s
            result = self._compute(current, s.operator, s.operand2)
            if result is None: return self._set_error("Division by zero")
            fmt = self._format(result)
            hist = f"{self._format(current)} {s.operator} {self._format(s.operand2)} = {fmt}"
            self._s = CalcState(display=fmt, history=hist, phase="result", operator=s.operator, operand1=result, operand2=s.operand2, fresh=True)
            return self._s
        if s.operator is None: return s
        b = s.operand2 if s.fresh and s.operand2 is not None else current
        result = self._compute(s.operand1, s.operator, b)
        if result is None: return self._set_error("Division by zero")
        fmt = self._format(result)
        hist = f"{self._format(s.operand1)} {s.operator} {self._format(b)} = {fmt}"
        self._s = CalcState(display=fmt, history=hist, phase="result", operator=s.operator, operand1=result, operand2=b, fresh=True)
        return self._s

    def clear(self):
        self._s = CalcState()
        return self._s

    def backspace(self):
        s = self._s
        if s.phase in ("error","result") or s.fresh: return self.clear()
        if len(s.display) <= 1 or (len(s.display)==2 and s.display.startswith("-")):
            self._s = CalcState(**{**s.__dict__, "display":"0", "fresh":True})
        else:
            nd = s.display[:-1].rstrip(".") if s.display[:-1].endswith(".") else s.display[:-1]
            self._s = CalcState(**{**s.__dict__, "display":nd})
        return self._s

    def sign(self):
        s = self._s
        if s.phase=="error" or s.display in ("0","0."): return s
        nd = s.display[1:] if s.display.startswith("-") else "-"+s.display
        self._s = CalcState(**{**s.__dict__, "display":nd})
        return self._s

    def percent(self):
        s = self._s
        if s.phase=="error": return s
        n = self._parse(s.display)
        result = (s.operand1*n/100) if s.operand1 and s.operator else n/100
        self._s = CalcState(**{**s.__dict__, "display":self._format(result)})
        return self._s

    @property
    def state(self): return self._s

    @staticmethod
    def _parse(t):
        try: return Decimal(t)
        except: return Decimal("0")

    @staticmethod
    def _compute(a, op, b):
        if op=="+": return a+b
        if op=="−": return a-b
        if op=="×": return a*b
        if op=="÷": return None if b==0 else a/b
        return b

    @staticmethod
    def _format(n):
        try:
            f = float(n)
            if abs(f)>=1e13 or (abs(f)<1e-6 and f!=0): return f"{f:.6e}"
            r = float(f"{f:.10g}")
            s = str(r)
            if "." in s: s=s.rstrip("0").rstrip(".")
            return s
        except: return "Error"

    def _set_error(self, msg):
        self._s = CalcState(display=msg, phase="error", history=self._s.history)
        return self._s
