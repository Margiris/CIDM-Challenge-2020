#!/bin/sh
set -x

crontab -l | sed '/.*# repeated until success/d' | crontab -

PROGRAM_FOLDER="distance_pinger"
PROGRAM="${PROGRAM_FOLDER}.py"
output_file="/home/pi/${PROGRAM_FOLDER}/trash_levels.csv"
CMD="run_dir=/home/pi/${PROGRAM_FOLDER}; \${run_dir}/${PROGRAM} --file ${output_file} --log \${run_dir}/program.log --timeout 60 --count 10"

add_to_crontab() {
	(
		crontab -u pi -l
		echo "$1"
	) | sort - | uniq - | crontab -u pi -
}

die() {
	# Write to crontab for running later, until it succeeds
	add_to_crontab "*/5 * * * * $1 >> /home/pi/setup.log 2>&1 # repeated until success"
	echo "Error!"
	exit 1
}

echo "Installing DistancePinger to ~/$PROGRAM_FOLDER..."

cd ~/ || die "$0"

archive_line_num=$(grep --text --line-number 'ARCHIVE:$' "$0" | cut -f1 -d:)
tail -n +$((archive_line_num + 1)) "$0" | gzip -vdc - | tar -xvf - >/dev/null || die "$0"

if ! sudo dpkg -R -i $PROGRAM_FOLDER/debs; then
	echo "Failed to install dependencies from local, trying to connect to internet..."
	# sudo apt update
	# sudo apt install -y python3-pip ||
	die "$0"
fi

if ! pip3 install --no-index --find-links ${PROGRAM_FOLDER}/pip -r ${PROGRAM_FOLDER}/requirements.txt; then
	echo "Failed to install dependencies from local, trying to connect to internet..."
	pip3 install -r ${PROGRAM_FOLDER}/requirements.txt || die "$0"
fi

chmod +x ${PROGRAM_FOLDER}/${PROGRAM}

if [ ! -e $output_file ]; then
	echo "Date,Time,Distance,GPS time,Latitude,Latitude Direction,Longitude,Longitude Direction,Altitude,Altitude units" >$output_file
fi
add_to_crontab "* * * * * ${CMD}"

echo "Installation successful, cleaning up..."

rm -r ${PROGRAM_FOLDER}/debs
rm -r ${PROGRAM_FOLDER}/pip
rm ${PROGRAM_FOLDER}/requirements.txt
rm "$0"

echo "Done."
exit 0

ARCHIVE:
