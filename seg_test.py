import sys
import os, os.path
def seg_extract(in_file, out_file):
#    trs = open(in_file, 'r', encoding = 'utf-8')
    lines = in_file.readlines()
    in_file.close()
    seg = out_file
#    seg = open('out_file', 'w', encoding = 'utf-8')
    print(len(lines))
    lines_sp = []
    for x in range(len(lines)):
        cline = 's' + lines[x]
#        print('s' + cline)
#        while cline != '':
        if cline != '':
            cline = cline.replace('=', ' ')
            cline = cline.replace('\"', ' ')
            cline_sp = cline.split()
            speaker = ' '
#            print(cline_sp)
            if cline_sp[0] == "s<Turn":
#                print('turn----')
                for i in range(1, len(cline_sp)-1, 2):
                    if cline_sp[i] == 'speaker':
                        speaker = cline_sp[i+1]
#                        print(speaker)
                    elif cline_sp[i] == 'startTime':
                        start = float(cline_sp[i+1])
#                        print(str(start)) 
                    elif cline_sp[i] == 'endTime':
                        end = float(cline_sp[i+1])
#                        print(str(end)) 
                if speaker != ' ':
                    seg.write('Turn' + ', ' + speaker + ', ' + str(start) + ', ' + str(end)+ '\n')
                else: 
                    seg.write('Turn' + ',' + str(start) + ', ' + str(end)+ '\n')
            elif cline_sp[0] == "s<Sync":
#                print('sync----')
                time = float(cline_sp[2])
#                print(str(time)) 
                seg.write('Sync' + ', ' + str(time) + '\n')
            else:
                seg.write('')
            
#    seg.close()
    out_file = seg
    return

def compare_files(f1, f2):
#    f1=open(file1,"r", encoding = 'utf-8') 
#    f2=open(file2,"r", encoding = 'utf-8') 
    count = 0
    result = []
    for line1 in f1: 
        for line2 in f2: 
            if line1==line2: 
                print("SAME\n") 
            else: 
                result.append(line1)
                result.append(line2)
                count = count + 1
            break 
    f1.close() 
    f2.close()
    return(count, result)

def trs_seg_diff(file1, res1, file2, res2, cp):
    #trs = open("AT-010_lioksan20210608.trs", 'r', encoding = 'utf-8')
#    trs = open(sys.argv[1], 'r', encoding = 'utf-8')
    trs = open(file1, 'r', encoding = 'utf-8')
#    name = file1.split('\\')
#    seg_name = name
#    print(name)
    seg = open(res1, 'w+', encoding = 'utf-8')
    seg_extract(trs, seg)
    trs.close()
    # seg.close()
    trs1 = open(file2, 'r', encoding = 'utf-8')
#    name1 = file2.split('.')
#    trs1 = open(sys.argv[3], 'r', encoding = 'utf-8')
#    seg1 = open(sys.argv[4], 'w+', encoding = 'utf-8')
    seg1 = open(res2, 'w+', encoding = 'utf-8')
    seg_extract(trs1, seg1)
    trs1.close()
    # seg1.close()
    count, result = compare_files(seg, seg1)
#    f3 = open('result_AT_010.txt', 'w', encoding = 'utf-8')
    f3 = open(cp, 'w', encoding = 'utf-8')
#    print('diff1:' + name[0] + "_result.txt")
    f3.write(str(count)+'\n')
    for i in result:
        f3.write(i + '\n')
    f3.close()
    return(count)
#    if count == 0:
#        print('matched')

def main():
    path = os.getcwd()
#    print(path)
    ls = os.listdir(os.path.join(path,'trs_ty'))
#    print(ls)
#    path0 = 'I:\\working-area\\'
    f3 = open(os.path.join(path, 'seg_diff.csv'), 'w', encoding = 'utf-8')
    f3.write('file name, count' + '\n')
    for x in ls:
        print(x)
#        file01 = ".\\trs_ty\\" + x
        x_sp = x.split('.') 
        file01 = os.path.join(path, "trs_ty", x)
        res01 = os.path.join(path, 'res_ty', 'seg_' + x_sp[0] + '.txt')
        print(file01)
        file02 = os.path.join(path, "trs_com", x)
        res02 = os.path.join(path, 'res_com', 'seg_' + x_sp[0] + '.txt')
        print(file02)
        compare = os.path.join(path, 'res_ty', 'res_' + x_sp[0] + '.txt')
        count = trs_seg_diff(file01, res01, file02, res02, compare)
        f3.write(x + ',' + str(count) + '\n')

main()
