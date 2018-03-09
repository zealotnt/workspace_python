import sh, sys
from io import StringIO, BytesIO
import threading
import time
import collections
import alsaaudio
import wave
import os
import logging
import json
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path, verbose=True)

# remember to chmod ugo+x hotword.py before running this
ggAssistCmd = sh.Command(os.environ.get("HOTWORD_PATH"))
audio_device_name = os.environ.get("AUDIO_DEVICE_NAME")

std_out_buf = StringIO()
std_err_buf = StringIO()

useThread = True
# useThread = False

DETECT_DING=os.environ.get("DING_FILE_PATH")

def play_audio_file(audio_device_name, f):
	device = alsaaudio.PCM(device=audio_device_name)

	# print('%d channels, %d sampling rate\n' % (f.getnchannels(), f.getframerate()))
	# Set attributes
	device.setchannels(f.getnchannels())
	device.setrate(f.getframerate())

	# 8bit is unsigned in wav files
	if f.getsampwidth() == 1:
		device.setformat(alsaaudio.PCM_FORMAT_U8)
	# Otherwise we assume signed data, little endian
	elif f.getsampwidth() == 2:
		device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
	elif f.getsampwidth() == 3:
		device.setformat(alsaaudio.PCM_FORMAT_S24_3LE)
	elif f.getsampwidth() == 4:
		device.setformat(alsaaudio.PCM_FORMAT_S32_LE)
	else:
		raise ValueError('Unsupported format')

	periodsize = f.getframerate() / 8
	periodsize = int(periodsize)
	device.setperiodsize(periodsize)

	data = f.readframes(periodsize)
	while data:
		# Read data from stdin
		device.write(data)
		data = f.readframes(periodsize)
	f.rewind()
	device.close()

def StdOutAnalyzer():
	STATE_TURN_STARTED_STR = "ON_CONVERSATION_TURN_STARTED"
	time.sleep(0.5)
	print ("StdOutAnalyzer thread started")

	global std_out_buf
	global audio_device_name
	lastFollowOnTurn = False
	allData = ""
	ding_wav = wave.open(DETECT_DING, 'rb')
	while True:
		time.sleep(0.1)
		data = std_out_buf.getvalue()
		std_out_buf.truncate(0)
		if len(data) != 0:
			allData += data
			sys.stdout.write(data)
			if "with_follow_on_turn" in allData:
				startIdx = allData.rfind("{'with_follow_on_turn'")
				jsonStr = allData[startIdx:].splitlines()[0]
				jsonStr = jsonStr.replace("'", "\"")
				jsonStr = jsonStr.rstrip()
				jsonStr = jsonStr.replace("False", "false")
				jsonStr = jsonStr.replace("True", "true")
				jsonObj = json.loads(jsonStr)
				print (jsonStr)
				print ("Parsed json: ", jsonObj["with_follow_on_turn"])
				lastFollowOnTurn = jsonObj["with_follow_on_turn"]
			if STATE_TURN_STARTED_STR in allData:
				if lastFollowOnTurn is False:
					print ("WW Done!!!")
					play_audio_file(audio_device_name, ding_wav)
				# strip the STATE_TURN_STARTED_STR out of the allData buff
				allData = allData[allData.rfind(STATE_TURN_STARTED_STR)+len(STATE_TURN_STARTED_STR):]
				print ("After strip: ", allData, "*********")
		data_err = std_err_buf.getvalue()
		std_err_buf.truncate(0)
		if len(data_err) != 0:
			sys.stdout.write(data_err)

def main():
	if useThread:
		print("Init thread")
		stdoutAnalyzer = threading.Thread(target=StdOutAnalyzer)
		stdoutAnalyzer.start()
	else:
		print ("Not use thread")

	if useThread:
		stdOutParam = std_out_buf
		stdErrParam = std_err_buf
	else:
		stdOutParam = sys.stdout
		stdErrParam = sys.stderr

	ggAssistCmd("--device_model_id",
				os.environ.get("DEVICE_MODEL_ID"),
				"--project_id",
				os.environ.get("PROJECT_ID"),
				_out=stdOutParam,
				_err=stdErrParam,
				_tty_out=True)
	ggAssistCmd.wait()

if __name__ == "__main__":
	main()
