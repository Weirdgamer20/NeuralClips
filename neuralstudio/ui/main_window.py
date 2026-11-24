import json
from pathlib import Path
from PySide6.QtWidgets import *
from PySide6.QtCore import QThread,Signal
from neuralstudio.analyzer.extractor import analyze_project
from neuralstudio.analyzer.builder import generate_code
from neuralstudio.analyzer.runtime import inspect_pytorch_file
from neuralstudio.ui.graph import GraphView
from neuralstudio.analyzer.extractor import Node, Edge

class Worker(QThread):
    done=Signal(object); error=Signal(str)
    def __init__(self,root): super().__init__(); self.root=root
    def run(self):
        try: self.done.emit(analyze_project(self.root))
        except Exception as e: self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Neural Studio"); self.resize(1360,850)
        self.root=None; self.result=None; self.worker=None
        central=QWidget(); self.setCentralWidget(central); outer=QVBoxLayout(central)
        bar=QHBoxLayout(); title=QLabel("NEURAL STUDIO"); title.setStyleSheet("font-size:22px;font-weight:bold;color:#7dd3fc")
        bar.addWidget(title); bar.addStretch(); self.path=QLabel("No project selected"); bar.addWidget(self.path)
        openb=QPushButton("Open Project"); openb.clicked.connect(self.open_project); bar.addWidget(openb)
        self.scanb=QPushButton("Scan Project"); self.scanb.setEnabled(False); self.scanb.clicked.connect(self.scan); bar.addWidget(self.scanb)
        outer.addLayout(bar); self.tabs=QTabWidget(); outer.addWidget(self.tabs)
        self.make_overview(); self.make_graph(); self.make_sources(); self.make_builder(); self.make_runtime()
        self.setStyleSheet("""
        QMainWindow,QWidget{background:#151d29;color:#e7edf5;font-size:13px}
        QTabWidget::pane{border:1px solid #344256} QTabBar::tab{background:#202c3b;padding:10px 18px}
        QTabBar::tab:selected{background:#28516b} QPushButton{background:#245a78;padding:8px 13px;border:0;border-radius:4px}
        QPushButton:hover{background:#32799e} QPushButton:disabled{background:#394655;color:#8793a2}
        QLineEdit,QTextEdit,QTreeWidget,QTableWidget,QComboBox{background:#0f1722;border:1px solid #344256;padding:6px;color:#e7edf5}
        QHeaderView::section{background:#263447;padding:5px;border:0}""")
    def make_overview(self):
        w=QWidget(); l=QVBoxLayout(w); self.summary=QLabel("Open a project. Static scanning does not execute source code.")
        self.summary.setWordWrap(True); l.addWidget(self.summary)
        self.metrics=QTableWidget(0,2); self.metrics.setHorizontalHeaderLabels(["Metric","Value"])
        self.metrics.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); l.addWidget(self.metrics)
        self.warn=QTextEdit(); self.warn.setReadOnly(True); l.addWidget(self.warn); self.tabs.addTab(w,"Overview")
    def make_graph(self):
        w=QWidget(); l=QVBoxLayout(w); self.graph=GraphView(); l.addWidget(self.graph)
        self.graphinfo=QTextEdit(); self.graphinfo.setReadOnly(True); self.graphinfo.setMaximumHeight(170); l.addWidget(self.graphinfo)
        self.tabs.addTab(w,"Architecture")
    def make_sources(self):
        w=QWidget(); l=QVBoxLayout(w); self.tree=QTreeWidget(); self.tree.setHeaderLabels(["Symbol / layer","File : line"]); l.addWidget(self.tree)
        self.tabs.addTab(w,"Source Navigator")
    def make_builder(self):
        w=QWidget(); l=QVBoxLayout(w); form=QFormLayout()
        self.sizes=QLineEdit("4, 8, 8, 2"); self.act=QComboBox(); self.act.addItems(["ReLU","Tanh","Sigmoid","GELU"])
        form.addRow("Layer sizes",self.sizes); form.addRow("Hidden activation",self.act); l.addLayout(form)
        row=QHBoxLayout(); gen=QPushButton("Generate code"); gen.clicked.connect(self.generate); save=QPushButton("Save .py")
        save.clicked.connect(self.save_code); row.addWidget(gen); row.addWidget(save); row.addStretch(); l.addLayout(row)
        self.builder_graph=GraphView(); self.builder_graph.setMinimumHeight(230); l.addWidget(self.builder_graph)
        self.sizes.editingFinished.connect(self.update_builder_preview)
        self.code=QTextEdit(); l.addWidget(self.code); self.tabs.addTab(w,"Visual Builder")
        self.update_builder_preview()
    def make_runtime(self):
        w=QWidget(); l=QVBoxLayout(w)
        note=QLabel("Runtime inspection imports and executes selected Python code. Only inspect trusted files. Requires optional PyTorch installation and a no-argument torch.nn.Module.")
        note.setWordWrap(True); l.addWidget(note); row=QHBoxLayout()
        self.runtimepath=QLineEdit(); self.runtimepath.setPlaceholderText("Trusted .py model file")
        browse=QPushButton("Browse"); browse.clicked.connect(self.browse_runtime)
        run=QPushButton("Inspect runtime"); run.clicked.connect(self.runtime)
        row.addWidget(self.runtimepath); row.addWidget(browse); row.addWidget(run); l.addLayout(row)
        self.runtimeout=QTextEdit(); self.runtimeout.setReadOnly(True); l.addWidget(self.runtimeout); self.tabs.addTab(w,"Runtime & Hardware")
    def open_project(self):
        p=QFileDialog.getExistingDirectory(self,"Select project directory")
        if p: self.root=p; self.path.setText(p); self.scanb.setEnabled(True); self.summary.setText("Project selected. Click Scan Project.")
    def scan(self):
        self.scanb.setEnabled(False); self.summary.setText("Scanning…")
        self.worker=Worker(self.root); self.worker.done.connect(self.scan_done); self.worker.error.connect(self.scan_error)
        self.worker.finished.connect(lambda:self.scanb.setEnabled(True)); self.worker.start()
    def scan_error(self,msg):
        QMessageBox.critical(self,"Scan failed",msg); self.summary.setText("Scan failed.")
    def scan_done(self,r):
        self.result=r; self.summary.setText(f"Scanned {r.files_scanned} source files in {r.root}")
        rows=[("Files scanned",r.files_scanned),("Languages",", ".join(f"{k}: {v}" for k,v in r.languages.items())),
              ("Framework indicators",", ".join(r.frameworks) or "None"),("Model symbols",len(r.models)),
              ("Layer declarations",len(r.nodes)),("Inferred edges",len(r.edges))]
        self.metrics.setRowCount(len(rows))
        for i,(k,v) in enumerate(rows): self.metrics.setItem(i,0,QTableWidgetItem(str(k))); self.metrics.setItem(i,1,QTableWidgetItem(str(v)))
        self.warn.setPlainText("\n".join(r.warnings) or "No warnings.")
        self.graph.show_graph(r.nodes,r.edges)
        self.graphinfo.setPlainText("\n".join(f"{n.label} — {n.path}:{n.line} | {n.details}" for n in r.nodes))
        self.tree.clear()
        for m in r.models: self.tree.addTopLevelItem(QTreeWidgetItem([m["name"],f'{m["file"]}:{m["line"]}']))
        for n in r.nodes: self.tree.addTopLevelItem(QTreeWidgetItem([n.label,f"{n.path}:{n.line}"]))
    def update_builder_preview(self):
        try:
            sizes=[int(x.strip()) for x in self.sizes.text().split(",") if x.strip()]
            if len(sizes)<2 or any(x<=0 for x in sizes): raise ValueError("Enter at least two positive layer sizes.")
            nodes=[]; edges=[]
            for i,size in enumerate(sizes):
                node=Node(f"builder_{i}",f"Layer {i+1}\\n{size} units","layer",
                          {"units":size,"role":"input" if i==0 else ("output" if i==len(sizes)-1 else "hidden")})
                nodes.append(node)
                if i: edges.append(Edge(nodes[i-1].id,node.id,"fully connected"))
            self.builder_graph.show_graph(nodes,edges)
        except Exception:
            self.builder_graph.show_graph([],[])
    def generate(self):
        try:
            sizes=[int(x.strip()) for x in self.sizes.text().split(",") if x.strip()]
            self.code.setPlainText(generate_code(sizes,self.act.currentText()))
            self.update_builder_preview()
        except Exception as e: QMessageBox.warning(self,"Invalid network",str(e))
    def save_code(self):
        if not self.code.toPlainText().strip(): self.generate()
        if not self.code.toPlainText().strip(): return
        p,_=QFileDialog.getSaveFileName(self,"Save generated network","generated_network.py","Python (*.py)")
        if p: Path(p).write_text(self.code.toPlainText(),encoding="utf-8")
    def browse_runtime(self):
        p,_=QFileDialog.getOpenFileName(self,"Select trusted Python file",self.root or "","Python (*.py)")
        if p: self.runtimepath.setText(p)
    def runtime(self):
        p=self.runtimepath.text().strip()
        if not p: QMessageBox.information(self,"Select file","Choose a Python file."); return
        answer=QMessageBox.warning(self,"Execute project code?","This imports and executes the selected file. Continue only if trusted.",
            QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)
        if answer!=QMessageBox.StandardButton.Yes: return
        try: self.runtimeout.setPlainText(json.dumps(inspect_pytorch_file(p),indent=2))
        except Exception as e: self.runtimeout.setPlainText(f"Inspection failed: {e}")
