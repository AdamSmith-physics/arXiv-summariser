#!/bin/bash

conda activate arxiv-summariser
nohup python -u run_summariser.py > logs/summariser_log.out 2>&1 &

echo "Summariser is running in the background. Check summariser_log.txt for output."