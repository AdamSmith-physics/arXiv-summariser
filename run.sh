#!/bin/bash

PYTHON = "/opt/anaconda3/envs/arxiv-summariser/bin/python"

# source activate arxiv-summariser
nohup /opt/anaconda3/envs/arxiv-summariser/bin/python -u run_summariser.py > logs/summariser_log.out 2>&1 &

echo "Summariser is running in the background. Check summariser_log.txt for output."