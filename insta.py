try:
    from requests.exceptions import RequestException
    import requests, re, json, time, os, sys
    from rich.console import Console
    from rich.panel import Panel
    from rich import print as printf
    from requests.exceptions import SSLError
except (ModuleNotFoundError) as e:
    __import__('sys').exit(f"[Error] {str(e).capitalize()}!")

# Global tracking variables
SUCCESS, FAILED, FOLLOWERS, STATUS, BAD, CHECKPOINT, ERROR_LIST, TRY = [], [], {
    "COUNT": 0
}, [], [], [], [], []

class SEND_FOLLOWERS:

    def __init__(self) -> None:
        pass

    def FOLLOWER_PROCESS(self, session, username, password, host, your_username):
        global SUCCESS, FAILED, STATUS, ERROR_LIST, BAD, CHECKPOINT
        session.headers.update({
            'Accept-Encoding': 'gzip, deflate',
            'Sec-Fetch-Mode': 'navigate',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Accept-Language': 'en-US,en;q=0.9',
            'Sec-Fetch-Site': 'none',
            'Host': '{}'.format(host),
            'Sec-Fetch-Dest': 'document',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Connection': 'keep-alive'
        })
        response = session.get('https://{}/login'.format(host))
        self.ANTI_FORGERY_TOKEN = re.search(r'"&antiForgeryToken=(.*?)";', str(response.text))
        
        if self.ANTI_FORGERY_TOKEN != None:
            self.TOKEN = self.ANTI_FORGERY_TOKEN.group(1)
            session.headers.update({
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Sec-Fetch-Site': 'same-origin',
                'Referer': 'https://{}/login'.format(host),
                'Sec-Fetch-Mode': 'cors',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Sec-Fetch-Dest': 'empty',
                'Cookie': '; '.join([str(key) + '=' + str(value) for key, value in session.cookies.get_dict().items()]),
                'Origin': 'https://{}'.format(host)
            })
            data = {
                'username': f'{username}',
                'antiForgeryToken': f'{self.TOKEN}',
                'userid': '',
                'password': f'{password}'
            }
            response2 = session.post('https://{}/login?'.format(host), data = data)
            self.JSON_RESPONSE = json.loads(response2.text)
            
            # Check login success
            if '\'status\': \'success\'' in str(self.JSON_RESPONSE):
                session.headers.update({
                    'Referer': 'https://{}/tools/send-follower'.format(host),
                    'Cookie': '; '.join([str(key) + '=' + str(value) for key, value in session.cookies.get_dict().items()])
                })
                data = {'username': f'{your_username}'}
                response3 = session.post('https://{}/tools/send-follower?formType=findUserID'.format(host), data = data)
                
                if 'name="userID"' in str(response3.text):
                    self.USER_ID = re.search(r'name="userID" value="(\d+)">', str(response3.text)).group(1)
                    session.headers.update({
                        'Cookie': '; '.join([str(key) + '=' + str(value) for key, value in session.cookies.get_dict().items()])
                    })
                    data = {
                        'userName': f'{your_username}',
                        'adet': '500',
                        'userID': f'{self.USER_ID}',
                    }
                    response4 = session.post('https://{}/tools/send-follower/{}?formType=send'.format(host, self.USER_ID), data = data)
                    self.JSON_RESPONSE4 = json.loads(response4.text)
                    
                    if '\'status\': \'success\'' in str(self.JSON_RESPONSE4):
                        SUCCESS.append(f'{self.JSON_RESPONSE4}')
                        STATUS.append(f'{self.JSON_RESPONSE4}')
                    elif '\'code\': \'nocreditleft\'' in str(self.JSON_RESPONSE4):
                        printf(f"[bold bright_black]   ──>[bold red] YOUR CREDITS HAVE RUN OUT!           ", end='\r')
                        time.sleep(4.5)
                    elif '\'code\': \'nouserleft\'' in str(self.JSON_RESPONSE4):
                        printf(f"[bold bright_black]   ──>[bold red] NO USERS FOUND!                      ", end='\r')
                        time.sleep(4.5)
                    elif 'istek engellendi.' in str(self.JSON_RESPONSE4): # Request Blocked (Turkish)
                        TRY.append(f'{self.JSON_RESPONSE4}')
                        if len(TRY) >= 3:
                            TRY.clear()
                            printf(f"[bold bright_black]   ──>[bold red] REQUEST TO SEND FOLLOWERS BLOCKED!  ", end='\r')
                            time.sleep(4.5)
                            return (False)
                        else:
                            self.FOLLOWER_PROCESS(session, username, password, host, your_username)
                    else:
                        FAILED.append(f'{self.JSON_RESPONSE4}')
                        printf(f"[bold bright_black]   ──>[bold red] ERROR WHILE SENDING FOLLOWERS!      ", end='\r')
                        time.sleep(4.5)
                    printf(f"[bold bright_black]   ──>[bold green] FINISH FROM {str(host).split('.')[0].upper()} SERVICE!           ", end='\r')
                    time.sleep(5.0)
                    return (True)
                else:
                    printf(f"[bold bright_black]   ──>[bold red] TARGET USERNAME NOT FOUND!           ", end='\r')
                    time.sleep(4.5)
                    return (False)
            elif 'Güvenliksiz giriş tespit edildi.' in str(self.JSON_RESPONSE): # Checkpoint (Turkish)
                CHECKPOINT.append(f'{self.JSON_RESPONSE}')
                printf(f"[bold bright_black]   ──>[bold red] YOUR ACCOUNT IS CHECKPOINT!          ", end='\r')
                time.sleep(4.5)
                return (False)
            elif 'Üzgünüz, şifren yanlıştı.' in str(self.JSON_RESPONSE): # Wrong Password (Turkish)
                BAD.append(f'{self.JSON_RESPONSE}')
                printf(f"[bold bright_black]   ──>[bold red] YOUR PASSWORD IS WRONG!              ", end='\r')
                time.sleep(4.5)
                return (False)
            else:
                ERROR_LIST.append(f'{self.JSON_RESPONSE}')
                printf(f"[bold bright_black]   ──>[bold red] LOGIN ERROR!                          ", end='\r')
                time.sleep(4.5)
                return (False)
        else:
            printf(f"[bold bright_black]   ──>[bold red] FORGERY TOKEN NOT FOUND!           ", end='\r')
            time.sleep(2.5)
            return (False)

class INFO:

    def __init__(self) -> None:
        pass

    def GET_FOLLOWERS(self, your_username, updated):
        global FOLLOWERS
        with requests.Session() as session:
            session.headers.update({
                'User-Agent': 'Instagram 317.0.0.0.3 Android (27/8.1.0; 360dpi; 720x1280; LAVA; Z60s; Z60s; mt6739; en_IN; 559698990)',
                'Host': 'i.instagram.com',
                'Accept-Language': 'en-US,en;q=0.9',
            })
            response = session.get('https://i.instagram.com/api/v1/users/web_profile_info/?username={}'.format(your_username))
            if '"status":"ok"' in str(response.text):
                self.COUNT = json.loads(response.text)['data']['user']['edge_followed_by']['count']
                if bool(updated) == True:
                    FOLLOWERS.update({"COUNT": int(self.COUNT)})
                    return (True)
                else:
                    self.INCREASE = (int(self.COUNT) - int(FOLLOWERS['COUNT']))
                    return (f'+{self.INCREASE} > {self.COUNT}')
            else:
                if bool(updated) == True:
                    FOLLOWERS.update({"COUNT": 0})
                    return (False)
                else:
                    return ('-+500')

class MAIN:

    def __init__(self):
        global CHECKPOINT, BAD, ERROR_LIST
        try:
            self.LOGO()
            printf(Panel(f"[bold white]Please fill in your Instagram account details (username:password).\nUse a fake account to log in!", width=59, style="bold bright_black", title="[Login Required]", subtitle="╭──────", subtitle_align="left"))
            self.ACCOUNTS = Console().input("[bold bright_black]   ╰─> ")
            
            if ':' in str(self.ACCOUNTS):
                self.USERNAME, self.PASSWORD = self.ACCOUNTS.split(':')[0], self.ACCOUNTS.split(':')[1]
                printf(Panel(f"[bold white]Enter target Instagram username. Make sure the account is public.\nExample: @username", width=59, style="bold bright_black", title="[Target Username]", subtitle="╭──────", subtitle_align="left"))
                self.YOUR_USERNAME = Console().input("[bold bright_black]   ╰─> ").replace('@', '')
                
                if len(self.YOUR_USERNAME) != 0:
                    printf(Panel(f"[bold white]Use [bold yellow]CTRL + C[/] to skip or [bold red]CTRL + Z[/] to stop the script.", width=59, style="bold bright_black", title="[Notes]"))
                    while (True):
                        try:
                            INFO().GET_FOLLOWERS(your_username=self.YOUR_USERNAME, updated=True)
                            CHECKPOINT.clear(); BAD.clear(); ERROR_LIST.clear()
                            
                            for HOST in ['instamoda.org', 'takipcitime.com', 'takipcikrali.com', 'bigtakip.net', 'takipcimx.net']:
                                try:
                                    with requests.Session() as session:
                                        SEND_FOLLOWERS().FOLLOWER_PROCESS(session, self.USERNAME, self.PASSWORD, HOST, self.YOUR_USERNAME)
                                        continue
                                except (SSLError):
                                    ERROR_LIST.append(f'{HOST}')
                                    BAD.append(f'{HOST}')
                                    CHECKPOINT.append(f'{HOST}')
                                    printf(f"[bold bright_black]   ──>[bold red] UNABLE TO CONNECT TO {str(HOST).split('.')[0].upper()}! ", end='\r')
                                    time.sleep(2.5)
                                    continue
                            
                            # Validation checks
                            if len(CHECKPOINT) >= 5:
                                printf(Panel(f"[bold red]Account checkpoint triggered. Please approve login on another device.", width=59, title="[Checkpoint]"))
                                sys.exit()
                            elif len(BAD) >= 5:
                                printf(Panel(f"[bold red]Incorrect password. New accounts are not recommended for this service.", width=59, title="[Login Failed]"))
                                sys.exit()
                            elif len(ERROR_LIST) >= 5:
                                printf(Panel(f"[bold red]Unknown login error. Service might be down or account restricted.", width=59, title="[Service Error]"))
                                sys.exit()
                            else:
                                if len(STATUS) != 0:
                                    try:
                                        self.COUNTDOWN(0, 300, self.YOUR_USERNAME)
                                        self.AMOUNT = INFO().GET_FOLLOWERS(your_username=self.YOUR_USERNAME, updated=False)
                                    except:
                                        self.AMOUNT = ('null')
                                    
                                    printf(Panel(f"[bold white]Status : [bold green]Success![/]\n[bold white]Link   : [bold red]https://instagram.com/{self.YOUR_USERNAME}\n[bold white]Gain   : [bold yellow] {self.AMOUNT}", width=59, title="[Success]"))
                                    self.COUNTDOWN(0, 600, self.YOUR_USERNAME)
                                    STATUS.clear()
                                else:
                                    self.COUNTDOWN(0, 600, self.YOUR_USERNAME)
                                    continue
                        except (RequestException):
                            printf(f"[bold bright_black]   ──>[bold red] CONNECTION PROBLEM DETECTED! ", end='\r')
                            time.sleep(9.5); continue
                        except (KeyboardInterrupt):
                            time.sleep(2.5); continue
                else:
                    printf(Panel(f"[bold red]Target username cannot be empty!", width=59, title="[Error]"))
                    sys.exit()
            else:
                printf(Panel(f"[bold red]Wrong format! Use 'username:password'.", width=59, title="[Format Error]"))
                sys.exit()
        except Exception as e:
            printf(Panel(f"[bold red]{str(e).capitalize()}!", width=59, title="[System Error]"))
            sys.exit()

    def LOGO(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        printf(Panel(r"""[bold red] _____                    ______            _        
(_____)           _        |  ___ \          | |       
   _    ____   ___| |_  ____| | _ | | ___   _ | | ____ 
  | | |  _ \ /___)  _)/ _  | || || |/ _ \ / || |/ _  |
 _| |_| | | |___ | |_( ( | | || || | |_| ( (_| ( ( | |
[bold white](_____)_| |_(___/ \___)_||_|_||_||_|\___/ \____|\_||_|
         [underline green]Free Instagram Followers""", width=59, style="bold bright_black"))
        return (True)

    def COUNTDOWN(self, minutes, seconds, your_username):
        self.TOTAL = (minutes * 60 + seconds)
        while (self.TOTAL):
            M, S = divmod(self.TOTAL, 60)
            printf(f"[bold bright_black]   ──>[bold green] @{str(your_username)[:20].upper()}[bold white]/[bold green]{M:02d}:{S:02d}[bold white] SUCCESS:-[bold green]{len(SUCCESS)}[bold white] FAILED:-[bold red]{len(FAILED)}     ", end='\r')
            time.sleep(1)
            self.TOTAL -= 1
        return (True)

if __name__ == '__main__':
        MAIN()
