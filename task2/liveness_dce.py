import json
import sys
from typing import Dict, Set, List, Any, Tuple

def get_uses(instr: Dict[str, Any]) -> Set[str]:
    return set(instr.get('args', []))

def get_defs(instr: Dict[str, Any]) -> Set[str]:
    return {instr['dest']} if 'dest' in instr else set()

def analyze_live_variables(func: Dict[str, Any]) -> List[Set[str]]:
    instrs = func['instrs']
    live_out = [set() for _ in instrs]
    
    changed = True
    while changed:
        changed = False
        for i in reversed(range(len(instrs))):
            instr = instrs[i]
            live_in = live_out[i].copy()
            live_in |= get_uses(instr)
            live_in -= get_defs(instr)
            
            if i > 0 and live_in != live_out[i-1]:
                live_out[i-1] = live_in
                changed = True
    
    return live_out

def minimal_dce(func: Dict[str, Any]) -> Dict[str, Any]:
    live_out = analyze_live_variables(func)
    new_instrs = []
    
    for i, instr in enumerate(func['instrs']):
        if (
            'op' in instr
            and instr['op'] not in ['const', 'id']
            or 'dest' not in instr
            or instr.get('dest') in live_out[i]
            or instr.get('op') in ['print', 'ret', 'br', 'jmp', 'call']
            or 'label' in instr
        ):
            new_instrs.append(instr)
    
    func['instrs'] = new_instrs
    return func

def optimize_function(func: Dict[str, Any]) -> Dict[str, Any]:
    return minimal_dce(func)

def optimize(prog: Dict[str, Any]) -> Dict[str, Any]:
    for func in prog['functions']:
        optimize_function(func)
    return prog

if __name__ == "__main__":
    try:
        prog = json.load(sys.stdin)
        optimized = optimize(prog)
        json.dump(optimized, sys.stdout, indent=2)
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    except BrokenPipeError:
        import os
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {str(e)}", file=sys.stderr)
        sys.exit(1)