import sh, sys
from io import StringIO, BytesIO
import threading
import time
import collections
import pyaudio
import wave
import os
import logging
import json
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path, verbose=True)

# remember to chmod ugo+x hotword.py before running this
ggAssistCmd = sh.Command(os.environ.get("HOTWORD_PATH"))

std_out_buf = StringIO()
std_err_buf = StringIO()

useThread = True
# useThread = False

DETECT_DING=os.environ.get("DING_FILE_PATH")
ding_wav = wave.open(DETECT_DING, 'rb')
ding_data = ding_wav.readframes(ding_wav.getnframes())

def play_audio_file():
    """Simple callback function to play a wave file. By default it plays
    a Ding sound.

    :return: None
    """
    global ding_wav
    global ding_data
    audio = pyaudio.PyAudio()
    stream_out = audio.open(
        format=audio.get_format_from_width(ding_wav.getsampwidth()),
        channels=ding_wav.getnchannels(),
        rate=ding_wav.getframerate(), input=False, output=True)
    stream_out.start_stream()
    stream_out.write(ding_data)
    time.sleep(0.2)
    stream_out.stop_stream()
    stream_out.close()
    audio.terminate()

def StdOutAnalyzer():
	global std_out_buf
	time.sleep(0.5)
	print ("StdOutAnalyzer thread started")
	lastFollowOnTurn = False
	allData = ""

	STATE_TURN_STARTED_STR = "ON_CONVERSATION_TURN_STARTED"
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
					play_audio_file()
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
