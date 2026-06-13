#!/bin/bash
# run_blender_tests.sh
# Wrapper to source OpenFOAM environment and run Blender headless tests

OF_BASHRC="$HOME/OpenFOAM/OpenFOAM-13/etc/bashrc"

if [ -f "$OF_BASHRC" ]; then
    echo "Sourcing OpenFOAM environment from $OF_BASHRC"
    source "$OF_BASHRC"
else
    echo "Warning: OpenFOAM bashrc not found at $OF_BASHRC. OpenFOAM tests will be skipped."
fi

# Run the test script headlessly
/opt/blender-4.1/blender -b --python tests/test_blender_integration.py
