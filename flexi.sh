#!/bin/bash


source activate flexiEnv

PYTHONPATH=$(pwd) python -u python/main.py -root $(pwd)/python -job $2 -prop $1
