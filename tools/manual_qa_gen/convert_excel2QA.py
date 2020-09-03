import xlrd
import base64
import binascii

def genA(x):
    ret = []
    sl = x.sheet_by_name('lines')
    dl = ([sl.row_values(i) for i in range(sl.nrows)])
    text = '\n'.join([','.join(["0" if e=="" else e for e in l]) for l in dl])
    ret.append("A1")
    ret.append("SIZE {}X{}".format(sl.ncols, sl.nrows))
    ret.append(text)

    ret.append("")

    blockdic = {}
    sp = x.sheet_by_name('blockpos')
    dp = ([sp.row_values(i) for i in range(sp.nrows)])
    for j,drow in enumerate(dp):
        for i,val in enumerate(drow):
            if val != "":
                num = int(val)
                blockdic[num] = "BLOCK#{} @({},{})".format(num, i,j)
    for i in range(1,len(blockdic)+1):
        ret.append(blockdic[i])
    return "\n".join(ret)

def genQ(x):
    ret = []
    sp = x.sheet_by_name('blockpos')
    dp = ([sp.row_values(i) for i in range(sp.nrows)])

    def findval(val, posx, posy):
        shapedic = {
                '1000000000000000': ("1X1", (('+'),),         ), # "M"
                '1111000000000000': ("4X1", (('++++'),),      ), # "I"
                '1000100010001000': ("1X4", ('+','+','+','+'),), # "I"
                '1100110000000000': ("2X2", ('++','++'),      ), # "O"
                '0100111000000000': ("3X2", ('0+0','+++'),    ), # "T"
                '1000110010000000': ("2X3", ('+0','++','+0'), ), # "T"
                '1110010000000000': ("3X2", ('+++','0+0'),    ), # "T"
                '0100110001000000': ("2X3", ('0+','++','0+'), ), # "T"
                '0100010011000000': ("2X3", ('0+','0+','++'), ), # "J"
                '1000111000000000': ("3X2", ('+00','+++'),    ), # "J"
                '1100100010000000': ("2X3", ('++','+0','+0'), ), # "J"
                '1110001000000000': ("3X2", ('+++','00+'),    ), # "J"
                '1000100011000000': ("2X3", ('+0','+0','++'), ), # "L"
                '1110100000000000': ("3X2", ('+++','+00'),    ), # "L"
                '1100010001000000': ("2X3", ('++','0+','0+'), ), # "L"
                '0010111000000000': ("3X2", ('00+','+++'),    ), # "L"
                '0110110000000000': ("3X2", ('0++','++0'),    ), # "S"
                '1000110001000000': ("2X3", ('+0','++','0+'), ), # "S"
                '1100011000000000': ("3X2", ('++0','0++'),    ), # "Z"
                '0100110010000000': ("2X3", ('0+','++','+0'), ), # "Z"
                }
        sb = x.sheet_by_name('blocks')
        around = ([['1' if e==val else '0' for e in sb.row_values(i)[posx:min(posx+4, sb.ncols)]] for i in range(posy, min(posy+4, sb.nrows))])
        for i in range(4-len(around)):
            around.append(['0']*4)
        for a in around:
            for i in range(4-len(a)):
                a.append('0')
        #print(posx,posy,val)
        #print(around)
        key = ''.join([''.join(l) for l in around])
        size, shape = shapedic[key]
        return size,shape

    sl = x.sheet_by_name('lines')
    dl = ([sl.row_values(i) for i in range(sl.nrows)])

    maxnum = 0

    blockdic = {}
    head = []
    for posy,prow in enumerate(dp):
        for posx,val in enumerate(prow):
            if val != "":
                maxnum = max(maxnum, int(val))
                size, shape = findval(val, posx, posy)
                bret = []
                bret.append("BLOCK#{} {}".format(val,size))

                # check via(line) number and update
                shapelist = [list(t) for t in shape]
                for ofy, line in enumerate(shape):
                    for ofx, e in enumerate(line):
                        if posy+ofy < sl.nrows and posx+ofx < sl.ncols:
                            lval = dl[posy+ofy][posx+ofx]
                            if e=='+' and lval != '+':
                                shapelist[ofy][ofx] = lval
                for shapeline in shapelist:
                    bret.append(','.join(shapeline))
                bret.append("")
                blockdic[int(val)] = bret
    head.append("SIZE 72X72")
    head.append("BLOCK_NUM {}".format(maxnum))
    head.append("")
    ret = head
    for i in range(1,maxnum+1):
        ret = ret + blockdic[i]
    return '\n'.join(ret)

def convert(xlsname):
    x = xlrd.open_workbook(xlsname)
    return genA(x), genQ(x)

def genA_from_b64(data):
    try:
        data_decoded = base64.b64decode(data)
        x = xlrd.open_workbook(file_contents=data_decoded)
        return genA(x)
    except binascii.Error:
        # maybe not b64 encoded data, and it is text
        return data

if __name__ == "__main__":
    import sys
    import os.path
    xlsname = sys.argv[1]
    name,ext = os.path.splitext(xlsname)

    try:
        x = xlrd.open_workbook(xlsname)
        #A,Q = convert(xfile)
        A = genA(x)
        with open(name+"_A.txt", 'wt') as f:
            f.write(A)

        Q = genQ(x)
        with open(name+"_Q.txt", 'wt') as f:
            f.write(Q)
    except xlrd.biffh.XLRDError:
        print("maybe not excel file")
        raise

