#!/usr/bin/env python3
import json
import sys
from collections import defaultdict, deque

def find_basic_blocks(instrs):
    blocks = []
    current = []
    
    for instr in instrs:
        if 'label' in instr:
            if current:
                blocks.append(current)
            current = [instr]
        else:
            current.append(instr)
            if 'op' in instr and instr['op'] in ['jmp', 'br']:
                blocks.append(current)
                current = []
    
    if current:
        blocks.append(current)
    
    return blocks

def build_cfg(blocks):
    cfg = defaultdict(list)
    labels = {}
    rev_cfg = defaultdict(list)
    
    # Map labels to block indices
    for i, block in enumerate(blocks):
        if block and 'label' in block[0]:
            labels[block[0]['label']] = i
    
    # Build forward and reverse edges
    for i, block in enumerate(blocks):
        if not block:
            continue
        last = block[-1]
        if 'op' in last:
            if last['op'] == 'jmp':
                succ = labels[last['labels'][0]]
                cfg[i].append(succ)
                rev_cfg[succ].append(i)
            elif last['op'] == 'br':
                for label in last['labels']:
                    succ = labels[label]
                    cfg[i].append(succ)
                    rev_cfg[succ].append(i)
            elif i + 1 < len(blocks):
                cfg[i].append(i + 1)
                rev_cfg[i + 1].append(i)
        elif i + 1 < len(blocks):
            cfg[i].append(i + 1)
            rev_cfg[i + 1].append(i)
    
    return cfg, rev_cfg, labels

def find_dominators(cfg, entry):
    dom = {v: set(cfg.keys()) for v in cfg}
    dom[entry] = {entry}
    
    changed = True
    while changed:
        changed = False
        for node in cfg:
            if node == entry:
                continue
            preds = [p for p in cfg if node in cfg[p]]
            if not preds:
                continue
            new_dom = {node} | set.intersection(*(dom[p] for p in preds))
            if new_dom != dom[node]:
                dom[node] = new_dom
                changed = True
    
    return dom

def find_loops(cfg, rev_cfg, dom):
    loops = []
    visited = set()
    
    def find_loop_body(header, back_edge_source):
        body = {back_edge_source}
        stack = [back_edge_source]
        
        while stack:
            node = stack.pop()
            for pred in rev_cfg[node]:
                if pred != header and pred not in body:
                    body.add(pred)
                    stack.append(pred)
        
        body.add(header)
        return body

    # Find natural loops
    for header in cfg:
        for pred in rev_cfg[header]:
            if header in dom[pred] and (header, pred) not in visited:
                # Found a back edge
                visited.add((header, pred))
                loop_body = find_loop_body(header, pred)
                
                # Find preheader
                preheader = None
                preds = [p for p in rev_cfg[header] if p not in loop_body]
                if preds:
                    preheader = preds[0]
                
                if preheader is not None:
                    loops.append((header, loop_body, preheader))
    
    return loops

def is_loop_invariant(instr, loop_blocks, defs_in_loop):
    if 'op' not in instr:
        return False
    
    # Constants are always invariant
    if instr['op'] == 'const':
        return True
    
    # Never move memory operations, calls, or control flow
    if instr['op'] in ['load', 'store', 'call', 'print', 'br', 'jmp', 'ret']:
        return False
    
    # Never move phi nodes
    if instr['op'] == 'phi':
        return False
    
    # For other operations, check if all arguments are loop-invariant
    if 'args' in instr:
        return not any(arg in defs_in_loop for arg in instr['args'])
    
    return True

def process_function(func):
    if 'instrs' not in func:
        return func
    
    blocks = find_basic_blocks(func['instrs'])
    if not blocks:
        return func
    
    cfg, rev_cfg, labels = build_cfg(blocks)
    
    # Find entry block
    entry = 0
    for i, block in enumerate(blocks):
        if block and 'label' in block[0] and block[0]['label'] == func['name']:
            entry = i
            break
    
    dom = find_dominators(cfg, entry)
    loops = find_loops(cfg, rev_cfg, dom)
    
    if not loops:
        return func
    
    # Process loops from innermost to outermost
    modified = False
    for header, loop_body, preheader in sorted(loops, key=lambda x: len(x[1]), reverse=True):
        # Find all definitions in the loop
        defs_in_loop = set()
        for block_id in loop_body:
            for instr in blocks[block_id]:
                if 'dest' in instr:
                    defs_in_loop.add(instr['dest'])
        
        # Find and move invariant instructions
        for block_id in loop_body:
            invariant_instrs = []
            remaining_instrs = []
            
            for instr in blocks[block_id]:
                if is_loop_invariant(instr, loop_body, defs_in_loop):
                    invariant_instrs.append(instr)
                    if 'dest' in instr:
                        defs_in_loop.remove(instr['dest'])
                else:
                    remaining_instrs.append(instr)
            
            if invariant_instrs:
                modified = True
                blocks[block_id] = remaining_instrs
                
                # Insert at the appropriate position in preheader
                insert_pos = len(blocks[preheader])
                for i, instr in enumerate(blocks[preheader]):
                    if 'op' in instr and instr['op'] in ['jmp', 'br']:
                        insert_pos = i
                        break
                
                blocks[preheader][insert_pos:insert_pos] = invariant_instrs
    
    if modified:
        # Reconstruct function instructions
        func['instrs'] = [instr for block in blocks for instr in block]
    
    return func

def main():
    try:
        prog = json.load(sys.stdin)
        if 'functions' in prog:
            prog['functions'] = [process_function(f) for f in prog['functions']]
        json.dump(prog, sys.stdout)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()