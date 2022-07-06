#!/bin/bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

cd "$parent_path"
cd locations/

if [ $1 == "help" ]
then
    echo "command syntax: 'bash extract_transform.sh {country:str} {location:bool} {coord:bool}'"
    echo "Special commands: 'bash extract_transform.sh help'"
    exit
fi
echo "running extractor"
python3 extract.py --country $1
if [ $2 == "true" ] ; then
    echo "running location transform"
    python3 transform.py --country $1
elif [ $2 == "false" ] ; then
    :
else
    echo "location should be 'true' or 'false'"
fi
if [ $3 == "true" ] ; then
    echo "coord comming soon (WIP)"
elif [ $3 == "false" ] ; then
    :
else
    echo "coord should be 'true' or 'false'"
fi
