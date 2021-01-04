import argparse
import numpy as np
import os
from prettytable import PrettyTable
import re

import pathedgeCount
import memRatio

app2abbr = {"bus.chio.wishmaster_1002.apk" : "BCW", "com.alfray.timeriffic_10905.apk" : "CAT", "F-Droid.apk" : "F-Droid", "hashengineering.groestlcoin.wallet_71107.apk" : "HGW", "nya.miku.wishmaster_54.apk" : "NMW", "org.fdroid.fdroid_1008000.apk" : "OFF", "org.gateshipone.odyssey_30.apk" : "OGO", "org.lumicall.android_190.apk" : "OLA", "org.yaxim.androidclient_53.apk" : "OYA", "com.github.axet.bookreader_375.apk" : "CGAB", "com.kanedias.vanilla.metadata_5.apk" : "CKVM", "org.secuso.privacyfriendlyweather_6.apk" : "OSP", "org.smssecure.smssecure_211.apk" : "OSS", "fr.gouv.etalab.mastodon_345.apk" : "FGEM", "com.genonbeta.TrebleShot_98.apk" : "CGT", "com.github.axet.callrecorder_219.apk" : "CGAC", "com.zeapo.pwdstore_10303.apk" : "CZP", "de.k3b.android.androFotoFinder_44.apk" : "DKAA", "org.kde.kdeconnect_tp_11350.apk" : "OKKT"}

group1 = ["bus.chio.wishmaster_1002.apk", "F-Droid.apk", "nya.miku.wishmaster_54.apk", "org.gateshipone.odyssey_30.apk", "org.yaxim.androidclient_53.apk", "com.alfray.timeriffic_10905.apk", "hashengineering.groestlcoin.wallet_71107.apk", "org.fdroid.fdroid_1008000.apk", "org.lumicall.android_190.apk"]
group2 = ["com.github.axet.bookreader_375.apk", "com.kanedias.vanilla.metadata_5.apk", "fr.gouv.etalab.mastodon_345.apk", "org.secuso.privacyfriendlyweather_6.apk", "org.smssecure.smssecure_211.apk"]
group3 = ["com.genonbeta.TrebleShot_98.apk", "com.github.axet.callrecorder_219.apk", "com.zeapo.pwdstore_10303.apk", "de.k3b.android.androFotoFinder_44.apk"]
group4 = ["org.kde.kdeconnect_tp_11350.apk"]

flowdroidTimeAvg = {}
flowdroidForwardPEAvg = {}
flowdroidBackwardPEAvg = {}
flowdroidMemoryAvg = {}
flowdroidTotalPEAvg = {}

runTimes = 5;
def extract_data(filePath, dataType, data, isDisk):
	valid = True
	app = ""
	targetData = 0
	for line in open(filePath):
		lineStrip = line.strip()
		if lineStrip.endswith("apk"):
			valid = True
			app = lineStrip
		if dataType == "dataFlowTime" and "Data flow solver took" in line:
			V = re.match(r'.*Data flow solver took (\d+) seconds.*', line)
			targetData = int(V.group(1))
		if dataType == "forwardPE" and "InPlaceInfoflow - IFDS problem with " in line:
			V = re.match(r'.*InPlaceInfoflow - IFDS problem with (\d+) forward and (\d+) backward edges.*', line)
			targetData = int(V.group(1))
		if dataType == "backwardPE" and "InPlaceInfoflow - IFDS problem with " in line:
			V = re.match(r'.*InPlaceInfoflow - IFDS problem with (\d+) forward and (\d+) backward edges.*', line)
			targetData = int(V.group(2))
		if dataType == "memory" and "Current memory consumption" in line:
			V = re.match(r'.*Current memory consumption: (\d+) MB.*', line)
			targetData = int(V.group(1))
		if dataType == "totalPE" and "InPlaceInfoflow - IFDS problem with " in line:
			V = re.match(r'.*InPlaceInfoflow - IFDS problem with (\d+) forward and (\d+) backward edges.*', line)
			targetData = int(V.group(1)) + int(V.group(2))
		if "Triggering memory warning" in line:
			if not isDisk:
				valid = False
		if "Timeout reached" in line:
			valid = False
		if "nextAPP" in line:
			if valid == True:
				if not targetData == 0:
					if app not in data:
						data[app] = []
					data[app].append(targetData)

def out_of_mem_or_timeout(d):
	for key, value in d.items():
		length = len(value)
		if (length != runTimes):
			print(str(runTimes-length) + "/" + str(runTimes) + " of " + key + " run out of memory or timeout")

def analysis_flowdroid():
	# run jar
	flowdroidDir = os.path.join(resultDir, "flowdroid")
	createNewDir(flowdroidDir)

	for i in range(runTimes):
		run_flowdroid(i, "flowdroid.jar", flowdroidDir)

	flowdroidTime = {}
	flowdroidForwardPE = {}
	flowdroidBackwardPE = {}
	flowdroidMemory = {}
	flowdroidTotalPE = {}
	for i in range(runTimes):
		flowdroidResult = os.path.join(os.path.join(flowdroidDir, str(i)), "result")
		extract_data(flowdroidResult, "dataFlowTime", flowdroidTime, False)
		extract_data(flowdroidResult, "forwardPE", flowdroidForwardPE, False)
		extract_data(flowdroidResult, "backwardPE", flowdroidBackwardPE, False)
		extract_data(flowdroidResult, "memory", flowdroidMemory, False)
		extract_data(flowdroidResult, "totalPE", flowdroidTotalPE, False)
	calculate_avg(flowdroidTime, flowdroidTimeAvg)
	calculate_avg(flowdroidForwardPE, flowdroidForwardPEAvg)
	calculate_avg(flowdroidBackwardPE, flowdroidBackwardPEAvg)
	calculate_avg(flowdroidMemory, flowdroidMemoryAvg)
	calculate_avg(flowdroidTotalPE, flowdroidTotalPEAvg)
	out_of_mem_or_timeout(flowdroidTime)
	print("\r\n")
	print("Table 2: Statistics of FlowDroid in analyzing 18 apps")
	table = PrettyTable(['app', 'Abbr', 'Mem(MB)', '#FPE', '#BPE', 'Time(s)'])
	table.add_row([app, app2abbr[app], flowdroidMemoryAvg[app], flowdroidForwardPEAvg[app], flowdroidBackwardPEAvg[app], flowdroidTimeAvg[app]])
	print(table)

# only hot edge
def only_hotedge():
	# run jar
	onlyHotedgeDir = os.path.join(resultDir, "onlyHotedgeDir")
	createNewDir(onlyHotedgeDir)

	for i in range(runTimes):
		run_flowdroid(i, "onlyHotedge.jar", onlyHotedgeDir)
	totalPE = {}
	totalPEAvg = {}
	time = {}
	timeAvg = {}
	memory = {}
	memoryAvg = {}
	for i in range(runTimes):
		onlyHotedgeResult = os.path.join(os.path.join(onlyHotedgeDir, str(i)), "result")
		extract_data(onlyHotedgeResult, "totalPE", totalPE, False)
		extract_data(onlyHotedgeResult, "memory", memory, False)
		extract_data(onlyHotedgeResult, "dataFlowTime", time, False)
	calculate_avg(totalPE, totalPEAvg)
	calculate_avg(memory, memoryAvg)
	calculate_avg(time, timeAvg)
	print("\r\n")
	print("Figure 6: The differences of run time performance and memory usages of applying hot edge optimization to FlowDroid")
	table = PrettyTable(['Abbr', 'FlowDroidTime', 'FlowDroidMemory', 'OnlyHotedgeTime', 'OnlyHotedgeMemory'])
	table.add_row([app2abbr[app],  flowdroidTimeAvg[app], flowdroidMemoryAvg[app], timeAvg[app], memoryAvg[app]])
	print(table)
	print("\r\n")
	print("Table 4: Number of computed path edges by only using hot edges")
	table2 = PrettyTable(['Abbr', '#FlowDroid', '#OnlyHotedge'])
	table2.add_row([app2abbr[app], flowdroidTotalPEAvg[app], totalPEAvg[app]])
	print(table2)

msTimeAvg = {}
mtTimeAvg = {}
sTimeAvg = {}
tTimeAvg = {}
writeRandom50Avg = {}
write70Avg = {}
writeWorklistAvg = {}
def analysis_disk():
	method_source()
	method_target()
	source()
	target()
	write_random_50()
	write_70()
	write_worklist()

	print("\r\n")
	print("Figure 5: Performance differences of DiskDroid against FlowDroid.")
	table3 = PrettyTable(['Abbr', 'FlowDroid', 'DiskDroid'])
	time1 = flowdroidTimeAvg[app] if app in flowdroidTimeAvg else "NULL"
	time2 = sTimeAvg[app] if app in sTimeAvg else "NULL"
	table3.add_row([app2abbr[app], time1, time2])
	print(table3)

	print("\r\n")
	print("Figure 7: Performance differences with different grouping schemes")
	table = PrettyTable(['Abbr', 'FlowDroid', 'Method&Source', 'Method&Target', 'Source', 'Target'])
	time1 = flowdroidTimeAvg[app] if app in flowdroidTimeAvg else "NULL"
	time2 = msTimeAvg[app] if app in msTimeAvg else "NULL"
	time3 = mtTimeAvg[app] if app in mtTimeAvg else "NULL"
	time4 = sTimeAvg[app] if app in sTimeAvg else "NULL"
	time5 = tTimeAvg[app] if app in tTimeAvg else "NULL"
	table.add_row([app2abbr[app], time1, time2, time3, time4, time5])
	print(table)

	print("\r\n")
	print("Figure 8: Performance differences using different swapping policies.")
	table2 = PrettyTable(['Abbr', 'FlowDroid', 'Default 50%', 'Default 70%', 'Default 0%', 'Random 50%'])
	time1 = flowdroidTimeAvg[app] if app in flowdroidTimeAvg else "NULL" 
	time2 = sTimeAvg[app] if app in sTimeAvg else "NULL"
	time3 = write70Avg[app] if app in write70Avg else "NULL"
	time4 = writeWorklistAvg[app] if app in writeWorklistAvg else "NULL"
	time5 = writeRandom50Avg[app] if app in writeRandom50Avg else "NULL"
	table2.add_row([app2abbr[app], time1, time2, time3, time4, time5])
	print(table2)

def method_source():
	msTime = {}
	msDir = os.path.join(resultDir, "method-source")
	createNewDir(msDir)

	for i in range(runTimes):
		run_disk('ms.jar', i, msDir)
	for i in range(runTimes):
		msResult = os.path.join(os.path.join(msDir, str(i)), "result")
		extract_data(msResult, "dataFlowTime", msTime, True)
	calculate_avg(msTime, msTimeAvg)
def method_target():
	mtTime = {}
	mtDir = os.path.join(resultDir, "method-target")
	createNewDir(mtDir)

	for i in range(runTimes):
		run_disk('mt.jar', i, mtDir)
	for i in range(runTimes):
		mtResult = os.path.join(os.path.join(mtDir, str(i)), "result")
		extract_data(mtResult, "dataFlowTime", mtTime, True)
	calculate_avg(mtTime, mtTimeAvg)
def source():
	sTime = {}
	sDir = os.path.join(resultDir, "source")
	createNewDir(sDir)

	for i in range(runTimes):
		run_disk('s.jar', i, sDir)
	for i in range(runTimes):
		sResult = os.path.join(os.path.join(sDir, str(i)), "result")
		extract_data(sResult, "dataFlowTime", sTime, True)
	calculate_avg(sTime, sTimeAvg)
def target():
	tTime = {}
	tDir = os.path.join(resultDir, "target")
	createNewDir(tDir)

	for i in range(runTimes):
		run_disk('t.jar', i, tDir)
	for i in range(runTimes):
		tResult = os.path.join(os.path.join(tDir, str(i)), "result")
		extract_data(tResult, "dataFlowTime", tTime, True)
	calculate_avg(tTime, tTimeAvg)
def write_random_50():
	writeRandom50 = {}
	writeRandom50Dir = os.path.join(resultDir, "writeRandom50")
	createNewDir(writeRandom50Dir)

	for i in range(runTimes):
		run_disk('s-random.jar', i, writeRandom50Dir)
	for i in range(runTimes):
		writeRandom50Result = os.path.join(os.path.join(writeRandom50Dir, str(i)), "result")
		extract_data(writeRandom50Result, "dataFlowTime", writeRandom50, True)
	calculate_avg(writeRandom50, writeRandom50Avg)
def write_70():
	write70 = {}
	write70Dir = os.path.join(resultDir, "write70")
	createNewDir(write70Dir)

	for i in range(runTimes):
		run_disk('s-write70.jar', i, write70Dir)
	for i in range(runTimes):
		write70Result = os.path.join(os.path.join(write70Dir, str(i)), "result")
		extract_data(write70Result, "dataFlowTime", write70, True)
	calculate_avg(write70, write70Avg)
def write_worklist():
	writeWorklist = {}
	writeWorklistDir = os.path.join(resultDir, "writeWorklist")
	createNewDir(writeWorklistDir)

	for i in range(runTimes):
		run_disk('s-onlyWorklist.jar', i, writeWorklistDir)
	for i in range(runTimes):
		writeWorklistResult = os.path.join(os.path.join(writeWorklistDir, str(i)), "result")
		extract_data(writeWorklistResult, "dataFlowTime", writeWorklist, True)
	calculate_avg(writeWorklist, writeWorklistAvg)

def calculate_avg(originDict, result):
	for key, value in originDict.items():
		result[key] = round(np.mean(value))

def run_disk(jarFile, times, outputParent):
	outputDir = os.path.join(outputParent, str(times))
	if not os.path.isdir(outputDir):
		os.mkdir(outputDir)
	outputFile = os.path.join(outputDir, "result")
	cmd = "java -noverify -Xmx10g -Xms10g -jar lib/" + jarFile + " -a " + appPath + " -s SourcesAndSinks.txt -t EasyTaintWrapperSource.txt -p platforms -dt 10800 >> " + outputFile + " 2>&1"
	#print(cmd)
	os.system("echo " + app + " >> " + outputFile)
	os.system(cmd)
	os.system("echo nextAPP >> " + outputFile)
	os.system("rm -rf " + appPath + ".disk")

def run_flowdroid(times, jarFile, outputParent):
	outputDir = os.path.join(outputParent, str(times))
	if not os.path.isdir(outputDir):
		os.mkdir(outputDir)
	outputFile = os.path.join(outputDir, "result")
	cmd = ""
	if app in group1:
		cmd = "java -noverify -Xmx20g -Xms20g -jar lib/" + jarFile + " -a " + appPath + " -s SourcesAndSinks.txt -t EasyTaintWrapperSource.txt -p platforms -dt 10800 >> " + outputFile + " 2>&1"
	elif app in group2:
		cmd = "java -noverify -Xmx30g -Xms30g -jar lib/" + jarFile + " -a " + appPath + " -s SourcesAndSinks.txt -t EasyTaintWrapperSource.txt -p platforms -dt 10800 >> " + outputFile + " 2>&1"
	elif app in group3:
		cmd = "java -noverify -Xmx60g -Xms60g -jar lib/" + jarFile + " -a " + appPath + " -s SourcesAndSinks.txt -t EasyTaintWrapperSource.txt -p platforms -dt 10800 >> " + outputFile + " 2>&1"
	elif app in group4:
		cmd = "java -noverify -Xmx128g -Xms128g -jar lib/" + jarFile + " -a " + appPath + " -s SourcesAndSinks.txt -t EasyTaintWrapperSource.txt -p platforms -dt 10800 >> " + outputFile + " 2>&1"
	#print(cmd)
	os.system("echo " + app + " >> " + outputFile)
	os.system(cmd)
	os.system("echo nextAPP >> " + outputFile)

def run_flowdroid_60(times, jarFile, outputParent):
	outputDir = os.path.join(outputParent, str(times))
	if not os.path.isdir(outputDir):
		os.mkdir(outputDir)
	outputFile = os.path.join(outputDir, "result")
	cmd = "java -noverify -Xmx60g -Xms60g -jar lib/" + jarFile + " -a " + appPath + " -s SourcesAndSinks.txt -t EasyTaintWrapperSource.txt -p platforms -dt 10800 >> " + outputFile + " 2>&1"
	#print(cmd)
	os.system("echo " + app + " >> " + outputFile)
	os.system(cmd)
	os.system("echo nextAPP >> " + outputFile)

def createNewDir(dirPath):
	if os.path.isdir(dirPath):
		os.system("rm -rf " + dirPath)
	os.mkdir(dirPath)

def mem_ratio():
	memRatioDir = os.path.join(resultDir, "memRatio")
	createNewDir(memRatioDir)

	run_flowdroid_60(0, 'memRatio.jar', memRatioDir)
	result = os.path.join(os.path.join(memRatioDir, "0"), "result")
	memRatio.collect_mem(result)

def edge_access_num():
	print("\r\n")
	print("Figure 4: Distribution of pass edge access number for CGAB")
	cmd = "java -noverify -Xmx60g -Xms60g -jar lib/PECount.jar -a " + appPath +" -s SourcesAndSinks.txt -t EasyTaintWrapperSource.txt -p platforms -dt 10800 > result/accessNum 2>&1"
	#print(cmd)
	os.system(cmd)
	pathedgeCount.distribution("result/accessNum")

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='DiskDroid')
	parser.add_argument('-t', help='Target path')
	parser.add_argument('-k', default='ALL', help='Analaysis kind, default ALL')
	parser.add_argument('-times', type=int, default=1, help='Analaysis times for each benchmark')
	args = parser.parse_args()
	appPath = args.t
	runTimes = args.times

	tmpDir = "result-single"
	if not os.path.isdir(tmpDir):
		os.mkdir(tmpDir)

	app = appPath[appPath.rindex('/') + 1 : len(appPath)]
	resultDir = tmpDir + "/" + app
	if not os.path.isdir(resultDir):
		os.mkdir(resultDir)

	if args.k == 'ALL':
		analysis_flowdroid()
		only_hotedge()
		analysis_disk()
	elif args.k == 'flowdroid':
		analysis_flowdroid()
	elif args.k == 'memoryUsage':
		mem_ratio()
	elif args.k == 'pathedgeAccessNum':
		edge_access_num()
	elif args.k == 'onlyHotEdge':
		only_hotedge()
	elif args.k == 'sourceGroup':
		source()
		dt = sTimeAvg[app] if app in sTimeAvg else "NULL"
		print('analysis time : ' + str(dt))
	elif args.k == 'methodSourceGroup':
		method_source()
		dt = msTimeAvg[app] if app in msTimeAvg else "NULL"
		print('analysis time : ' + str(dt))
	elif args.k == 'methodTargetGroup':
		method_target()
		dt = mtTimeAvg[app] if app in mtTimeAvg else "NULL"
		print('analysis time : ' + str(dt))
	elif args.k == 'targetGroup':
		target()
		dt = tTimeAvg[app] if app in tTimeAvg else "NULL"
		print('analysis time : ' + str(dt))
	elif args.k == 'Random_50':
		write_random_50()
		dt = writeRandom50Avg[app] if app in writeRandom50Avg else "NULL"
		print('analysis time : ' + str(dt))
	elif args.k == 'Default_70':
		write_70()
		dt = write70Avg[app] if app in write70Avg else "NULL"
		print('analysis time : ' + str(dt))
	elif args.k == 'Default_0':
		write_worklist()
		dt = writeWorklistAvg[app] if app in writeWorklistAvg else "NULL"
		print('analysis time : ' + str(dt))


