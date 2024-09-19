import json
import sys

def local_value_numbering(block):
    value_table = {}
    var_to_num = {}
    num_to_var = {}
    next_num = 0
    commutative_ops = {'add', 'mul'}
    optimized_block = []

    for instr in block:
        if 'op' not in instr:
            # Keep instructions without 'op' as-is (e.g., labels)
            optimized_block.append(instr)
            continue

        if 'dest' in instr:
            # Handle 'call', 'store', 'load' instructions separately
            if instr['op'] in ('call', 'store', 'load'):
                # Assign a unique value number; do not optimize
                num = f"vn{next_num}"
                next_num += 1
                num_to_var[num] = instr['dest']
                var_to_num[instr['dest']] = num
                optimized_block.append(instr)
                continue

            # Process arguments
            args = instr.get('args', [])
            args_value_numbers = []
            for arg in args:
                if arg in var_to_num:
                    arg_vn = var_to_num[arg]
                else:
                    # Assign a unique value number to this variable
                    arg_vn = f"var_{arg}"
                    var_to_num[arg] = arg_vn
                    num_to_var[arg_vn] = arg
                args_value_numbers.append(arg_vn)

            if instr['op'] in commutative_ops:
                # Sort the arguments
                args_value_numbers = sorted(args_value_numbers)

            # Create a value key for the instruction
            if instr['op'] == 'const':
                value = ('const', instr['value'])
            else:
                value = (instr['op'],) + tuple(args_value_numbers)

            if value in value_table:
                # Redundant computation found
                num = value_table[value]
                optimized_block.append({
                    'op': 'id',
                    'dest': instr['dest'],
                    'type': instr.get('type'),
                    'args': [num_to_var[num]]
                })
            else:
                # New computation
                num = f"vn{next_num}"
                next_num += 1
                value_table[value] = num
                num_to_var[num] = instr['dest']
                optimized_block.append(instr)

            var_to_num[instr['dest']] = num
        else:
            # Instructions without 'dest' are added as-is
            optimized_block.append(instr)

    return optimized_block

def split_basic_blocks(instrs):
    blocks = []
    current_block = []
    labels = set()

    # Collect all labels
    for instr in instrs:
        if 'label' in instr:
            labels.add(instr['label'])

    for instr in instrs:
        if 'label' in instr:
            # Start a new block with the label
            if current_block:
                blocks.append(current_block)
            current_block = [instr]
        else:
            current_block.append(instr)
            # If the instruction is a jump, branch, or return, end the current block
            if instr.get('op') in ('jmp', 'br', 'ret'):
                blocks.append(current_block)
                current_block = []

    if current_block:
        blocks.append(current_block)

    return blocks

def local_value_numbering_function(func):
    instrs = func['instrs']
    blocks = split_basic_blocks(instrs)
    optimized_instrs = []

    for block in blocks:
        optimized_block = local_value_numbering(block)
        optimized_instrs.extend(optimized_block)

    func['instrs'] = optimized_instrs

if __name__ == "__main__":
    prog = json.load(sys.stdin)
    for func in prog["functions"]:
        local_value_numbering_function(func)
    json.dump(prog, sys.stdout, indent=2)
