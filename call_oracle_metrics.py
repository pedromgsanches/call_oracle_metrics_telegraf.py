import sqlite3, os, os.path, getopt, sys
from cryptography.fernet import Fernet

script_file = "./python3 oracle_metrics.py"
# SQLite catálogo
inventorydb = "./inventory.db"
# Ficheiro escondido com a chave de desencriptação das passwords
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
                answer = input("## WARNING ## \n This will invalidate existing saved passwords! \n 'saltfile' file exists. Replace? (y/n)")
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
#       dec_pwd = fernetw.decrypt(str.encode(str_to_decode)).decode()
        dec_pwd = fernetw.decrypt(str_to_decode).decode()
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

    def list_connection():
        with sqlite3.connect(inventorydb) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, dsn, user, instance from connections')
            print("# Registered Connections:")
            idList = []
            for row in cursor.fetchall():
                print("## ID=" + str(row[0]) + ": " + row[2] + "/******@" + row[1] + "/" + row[3])
                idList.append(int(row[0]))    
            cursor.close()

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
                #print("## ID=" + str(row[0]) + ": " + row[2] + '/' + crypto.salt_decode(row[3]) + '@' + row[1] + "/" + row[4])
                #python3 "$SCRIPT" --dsn "$DSN" --user "$USER" --password "$PASSWORD" --instance "$INSTANCE"
                exec_command = "nohup " + script_file + " --dsn " + row[1] + " --user " + row[2] + " --password " + crypto.salt_decode(row[3]) + " --instance " + row[4] + " & 2>/dev/null"
                # print(exec_command) ## descomentar apenas para debug
                os.system(exec_command)
        return(1)


argumentList = sys.argv[1:]
options = "hslcdxa:"
long_options = ["help", "salt","list", "create-db", "del-target", "execute", "add-target"]

print("-")
print("###### Run Oracle Metrics ###################################")
print("# Try ./call_oracle_metrics -h for help about using me")
try:
    # Parsing argument
    arguments, values = getopt.getopt(argumentList, options, long_options)
    # checking each argument
    for currentArgument, currentValue in arguments:
 
        if currentArgument in ("-h", "--help"):
            print (
                "Run Oracle Metrics Help: \n" 
                "    -h, --help                                                    - show this dialog \n"
                "    -l, --list                                                    - list connections \n"
                "    -s, --salt                                                    - create saltfile for password encryption \n"
                "    -c, --create-db                                               - Create database for targets inventory \n"
                "    -a, --add-target dsn user password instance-name              - Add target to database. Example: \n"
                "                                                                    ./call_oracle_metrics -a xapp-prod:1521 xapp_user Passw0rd666 instance01 \n"        
                "    -d, --del-target                                              - Delete target from database \n"
                "    -x,  --execute                                                - Run Oracle Metrics" )
             
        elif currentArgument in ("-s", "--salt"):
            exec = crypto.create_saltfile()
        elif currentArgument in ("-c", "--create-db"):
            exec = database.create_database()
        elif currentArgument in ("-l", "--list"):
            exec = database.list_connection()
        elif currentArgument in ("-a", "--add-target"):
            exec = database.add_connection(sys.argv[2],sys.argv[3],sys.argv[4], sys.argv[5])
            #exec = database.add_connection('prdserver:1521','gamesapp','passwordprd','instance10')
        elif currentArgument in ("-d", "--del-target"):
            exec = database.del_connection()         
        elif currentArgument in ("-x", "--execute"):
            exec = callTelegraf.runALL()                 
except getopt.error as err:
    # output error, and return with an error code
    print (str(err))

print("-")


############################################### FUNCTIONS USAGE #########################################################################

## saltfile usage
# cria_saltfile = crypto.create_saltfile()
# read_saltexpr = crypto.read_saltword()
# print(crypto.salt_encode('bananas123'))
#print(crypto.salt_decode("gAAAAABhs_aM9V-eisDLEZeWdnfiGRU3UOFaCR2IOFzdISH9vAwrjNdDemAwfNBLs1TrqAjDDvTVPxwF1dfwzowpwq-916hBqg=="))

### database usage
# database.create_database()
# database.add_connection('prdserver:1521','gamesapp','passwordprd','instance10')
# database.del_connection()
# database.list_connection()

## run(ALL)
# print(callTelegraf.runALL())
