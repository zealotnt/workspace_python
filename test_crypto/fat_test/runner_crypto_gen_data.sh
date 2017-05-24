#!/bin/bash


##################################################################################################
# constant definition
##################################################################################################
TEST_SCRIPT_VERSION="0.0.1"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

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
	echo "  -f FILE_PREFIX | --file=FILE_PREFIX          Prefix of file that will be dump data"
	echo "  -h | --help                                  Show this message"
	echo "Script Version: $TEST_SCRIPT_VERSION"
	exit 1
}

##################################################################################################
# main program
##################################################################################################
# process arguments
while [[ $# -gt 0 ]]
do
	case "$1" in
		-f)
		FILE_PREFIX="$2"
		if [[ $FILE_PREFIX == "" ]]; then echoerr "-s argument required"; usage; fi
		shift 2
		;;
		--file=*)
		FILE_PREFIX="${1#*=}"
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

if [[ "$FILE_PREFIX" == "" ]]; then
	echoerr "file prefix missing."
	usage
fi

GEN_SCRIPT=(
	"cmac.py"
	"dsa.py"
	"ecdsa.py"
	"rsa.py"
)
GEN_ADDITIONAL_PARAM=(
	"raw" 			#CMAC
	"raw" 			#DSA
	"raw"			#ECDSA
	"raw"			#RSA
)

count=${#GEN_SCRIPT[@]}
for ((j=0; j < $count; j++)); do
	cipher_algo_name=${GEN_SCRIPT[j]%.py}
	python $DIR/${GEN_SCRIPT[j]} ${FILE_PREFIX}_${cipher_algo_name}.txt ${GEN_ADDITIONAL_PARAM[j]}
done
