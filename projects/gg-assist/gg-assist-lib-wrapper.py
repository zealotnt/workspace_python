import sh, sys
from io import StringIO, BytesIO
import threading
import time
import collections
import alsaaudio
import wave
import os
import logging, logging.config
import json
from dotenv import load_dotenv
import platform
from tendo import singleton
import urllib.request
import progressbar
import re, pprint

# [Ref](https://stackoverflow.com/questions/380870/python-single-instance-of-program)
me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path, verbose=True)

# remember to chmod ugo+x hotword.py before running this
audio_device_name = os.environ.get("AUDIO_DEVICE_NAME")

std_out_buf = StringIO()
std_err_buf = StringIO()

useThread = True
# useThread = False

# read initial config file
## [Ref](https://stackoverflow.com/questions/23161745/python-logging-file-config-keyerror-formatters)
## use this to pass the correct logging.conf file path, otherwise, configparser will complain
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.conf')
logging.config.fileConfig(log_file_path, disable_existing_loggers=False)

# create and start listener on port 9999
t = logging.config.listen(9999)
t.start()

logger = logging.getLogger('gg_assist_wrapper')

DETECT_DING=os.environ.get("DING_FILE_PATH")

def isBoard():
	if "armv7l" in platform.processor():
		return True
	return False

def play_audio_file(audio_device_name, f):
	device = alsaaudio.PCM(device=audio_device_name)

	# logger.info('%d channels, %d sampling rate\n' % (f.getnchannels(), f.getframerate()))
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

class CheckNetworkThread(threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self)
		self.name = name
		self.shouldKilled = False
		self.retry_count = 0
		self.MAX_RETRY_NETWORK = 10 # after 2s of no internet connection, restart the assistant
		self.INTERVAL_EACH_RETRY = 0.2

	def kill_hotword(self):
		self.retry_count += 1
		if self.retry_count <= self.MAX_RETRY_NETWORK:
			return
		self.retry_count = 0

		app_pid = GetHotwordPID()
		if app_pid is not None:
			logger.info ("[CheckNetworkThread] kill assist-app")
			os.system("kill -9 %d" % app_pid)
		# else:
		# 	logger.info ("[CheckNetworkThread] can't find hotword")

	def run(self):
		logger.info ("Starting " + self.name)
		while self.shouldKilled is False:
			try:
				if internet_on() is False:
					self.kill_hotword()
				else:
					self.retry_count = 0
				# logger.info ("[CheckNetworkThread] Just Check")
			except:
				self.kill_hotword()
			time.sleep(self.INTERVAL_EACH_RETRY)
		logger.info ("Exiting " + self.name)

class BlinkLedThread(threading.Thread):
	SYSFS_GPIO_VALUE_HIGH = '1'
	SYSFS_GPIO_VALUE_LOW = '0'
	PATTERN_ERROR = [1]
	PATTERN_ON_POWERUP = [7, 0]
	PATTERN_ON_START_FINISHED = [7]
	PATTERN_WAIT_FOR_WAKE_WORD = [6]
	PATTERN_WAIT_FOR_SPEECH = [0, 2]
	PATTERN_PROCESSING = [0, 3]
	PATTERN_PLAYING = [0, 4]
	PATTERN_RAINBOW = [0, 1, 2, 3, 4, 5, 6, 7]

	def __init__(self, name):
		threading.Thread.__init__(self)
		self.name = name
		self.shouldKilled = False

	def run(self):
		logger.info ("Starting " + self.name)
		self.BlinkLed()
		logger.info ("Exiting " + self.name)

	def SetLedColor(self, value):
		if (value & 0x01):
			self.f_red.write(self.SYSFS_GPIO_VALUE_HIGH)
		else:
			self.f_red.write(self.SYSFS_GPIO_VALUE_LOW)

		if (value & 0x02):
			self.f_green.write(self.SYSFS_GPIO_VALUE_HIGH)
		else:
			self.f_green.write(self.SYSFS_GPIO_VALUE_LOW)

		if (value & 0x04):
			self.f_blue.write(self.SYSFS_GPIO_VALUE_HIGH)
		else:
			self.f_blue.write(self.SYSFS_GPIO_VALUE_LOW)

		self.f_red.seek(0)
		self.f_green.seek(0)
		self.f_blue.seek(0)

	def SetLedPattern(self, pattern_type):
		patternDict = {
			"STATE_POWERUP": self.PATTERN_ON_POWERUP,
			"STATE_ON_START_FINISHED": self.PATTERN_ON_START_FINISHED,
			"STATE_WAIT_WAKE_WORD": self.PATTERN_WAIT_FOR_WAKE_WORD,
			"STATE_WAIT_SPEECH": self.PATTERN_WAIT_FOR_SPEECH,
			"STATE_PROCESSING": self.PATTERN_PROCESSING,
			"STATE_PlAYING": self.PATTERN_PLAYING,
			"STATE_ERROR": self.PATTERN_ERROR,
		}
		self.color_list = patternDict[pattern_type]

	def BlinkLed(self):
		LED_RED = 150
		LED_GREEN = 151
		LED_BLUE = 152

		self.color_list = self.PATTERN_ON_POWERUP

		# Export gpio
		os.system("echo 150 > /sys/class/gpio/export")
		os.system("echo 151 > /sys/class/gpio/export")
		os.system("echo 152 > /sys/class/gpio/export")

		# Set output
		os.system("echo out > /sys/class/gpio/gpio150/direction")
		os.system("echo out > /sys/class/gpio/gpio151/direction")
		os.system("echo out > /sys/class/gpio/gpio152/direction")

		self.f_red = open("/sys/class/gpio/gpio150/value", "r+")
		self.f_green = open("/sys/class/gpio/gpio151/value", "r+")
		self.f_blue = open("/sys/class/gpio/gpio152/value", "r+")

		while self.shouldKilled == False:
			for color in self.color_list:
				self.SetLedColor(color)
				time.sleep(0.1)

	def StopThread(self):
		self.shouldKilled = True

STATE_ON_START_FINISHED = "ON_START_FINISHED"
STATE_TURN_STARTED_STR = "ON_CONVERSATION_TURN_STARTED"
STATE_ON_END_OF_UTTERANCE = "ON_END_OF_UTTERANCE"
STATE_ON_RECOGNIZING_SPEECH_FINISHED = "ON_RECOGNIZING_SPEECH_FINISHED"
STATE_ON_RESPONDING_STARTED = "ON_RESPONDING_STARTED"
STATE_ON_RESPONDING_FINISHED = "ON_RESPONDING_FINISHED"
STATE_ERROR_NO_MIC = "Input error"
STATE_ERROR_NO_SPEAKER = "Invalid value for card"
STATE_ON_CONVERSATION_TURN_TIMEOUT = "ON_CONVERSATION_TURN_TIMEOUT"
STATE_ON_CONVERSATION_TURN_FINISHED = "ON_CONVERSATION_TURN_FINISHED"

STATES_LED_PATTERN = {
	STATE_ON_CONVERSATION_TURN_FINISHED: "STATE_WAIT_WAKE_WORD",
	STATE_ON_START_FINISHED: "STATE_WAIT_WAKE_WORD",
	STATE_TURN_STARTED_STR: "STATE_WAIT_SPEECH",
	STATE_ON_END_OF_UTTERANCE: "STATE_PROCESSING",
	STATE_ON_RECOGNIZING_SPEECH_FINISHED: "STATE_PROCESSING",
	STATE_ON_RESPONDING_STARTED: "STATE_PROCESSING",
	STATE_ON_RESPONDING_FINISHED: "STATE_WAIT_WAKE_WORD",
	STATE_ERROR_NO_MIC: "STATE_ERROR",
	STATE_ERROR_NO_SPEAKER: "STATE_ERROR",
	STATE_ON_CONVERSATION_TURN_TIMEOUT: "STATE_WAIT_WAKE_WORD"
}

def AnalyzeStdoutForLED(all_data):
	if "armv7l" not in platform.processor():
		return
	global blink_led
	max_len = len(all_data)
	idx = max_len
	while idx >= 0:
		check = all_data[idx:]
		for state in STATES_LED_PATTERN:
			if state in check:
				blink_led.SetLedPattern(STATES_LED_PATTERN[state])
				return
		idx -= 1

def StdOutAnalyzer():

	time.sleep(0.5)
	logger.info ("StdOutAnalyzer thread started")

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
			logger.info (data)

			AnalyzeStdoutForLED(allData)
			if "with_follow_on_turn" in allData:
				startIdx = allData.rfind("{'with_follow_on_turn'")
				jsonStr = allData[startIdx:].splitlines()[0]
				jsonStr = jsonStr.replace("'", "\"")
				jsonStr = jsonStr.rstrip()
				jsonStr = jsonStr.replace("False", "false")
				jsonStr = jsonStr.replace("True", "true")
				jsonObj = json.loads(jsonStr)
				logger.info (jsonStr)
				logger.info ("Parsed json: %s" % jsonObj["with_follow_on_turn"])
				lastFollowOnTurn = jsonObj["with_follow_on_turn"]

			if STATE_TURN_STARTED_STR in allData:
				if lastFollowOnTurn is False:
					logger.info ("WW Done!!!")
					try:
						play_audio_file(audio_device_name, ding_wav)
					except:
						blink_led.SetLedPattern("STATE_ERROR")
						pass

				# strip the STATE_TURN_STARTED_STR out of the allData buff
				allData = allData[allData.rfind(STATE_TURN_STARTED_STR)+len(STATE_TURN_STARTED_STR):]
				logger.info ("After strip: %s *********" % allData)
		data_err = std_err_buf.getvalue()
		std_err_buf.truncate(0)
		if len(data_err) != 0:
			logger.info ("[ERROR] " + data_err)
			allData += data_err
			AnalyzeStdoutForLED(allData)

def GetHotwordPID():
	# logger.info (sh.glob("*"))
	# logger.info(sh.sort(sh.du(sh.glob("*"), "-sb"), "-rn"))
	# logger.info(sh.grep(sh.grep(sh.ps("-aux"), "python"), "hotword"))
	# logger.info(sh.grep(sh.grep(sh.ps("-aux"), "python")), "hotword")

	out = sh.grep(sh.ps("-aux"), "python")
	# logger.info ("***out***:\r\n", out, "*******")
	# logger.info (type(out))
	match = re.findall(b'[^\s]+\s+(\d+).+hotword.py', out.stdout, re.MULTILINE)
	# pprint.pprint(match)
	for item in match:
		plogger.info.plogger.info (item)
		return int(item.decode("utf-8"))

def internet_on():
	try:
		urllib.request.urlopen('http://216.58.192.142', timeout=1)
		return True
	except urllib.request.URLError as err:
		return False

if isBoard():
	blink_led = BlinkLedThread("Led blinker")
	blink_led.start()
	check_network = CheckNetworkThread("Network checker")
	check_network.start()

def CheckNetwork(is_debug=False):
	if is_debug is False:
		return internet_on()

	if isBoard():
		global blink_led
		blink_led.SetLedPattern("STATE_POWERUP")
	# bbar = progressbar.ProgressBar(widgets=[progressbar.AnimatedMarker()], maxval=progressbar.UnknownLength).start()
	network_availbility = internet_on()
	while network_availbility is False:
		network_availbility = internet_on()
		time.sleep(1)
		# for i in range(30):
		# 	bbar.update(i)
		# 	time.sleep(0.1)
		logger.info ("Checking for internet: %s" % ("ok" if network_availbility is True else "not ok"))
	if isBoard():
		blink_led.SetLedPattern("STATE_ON_START_FINISHED")

def main():
	if useThread:
		logger.info("Init thread")
		stdoutAnalyzer = threading.Thread(target=StdOutAnalyzer)
		stdoutAnalyzer.start()
	else:
		logger.info ("Not use thread")

	if useThread:
		stdOutParam = std_out_buf
		stdErrParam = std_err_buf
	else:
		stdOutParam = sys.stdout
		stdErrParam = sys.stderr

	while True:
		CheckNetwork(True)
		logger.info ("Preparing to run")
		try:
			ggAssistCmd = sh.Command(os.environ.get("HOTWORD_PATH"))
			ggAssistCmd("--device_model_id",
						os.environ.get("DEVICE_MODEL_ID"),
						"--project_id",
						os.environ.get("PROJECT_ID"),
						_out=stdOutParam,
						_err=stdErrParam,
						_tty_out=True)
						# _bg=True)
			logger.info ("Going to wait")
			ggAssistCmd.wait()
		except:
			logger.info("App die, start again")

if __name__ == "__main__":
	main()

