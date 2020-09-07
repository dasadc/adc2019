import base64

if __name__ == '__main__':
    import sys
    fname = sys.argv[1]
    oname = fname + '.b64.txt'
    with open(fname, 'rb') as f:
        data = f.read()
    data_encoded = base64.b64encode(data)
    with open(oname, 'wb') as f:
        f.write(data_encoded)

