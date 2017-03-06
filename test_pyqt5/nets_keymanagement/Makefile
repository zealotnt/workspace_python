CASIGN_HOST_PATH				?= /home/zealot/workspace_sirius/secureROM/Host/casign/bin/linux
SESSION_BUILD_HOST_PATH			?= /home/zealot/workspace_sirius/secureROM/Host/session_build/bin/linux
TAGET_APP						?= key_management.py
QT5_LIB_PATH					?= "C:\Users\Zealot\AppData\Local\Programs\Python\Python35-32\Lib\site-packages\PyQt5\Qt\bin"

all: gen_gui gen_key

build:
	pyinstaller.exe -p $(QT5_LIB_PATH) $(TAGET_APP)

gen_key:
	python3 maxim_2_pem.py Casign/crk_ecdsa_angela_test.key private.pem

gen_gui:
	pyuic5 -x mainwindow.ui -o mainwindow_gui_auto.py

link_secure_folder:
	ln -fs $(CASIGN_HOST_PATH) Casign
	ln -fs $(SESSION_BUILD_HOST_PATH) session_build

clean:
	# Remove auto-gen folder
	rm -rf scp_out/
	rm -rf build/
	rm -rf dist/
	# Remove auto-gen files
	rm -f binary.s19
	rm -f ca_sign_build.ini
	rm -f session_build.ini
	rm -f maximtestcrk.key
	rm -f sb_script.txt
	rm -f bootloader.zip
	rm -f *.bin
	rm -f *.sig
	rm -f *.pem
	rm -f *.spec
	rm -f *.key
