#!/bin/bash

# Function to process a single Bril file
test_file() {
    local file=$1
    echo "Testing file: $(basename $file)"
    echo "===================="
    echo "BEFORE:"
    cat $file | bril2json | bril2txt
    echo "--------------------"
    echo "AFTER:"
    cat $file | bril2json | python3 licm.py | bril2txt
    echo "===================="
    echo
}

# Base directory for tests
BASE_DIR="../../examples/test"

echo "=== Testing Dominator Examples ==="
echo "********************************"
for file in $BASE_DIR/dom/*.bril; do
    test_file "$file"
done

echo "=== Testing SSA Examples ==="
echo "********************************"
for file in $BASE_DIR/ssa/*.bril; do
    test_file "$file"
done

echo "=== Testing to_SSA Examples ==="
echo "********************************"
for file in $BASE_DIR/to_ssa/*.bril; do
    test_file "$file"
done