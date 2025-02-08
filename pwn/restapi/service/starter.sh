#!/usr/bin/env bash
portgood=no

for attempt in {1..1000}; do
    port="$(shuf -i 30000-31000 -n 1)"
    porthex="$(printf '%04X\n' $port)"

    if ! grep -q ": 00000000:$porthex" /proc/net/tcp; then
        portgood=yes
        break
    fi
done

if [[ "$portgood" = "yes" ]]; then
    echo Listening on port $port

    # run program
    exec nsjail --config nsjail.config -- /chal/restapi $port
else
    echo "Couldn't find a free port, contact an admin"
fi
