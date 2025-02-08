#!/usr/bin/env bash

# run under e.g. nix-shell -p yq -p python3 -p python3Packages.pwntools -p python3Packages.requests

if [[ "$#" != "1" ]] 
then
	echo "Please pass a hostname"
	exit 1
fi

readarray lines < <(yq -r '.services|to_entries[]|"\(.key|sub("_"; "/")|gsub("_"; "-")) \(.value.ports|map(select(split(":")[1]=="1337"))[0]|split(":")[0])"' docker-compose.yml)

tmpdir=$(mktemp -d)

anyfails=no

for line in "${lines[@]}"
do
	read path port <<< "$line"
	echo -n -e "Checking \e[1m$path\e[0m on \e[1m$1:$port\e[0m... "
	expectflag="$(grep -oP '(?<=Flag: `)oiccflag\{.*\}(?=`)' $path/README.md)"

	tmpfile="$tmpdir/${path//\//_}"

	$path/solution/solve.?? $1 $port > "$tmpfile" 2>$tmpfile.stderr

	if grep -qF "$expectflag" "$tmpfile"
	then
		echo -e "\e[32mPASS\e[0m"

	else
		echo -e "\e[31mFAIL\e[0m, see $tmpfile and $tmpfile.stderr"
		anyfails=yes
	fi
done

if [[ "$anyfails" == "no" ]]
then
	rm -rf "$tmpdir"
fi
