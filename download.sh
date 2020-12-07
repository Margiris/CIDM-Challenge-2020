#!/bin/bash

sudo apt update

mkdir ./debs
cd ./debs || exit 1

installed=$(apt list --installed | awk -F '/' '{print $1}')

FILES="gpsd python3-pip"
OLD_FILES=""

apt download "$FILES"

while [ "$FILES" != "$OLD_FILES" ]; do
    echo
    echo
    for f in $FILES; do
        PACKAGE=$(echo "$f" | awk -F '_' '{ print $1 }')
        echo "Downloading dependencies for ${PACKAGE}"

        dependencies=$(apt-cache depends -i "$PACKAGE" | awk 'BEGIN { ORS=" " }; /Depends:/ { print $2 }' | sed 's/<\(.*\)>/\1/' | sed 's/\(.*\):.*/\1/' )
        echo "They are: ${dependencies}"

        for dep in $dependencies; do
            found_installed=false

            for inst in $installed; do
                if [ "$dep" == "$inst" ]; then
                    echo "${dep} is already installed"
                    found_installed=true
                    break
                fi
            done
            if [ "$found_installed" = false ]; then
                echo "Downloading ${dep}"
                apt download "$dep"
            fi
        done
        echo
    done

    OLD_FILES=$FILES
    FILES=$(ls -- *.deb)
done

mkdir ../pip
cd ../pip || exit 1

pip3 download pynmea2 pyserial RPi.GPIO -d .

echo "Done"
