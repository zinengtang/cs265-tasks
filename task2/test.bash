# echo this is cond.bril by constant_propagation.py
# echo after
# cat ../../examples/test/df/cond.bril | bril2json | python3 constant_propagation.py | bril2txt
# echo before
# cat ../../examples/test/df/cond.bril | bril2json | bril2txt

# echo this is cond.bril by constant_propagation.py
# echo after
# cat ../../examples/test/df/fact.bril | bril2json | python3 constant_propagation.py | bril2txt
# echo before
# cat ../../examples/test/df/fact.bril | bril2json | bril2txt

# echo this is cond.bril by constant_propagation.py
# echo after
# cat ../../examples/test/df/cond-args.bril | bril2json | python3 constant_propagation.py | bril2txt
# echo before
# cat ../../examples/test/df/cond-args.bril | bril2json | bril2txt


# echo this is cond.bril by liveness_dice.py
# echo after
# cat ../../examples/test/df/cond.bril | bril2json | python3 liveness_dce.py | bril2txt
# echo before
# cat ../../examples/test/df/cond.bril | bril2json | bril2txt

# echo this is cond.bril by liveness_dice.py
# echo after
# cat ../../examples/test/df/fact.bril | bril2json | python3 liveness_dce.py | bril2txt
# echo before
# cat ../../examples/test/df/fact.bril | bril2json | bril2txt

# echo this is cond.bril by liveness_dice.py
# echo after
# cat ../../examples/test/df/cond-args.bril | bril2json | python3 liveness_dce.py | bril2txt
# echo before
# cat ../../examples/test/df/cond-args.bril | bril2json | bril2txt

echo this is cond.bril by liveness_dice.py and constant_propagation
echo after
cat ../../examples/test/df/cond.bril | bril2json | python3 liveness_dce.py | python3 liveness_dce.py | bril2txt
echo before
cat ../../examples/test/df/cond.bril | bril2json | bril2txt

echo this is fact.bril by liveness_dice.py and constant_propagation
echo after
cat ../../examples/test/df/fact.bril | bril2json | python3 liveness_dce.py | python3 liveness_dce.py | bril2txt
echo before
cat ../../examples/test/df/fact.bril | bril2json | bril2txt

echo this is cond-args.bril by liveness_dice.py and constant_propagation
echo after
cat ../../examples/test/df/cond-args.bril | bril2json | python3 liveness_dce.py | python3 liveness_dce.py | bril2txt
echo before
cat ../../examples/test/df/cond-args.bril | bril2json | bril2txt

# echo this is ackermann.bril by liveness_dice.py
# echo after
# cat ../../benchmarks/core/ackermann.bril | bril2json | python3 liveness_dce.py | bril2txt
# echo before
# cat ../../benchmarks/core/ackermann.bril | bril2json | bril2txt

# echo this is catalan.bril by liveness_dice.py
# echo after
# cat ../../benchmarks/core/catalan.bril | bril2json | python3 liveness_dce.py | bril2txt
# echo before
# cat ../../benchmarks/core/catalan.bril | bril2json | bril2txt

# echo this is cond.bril by liveness_dice.py
# echo after
# cat ../../benchmarks/core/birthday.bril | bril2json | python3 liveness_dce.py | bril2txt
# echo before
# cat ../../benchmarks/core/birthday.bril | bril2json | bril2txt

# echo this is bitshift.bril by liveness_dice.py
# echo after
# cat ../../benchmarks/core/bitshift.bril | bril2json | python3 liveness_dce.py | bril2txt
# echo before
# cat ../../benchmarks/core/bitshift.bril | bril2json | bril2txt

# cat ../../examples/test/df/cond.bril | bril2json | python3 liveness_dce.py | bril2txt
# cat ../../examples/test/df/cond.bril | bril2json | bril2txt

# cat ../../examples/test/df/fact.bril | bril2json | python3 liveness_dce.py | bril2txt
# cat ../../examples/test/df/fact.bril | bril2json | bril2txt

# cat ../../examples/test/df/cond-args.bril | bril2json | python3 liveness_dce.py | bril2txt
# cat ../../examples/test/df/cond-args.bril | bril2json | bril2txt