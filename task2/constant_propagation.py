import json
import sys
from typing import Dict, Set, List, Tuple, Optional

class BasicBlock:
    def __init__(self, label: str):
        self.label = label
        self.instructions = []
        self.predecessors = set()
        self.successors = set()
        self.dominator = None
        self.loop_header = None

def build_cfg(func):
    blocks = {}
    current_block = None
    
    for instr in func['instrs']:
        if 'label' in instr:
            if current_block:
                blocks[current_block.label] = current_block
            current_block = BasicBlock(instr['label'])
        else:
            if not current_block:
                # Create an entry block if we start with non-label instruction
                current_block = BasicBlock("__entry")
            current_block.instructions.append(instr)
            
            if 'op' in instr and instr['op'] in ['jmp', 'br']:
                current_block.successors.update(instr.get('labels', []))
                blocks[current_block.label] = current_block
                current_block = None

    # Add the last block if it's not already added
    if current_block and current_block.instructions:
        blocks[current_block.label] = current_block

    # Set predecessors
    for label, block in blocks.items():
        for succ_label in block.successors:
            if succ_label in blocks:
                blocks[succ_label].predecessors.add(label)
            else:
                # Create a new block for unknown successors
                new_block = BasicBlock(succ_label)
                new_block.predecessors.add(label)
                blocks[succ_label] = new_block

    return blocks


def compute_dominators(blocks, entry_label):
    dom = {label: set(blocks.keys()) for label in blocks}
    dom[entry_label] = {entry_label}
    changed = True
    while changed:
        changed = False
        for label in blocks:
            if label == entry_label:
                continue
            new_dom = {label} | set.intersection(*(dom[p] for p in blocks[label].predecessors))
            if new_dom != dom[label]:
                dom[label] = new_dom
                changed = True
    return dom

def identify_loops(blocks, dom):
    for header, block in blocks.items():
        for pred in block.predecessors:
            if header in dom[pred]:
                blocks[pred].loop_header = header

def is_pure(instr):
    return instr.get('op') not in ['call', 'store', 'print', 'alloc', 'free']

def constant_fold(instr, constants):
    if 'op' in instr and instr['op'] in ['add', 'mul', 'sub', 'div', 'eq', 'lt', 'gt', 'le', 'ge', 'ne']:
        if all(arg in constants for arg in instr['args']):
            val1, val2 = [constants[arg] for arg in instr['args']]
            result = None
            if instr['op'] == 'add':
                result = val1 + val2
            elif instr['op'] == 'mul':
                result = val1 * val2
            elif instr['op'] == 'sub':
                result = val1 - val2
            elif instr['op'] == 'div' and val2 != 0:
                result = val1 // val2
            elif instr['op'] == 'eq':
                result = int(val1 == val2)
            elif instr['op'] == 'lt':
                result = int(val1 < val2)
            elif instr['op'] == 'gt':
                result = int(val1 > val2)
            elif instr['op'] == 'le':
                result = int(val1 <= val2)
            elif instr['op'] == 'ge':
                result = int(val1 >= val2)
            elif instr['op'] == 'ne':
                result = int(val1 != val2)
            
            if result is not None:
                return {'op': 'const', 'dest': instr['dest'], 'type': instr['type'], 'value': result}
    return instr

def analyze_block(block: BasicBlock, in_constants: Dict[str, Optional[int]]) -> Tuple[Dict[str, Optional[int]], List[Dict]]:
    constants = in_constants.copy()
    new_instructions = []
    
    for instr in block.instructions:
        folded_instr = constant_fold(instr, constants)
        new_instructions.append(folded_instr)
        
        if is_pure(folded_instr):
            if folded_instr['op'] == 'const':
                constants[folded_instr['dest']] = folded_instr['value']
            elif 'dest' in folded_instr:
                if block.loop_header:
                    constants[folded_instr['dest']] = None  # Not a constant in a loop
                else:
                    constants.pop(folded_instr['dest'], None)
    
    return constants, new_instructions

def constant_propagation(func):
    blocks = build_cfg(func)
    if not blocks:
        return func['instrs']
    
    entry_label = "__entry" if "__entry" in blocks else next(iter(blocks))
    
    dom = compute_dominators(blocks, entry_label)
    identify_loops(blocks, dom)
    
    in_constants = {label: {} for label in blocks}
    out_constants = {label: {} for label in blocks}
    worklist = list(blocks.keys())
    
    while worklist:
        label = worklist.pop(0)
        block = blocks[label]
        
        new_in = {}
        if not block.predecessors:
            new_in = {}
        else:
            new_in = out_constants[next(iter(block.predecessors))].copy()
            for pred in block.predecessors:
                new_in = {var: val for var, val in new_in.items() if var in out_constants[pred] and out_constants[pred][val] == val}
        
        if new_in != in_constants[label]:
            in_constants[label] = new_in
            new_out, new_instructions = analyze_block(block, new_in)
            if new_out != out_constants[label]:
                out_constants[label] = new_out
                worklist.extend(block.successors)
            block.instructions = new_instructions
    
    return reconstruct_function(blocks)

def dead_code_elimination(instrs):
    used_vars = set()
    new_instrs = []
    
    for instr in reversed(instrs):
        if 'args' in instr:
            used_vars.update(instr['args'])
        
        if 'op' in instr and instr['op'] in ['br', 'jmp', 'ret'] or not is_pure(instr) or ('dest' in instr and instr['dest'] in used_vars):
            new_instrs.append(instr)
            if 'dest' in instr:
                used_vars.add(instr['dest'])
        elif 'label' in instr:
            new_instrs.append(instr)  # Always keep labels
    
    return list(reversed(new_instrs))

def conditional_constant_propagation(func):
    instrs = constant_propagation(func)
    instrs = dead_code_elimination(instrs)
    
    new_instrs = []
    skip_until_label = None
    for instr in instrs:
        if skip_until_label:
            if 'label' in instr and instr['label'] == skip_until_label:
                skip_until_label = None
            continue
        
        if 'op' in instr and instr['op'] == 'br' and 'args' in instr and len(instr['args']) == 1:
            cond = instr['args'][0]
            if isinstance(cond, bool) or (isinstance(cond, str) and cond in ['true', 'false']):
                target_label = instr['labels'][0] if cond == True or cond == 'true' else instr['labels'][1]
                new_instrs.append({'op': 'jmp', 'labels': [target_label]})
                skip_until_label = target_label
            else:
                new_instrs.append(instr)
        else:
            new_instrs.append(instr)
    
    return new_instrs

def reconstruct_function(blocks):
    new_instrs = []
    for label, block in blocks.items():
        if label != "__entry":
            new_instrs.append({'label': label})
        new_instrs.extend(block.instructions)
    return new_instrs

def optimize(prog):
    for func in prog['functions']:
        func['instrs'] = conditional_constant_propagation(func)
    return prog

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    optimized = optimize(prog)
    json.dump(optimized, sys.stdout, indent=2)