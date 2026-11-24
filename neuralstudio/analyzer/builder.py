def generate_code(sizes, activation="ReLU"):
    sizes=[int(x) for x in sizes]
    if len(sizes)<2 or any(x<=0 for x in sizes): raise ValueError("Enter at least two positive layer sizes.")
    if activation not in {"ReLU","Tanh","Sigmoid","GELU"}: raise ValueError("Unsupported activation.")
    out=["import torch","import torch.nn as nn","","class GeneratedNetwork(nn.Module):",
         "    def __init__(self):","        super().__init__()","        layers = []"]
    for i,(a,b) in enumerate(zip(sizes,sizes[1:])):
        out.append(f"        layers.append(nn.Linear({a}, {b}))")
        if i<len(sizes)-2: out.append(f"        layers.append(nn.{activation}())")
    out += ["        self.network = nn.Sequential(*layers)","","    def forward(self, x):","        return self.network(x)",""]
    return "\n".join(out)
