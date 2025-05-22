#!/bin/bash

# Set the Python path to include the current directory
export PYTHONPATH=$PYTHONPATH:/Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/nlp-analysis

# Run the code synthesis workflow
cd /Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/nlp-analysis
python3 src/code_synthesis_workflow.py \
  --input-file /Users/bhaktichindhe/Desktop/Project/RepoMind/test-project-employee/EmployeeByDepartmentRequirement.txt \
  --db-path /Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/.lancedb \
  --output-dir /Users/bhaktichindhe/Desktop/Project/RepoMind/codebase-analyser/output \
  --rag-type multi_hop \
  --generate-code
