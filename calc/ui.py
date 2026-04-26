import tkinter as tk
from tkinter import font as tkfont
from calc.engine import CalculatorEngine

THEME = {"bg":"#0d0d0d","surface":"#161616","border":"#252525","text":"#e8e4dc","text_dim":"#5a5a5a","accent":"#c8f04d","accent_fg":"#0d0d0d","accent2":"#f0a854","danger":"#f05454","btn_bg":"#1c1c1c","btn_hover":"#262626","btn_press":"#2e2e2e"}

BUTTONS = [
    ("AC","clear",1,"clr"),("+/−","sign",1,"fn"),("%","percent",1,"fn"),("÷",("operator","÷"),1,"op"),
    ("7",("digit","7"),1,"n"),("8",("digit","8"),1,"n"),("9",("digit","9"),1,"n"),("×",("operator","×"),1,"op"),
    ("4",("digit","4"),1,"n"),("5",("digit","5"),1,"n"),("6",("digit","6"),1,"n"),("−",("operator","−"),1,"op"),
    ("1",("digit","1"),1,"n"),("2",("digit","2"),1,"n"),("3",("digit","3"),1,"n"),("+",("operator","+"),1,"op"),
    ("0",("digit","0"),2,"zero"),(".",("decimal",),1,"n"),("=","equals",1,"eq"),
]

class CalcApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calc")
        self.resizable(False,False)
        self.configure(bg=THEME["bg"])
        self._engine = CalculatorEngine()
        self._btns = []
        self._build()
        self._bind_keys()
        self._render(self._engine.state)

    def _build(self):
        hdr = tk.Frame(self,bg=THEME["bg"],height=44)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr,text="CALC",bg=THEME["bg"],fg=THEME["accent"],font=("Courier New",11,"bold")).pack(side="left",padx=16)

        disp = tk.Frame(self,bg="#111111",height=120,highlightbackground=THEME["border"],highlightthickness=1)
        disp.pack(fill="x")
        disp.pack_propagate(False)
        self._lbl_hist = tk.Label(disp,text="",bg="#111111",fg=THEME["text_dim"],font=("Courier New",9),anchor="e",justify="right")
        self._lbl_hist.pack(fill="x",padx=14,pady=(8,0))
        self._lbl_expr = tk.Label(disp,text="",bg="#111111",fg=THEME["text_dim"],font=("Courier New",12),anchor="e",justify="right")
        self._lbl_expr.pack(fill="x",padx=14)
        self._lbl_out = tk.Label(disp,text="0",bg="#111111",fg=THEME["text"],font=("Courier New",42,"bold"),anchor="e",justify="right")
        self._lbl_out.pack(fill="both",expand=True,padx=14,pady=(0,8))

        grid = tk.Frame(self,bg=THEME["border"])
        grid.pack(fill="both",expand=True)
        col,row=0,0
        for label,action,span,style in BUTTONS:
            colors={"n":(THEME["text"],THEME["btn_bg"]),"fn":(THEME["text_dim"],THEME["btn_bg"]),"op":(THEME["accent2"],THEME["btn_bg"]),"eq":(THEME["accent_fg"],THEME["accent"]),"clr":(THEME["danger"],THEME["btn_bg"]),"zero":(THEME["text"],THEME["btn_bg"])}.get(style,(THEME["text"],THEME["btn_bg"]))
            f=tk.Frame(grid,bg=colors[1],cursor="hand2")
            f.grid(row=row,column=col,columnspan=span,sticky="nsew",padx=(0,1),pady=(0,1))
            anchor="w" if style=="zero" else "center"
            px=(20,0) if style=="zero" else 0
            lbl=tk.Label(f,text=label,bg=colors[1],fg=colors[0],font=("Courier New",16,"bold") if style not in ("fn","clr") else ("Courier New",12),anchor=anchor,padx=px)
            lbl.pack(fill="both",expand=True)
            for w in (f,lbl):
                w.bind("<Button-1>",lambda e,a=action,fr=f,lb=lbl,c=colors:self._press(a,fr,lb,c))
                w.bind("<ButtonRelease-1>",lambda e,fr=f,lb=lbl,c=colors:self._release(fr,lb,c))
                w.bind("<Enter>",lambda e,fr=f,lb=lbl,c=colors:(fr.config(bg=THEME["btn_hover"]),lb.config(bg=THEME["btn_hover"])))
                w.bind("<Leave>",lambda e,fr=f,lb=lbl,c=colors:(fr.config(bg=c[1]),lb.config(bg=c[1])))
            self._btns.append((f,lbl,action,colors))
            col+=span
            if col>=4: col=0;row+=1
        for c in range(4): grid.columnconfigure(c,weight=1,minsize=80)
        for r in range(5): grid.rowconfigure(r,weight=1,minsize=68)

    def _press(self,action,fr,lbl,colors):
        fr.config(bg=THEME["btn_press"]);lbl.config(bg=THEME["btn_press"])
        self._do(action)

    def _release(self,fr,lbl,colors):
        fr.config(bg=colors[1]);lbl.config(bg=colors[1])

    def _bind_keys(self):
        for d in "0123456789":
            self.bind(f"<Key-{d}>",lambda e,v=d:self._do(("digit",v)))
        self.bind("<period>",lambda e:self._do(("decimal",)))
        self.bind("<plus>",lambda e:self._do(("operator","+")))
        self.bind("<minus>",lambda e:self._do(("operator","−")))
        self.bind("<asterisk>",lambda e:self._do(("operator","×")))
        self.bind("<slash>",lambda e:self._do(("operator","÷")))
        self.bind("<Return>",lambda e:self._do("equals"))
        self.bind("<equal>",lambda e:self._do("equals"))
        self.bind("<Escape>",lambda e:self._do("clear"))
        self.bind("<BackSpace>",lambda e:self._do("backspace"))
        self.bind("<percent>",lambda e:self._do("percent"))

    def _do(self,action):
        e=self._engine
        if action=="clear": s=e.clear()
        elif action=="sign": s=e.sign()
        elif action=="percent": s=e.percent()
        elif action=="equals": s=e.equals()
        elif action=="backspace": s=e.backspace()
        elif isinstance(action,tuple):
            k=action[0]
            if k=="digit": s=e.digit(action[1])
            elif k=="operator": s=e.operator(action[1])
            elif k=="decimal": s=e.decimal()
            else: return
        else: return
        self._render(s)

    def _render(self,state):
        self._lbl_hist.config(text=state.history or "")
        self._lbl_expr.config(text=state.expression or "")
        t=state.display
        fg=THEME["danger"] if state.phase=="error" else THEME["text"]
        sz=42 if len(t)<=9 else 28 if len(t)<=12 else 18
        self._lbl_out.config(text=t,fg=fg,font=("Courier New",sz,"bold"))
