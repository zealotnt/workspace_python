#!/usr/bin/python
import os
import platform
import re
import subprocess
import Tkinter as tk
import tkMessageBox as mbox
from ttk import Frame, Button, Style, Entry
import inspect
import thread
import signal
import time
import glob
import serial


def serial_scan():
	"""
	Return a name list of available serial ports
	"""

	available = []

	if os.name == 'posix':
		available = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
	else:
		for i in range(256):
			try:
				s = serial.Serial(i)
				available.append(s.portstr)
				s.close()   # explicit close 'cause of delayed GC in java
			except serial.SerialException:
				pass
	return available

CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

ABOUT_DIALOG = """
Bus Terminal Test App

STYL Solutions Pte. Ltd.
81 Ubi Avenue 4 #05-07 UB.One Singapore 408830
Tel: +65-66948059 Fax: +65-66948060
The Rep. office of STYL Solutions Pte Ltd in Hcmc
109 Luong Dinh Cua, Binh An Ward, District 2, Hcmc, Vietnam
Tel: +84 8 62917497 Fax: +84 8 62917498
"""

TITLE_FONT = ("Helvetica", 18, "bold")
BTN_WIDTH = 20

# ENABLE_ARGUMENT = False
# ZEBRA_SCANNER_APP = "/home/root/post/ledindicator 1 5"
# WIFI_TEST_APP = "/home/root/post/ledindicator 2 5"
# GPS_3G_TEST_APP = "/home/root/post/ledindicator 3 5"
# CEPAS_TEST_APP = "/home/root/post/ledindicator 4 5"

ENABLE_ARGUMENT = True
RUN_SCRIPT = ""
ZEBRA_SCANNER_APP = "/home/root/busterminal_demo/mlsScaner"
WIFI_TEST_APP = "/home/root/busterminal_demo/mlsNetWorkClient"
GPS_3G_TEST_APP = "/home/root/busterminal_demo/BusTerminal"
WIFI_DOWN = "/sbin/ifconfig eth0 down"
CEPAS_TEST_APP = "/home/root/busterminal_demo/CEPASReader"

class SerialPort():
	def __init__(self):
		self.isConnected = False

	def Connect(self, port_name):
		self._port = serial.Serial(port=port_name, baudrate=9600, timeout=0.1)
		if self._port.isOpen() == True:
			self.isConnected = True

	def Write(self, data):
		self._port.write(data)

# serial_port = serial.Serial(port="COM46", baudrate=9600, timeout=0.1)
serial_port = SerialPort()

def GetApplicationName(argument):
	result = re.findall(r'/(\w+)[\s\r\n$]', argument)
	if len(result) == 0:
		result = re.findall(r'/(\w+)$', argument)
		return result[0]
	return result[0]

def KillApplication(name):
	return

def KillAllApp():
	KillApplication(GetApplicationName(ZEBRA_SCANNER_APP))
	KillApplication(GetApplicationName(WIFI_TEST_APP))
	KillApplication(GetApplicationName(GPS_3G_TEST_APP))
	KillApplication(GetApplicationName(CEPAS_TEST_APP))

def RunApplication(command):
	return

class SshSession():
	def __init__(self):
		self.running = False

	def StopSshSession(self):
		if self.running == True:
			self.pSsh.terminate()
			self.pSsh.kill()
			KillApplication(self._last_application)
			self.running = False

	def CallSshScript(self, argument):
		if argument == "":
			mbox.showerror("Error", "Empty ssh argument call")
			return
		self.running = True
		# os.system("echo y | " + CURRENT_DIR + "\plink.exe -ssh -2 -pw 123 root@192.168.100.15 " + argument);
		self.pSsh = RunApplication(argument)
		self._last_application = GetApplicationName(self.app_name)
		output, err = self.pSsh.communicate()
		print "plink end !!! with output: "
		print output

	def CreateSshSession(self, argument, app_name):
		# self.app_name = app_name
		# thread.start_new_thread(self.CallSshScript, (argument, ))
		serial_port.Write(argument + " \r\n")

ssh_session = SshSession()

def check_connection(ping_result):
	result = re.findall(r'(unreachable)', ping_result)
	if len(result) != 0:
		return False

	result = re.findall(r'\((\d+)\% loss\)', ping_result)
	lost_percent = result[0]
	if lost_percent == '0':
		return True
	return False

def test_connection(host_ip):
	"""
	Returns True if host responds to a ping request
	"""
	return

class StartPage(Frame):
	_title = "Bus Terminal Demo App"
	def __init__(self, parent, controller):
		Frame.__init__(self, parent)
		self.controller = controller
		self.parent = parent

		Style().configure("TButton", padding=(0, 5, 0, 5), font='serif 10')

		self.columnconfigure(0, pad=10)
		self.columnconfigure(1, pad=10)

		self.rowconfigure(0, pad=10)
		self.rowconfigure(1, pad=10)
		self.rowconfigure(2, pad=10)

		self.btn_wifi = Button(self,
			text="Wifi Connection Demo",
			command=lambda: controller.show_frame("Test_Wifi"), width=BTN_WIDTH)
		self.btn_wifi.grid(row=1, column=0)
		# self.btn_wifi.config(height=BTN_HEIGHT, width=BTN_WIDTH)

		self.btn_gps_3g = Button(self,
			text="3G + GPS Demo",
			command=lambda: controller.show_frame("Test_GPS3G"), width=BTN_WIDTH)
		self.btn_gps_3g.grid(row=1, column=1)

		self.btn_cepas = Button(self,
			text="Cepas Reader Demo",
			command=lambda: controller.show_frame("Test_Cepas"), width=BTN_WIDTH)
		self.btn_cepas.grid(row=2, column=0)

		self.btn_zebra_scanner = Button(self,
			text="Zebra Scanner Demo",
			command=lambda: controller.show_frame("Test_ZebraScanner"), width=BTN_WIDTH)
		self.btn_zebra_scanner.grid(row=2, column=1)

		self.pack()

	def _enable_test(self):
		self.btn_wifi.config(state="normal")
		self.btn_gps_3g.config(state="normal")
		self.btn_cepas.config(state="normal")
		self.btn_zebra_scanner.config(state="normal")

	def _disable_test(self):
		self.btn_wifi.config(state=tk.DISABLED)
		self.btn_gps_3g.config(state=tk.DISABLED)
		self.btn_cepas.config(state=tk.DISABLED)
		self.btn_zebra_scanner.config(state=tk.DISABLED)

class Test_ZebraScanner(tk.Frame):
	_title = "Zebra Scanner Demo"
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller

		label = tk.Label(self, text=self._title, font=TITLE_FONT)
		label.pack(side="top", fill="x", pady=10)

		btn_exit = tk.Button(self, text="Back",
						   command=self.OnClose)
		btn_exit.pack(side=tk.RIGHT, padx=5, pady=5)

		# btn_stop = tk.Button(self, text="Stop",
		# 				   command=lambda: controller.show_frame("StartPage"))
		# btn_stop.pack(side=tk.RIGHT, padx=5, pady=5)

		self.btn_test = tk.Button(self, text="Scan", command=self.ZebraScannerTest)
		self.btn_test.pack(side=tk.RIGHT, padx=5, pady=5)
	def OnClose(self):
		self.btn_test.config(state=tk.NORMAL)
		self.controller.show_frame("StartPage")

	def ZebraScannerTest(self):
		print "ZebraScannerTest"
		self.btn_test.config(state=tk.DISABLED)
		KillApplication(GetApplicationName(ZEBRA_SCANNER_APP))
		ssh_session.CreateSshSession(RUN_SCRIPT + ZEBRA_SCANNER_APP, ZEBRA_SCANNER_APP)
		self.btn_test.config(state=tk.NORMAL)

class Test_Wifi(tk.Frame):
	_title = "Wifi Demo"
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller

		label = tk.Label(self, text=self._title, font=TITLE_FONT)
		label.pack(side="top", fill="x", pady=10)

		frame_ssid = tk.Frame(self)
		frame_ssid.pack(fill=tk.X)
		lbl_ssid = tk.Label(frame_ssid, text="ssid", width=6)
		lbl_ssid.pack(side=tk.LEFT, padx=5, pady=5)
		self.entry_ssid = Entry(frame_ssid)
		self.entry_ssid.pack(fill=tk.X, padx=5, expand=True)

		frame_password = tk.Frame(self)
		frame_password.pack(fill=tk.X)
		lbl_password = tk.Label(frame_password, text="password", width=6)
		lbl_password.pack(side=tk.LEFT, padx=5, pady=5)
		self.entry_password = Entry(frame_password)
		self.entry_password.pack(fill=tk.X, padx=5, expand=True)

		frame_url = tk.Frame(self)
		frame_url.pack(fill=tk.X)
		lbl_url = tk.Label(frame_url, text="url", width=6)
		lbl_url.pack(side=tk.LEFT, padx=5, pady=5)
		self.entry_url = Entry(frame_url)
		self.entry_url.insert(tk.END, 'google.com')
		self.entry_url.pack(fill=tk.X, padx=5, expand=True)

		btn_exit = tk.Button(self, text="Back",
						   command=self.OnClose)
		btn_exit.pack(side=tk.RIGHT, padx=5, pady=5)

		self.btn_test = tk.Button(self, text="Run",
						   command=self.WifiTest)
		self.btn_test.pack(side=tk.RIGHT, padx=5, pady=5)

	def OnClose(self):
		self.btn_test.config(state=tk.NORMAL)
		self.controller.show_frame("StartPage")

	def WifiTest(self):
		if self.entry_ssid.get() == "":
			mbox.showerror("Error", "ssid should not be blank")
			return
		if self.entry_password.get() == "":
			mbox.showerror("Error", "password should not be blank")
			return
		if self.entry_url.get() == "":
			mbox.showerror("Error", "url should not be blank")
			return

		App_Argument = ""
		if ENABLE_ARGUMENT == True:
			App_Argument += " -t wifi -s " + self.entry_ssid.get() + \
						" -p " + self.entry_password.get() + \
						" -l " + self.entry_url.get()
		print RUN_SCRIPT + WIFI_TEST_APP + App_Argument

		ssh_session.CreateSshSession(RUN_SCRIPT + WIFI_TEST_APP + App_Argument, WIFI_TEST_APP)
		self.btn_test.config(state=tk.DISABLED)

class Test_GPS3G(tk.Frame):
	_title = "GPS + 3G Demo"
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller

		label = tk.Label(self, text=self._title, font=TITLE_FONT)
		label.pack(side="top", fill="x", pady=10)

		frame_apn = tk.Frame(self)
		frame_apn.pack(fill=tk.X)
		lbl_apn = tk.Label(frame_apn, text="apn", width=8)
		lbl_apn.pack(side=tk.LEFT, padx=5, pady=5)
		self.entry_apn = Entry(frame_apn)
		self.entry_apn.insert(tk.END, 'internet')
		self.entry_apn.pack(fill=tk.X, padx=5, expand=True)

		frame_username = tk.Frame(self)
		frame_username.pack(fill=tk.X)
		lbl_username = tk.Label(frame_username, text="username", width=8)
		lbl_username.pack(side=tk.LEFT, padx=5, pady=5)
		self.entry_username = Entry(frame_username)
		self.entry_username.pack(fill=tk.X, padx=5, expand=True)

		frame_password = tk.Frame(self)
		frame_password.pack(fill=tk.X)
		lbl_password = tk.Label(frame_password, text="password", width=8)
		lbl_password.pack(side=tk.LEFT, padx=5, pady=5)
		self.entry_password = Entry(frame_password)
		self.entry_password.pack(fill=tk.X, padx=5, expand=True)

		frame_dial_number = tk.Frame(self)
		frame_dial_number.pack(fill=tk.X)
		lbl_dial_number = tk.Label(frame_dial_number, text="dial_number", width=8)
		lbl_dial_number.pack(side=tk.LEFT, padx=5, pady=5)
		self.entry_dial_number = Entry(frame_dial_number)
		self.entry_dial_number.insert(tk.END, '*99#')
		self.entry_dial_number.pack(fill=tk.X, padx=5, expand=True)

		btn_exit = tk.Button(self, text="Back",
						   command=self.OnClose)
		btn_exit.pack(side=tk.RIGHT, padx=5, pady=5)

		self.btn_test = tk.Button(self, text="Run",
						   command=self.GPS3GTest)
		self.btn_test.pack(side=tk.RIGHT, padx=5, pady=5)

	def OnClose(self):
		self.btn_test.config(state=tk.NORMAL)
		self.controller.show_frame("StartPage")

	def GPS3GTest(self):
		if self.entry_apn.get() == "":
			mbox.showerror("Error", "apn should not be blank")
			return

		App_Argument = ""
		if ENABLE_ARGUMENT == True:
			App_Argument += " -a " + self.entry_apn.get() + \
						" -d " + self.entry_dial_number.get()
			if len(self.entry_username.get()) > 0:
				App_Argument += " -u " + self.entry_username.get()
			if len(self.entry_password.get()) > 0:
				App_Argument += " -p " + self.entry_password.get()
		print RUN_SCRIPT + GPS_3G_TEST_APP + App_Argument

		ssh_session.CreateSshSession(RUN_SCRIPT + WIFI_DOWN, WIFI_DOWN)
		time.sleep(2)
		ssh_session.CreateSshSession(RUN_SCRIPT + GPS_3G_TEST_APP + App_Argument, GPS_3G_TEST_APP)
		self.btn_test.config(state=tk.DISABLED)

class Test_Cepas(tk.Frame):
	_title = "Cepas reader Demo"
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller

		label = tk.Label(self, text=self._title, font=TITLE_FONT)
		label.pack(side="top", fill="x", pady=10)

		btn_exit = tk.Button(self, text="Back",
						   command=self.OnClose)
		btn_exit.pack(side=tk.RIGHT, padx=5, pady=5)

		self.btn_test = tk.Button(self, text="Run",
						   command=self.CepasTest)
		self.btn_test.pack(side=tk.RIGHT, padx=5, pady=5)

	def OnClose(self):
		self.btn_test.config(state=tk.NORMAL)
		self.controller.show_frame("StartPage")

	def CepasTest(self):
		print "CepasTest"
		ssh_session.CreateSshSession(RUN_SCRIPT + CEPAS_TEST_APP, CEPAS_TEST_APP)
		self.btn_test.config(state=tk.DISABLED)

class UI(tk.Tk):
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)

		# the container is where we'll stack a bunch of frames
		# on top of each other, then the one we want visible
		# will be raised above the others
		container = Frame(self)
		container.pack(side="top", fill="both", expand=True)
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)

		menubar = tk.Menu(container)
		self.config(menu=menubar)
		fileMenu = tk.Menu(menubar, tearoff=False)
		fileMenu.add_command(label="Test Connect", command=self.TestConnection)
		fileMenu.add_command(label="Exit", command=self.onExit)
		menubar.add_cascade(label="Connect", menu=fileMenu)

		aboutMenu = tk.Menu(menubar, tearoff=False)
		aboutMenu.add_command(label="About", command=self.About)
		menubar.add_cascade(label="Help", menu=aboutMenu)

		self.frames = {}
		self.titles = {}
		for F in (StartPage, Test_ZebraScanner, Test_Wifi, Test_GPS3G, Test_Cepas):
			page_name = F.__name__
			title_name = F._title
			frame = F(parent=container, controller=self)
			self.frames[page_name] = frame
			self.titles[page_name] = title_name

			# put all of the pages in the same location;
			# the one on the top of the stacking order
			# will be the one that is visible.
			frame.grid(row=0, column=0, sticky="nsew")

		frame = self.show_frame("StartPage")
		frame._disable_test()

	def About(self):
		mbox.showinfo("About", ABOUT_DIALOG)

	def onExit(self):
		self.quit()

	def TestConnection(self):
		self.com_chooser_windows = tk.Toplevel(self)
		self.com_chooser_windows.wm_title("Comport chooser")
		self.com_chooser_windows.wm_attributes("-topmost", True)
		self.com_chooser_windows.focus_force()

		self.com_chooser_windows.grid_rowconfigure(0, weight=1)
		self.com_chooser_windows.grid_columnconfigure(0, weight=1)

		frame_comport = tk.Frame(self.com_chooser_windows)
		frame_comport.pack(fill=tk.X)

		serial_list = serial_scan()
		if serial_list == []:
			serial_list.append(r'<no comport available>')

		self.serial_value = tk.StringVar(self.com_chooser_windows)
		self.serial_value.set("")

		lbl_ports = tk.Label(frame_comport, text="Ports", width=8)
		lbl_ports.pack(side=tk.LEFT, padx=5, pady=5)
		dropdown_ports = tk.OptionMenu(frame_comport,
									self.serial_value,
									*serial_list,
									command=self.ComConnectSelectEvent)
		dropdown_ports.pack()

		btn_serial_exit = tk.Button(self.com_chooser_windows, text="Back",
							command=self.SerialOnClose)
		btn_serial_exit.pack(side=tk.RIGHT, padx=5, pady=5)

		self.btn_serial_connect = tk.Button(self.com_chooser_windows, text="Connect",
							command=self.SerialConnect)
		self.btn_serial_connect.pack(side=tk.RIGHT, padx=5, pady=5)
		self.btn_serial_connect.config(state=tk.DISABLED)

	def ComConnectSelectEvent(self, event):
		if self.serial_value.get() == r'<no comport available>':
			self.serial_value.set("")
			return

		self.btn_serial_connect.config(state=tk.NORMAL)

	def SerialConnect(self):
		serial_port.Connect(self.serial_value.get())
		if serial_port.isConnected == True:
			mbox.showinfo("Connection Result", "Connect ok")
			frame = self.show_frame("StartPage")
			frame._enable_test()
			self.com_chooser_windows.destroy()
		else:
			mbox.showerror("Connection Result", "Connect fail, please try again !!!")

	def SerialOnClose(self):
		self.com_chooser_windows.destroy()

	def show_frame(self, page_name):
		'''Show a frame for the given page name'''
		ssh_session.StopSshSession()
		frame = self.frames[page_name]
		self.title(self.titles[page_name])
		frame.tkraise()
		return frame

app = UI()
app.mainloop()
