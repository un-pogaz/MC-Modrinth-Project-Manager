#!/bin/bash
# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")


while :
do
  read -p "mcsmp.py " cmd
  python $SCRIPTPATH/mcsmp.py $cmd
  cmd=""
  echo
done
