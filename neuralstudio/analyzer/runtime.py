from pathlib import Path
import importlib.util,inspect,sys
def inspect_pytorch_file(file_path):
    path=Path(file_path).resolve()
    if not path.is_file() or path.suffix.lower()!=".py": raise ValueError("Choose a Python source file.")
    spec=importlib.util.spec_from_file_location("neuralstudio_user_model",path)
    if spec is None or spec.loader is None: raise RuntimeError("Could not load selected file.")
    module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module
    try:
        spec.loader.exec_module(module)
        import torch,torch.nn as nn
        classes=[c for _,c in inspect.getmembers(module,inspect.isclass)
                 if c.__module__==module.__name__ and issubclass(c,nn.Module) and c is not nn.Module]
        if not classes: raise RuntimeError("No locally defined torch.nn.Module subclass found.")
        cls=classes[0]
        try: model=cls()
        except Exception as e: raise RuntimeError(f"Model constructor needs arguments or failed: {e}") from e
        device="cuda" if torch.cuda.is_available() else "cpu"; model.to(device).eval()
        layers=[]; hooks=[]
        def make_hook(name):
            def hook(mod,inputs,out):
                def shape(x): return list(x.shape) if hasattr(x,"shape") else type(x).__name__
                layers.append({"name":name,"type":type(mod).__name__,
                    "input_shapes":[shape(x) for x in inputs],"output_shape":shape(out),
                    "device":str(out.device) if hasattr(out,"device") else "unknown"})
            return hook
        for name,child in model.named_modules():
            if name and not list(child.children()): hooks.append(child.register_forward_hook(make_hook(name)))
        try:
            traced=torch.fx.symbolic_trace(model)
            fx=[{"name":n.name,"op":n.op,"target":str(n.target)} for n in traced.graph.nodes]
            fx_error=""
        except Exception as e: fx=[]; fx_error=str(e)
        example=getattr(module,"example_input",None)
        if callable(example): example=example()
        if example is not None:
            if isinstance(example,torch.Tensor): example=example.to(device)
            elif isinstance(example,(tuple,list)):
                example=type(example)(x.to(device) if isinstance(x,torch.Tensor) else x for x in example)
            with torch.no_grad(): model(*example) if isinstance(example,(tuple,list)) else model(example)
        for h in hooks: h.remove()
        return {"class":cls.__name__,"device":device,"cuda_available":torch.cuda.is_available(),
          "cuda_device":torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
          "parameter_count":sum(p.numel() for p in model.parameters()),"layers":layers,
          "fx_graph":fx,"fx_error":fx_error,"forward_executed":example is not None,
          "note":"Forward hooks run only if module.example_input exists. Runtime inspection executes selected code; use trusted files only."}
    finally: sys.modules.pop(spec.name,None)
