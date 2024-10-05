import json
import sys
from typing import Dict, Set, List

def is_pure(instr):
    return instr.get('op') not in ['call', 'store', 'print']

def get_uses(instr):
    return set(instr.get('args', []))

def get_defs(instr):
    return {instr['dest']} if 'dest' in instr else set()

def analyze_liveness(func):
    live_vars = set()
    for instr in reversed(func['instrs']):
        if 'label' in instr:
            continue
        if 'dest' in instr and instr['dest'] in live_vars:
            live_vars.remove(instr['dest'])
        live_vars.update(get_uses(instr))
    return live_vars

def dead_code_elimination(func):
    live_vars = analyze_liveness(func)
    new_instrs = []
    
    for instr in func['instrs']:
        if 'label' in instr:
            new_instrs.append(instr)
        elif not is_pure(instr) or 'dest' not in instr or instr['dest'] in live_vars:
            new_instrs.append(instr)
            if 'dest' in instr:
                live_vars.add(instr['dest'])
            live_vars.update(get_uses(instr))
    
    func['instrs'] = new_instrs
    return func

def optimize(prog):
    for func in prog['functions']:
        func = dead_code_elimination(func)
    return prog

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    optimized = optimize(prog)
    json.dump(optimized, sys.stdout, indent=2)
