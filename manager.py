import pyAesCrypt
import os
import io
import secrets
import hashlib

def add_passwd(site,passwd,key,forced=False):
    buf=64*1024
    hasher=hashlib.sha256()
    hasher.update((site+key).encode())
    site_hash=hasher.hexdigest()
    file=fr"passwords\{site_hash}"+".crp"
    if not os.path.isfile(file) or forced:
        fIn=io.BytesIO(passwd.encode())
        fCiph=io.BytesIO()
        pyAesCrypt.encryptStream(fIn,fCiph,key,buf)
        with open(file,'wb') as o:
            o.write(fCiph.getvalue())
        return 1
    else:
        print(f"You already have password for this site! Input 3, then '{site}' to see it.")
        return None

def remove_passwd(site,key):
    hasher=hashlib.sha256()
    hasher.update((site+key).encode())
    site_hash=hasher.hexdigest()
    file=fr"passwords\{site_hash}"+".crp"
    try:
        os.remove(file)
        return 1
    except FileNotFoundError:
        print("No password for this site")
        return None

def read_passwd(site,key):
    buf=64*1024
    hasher=hashlib.sha256()
    hasher.update((site+key).encode())
    site_hash=hasher.hexdigest()
    file=fr"passwords\{site_hash}"+".crp"
    if os.path.isfile(file):
        with open(file,'rb') as o:
            passwd=o.read()
        fIn=io.BytesIO(passwd)
        fDec=io.BytesIO()
        try:
            pyAesCrypt.decryptStream(fIn,fDec,key,buf)
        except ValueError:
            print("Incorrect master-password")
            return None
        return str(fDec.getvalue())
    else:
        print("No password for this site")
        return None

def create_key(master_passwd):
    key=hashlib.pbkdf2_hmac('sha256',master_passwd.encode(),b'''{Ano<x#{#OBy1X8izQbwP"7}?])kr2(8Q3r~r&('rA1zz#8r<g]BDXyxZXfgdmbQ''',10**5,32)
    return str(key)

def hardware_passwd_to_key(passwd):
    print("Wait a bit...")
    symbols="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+-"
    key=0
    for x in passwd:
        if x in symbols:
            key+=symbols.find(x)
            key<<=6
        else:
            print("Invalid password")
            return 0
    return key
    
def read_hardware_key(disk,pos):
    c=wmi.WMI()
    for x in c.Win32_LogicalDisk():
        if x.DeviceID=='C:':
            main_disk_id=x.VolumeSerialNumber
        if x.DeviceID==disk+':':
            disk_id=x.VolumeSerialNumber
    key=hashlib.pbkdf2_hmac('sha256',disk_id.encode(),main_disk_id.encode(),2*10**6,32)
    key=str(key)
    buf=1024**3
    try:
        pyAesCrypt.decryptFile(f"{disk}:\\key.key","key.key",key,buf)
    except ValueError:
        print("Wrong hardware key or wrong computer")
        return 0
    except FileNotFoundError:
        print("Key not found")
    with open('key.key','rb') as o:
        o.seek(pos) #you don't want to read all file
        data=o.read(32)
    os.remove("key.key")
    key=0
    for x in range(pos,pos+32):
        key+=data[x]
        key<<=8
    data=0
    return key

def main():
    print("Instruction for using hardware key - hardware.txt")
    printable='''0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~''' #string.printable without ' \t\n\r\x0b\x0c' 
    master_passwd=input("Input master-password: ")
    lst=master_passwd.split()
    if lst[0]=="HARDWARE" and len(lst)==3:
        if os.path.exists(lst[1]+':'):
            pos=hardware_passwd_to_key(lst[2])
            if pos:
                pre_key=read_hardware_key(lst[1]+':',pos)
                if pre_key:
                    key=create_key(pre_key)
                else:
                    return 0
            else:
                return 0
        else:
            print("Disk is not connected")
    else:
        key=create_key(master_passwd)
    master_passwd=os.urandom(16)
    os.system('cls')
    while True:
        site=os.urandom(16)
        passwd=os.urandom(16)
        action=input('''Select an action:
1. Add password
2. Remove password
3. Read password
4. Exit
Your choice: ''')
        if action=='1':
            site=input("Site: ")
            passwd=input("Password (leave empty for auto-generation): ")
            if not passwd:
                for x in range(32):
                    passwd+=secrets.choice(printable)
                print(f"Generated password: {passwd}")
            if add_passwd(site,passwd,key):
                print("Password added successfully!")
            else:
                if input("Input 'ok' to overwrite: "):
                    add_passwd(site,passwd,key,forced=True)
                    print("Password overwritten successfully!")
        elif action=='2':
            site=input("Site: ")
            if remove_passwd(site,key):
                print("Password removed successfully!")
        elif action=='3':
            site=input("Site: ")
            passwd=read_passwd(site,key)[2:-1] #Returns string like "b'password'", so without [2:-1] will print b'password'
            if passwd:  
                print(f"Password for {site}: {passwd}")
        elif action=='4':
            exit()
        else:
            print("Invalid action")
        input("Press enter for next action...")
        os.system('cls')
if __name__=='__main__':
    main()
    input("Press enter to exit...")
