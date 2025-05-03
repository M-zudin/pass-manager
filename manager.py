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
        print(f"Уже есть пароль для этого сайта! Введите 3, а затем '{site}' чтобы посмотреть его.")
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
        print("Нет пароля для этого сайта")
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
            print("Неверный мастер-пароль")
            return None
        return str(fDec.getvalue())
    else:
        print("Нет пароля для этого сайта")
        return None

def create_key(master_passwd):
    key=hashlib.pbkdf2_hmac('sha256',master_passwd.encode(),b'''{Ano<x#{#OBy1X8izQbwP"7}?])kr2(8Q3r~r&('rA1zz#8r<g]BDXyxZXfgdmbQ''',10**5,32)
    return str(key)

def hardware_passwd_to_key(passwd):
    print("Подождите...")
    symbols="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+-"
    key=0
    for x in passwd:
        if x in symbols:
            key+=symbols.find(x)
            key<<=6
        else:
            print("Некорректный пароль")
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
        print("Не та флешка или не тот компьютер")
        return 0
    except FileNotFoundError:
        print("Файл ключа не найден")
    with open('key.key','rb') as o:
        o.seek(pos) #чтобы не читать весь файл
        data=o.read(32)
    os.remove("key.key")
    key=0
    for x in range(pos,pos+32):
        key+=data[x]
        key<<=8
    data=0
    return key

def main():
    print("Инструкция по использованию физического ключа - hardware.txt")
    printable='''0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~''' #string.printable, но без ' \t\n\r\x0b\x0c' 
    master_passwd=input("Введите мастер-пароль: ")
    lst=master_passwd.split()
    if lst[0]=="HARDWARE" and len(lst)==3:
        if os.path.exists(lst[1]+':'):
            pos=hardware_passwd_to_key(lst[2])
            if pos:
                pre_key=read_hardware_key(disk+':',pos)
                if pre_key:
                    key=create_key(pre_key)
                else:
                    return 0
            else:
                return 0
        else:
            print("Диск не подключен")
    else:
        key=create_key(master_passwd)
    master_passwd=os.urandom(16)
    os.system('cls')
    while True:
        site=os.urandom(16)
        passwd=os.urandom(16)
        action=input('''Выберите действие:
1. Добавить пароль
2. Удалить пароль
3. Прочитать пароль
4. Выход
Ваш выбор: ''')
        if action=='1':
            site=input("Сайт: ")
            passwd=input("Пароль (оставьте пустым для авто-генерации): ")
            if not passwd:
                for x in range(32):
                    passwd+=secrets.choice(printable)
                print(f"Сгенерированный пароль: {passwd}")
            if add_passwd(site,passwd,key):
                print("Пароль добавлен!")
            else:
                if input("Введите 'ok' чтобы перезаписать: "):
                    add_passwd(site,passwd,key,forced=True)
                    print("Пароль перезаписан!")
        elif action=='2':
            site=input("Сайт: ")
            if remove_passwd(site,key):
                print("Пароль удалён!")
        elif action=='3':
            site=input("Сайт: ")
            passwd=read_passwd(site,key)[2:-1] #Возврашает строку вида "b'password'", без [2:-1] выводилось бы b'password'
            if passwd:  
                print(f"Пароль: {passwd}")
        elif action=='4':
            exit()
        else:
            print("Неверное действие")
        input("Нажмите enter для следующего действия...")
        os.system('cls')
if __name__=='__main__':
    main()
    input("Нажмите enter для выхода...")
