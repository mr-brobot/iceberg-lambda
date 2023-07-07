#!/bin/bash

python -m pip install --user --requirement <(poetry export --without-hashes)

SITE_PACKAGES=$(python -m pip show aws-glue-sessions | grep Location | awk '{print $2}') && \
  python -m jupyter kernelspec install --user $SITE_PACKAGES/aws_glue_interactive_sessions_kernel/glue_pyspark