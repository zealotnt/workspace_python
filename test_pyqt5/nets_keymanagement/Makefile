all: gen_gui link_secure_folder

gen_gui:
	pyuic5 -x mainwindow.ui -o mainwindow_gui_auto.py

link_secure_folder:
	ln -s /home/zealot/workspace_sirius/secureROM/Host/casign/bin/linux Casign
	ln -s /home/zealot/workspace_sirius/secureROM/Host/session_build/bin/linux session_build

clean:
	rm -f binary.s19
	rm -f ca_sign_build.ini
	rm -f session_build.ini
	rm -f maximtestcrk.key
	rm -f sb_script.txt
	rm -rf scp_out
