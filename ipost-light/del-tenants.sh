#!/bin/bash
for i in iCorp iRetail iWealth; do
    params=$(printf '{"tn": "POC-%s"}' $i)
    echo "DEBUG: $params"
    python ipost-light.py --template del-tenant.xml --params "$params"
done
