import sqlite3, os.path
from cryptography.fernet import Fernet

inventorydb = "./inventory.db"
saltfile = "./.saltfile"

# Salt File
class crypto:
    #cria
    def saltwrite(saltkey):
        salt_file = open(saltfile, "w")
        salt_file.write(saltkey)
        salt_file.close()

    def create_saltfile():
        key = Fernet.generate_key()
        #print(key)
        if os.path.isfile(saltfile) is True:
            # Existe, confirma e escreve ou sai
            answer = 0
            while answer not in ["y","n"]:
                answer = input("# 'saltfile' file exists. Replace? (y/n) ")
            if answer == "y":
                crypto.saltwrite(key.decode("utf-8"))
                print("# 'saltfile' replaced!") # esmaga ficheiro
            elif answer == "n":
                print("# OK, bye!")
        else:
            crypto.saltwrite(key.decode("utf-8"))
            print("# New 'saltfile' on the block!") # esmaga ficheiro             
        return key

    def read_saltword():
        with open(saltfile) as sf:
            saltword = str.encode(sf.readline().rstrip())
        return(saltword)
    
    def salt_encode(str_to_encode):
        salt_wd = crypto.read_saltword()
        fernetw = Fernet(salt_wd)
        cry_pwd = fernetw.encrypt(str_to_encode.encode())
        return(cry_pwd)

    def salt_decode(str_to_decode):
        salt_wd = crypto.read_saltword()
        fernetw = Fernet(salt_wd)
        dec_pwd = fernetw.decrypt(str.encode(str_to_decode)).decode()
        return(dec_pwd)

# SQLite database class
class database:
    def create_database():
        with sqlite3.connect(inventorydb) as conn:
            conn.execute('CREATE TABLE IF NOT EXISTS connections (id integer primary key, dsn text, user text, password text, instance text)')

    def add_connection(db_dsn,db_user,db_password,db_instance):
        with sqlite3.connect(inventorydb) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT max(id) as max_id from connections')
            maxid = cursor.fetchone()
            print("maxid: ", isinstance(maxid[0], int))
            if isinstance(maxid[0], int):
                newid = maxid[0] + 1
            else:
                newid = 1
            print("new id:", newid)
            cursor.close()
            
            cursor = conn.cursor()
            insrt = """INSERT INTO connections 
                    (id, dsn, user, password, instance) 
                    VALUES
                    (?, ?, ?, ?, ?);"""
            db_password_crypto = crypto.salt_encode(db_password)
            dataTuple = (newid, db_dsn,db_user,db_password_crypto,db_instance)
            cursor.execute(insrt, dataTuple)
            conn.commit()

            cursor.execute('SELECT id, dsn,user,instance from connections')
            print("# Registered Connections:")
            for row in cursor.fetchall():
                print("## " + str(row[0]) + ": " + row[2] + "/******@" + row[1] + "/" + row[3])
            cursor.close()
        return(newid)

    def del_connection():
        with sqlite3.connect(inventorydb) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, dsn, user, instance from connections')
            print("# Registered Connections:")
            idList = []
            for row in cursor.fetchall():
                print("## ID=" + str(row[0]) + ": " + row[2] + "/******@" + row[1] + "/" + row[3])
                idList.append(int(row[0]))    
            cursor.close()
            print(idList)
            answer = 0
            yesno  = 0            
            while int(answer) not in idList:
                answer = input("# Choose one connection ID to delete:")
            while yesno not in ["y","n"]:
                yesno = input("Are you sure? (y/n)")

            if yesno == "n":
                print("# Ok, buBye!")
            elif yesno == "y":
                cursor = conn.cursor()
                cursor.execute('DELETE FROM connections where id = ?;', answer)
                conn.commit()
                cursor.close()
                print("# Connection ? deleted", answer)

class callTelegraf():
    def runALL():
        with sqlite3.connect(inventorydb) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, dsn, user, password, instance from connections')
            print("# Registered Connections:")
            for row in cursor.fetchall():
                print("## ID=" + str(row[0]) + ": " + row[2] + crypto.salt_decode(row[3]) + row[1] + "/" + row[4]) ## há aqui um erro qq 
                # CALL Ficheiro de execução, import, o que quiseres
        return(1)


############################################### FUNCTIONS USAGE #########################################################################

## saltfile usage
# cria_saltfile = crypto.create_saltfile()
# read_saltexpr = crypto.read_saltword()
# print(crypto.salt_encode('bananas123'))
# print(crypto.salt_decode("gAAAAABhs_aM9V-eisDLEZeWdnfiGRU3UOFaCR2IOFzdISH9vAwrjNdDemAwfNBLs1TrqAjDDvTVPxwF1dfwzowpwq-916hBqg=="))

## database usage
# cria_database = database.create_database()
# add_connectio = database.add_connection('qlyserver:1521','gamesapp','passwordqly','instanceX')
# del_connectio = database.del_connection()


## run(ALL)
# criar argumentos para executar: setup (create database, add e del connections) | saltfile create, read, encode, decode | run_all


############### RUN

print(callTelegraf.runALL())



