import sys
import re
from prettytable import PrettyTable

def collect_mem(resultFile):
	app2abbr = {"bus.chio.wishmaster_1002.apk" : "BCW", "com.alfray.timeriffic_10905.apk" : "CAT", "F-Droid.apk" : "F-Droid", "hashengineering.groestlcoin.wallet_71107.apk" : "HGW", "nya.miku.wishmaster_54.apk" : "NMW", "org.fdroid.fdroid_1008000.apk" : "OFF", "org.gateshipone.odyssey_30.apk" : "OGO", "org.lumicall.android_190.apk" : "OLA", "org.yaxim.androidclient_53.apk" : "OYA", "com.github.axet.bookreader_375.apk" : "CGAB", "com.kanedias.vanilla.metadata_5.apk" : "CKVM", "org.secuso.privacyfriendlyweather_6.apk" : "OSP", "org.smssecure.smssecure_211.apk" : "OSS", "fr.gouv.etalab.mastodon_345.apk" : "FGEM", "com.genonbeta.TrebleShot_98.apk" : "CGT", "com.github.axet.callrecorder_219.apk" : "CGAC", "com.zeapo.pwdstore_10303.apk" : "CZP", "de.k3b.android.androFotoFinder_44.apk" : "DKAA"}
	app = ""
	total = 0
	pe = 0
	incoming = 0
	endSum = 0
	print("------------------------------------------------------------------------\r\n")
	print("Figure 2: The memory usages of different data structures, PathEdge, Incoming, and EndSum")
	table = PrettyTable(['app', 'Abbr', 'Total', 'PathEdge', 'Incoming', 'EndSum'])
	for line in open(resultFile):
		lineStrip = line.strip()
		if lineStrip.endswith("apk"):
			app = lineStrip
		if "Current memory consumption:" in line:
			total = int(re.findall(r".*Current memory consumption: (.+?) MB", lineStrip)[0])
		if "before clean up jumpFunctions: " in line:
			beforePE = int(re.findall(r".*before clean up jumpFunctions: (.+?) MB", lineStrip)[0])
		if "after clean up jumpFunctions: " in line:
			afterPE = int(re.findall(r".*after clean up jumpFunctions: (.+?) MB", lineStrip)[0])
			pe = pe + int(beforePE - afterPE)
		if "after clean up incoming: " in line:
			afterIncoming = int(re.findall(r".*after clean up incoming: (.+?) MB", lineStrip)[0])
			incoming = incoming + int(afterPE - afterIncoming)
		if "after clean up endSummary: " in line:
			afterEndSum = int(re.findall(r".*after clean up endSummary: (.+?) MB", lineStrip)[0])
			endSum = endSum + int(afterIncoming - afterEndSum)
		if "nextAPP" in line:
			table.add_row([app, app2abbr[app], total, pe, incoming, endSum])
			total = 0
			pe = 0
			incoming = 0
			endSum = 0
	print(table)
if __name__ == '__main__':
	collect_mem(sys.argv[1])

