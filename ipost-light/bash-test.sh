#!/bin/bash

declare -A tenants=( ["10"]="Corp" ["20"]="Retail" ["30"]="Wealth" ["40"]="Card" )
vlanOffset=1200
for highByte in 10 20 30 40; do
  echo "##DEBUG## highByte is $highByte which means tenant is POC-${tenants[$highByte]}"
  i1=$highByte; i2=101; i3=1; i4=1
  max=255
  upper=103
  eval printf -v ip "%s\ " $i1.{$i2..$upper}.{$i3..$max}.$i4
  count=1
  tn=${tenants[$highByte]}
  for i in $ip; do
    echo "    index $count is $i; VLAN is $(($count+$vlanOffset))"
    bd=$(($count+$vlanOffset))
    params=$(printf '{"tn": "POC-i%s", "bd": "%s", "subnet": "%s"}' $tn $bd $i)
    echo "DEBUG: $params"
    python ipost-light.py --template bash-test-template.xml --params "$params"
    let count=count+1 
    if [ $count -gt 400 ]
    then
      let vlanOffset=vlanOffset+400
      break
    fi
  done
done
