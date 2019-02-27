
# coding: utf-8

def line2list(data_string):
    line = re.split(r'[,\s]+',data_string)
    if '' in line:
        line.remove('')
    else:
        pass
    for i in range(len(line)):
        line[i] = float(line[i])

    return line

joint = ["index", "上半身", "下半身", "首", "頭", "左肩", "左腕", "左ひじ","右肩", "右腕", "右ひじ"]
joints = []
for item in joint:
    if item == 'index':
        joints.append(item)
    else:
    	joints.append(item+'_x')
    	joints.append(item+'_y')
    	joints.append(item+'_z')

data = []
with open(input, 'r') as txtfile:
    cnt = 0
    for line in txtfile:
        line = line2list(line)
        line.insert(0, cnt)
        data.append(line)
        cnt += 1
data = np.array(data)
with open(output, 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(joints)
    writer.writerows(data)
print('saved')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='generate motion file from roadmap')
    parser.add_argument('-i', '--input', dest='input', type=str,
                        help='mmd file path')
    parser.add_argument('-o', '--output', dest='output', type=str,
                        help='ibuki file path')
    args = parser.parse_args()
    input = args.input
    output = args.output
