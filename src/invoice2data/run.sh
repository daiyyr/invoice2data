#!/bin/bash
if [[ ! $(pgrep -f batch_loop_scan.py) ]]; then
	python -u run.py &
	python -u batch_loop_scan.py &
fi
