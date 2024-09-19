import json
import sys

def is_pure(instr):
    # Safely access 'op' using instr.get('op')
    return instr.get('op', None) not in ['call', 'store', 'print']

def global_dce(program):
    used_vars = set()
    
    # First pass: collect all used variables
    for func in program['functions']:
        for instr in func['instrs']:
            if 'args' in instr:
                used_vars.update(instr['args'])
    
    # Second pass: remove dead instructions
    for func in program['functions']:
        new_instrs = []
        for instr in func['instrs']:
            if not is_pure(instr) or 'dest' not in instr or instr['dest'] in used_vars:
                new_instrs.append(instr)
                if 'args' in instr:
                    used_vars.update(instr['args'])
            elif instr.get('op') == 'const' and 'dest' in instr and instr['dest'] not in used_vars:
                # Skip unused constants
                continue
            else:
                new_instrs.append(instr)  # Keep other instructions
        func['instrs'] = new_instrs
    
    return program

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    optimized_prog = global_dce(prog)
    json.dump(optimized_prog, sys.stdout, indent=2)
