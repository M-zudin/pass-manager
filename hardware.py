import os
import shutil
import secrets
import pyAesCrypt
import wmi
import hashlib

def request_disks():
    disk=input("Input drive letter: ")+':'
    reserve_disk=input("Input reserve drive letter (optional): ")+':'
    return [disk,reserve_disk]

def clear_disks(disks):
    disk=disks[0]
    reserve_disk=disks[1]
    if os.path.exists(disk) and os.path.exists(reserve_disk) and disk!=reserve_disk or os.path.exists(disk) and reserve_disk==':':
        input("WARNING!!! ALL data on disk will be lost. Press enter, if you are sure. Or close the program immediatly.")
        print("Cleaning disk(s)...")
        for x in os.listdir(disk):
            path=os.path.join(disk,x)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        if reserve_disk!=':':   
            for x in os.listdir(reserve_disk):
                path=os.path.join(reserve_disk,x)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
    else:
        print("Disk(s) should exist and be different")
        return 1

def create_hardware_key(disks):
    disk=disks[0]
    reserve_disk=disks[1]
    print("Creating the key, it may take a while...")
    with open(disk+'\\key.key','wb') as o:
        disk_size=0
        size=1024**3
        while True:
            try:
                o.write(os.urandom(size))
                disk_size+=size
            except IOError:
                if size!=1:
                    size/=1024
                else:
                    break
    os.truncate(os.path.join(disk,"key.key"),disk_size-1024) #Some place (1 KB) for AES data
    return disk_size-1024

def encrypt_hardware_key(disks,disk_size):
    disk=disks[0]
    reserve_disk=disks[1]
    print("Encrypting your key, it may take a while too...")
    c=wmi.WMI()
    for x in c.Win32_LogicalDisk():
        if x.DeviceID=='C:':
            main_disk_id=x.VolumeSerialNumber
        elif x.DeviceID==disk:
            disk_id=x.VolumeSerialNumber
        elif x.DeviceID==reserve_disk:
            reserve_disk_id=x.VolumeSerialNumber
    key=hashlib.pbkdf2_hmac('sha256',disk_id.encode(),main_disk_id.encode(),2*10**6,32)
    key=str(key)
    buf=1024**3
    pyAesCrypt.encryptFile(f"{disk}\\key.key","key.key",key,buf)
    if reserve_disk!=':':
        shutil.copy(f"{disk}\\key.key","temp_key.key")
        os.remove(f"{disk}\\key.key")
        shutil.move("key.key",f"{disk}\\key.key")
        os.remove("key.key")
    print("Done! Password:")
    pos=secrets.randbelow(disk_size-32)
    symbols="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+-"
    passwd=''
    while pos:
        passwd+=symbols[pos%64]
        pos>>=6
    print(passwd)
    if os.path.exists("temp_key.key"):
        key=hashlib.pbkdf2_hmac('sha256',reserve_disk_id.encode(),main_disk_id.encode(),2*10**6,32)
        key=str(key)
        print("Creating reserve key...")
        for x in os.listdir(reserve_disk):
            path=os.path.join(reserve_disk,x)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        pyAesCrypt.encryptFile("temp_key.key",f"{reserve_disk}\\key.key",key,buf)
        os.remove("temp_key.key")
        print("Done!")
    key=os.urandom(16)
    return passwd

def main():
    disks=request_disks()
    if clear_disks(disks):
        return 1
    disk_size=create_hardware_key(disks)
    encrypt_hardware_key(disks,disk_size)
if __name__=="__main__":
    main()
    input("Press enter to exit...")