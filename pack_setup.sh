#!/bin/sh

PROGRAM="distance_pinger"
mkdir -p ./pi/payload/home/pi/
executable=./pi/payload/home/pi/${PROGRAM}_setup

cat setup.sh > ${executable}

tar -cvf ${PROGRAM}.tar ${PROGRAM}/ ; gzip -9 ${PROGRAM}.tar
cat ${PROGRAM}.tar.gz >> ${executable}
rm ${PROGRAM}.tar.gz

chmod +x ${executable}
