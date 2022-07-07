#!/bin/bash

if [ $# == 0 ]
then
    echo "No params provided"
    exit
fi

while [ $# -gt 0 ]; do
    case $1 in
        --db-deploy-stack)
            echo "db opt"
            ;;
        --extract_location)
            echo "extractor initialized, please input country: "
            cd sources; read c; bash extract_transform.sh $c false false
            echo "done"
            ;;
        --extract_transform_location)
            echo "extractor and locations transformer initialized, please input country: "
            cd sources; read c; bash extract_transform.sh $c true false
            echo "done"
            ;;
        --extract_transform_all)
            echo "extractor and all transformers initialized, please input country: "
            cd sources; read c; bash extract_transform.sh $c true true
            echo "done"
            ;;
        --transform_location)
            echo "locations transformer initialized, please input country: "
            cd sources/locations; read c; python3 transform.py --country $c
            echo "done"
            ;;
        --load_location)
            echo "locations loader initialized, please input country: "
            cd sources/locations; read c; python3 load.py --country $c
            echo "done"
            ;;
        --etl_location)
            echo "locations loader initialized, please input country: "
            cd sources; read c; bash extract_transform.sh $c false false; cd ../
            cd sources/locations; read c; python3 transform.py --country $c; cd ../../
            cd sources/locations; read c; python3 load.py --country $c; cd ../../
            echo "done"
            ;;
        --help|-help|-h|help)
            echo """Script Syntax: 'bash pipeline.sh --{PARAM_1} --{PARAM_2} (...)'. Possible params are:
                --db-deploy-stack: deploys the db stack
                --extract_location: extracts the desired location, country prompt will show for the user
                --extract_transform_location: Same as before but also parses the desired location if parser is implemented
                --extract_transform_all: Same as before but will also transform coordinates if available.
                --transform_location: Only parses the desired location, country promp will show for the user
                --load_location: loads data from buckets CSV resulting from transform step, country promp will show for the user
                --help|-help|-h|help: Displays this message
            """
            exit
            ;;
        *)
            echo "Invalid param: $1"
            ;;
    esac
    shift
done