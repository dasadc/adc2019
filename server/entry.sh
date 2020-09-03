#!/bin/bash

cp /tools/manual_qa_gen/convert_excel2QA.py /api/
gunicorn -b 0.0.0.0:4280 main:app

