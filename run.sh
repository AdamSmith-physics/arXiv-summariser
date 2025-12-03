#!/bin/bash

cd "$(dirname "$0")"

echo " "
echo "----------------------------------- "
echo "`date`"
echo "Starting the Arxiv Summariser..."
echo " "

PYTHON=/opt/anaconda3/envs/arxiv-summariser/bin/python

nohup $PYTHON -u run_summariser.py > logs/summariser_log.out 2>&1 &

echo "Summariser is running in the background. Check summariser_log.txt for output."
echo " "