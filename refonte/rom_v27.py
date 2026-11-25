"""UPS reversible à tailles égales, utilisé par les générateurs locaux."""
import struct,zlib
def crc(data): return zlib.crc32(data)&0xffffffff
def number(n):
    out=bytearray()
    while n>=128:
        out.append(n&127);n=(n>>7)-1
    out.append(n|128);return bytes(out)
def read_number(data,pos,end):
    n=0;shift=1
    while pos<end:
        b=data[pos];pos+=1;n+=(b&127)*shift
        if b&128:return n,pos
        shift*=128;n+=shift
    raise ValueError('UPS truncated')
def patch_create(a,b):
    if len(a)!=len(b):raise ValueError('Equal-sized images required')
    out=bytearray(b'UPS1'+number(len(a))+number(len(b)));pos=cursor=0
    while pos<len(a):
        if a[pos]==b[pos]:pos+=1;continue
        out+=number(pos-cursor)
        while pos<len(a) and a[pos]!=b[pos]:
            out.append(a[pos]^b[pos]);pos+=1
        out.append(0);cursor=pos+1;pos=cursor
    out+=struct.pack('<II',crc(a),crc(b));out+=struct.pack('<I',crc(out));return bytes(out)
def patch_apply(source,patch,reverse=False):
    if patch[:4]!=b'UPS1' or len(patch)<18 or crc(patch[:-4])!=struct.unpack('<I',patch[-4:])[0]:raise ValueError('Invalid UPS')
    end=len(patch)-12;a,p=read_number(patch,4,end);b,p=read_number(patch,p,end)
    ca,cb=struct.unpack('<II',patch[-12:-4])
    if reverse:a,b,ca,cb=b,a,cb,ca
    if len(source)!=a or a!=b or crc(source)!=ca:raise ValueError('Wrong source')
    result=bytearray(source);cursor=0
    while p<end:
        delta,p=read_number(patch,p,end);cursor+=delta
        while True:
            if p>=end:raise ValueError('Truncated block')
            x=patch[p];p+=1
            if not x:cursor+=1;break
            if cursor>=b:raise ValueError('Out of range')
            result[cursor]^=x;cursor+=1
    if crc(result)!=cb:raise ValueError('Wrong result')
    return bytes(result)
