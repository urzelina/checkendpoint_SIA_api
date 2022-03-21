#!/usr/bin/python3
# 
# Script to check if trunk is available and report issue 
# /usr/local/bin/checkendpoint.py
# Copy Right 2022  Geert Sillekens   www.apeer.nl


from subprocess import PIPE, run
import time, datetime
import requests, sqlite3, json




# Storing/sabotage alarm: TA
# https://zodiac.videomanager.info:8088/?cmd=SIA%2062.41.176.78%203200%206706%20TA%20240

# Storing/sabotage herstel: TR
# https://zodiac.videomanager.info:8088/?cmd=SIA%2062.41.176.78%203200%206706%20TR%20240

def write_checkline(line):
    with open('/tmp/check_module.txt', "a") as fhandle:
        fhandle.write("{} ".format(line) + str(datetime.datetime.now()) + "\n")
#write_checkline(ARG1 + ARG2 + ARG3 + ARG4 + ARG5 + ARG6 + ARG7)

def write_api_log(line):
    with open('/var/log/asterisk/api_sia01.log', "a") as fhandle:
        fhandle.write("{} ".format(line) + str(datetime.datetime.now()) + "\n")

def write_failed_requests(epoch , requrl, payload):
    api_request = {'epoch': epoch, 'requrl': requrl, 'payload': payload}
    api_request = json.dumps(api_request)
    with open('/var/lib/asterisk/failed_api_requests.txt', "a") as fhandle:
        fhandle.write(api_request + "\n")



def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn




def query_xtrunk():

    database = "/var/lib/asterisk/astdb.sqlite3"

    # create a database connection
    conn = create_connection(database)
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT value FROM astdb WHERE key like '%XTRUNK%'")
        xtrunk_select = cur.fetchone()
       
        
        
        #xtrunk_select = select_xtrunk(conn)# tuple first element is the value
        print(xtrunk_select[0])
        
            

def update_xtrunk(nwstatus):
    
    cmdlist = ["/usr/sbin/asterisk", "-rx", "database put XTRUNK vzamskw {}".format(nwstatus)]
    result = run(cmdlist, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    return result.stdout



def api_request(pac_ip, pac_port, aansluitnummer, sia_code, zone):
        # https://zodiac.videomanager.info:8088/?cmd=SIA%20[IP-ADRES]%20[POORT]%20[AANSLUITNUMMER]%20[SIA-CODE]%20[ZONE]
        requrl = "https://zodiac.videomanager.info:8088"
        # payloadcmd = "SIA%20{}%20{}%20{}%20{}%20{}".format(pac_ip, pac_port, aansluitnummer, sia_code, zone)
        payloadcmd = "SIA {} {} {} {} {}".format(pac_ip, pac_port, aansluitnummer, sia_code, zone)
        payload = {'cmd': payloadcmd}
        fire_result = fire_request(requrl, payload, "")
        return fire_result
       
        
        # fire the request
def fire_request(requrl, payload, orig_epoch):
        try:
            r = requests.get(requrl, payload, timeout=5)
            # structure the results 
            rstatus = str(r.status_code)
            #rurl = unquote(r.url)
            #rdict = r.json()
            #datadict = rdict.get(actie)
            write_api_log("RETURN > " + str(rstatus))
            
         
        except:
            pass

def main():

        
    
    ARG1 = '62.41.176.78'#PAC_IP
    ARG2 = '3200'#PAC_PORT
    ARG3 = '6706'#AANSLUITNUMMER
    ARG4 = 'TA'#SIA_CODE
    ARG5 = '20240'#ZONE
    
    # get example
    # https://zodiac.videomanager.info:8088/?cmd=SIA%20[IP-ADRES]%20[POORT]%20[AANSLUITNUMMER]%20[SIA-CODE]%20[ZONE]


    cmdlist = ["/usr/sbin/asterisk", "-rx", "pjsip show endpoint vzamskw"]
    result = run(cmdlist, stdout=PIPE, stderr=PIPE, universal_newlines=True)

    #print(result.returncode, result.stdout, result.stderr)
    # print(type(result.stdout))

    # print(result.stdout)

    # result.stdout is string

    if "Avail" in result.stdout:
        print("Found!")
        # endpoint vzamskw is Available
    else:
        # endpoint vzamskw is NOT Availalbe, fire api 
        print("Not found!")
    
        try:
            #def api_request(zone, sia_code, aansluitnummer, callerid):
            api_request(ARG1, ARG2, ARG3, ARG4, ARG5)
        except:
            pass
    try:
        query_xtrunk()
    except:
        pass
    print(update_xtrunk("not"))
    

if __name__ == '__main__':
    main()




