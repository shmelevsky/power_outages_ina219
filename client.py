from db import ConnectToDB
from subprocess import Popen, PIPE, STDOUT
from typing import Tuple, Optional
from time import sleep
from telega_msg_sender import TelegaMSGsender



def run_cmd(command, shell=False) -> Tuple[int, Optional[str]]:
    if not shell:
        command = command.split()
    try:
        process = Popen(command, stdout=PIPE, stderr=STDOUT, shell=shell)
        stdout, _ = process.communicate()
        stdout = stdout.decode(encoding='utf-8', errors='ignore')
        return process.returncode, stdout
    except FileNotFoundError as err:
        return 1, str(err)



if __name__ == "__main__":
    attempts = 1
    telega = TelegaMSGsender()
    while True:
        try:
            with ConnectToDB() as conn:
                conn.cur.execute('SELECT * FROM  outages ORDER BY date DESC')
                _, el, _, _ = conn.cur.fetchone()
            print(f"Rresult: {el}")
            if not el:
                if attempts >= 2:
                    telega.send_msg('NAS POWERING OFF')
                    _, _  = run_cmd('/usr/sbin/poweroff')
                attempts+=1
                continue   
            attempts = 1

        except Exception as err:
            print(f'DataBase. Error getting data from database {err}')
        
        finally:
            sleep(60)

