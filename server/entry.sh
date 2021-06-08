#!/bin/bash

gunicorn -b 0.0.0.0:4280 main:app

