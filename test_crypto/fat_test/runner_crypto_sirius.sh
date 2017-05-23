#!/bin/bash


##################################################################################################
# constant definition
##################################################################################################
TEST_SCRIPT_VERSION="0.0.1"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

TEST_TARGET_LIST=("APP" "RF" "ALL")
DEFAULT_TEST_TARGET="ALL"

SCRIPT_NAME=`basename "$0"`
SCRIPT_HDR="[$SCRIPT_NAME]"

##################################################################################################
# function definition
##################################################################################################
echoinfo() { if [[ $QUIET -ne 1 ]]; then echo -e "$SCRIPT_HDR $@${KRESET}${ENDL}" 1>&2; fi }
echoerr() { if [[ $QUIET -ne 1 ]]; then echo -e "${KBOLD}${KLRED}$SCRIPT_HDR $@${KRESET}${ENDL}" 1>&2; fi }
echonoti() { if [[ $QUIET -ne 1 ]]; then echo -e "${KBOLD}${KLGRN}$SCRIPT_HDR $@${KRESET}" 1>&2; fi }

usage()
{
	echo "Usage:"
	echo "  bash $cmdname [-p COMPORT] [-t upgrade-type]"
	echo "  -s PORT | --serport=PORT          Serial device to interface with reader"
	echo "                                 ex, -p /dev/ttyUSB0"
	echo "  -t | --target=TEST_TARGET_NAME Target to test crypto feature"
	echo "                                 support targets: '${TEST_TARGET_LIST[@]}', if no type specify, '$DEFAULT_TEST_TARGET' type will be default"
	echo "  -h | --help                    Show this message"
	echo "Script Version: $TEST_SCRIPT_VERSION"
	exit 1
}

CheckValidOption()
{
	# Usage
	# <option-to-be-checked> <list-contain-valid-item>
	# function usage:
	arguments=("$@")
	arguments_len=${#arguments[@]}
	array=("${arguments[@]:1:$arguments_len}")
	count=${#array[@]}
	for ((j=0; j < $count; j++)); do
		if [[ "$1" == ${array[j]} ]];then
			return
		fi
	done

	echoerr "Invalid option '$1'"
	usage
	exit 2
}

RunTestScritp()
{
	#function usage:
	arguments=("$@")
	arguments_len=${#arguments[@]}
	array=("${arguments[@]:1:$arguments_len}")
	count=${#array[@]}
	for ((j=0; j < $count; j++)); do
		echo ""
	done
}

##################################################################################################
# main program
##################################################################################################
# process arguments
while [[ $# -gt 0 ]]
do
	case "$1" in
		-s)
		SERIAL_PORT="$2"
		if [[ $SERIAL_PORT == "" ]]; then echoerr "-s argument required"; usage; fi
		shift 2
		;;
		--serport=*)
		SERIAL_PORT="${1#*=}"
		shift 1
		;;
		-t)
		TEST_TARGET_NAME="$2"
		if [[ $TEST_TARGET_NAME == "" ]]; then echoerr "-t argument required"; usage; fi
		shift 2
		;;
		--target=*)
		TEST_TARGET_NAME="${1#*=}"
		shift 1
		;;
		-h | --help)
		usage
		;;
		*)
		echoerr "Unknown argument: '$1'"
		usage
		;;
	esac
done

if [[ "$SERIAL_PORT" == "" ]]; then
	echoerr "Error: you need to provide an available serial port to continue."
	usage
fi

if [[ "$TEST_TARGET_NAME" == "" ]]; then
	echoinfo "No tested target specified, use upgrade '$DEFAULT_TEST_TARGET' as default"
	TEST_TARGET_NAME=$DEFAULT_TEST_TARGET
fi

CheckValidOption $TEST_TARGET_NAME "${TEST_TARGET_LIST[@]}"

TEST_SCRIPT=(
	"sirius_trng.py"
	"sirius_tdes.py"
	"sirius_aes.py"
	"sirius_cmac.py"
	"sirius_dsa.py"
	"sirius_ecdsa.py"
	"sirius_rsa.py"
	"sirius_sha.py"
)
TEST_SCRIPT_ADDITIONAL_ARGUMENTS=(
	"-n 100" 	#TRNG
	"" 			#TDES
	""			#AES
	""			#CMAC
	""			#DSA
	""			#ECDSA
	""			#RSA
	""			#SHA
)

if [[ "$TEST_TARGET_NAME" == "ALL" || "$TEST_TARGET_NAME" == "RF" ]]; then
	count=${#TEST_SCRIPT[@]}
	for ((j=0; j < $count; j++)); do
		python $DIR/${TEST_SCRIPT[j]} -s ${SERIAL_PORT} -t RF ${TEST_SCRIPT_ADDITIONAL_ARGUMENTS[j]}
	done
fi

if [[ "$TEST_TARGET_NAME" == "ALL" || "$TEST_TARGET_NAME" == "APP" ]]; then
	count=${#TEST_SCRIPT[@]}
	for ((j=0; j < $count; j++)); do
		python $DIR/${TEST_SCRIPT[j]} -s ${SERIAL_PORT} -t APP ${TEST_SCRIPT_ADDITIONAL_ARGUMENTS[j]}
	done
fi
