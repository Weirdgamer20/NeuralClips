from neuralstudio.analyzer.extractor import analyze_project
from neuralstudio.analyzer.builder import generate_code

def test_detects_layers(tmp_path):
    src = "\n".join([
        "import torch", "import torch.nn as nn", "class TinyNet(nn.Module):",
        "    def __init__(self):", "        self.fc1 = nn.Linear(4, 8)",
        "        self.relu = nn.ReLU()", "        self.fc2 = nn.Linear(8, 2)",
        "    def forward(self, x):", "        return self.fc2(self.relu(self.fc1(x)))"
    ])
    (tmp_path/"model.py").write_text(src,encoding="utf-8")
    r=analyze_project(str(tmp_path))
    assert "PyTorch" in r.frameworks
    assert len(r.nodes)>=3
    assert any(x["name"]=="TinyNet" for x in r.models)

def test_skips_node_modules(tmp_path):
    (tmp_path/"node_modules").mkdir()
    (tmp_path/"node_modules"/"model.py").write_text("nn.Linear(2,2)")
    (tmp_path/"app.js").write_text("const a = 1")
    assert analyze_project(str(tmp_path)).files_scanned==1

def test_code_generation():
    s=generate_code([4,8,2])
    assert "nn.Linear(4, 8)" in s and "nn.Linear(8, 2)" in s
