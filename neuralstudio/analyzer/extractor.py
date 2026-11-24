import ast,re,hashlib
from pathlib import Path
from dataclasses import dataclass,field
from .scanner import scan_project

@dataclass
class Node:
    id:str; label:str; kind:str="layer"; details:dict=field(default_factory=dict)
    path:str=""; line:int=1; symbol:str=""
@dataclass
class Edge:
    source:str; target:str; label:str="inferred order"
@dataclass
class Result:
    root:str; files_scanned:int; languages:dict; frameworks:list
    models:list; nodes:list; edges:list; warnings:list

FRAMEWORKS={
"PyTorch":[r"\btorch\b",r"nn\.Module",r"torch\.nn"],
"TensorFlow":[r"\btensorflow\b",r"tf\.keras"],
"Keras":[r"\bkeras\b",r"Sequential\s*\("],
"JAX":[r"\bjax\b",r"\bflax\b"],"ONNX":[r"\bonnx\b"]}
LAYERS=[
("Conv2D",r"(?:nn\.)?Conv2d\s*\(([^)]*)\)"),("Conv1D",r"(?:nn\.)?Conv1d\s*\(([^)]*)\)"),
("Linear",r"(?:nn\.)?Linear\s*\(([^)]*)\)"),("Dense",r"(?:layers\.)?Dense\s*\(([^)]*)\)"),
("LSTM",r"(?:nn\.)?LSTM\s*\(([^)]*)\)"),("GRU",r"(?:nn\.)?GRU\s*\(([^)]*)\)"),
("Embedding",r"(?:nn\.)?Embedding\s*\(([^)]*)\)"),("MaxPool",r"(?:nn\.)?MaxPool\w*\s*\(([^)]*)\)"),
("Dropout",r"(?:nn\.)?Dropout\s*\(([^)]*)\)"),("BatchNorm",r"(?:nn\.)?BatchNorm\w*\s*\(([^)]*)\)"),
("ReLU",r"(?:nn\.)?ReLU\s*\("),("GELU",r"(?:nn\.)?GELU\s*\("),
("Sigmoid",r"(?:nn\.)?Sigmoid\s*\("),("Tanh",r"(?:nn\.)?Tanh\s*\("),
("Softmax",r"(?:nn\.)?Softmax\s*\(")]
HINT=re.compile(r"nn\.Module|keras|tensorflow|torch\.nn|Sequential\s*\(|Conv[123]D\s*\(|Linear\s*\(|Dense\s*\(|LSTM\s*\(|GRU\s*\(",re.I)
def sid(s): return hashlib.sha1(s.encode()).hexdigest()[:12]
def symbols(txt):
    try: tree=ast.parse(txt)
    except SyntaxError: return [],[]
    cs=[]; fs=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.ClassDef): cs.append((n.name,n.lineno))
        elif isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)): fs.append((n.name,n.lineno))
    return cs,fs
def analyze_project(root):
    files,langs,warns=scan_project(root); fw=set(); models=[]; candidates=[]
    for path,lang,txt in files:
        rel=str(path.relative_to(Path(root).resolve()))
        for name,patterns in FRAMEWORKS.items():
            if any(re.search(p,txt,re.I) for p in patterns): fw.add(name)
        if not HINT.search(txt): continue
        cs,fs=symbols(txt) if lang=="Python" else ([],[])
        for name,line in cs:
            if re.search(rf"class\s+{re.escape(name)}\b[\s\S]{{0,800}}(?:nn\.Module|Model)",txt):
                models.append({"name":name,"file":rel,"line":line})
        for name,line in fs:
            if name.lower() in {"forward","call","predict","build"}:
                models.append({"name":name,"file":rel,"line":line})
        for lname,pat in LAYERS:
            for m in re.finditer(pat,txt,re.I):
                line=txt.count("\n",0,m.start())+1
                candidates.append((rel,lname,line,(m.group(1) if m.lastindex else "")[:120],lang))
    nodes=[]; edges=[]; seen=set()
    for i,(rel,name,line,args,lang) in enumerate(candidates):
        key=(rel,name,line)
        if key in seen: continue
        seen.add(key); ident=sid(f"{rel}:{name}:{line}:{i}")
        nodes.append(Node(ident,name,"layer",{"arguments":args,"language":lang,
            "confidence":"static heuristic","note":"Declaration order is not proven execution order."},rel,line,name))
        if len(nodes)>1: edges.append(Edge(nodes[-2].id,ident))
    if not nodes and models:
        for m in models:
            nodes.append(Node(sid(str(m)),m["name"],"model",{"confidence":"source symbol"},m["file"],m["line"],m["name"]))
    if not nodes: warns.append("No recognizable layer declarations found. Custom/dynamic model code may require a framework adapter or runtime tracing.")
    else: warns.append("Graph edges are inferred from source declaration order; they are not guaranteed runtime dataflow.")
    return Result(str(Path(root).resolve()),len(files),langs,sorted(fw),models,nodes,edges,warns)
