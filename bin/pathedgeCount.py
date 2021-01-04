import sys
from prettytable import PrettyTable

def distribution(targetFile):
	total = 0
	time1 = 0
	between1and10 = 0
	between10and100 = 0
	morethan100 = 0
	for line in open(targetFile):
		if "backward count ==> " in line:
			total = total + 1
			tmp = int(line.strip().split(" ==> ")[1])
			if tmp == 1:
				time1 = time1 + 1
			elif tmp < 10:
				between1and10 = between1and10 + 1
			elif tmp < 100:
				between10and100 = between10and100 + 1
			else:
				morethan100 = morethan100 + 1	
	print("total\t1\t(1,10)\t[10,100)\t>=100")
	table = PrettyTable(['total', '1', '(1,10)', '[10,100)', '>=100'])
	table.add_row([total, time1, between1and10, between10and100, morethan100])
	print(table)
if __name__ == '__main__':
	distribution(sys.argv[1])
