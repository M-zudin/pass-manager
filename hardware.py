import os
import shutil
import secrets
import pyAesCrypt
import wmi
import hashlib

disk=input("Введите букву диска: ")
if os.path.exists(disk+':'):
    input("ВНИМАНИЕ!!! Данные на диске будут потеряны. Нажмите enter, если вы уверены. Иначе закройте программу.")
    print("Очистка диска...")
    for x in os.listdir(disk+':'):
        if os.path.isdir(x):
            shutil.rmtree(x)
        else:
            os.remove(x)
    print("Создание ключа, это может занять некоторое время...")
    with open(disk+':'+'\\key.key','wb') as o:
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
    os.truncate(disk+':\\key.key',disk_size-64) #оставляем немного места для служебных данных AES
    print("Шифрование ключа, это тоже может занять некоторое время...")
    c=wmi.WMI()
    for x in c.Win32_LogicalDisk():
        if x.DeviceID=='C:':
            main_disk_id=x.VolumeSerialNumber
        if x.DeviceID==disk+':':
            disk_id=x.VolumeSerialNumber
    key=hashlib.pbkdf2_hmac('sha256',disk_id.encode(),main_disk_id.encode(),2*10**6,32)
    key=str(key)
    buf=1024**3
    pyAesCrypt.encryptFile(f"{disk}:\\key.key","key.key",key,buf)
    os.remove(f"{disk}:\\key.key")
    shutil.move("key.key",f"{disk}:\\key.key")
    os.remove("key.key")
    print("Готово! Пароль:")
    pos=secrets.randbelow(disk_size-96) #disk_size-64-32
    symbols="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+-"
    passwd=''
    while pos:
        passwd+=symbols[pos%64]
        pos>>=6
    print(passwd)
else:
    print("Нет такого диска")
input("Нажмите enter для выхода...")