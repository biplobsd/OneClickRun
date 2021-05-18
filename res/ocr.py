import os
from sys import exit as exx
import time
import uuid
import re
from subprocess import Popen,PIPE

HOME = os.path.expanduser("~")
CWD = os.getcwd()
tokens = {}

class ngrok:

  def __init__(self, TOKEN=None, USE_FREE_TOKEN=True,
               service=[['Service1', 80, 'tcp'], ['Service2', 8080, 'tcp']],
               region='us',
               dBug=[f"{HOME}/.ngrok2/ngrok.yml", 4040]):
    self.region = region
    self.configPath, self.dport = dBug
    self.TOKEN = TOKEN
    self.USE_FREE_TOKEN = USE_FREE_TOKEN
    self.service = service
    if USE_FREE_TOKEN:
      self.sdict = {}
      for i, sn in enumerate(service):
        tempcP = f'{HOME}/.ngrok2/'+sn[0]+'.yml'
        # Port, Protocol, config path
        self.sdict[sn[0]] = [self.dport+i, sn[2], tempcP]

  def nameport(self, TOKEN, AUTO):
    if AUTO:
        try:
            return tokens.popitem()[1]
        except KeyError:
            return "Invalid Token"
    elif not TOKEN:
        if not 'your' in tokens.keys():
            from IPython import get_ipython
            from IPython.display import clear_output
            ipython = get_ipython()

            print(r"Copy authtoken from https://dashboard.ngrok.com/auth")
            __temp = ipython.magic('%sx read -p "Token :"')
            tokens['your'] = __temp[0].split(':')[1]
            USR_Api = "your"
            clear_output()
        else:
            USR_Api = "your"
    else:
        USR_Api = "mind"
        tokens["mind"] = TOKEN
    return tokens[USR_Api]


  def ngrok_config(self, token, Gport, configPath, region, service):
    import os
    data = """
    region: {}
    update: false
    update_channel: stable
    web_addr: localhost:{}
    tunnels:\n""".format(region, Gport)
    if not self.USE_FREE_TOKEN:
      auth ="""
    authtoken: {}""".format(token)
      data = auth+data
    tunnels = ""
    for S in service:
        Sn, Sp, SpC = S
        tunnels += """      {}:
        addr: {}
        proto: {}
        inspect: false\n""".format(Sn, Sp, SpC)
    data = data + tunnels
    os.makedirs(f'{HOME}/.ngrok2/', exist_ok=True)
    with open(configPath, "w+") as configFile:
        configFile.write(data)
    return True


  def startWebUi(self, token, dport, nServer, region, btc, configPath,
               displayB, service, v):
    import os, time, urllib
    from IPython.display import clear_output
    from json import loads

    if token == "Invalid Token":
        print(tokens)
        os.exit()

    installNgrok()
    if v:
      clear_output()
      loadingAn(name="lds")
      textAn("Starting ngrok ...", ty='twg')
    if self.USE_FREE_TOKEN:
      for sn in service:
        self.ngrok_config(
          token,
          self.sdict[nServer][0],
          self.sdict[nServer][2],
          region,
          service)
        if sn[0] == nServer:
          runSh(f"ngrok {sn[2]} -config={self.sdict[nServer][2]} {sn[1]} &", shell=True)
    else:
      self.ngrok_config(token, dport, configPath, region, service)
      runSh(f"ngrok start --config {configPath} --all &", shell=True)
    time.sleep(3)
    try:
        if self.USE_FREE_TOKEN:
          dport = self.sdict[nServer][0]
          nServer = 'command_line'
          host = urllib.request.urlopen(f"http://localhost:{dport}/api/tunnels")
        else:
          host = urllib.request.urlopen(f"http://localhost:{dport}/api/tunnels")
        host = loads(host.read())['tunnels']
        for h in host:
          if h['name'] == nServer:
            host = h['public_url'][8:]
            break
    except urllib.error.URLError:
        if v:
          clear_output()
          loadingAn(name="lds")
          textAn("Ngrok Token is in used!. Again trying token ...", ty='twg')
        time.sleep(2)
        return True

    data = {"url": f"https://{host}"}
    if displayB:
      displayUrl(data, btc)
    return data


  def start(self, nServer, btc='b', displayB=True, v=True):
    import urllib
    from IPython.display import clear_output
    from json import loads

    try:
      nServerbk = nServer
      if self.USE_FREE_TOKEN:
          dport = self.sdict[nServer][0]
          nServer = 'command_line'
      else:
        dport = self.dport
      host = urllib.request.urlopen(f"http://localhost:{dport}/api/tunnels")
      host = loads(host.read())['tunnels']
      for h in host:
        if h['name'] == nServer:
          host = h['public_url'][8:]
          data = {"url": f"https://{host}"}
          if displayB:
            displayUrl(data, btc)
          return data

      raise Exception('Not found tunnels')
    except urllib.error.URLError:
      for run in range(10):
        if v:
          clear_output()
          loadingAn(name='lds')
        dati = self.startWebUi(
            self.nameport(self.TOKEN, self.USE_FREE_TOKEN) if not self.USE_FREE_TOKEN else {},
            self.dport,
            nServerbk,
            self.region,
            btc,
            self.configPath,
            displayB,
            self.service,
            v
            )
        if dati == True:
            continue
        return dati

def checkAvailable(path_="", userPath=False):
    from os import path as _p

    if path_ == "":
        return False
    else:
        return (
            _p.exists(path_)
            if not userPath
            else _p.exists(f"/usr/local/sessionSettings/{path_}")
        )

def accessSettingFile(file="", setting={}, v=True):
    from json import load, dump

    if not isinstance(setting, dict):
        if v:print("Only accept Dictionary object.")
        exx()
    fullPath = f"/usr/local/sessionSettings/{file}"
    try:
        if not len(setting):
            if not checkAvailable(fullPath):
                if v:print(f"File unavailable: {fullPath}.")
                exx()
            with open(fullPath) as jsonObj:
                return load(jsonObj)
        else:
            with open(fullPath, "w+") as outfile:
                dump(setting, outfile)
    except:
        if v:print(f"Error accessing the file: {fullPath}.")


def displayUrl(data, btc='b', pNamU='Public URL: ', EcUrl=None, ExUrl=None, cls=True):
    from IPython.display import HTML, clear_output

    if cls:
        clear_output()
    showTxT = f'{pNamU}{data["url"]}'
    if EcUrl:
      showUrL = data["url"]+EcUrl
    elif ExUrl:
      showUrL = ExUrl
    else:
      showUrL = data["url"]
    if btc == 'b':
          # blue
          bttxt = 'hsla(210, 50%, 85%, 1)'
          btcolor = 'hsl(210, 80%, 42%)'
          btshado = 'hsla(210, 40%, 52%, .4)'
    elif btc == 'g':
          # green
          bttxt = 'hsla(110, 50%, 85%, 1)'
          btcolor = 'hsla(110, 86%, 56%, 1)'
          btshado = 'hsla(110, 40%, 52%, .4)'
    elif btc == 'r':
          # red
          bttxt = 'hsla(10, 50%, 85%, 1)'
          btcolor = 'hsla(10, 86%, 56%, 1)'
          btshado = 'hsla(10, 40%, 52%, .4)'

    return display(HTML('''<style>@import url('https://fonts.googleapis.com/css?family=Source+Code+Pro:200,900');  :root {   --text-color: '''+bttxt+''';   --shadow-color: '''+btshado+''';   --btn-color: '''+btcolor+''';   --bg-color: #141218; }  * {   box-sizing: border-box; } button { position:relative; padding: 10px 20px;     border: none;   background: none;   cursor: pointer;      font-family: "Source Code Pro";   font-weight: 900;   font-size: 100%;     color: var(--text-color);      background-color: var(--btn-color);   box-shadow: var(--shadow-color) 2px 2px 22px;   border-radius: 4px;    z-index: 0;     overflow: hidden;    }  button:focus {   outline-color: transparent;   box-shadow: var(--btn-color) 2px 2px 22px; }  .right::after, button::after {   content: var(--content);   display: block;   position: absolute;   white-space: nowrap;   padding: 40px 40px;   pointer-events:none; }  button::after{   font-weight: 200;   top: -30px;   left: -20px; }   .right, .left {   position: absolute;   width: 100%;   height: 100%;   top: 0; } .right {   left: 66%; } .left {   right: 66%; } .right::after {   top: -30px;   left: calc(-66% - 20px);      background-color: var(--bg-color);   color:transparent;   transition: transform .4s ease-out;   transform: translate(0, -90%) rotate(0deg) }  button:hover .right::after {   transform: translate(0, -47%) rotate(0deg) }  button .right:hover::after {   transform: translate(0, -50%) rotate(-7deg) }  button .left:hover ~ .right::after {   transform: translate(0, -50%) rotate(7deg) }  /* bubbles */ button::before {   content: '';   pointer-events: none;   opacity: .6;   background:     radial-gradient(circle at 20% 35%,  transparent 0,  transparent 2px, var(--text-color) 3px, var(--text-color) 4px, transparent 4px),     radial-gradient(circle at 75% 44%, transparent 0,  transparent 2px, var(--text-color) 3px, var(--text-color) 4px, transparent 4px),     radial-gradient(circle at 46% 52%, transparent 0, transparent 4px, var(--text-color) 5px, var(--text-color) 6px, transparent 6px);    width: 100%;   height: 300%;   top: 0;   left: 0;   position: absolute;   animation: bubbles 5s linear infinite both; }  @keyframes bubbles {   from {     transform: translate();   }   to {     transform: translate(0, -66.666%);   } }    Resources</style><center><a href="'''+showUrL+'''" target="_blank"><div style="width: 700px;   height: 80px; padding-top:15px"><button style='--content: "'''+showTxT+'''";'">   <div class="left"></div>'''+showTxT+'''<div class="right"></div> </div></button></a></center>'''))


def findProcess(process, command="", isPid=False):
    from psutil import pids, Process

    if isinstance(process, int):
        if process in pids():
            return True
    else:
        for pid in pids():
            try:
                p = Process(pid)
                if process in p.name():
                    for arg in p.cmdline():
                        if command in str(arg):
                            return True if not isPid else str(pid)
                        else:
                            pass
                else:
                    pass
            except:
                continue

def installArgoTunnel():
    if checkAvailable(f"{HOME}/tools/argotunnel/cloudflared"):
        return
    else:
        import os
        from shutil import unpack_archive
        from urllib.request import urlretrieve
        
        os.makedirs(f'{HOME}/tools/argotunnel/', exist_ok=True)
        aTURL = findPackageR("cloudflare/cloudflared", "cloudflared-linux-amd64")
        urlretrieve(aTURL, f'{HOME}/tools/argotunnel/cloudflared')
        # unpack_archive('cloudflared.tgz',
        #   f'{HOME}/tools/argotunnel')
        os.chmod(f'{HOME}/tools/argotunnel/cloudflared', 0o755)
        # os.unlink('cloudflared.tgz')

def installNgrok():
    if checkAvailable("/usr/local/bin/ngrok"):
        return
    else:
        import os
        from zipfile import ZipFile
        from urllib.request import urlretrieve

        ngURL = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip"
        urlretrieve(ngURL, 'ngrok-amd64.zip')
        with ZipFile('ngrok-amd64.zip', 'r') as zip_ref:
            zip_ref.extractall('/usr/local/bin/')
        os.chmod('/usr/local/bin/ngrok', 0o755)
        os.unlink('ngrok-amd64.zip')

def installAutoSSH():
    if checkAvailable("/usr/bin/autossh"):
        return
    else:
        runSh("apt-get install autossh -qq -y")



def runSh(args, *, output=False, shell=False, cd=None):
    import subprocess, shlex

    if not shell:
        if output:
            proc = subprocess.Popen(
                shlex.split(args), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cd
            )
            while True:
                output = proc.stdout.readline()
                if output == b"" and proc.poll() is not None:
                    return
                if output:
                    print(output.decode("utf-8").strip())
        return subprocess.run(shlex.split(args), cwd=cd).returncode
    else:
        if output:
            return (
                subprocess.run(
                    args,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    cwd=cd,
                )
                .stdout.decode("utf-8")
                .strip()
            )
        return subprocess.run(args, shell=True, cwd=cd).returncode

def loadingAn(name="cal"):
      from IPython.display import HTML

      if name == "cal":
          return display(HTML('<style>.lds-ring {   display: inline-block;   position: relative;   width: 34px;   height: 34px; } .lds-ring div {   box-sizing: border-box;   display: block;   position: absolute;   width: 34px;   height: 34px;   margin: 4px;   border: 5px solid #cef;   border-radius: 50%;   animation: lds-ring 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;   border-color: #cef transparent transparent transparent; } .lds-ring div:nth-child(1) {   animation-delay: -0.45s; } .lds-ring div:nth-child(2) {   animation-delay: -0.3s; } .lds-ring div:nth-child(3) {   animation-delay: -0.15s; } @keyframes lds-ring {   0% {     transform: rotate(0deg);   }   100% {     transform: rotate(360deg);   } }</style><div class="lds-ring"><div></div><div></div><div></div><div></div></div>'))
      elif name == "lds":
          return display(HTML('''<style>.lds-hourglass {  display: inline-block;  position: relative;  width: 34px;  height: 34px;}.lds-hourglass:after {  content: " ";  display: block;  border-radius: 50%;  width: 34px;  height: 34px;  margin: 0px;  box-sizing: border-box;  border: 20px solid #dfc;  border-color: #dfc transparent #dfc transparent;  animation: lds-hourglass 1.2s infinite;}@keyframes lds-hourglass {  0% {    transform: rotate(0);    animation-timing-function: cubic-bezier(0.55, 0.055, 0.675, 0.19);  }  50% {    transform: rotate(900deg);    animation-timing-function: cubic-bezier(0.215, 0.61, 0.355, 1);  }  100% {    transform: rotate(1800deg);  }}</style><div class="lds-hourglass"></div>'''))

def textAn(TEXT, ty='d'):
      from IPython.display import HTML

      if ty == 'd':
            return display(HTML('''<style>@import url(https://fonts.googleapis.com/css?family=Raleway:400,700,900,400italic,700italic,900italic);#wrapper {   font: 17px 'Raleway', sans-serif;animation: text-shadow 1.5s ease-in-out infinite;    margin-left: auto;    margin-right: auto;    }#container {    display: flex;    flex-direction: column;    float: left;     }@keyframes text-shadow { 0% 20% {          transform: translateY(-0.1em);        text-shadow:             0 0.1em 0 #0c2ffb,             0 0.1em 0 #2cfcfd,             0 -0.1em 0 #fb203b,             0 -0.1em 0 #fefc4b;    }    40% {          transform: translateY(0.1em);        text-shadow:             0 -0.1em 0 #0c2ffb,             0 -0.1em 0 #2cfcfd,             0 0.1em 0 #fb203b,             0 0.1em 0 #fefc4b;    }       60% {        transform: translateY(-0.1em);        text-shadow:             0 0.1em 0 #0c2ffb,             0 0.1em 0 #2cfcfd,             0 -0.1em 0 #fb203b,             0 -0.1em 0 #fefc4b;    }   }@media (prefers-reduced-motion: reduce) {    * {      animation: none !important;      transition: none !important;    }}</style><div id="wrapper"><div id="container">'''+TEXT+'''</div></div>'''))
      elif ty == 'twg':
            textcover = str(len(TEXT)*0.55)
            return display(HTML('''<style>@import url(https://fonts.googleapis.com/css?family=Anonymous+Pro);.line-1{font-family: 'Anonymous Pro', monospace;    position: relative;   border-right: 1px solid;    font-size: 15px;   white-space: nowrap;    overflow: hidden;    }.anim-typewriter{  animation: typewriter 0.4s steps(44) 0.2s 1 normal both,             blinkTextCursor 600ms steps(44) infinite normal;}@keyframes typewriter{  from{width: 0;}  to{width: '''+textcover+'''em;}}@keyframes blinkTextCursor{  from{border-right:2px;}  to{border-right-color: transparent;}}</style><div class="line-1 anim-typewriter">'''+TEXT+'''</div>'''))

class LocalhostRun:
  def __init__(self,port,id=None,interval=30,retries=30):
    import os
    filePath = "/usr/local/sessionSettings/localhostDB.json"
    if not os.path.exists(filePath):
      os.makedirs(filePath[:-16], exist_ok=True)
      open(filePath, 'w').close()
    installAutoSSH()
    if not id:id=str(uuid.uuid4())[:8]
    self.connection=None
    self.id=id
    self.port=port
    self.interval=interval
    self.retries=retries

  def start(self):
    if self.connection:self.connection.kill()
    self.connection=Popen(f"ssh -R 80:localhost:{self.port} {self.id}@ssh.localhost.run -o StrictHostKeyChecking=no".split(), stdout=PIPE, stdin=PIPE)
    try:
      return re.findall("http://(.*?.localhost.run)",self.connection.stdout.readline().decode("utf-8"))[0]
    except:
      raise Exception(self.connection.stdout.readline().decode("utf-8"))

  def keep_alive(self):
    # if self.connection:self.connection.kill()
    import urllib
    try:
      localhostOpenDB = dict(accessSettingFile("localhostDB.json", v=False))
    except TypeError:
      localhostOpenDB = dict()

    if findProcess("autossh", f"80:localhost:{self.port}"):
      try:
        oldAddr = localhostOpenDB[str(self.port)]
        urllib.request.urlopen("http://"+oldAddr)
        return oldAddr
      except:
        pass
    for _ in range(2):
      self.connection=Popen(f"autossh -R 80:localhost:{self.port} {self.id}@ssh.localhost.run -o StrictHostKeyChecking=no -o ServerAliveInterval={self.interval} -o ServerAliveCountMax={self.retries}".split(),
        stdout=PIPE, stdin=PIPE, stderr=PIPE)
      #print("ssh -R 80:localhost:{self.port} {self.id}@ssh.localhost.run -o StrictHostKeyChecking=no -o ServerAliveInterval={self.interval} -o ServerAliveCountMax={self.retries}")
      try:
        newAddr = re.findall("(.*?.localhost.run)", self.connection.stdout.readline().decode("utf-8"))[0]
        localhostOpenDB[str(self.port)] = newAddr 
        accessSettingFile("localhostDB.json" , localhostOpenDB, v=False)
        return newAddr
      except:
        outs, errs = self.connection.communicate(timeout=15)
        self.connection.kill()
        # print(outs)
        # print(errs)
        if re.search(r"Permission\sdenied\s\(publickey\)", errs.decode("utf-8")):
          os.system("ssh-keygen -q -t rsa -N '' -f ~/.ssh/id_rsa")
          continue
        raise Exception(errs.decode("utf-8"))
      break

  def kill(self):
    self.connection.kill()

class ArgoTunnel:
  def __init__(self, port, proto='http', metrics=49589, interval=30, retries=30):
    import os
    filePath = "/usr/local/sessionSettings/argotunnelDB.json"
    if not os.path.exists(filePath):
      os.makedirs(filePath[:-17], exist_ok=True)
      open(filePath, 'w').close()
    
    #Installing argotunnel
    installArgoTunnel()

    self.connection=None
    self.proto=proto
    self.port=port
    self.metricPort=metrics
    self.interval=interval
    self.retries=retries

  # def start(self):
  #   if self.connection:self.connection.kill()
  #   # self.connection=Popen(f"ssh -R 80:localhost:{self.port} {self.id}@ssh.localhost.run -o StrictHostKeyChecking=no".split(), stdout=PIPE, stdin=PIPE)
  #   self.connection=Popen(f"/content/tools/argotunnel/cloudflared tunnel --url {self.proto}://0.0.0.0:{self.port} --logfile cloudflared.log".split(), stdout=PIPE, stdin=PIPE)
  #   try:
  #     return re.findall("https://(.*?.trycloudflare.com)",self.connection.stdout.readline().decode("utf-8"))[0]
  #   except:
  #     raise Exception(self.connection.stdout.readline().decode("utf-8"))

  def keep_alive(self):
    # if self.connection:self.connection.kill()
    import urllib, requests, re
    from urllib.error import HTTPError
    
    try:
      argotunnelOpenDB = dict(accessSettingFile("argotunnelDB.json", v=False))
    except TypeError:
      argotunnelOpenDB = dict()

    if findProcess("cloudflared", f"localhost:{self.metricPort}"):
      try:
        oldAddr = argotunnelOpenDB[str(self.port)]
        if requests.get("http://"+oldAddr).status_code == 200:
          return oldAddr
      except:
        pass

    self.connection=Popen(f"{HOME}/tools/argotunnel/cloudflared tunnel --url {self.proto}://0.0.0.0:{self.port} --logfile {HOME}/tools/argotunnel/cloudflared_{self.port}.log --metrics localhost:{self.metricPort}".split(),
      stdout=PIPE, stdin=PIPE, stderr=PIPE, universal_newlines=True)
    
    time.sleep(5)

    hostname = None
    for i in range(20):
      try:
        with urllib.request.urlopen(f"http://127.0.0.1:{self.metricPort}/metrics") as response:
            hostname = re.search(r'userHostname=\"https://(.+)\"',
             response.read().decode('utf-8'), re.MULTILINE)
            if not hostname:
              time.sleep(1)
              continue
            hostname = hostname.group(1)
            break
      except HTTPError:
        time.sleep(2)
        
    if not hostname:
      raise RuntimeError("Failed to get user hostname from cloudflared")
    
    argotunnelOpenDB[str(self.port)] = hostname
    accessSettingFile("argotunnelDB.json" , argotunnelOpenDB, v=False)
    return hostname

  def kill(self):
    self.connection.kill()

class jprq:
  def __init__(self, port, proto='http', ids=None):
    import os, uuid
    filePath = "/usr/local/sessionSettings/jprqDB.json"
    if not os.path.exists(filePath):
      os.makedirs(filePath[:-11], exist_ok=True)
      open(filePath, 'w').close()

    if not ids:self.ids=str(uuid.uuid4())[:12]
    #Installing jprq
    runSh("pip install jprq")

    self.connection=None
    self.proto=proto
    self.port=port

  def keep_alive(self):
    # if self.connection:self.connection.kill()
    import urllib, requests, re
    try:
      jprqOpenDB = dict(accessSettingFile("jprqDB.json", v=False))
    except TypeError:
      jprqOpenDB = dict()

    if findProcess("jprq", f"{self.port}"):
      try:
        oldAddr = jprqOpenDB[str(self.port)]
        if requests.get("http://"+oldAddr).status_code == 200:
          return oldAddr
      except:
        pass
    hostname = f"OneClickRun-{self.ids}"
    self.connection=Popen(f"jprq -s {hostname} {self.port}".split(),
      stdout=PIPE, stdin=PIPE, stderr=PIPE)
    
    time.sleep(3)

    # try:
    #   return re.findall("https://(.*?.jprq.live/)", self.connection.stdout.readline().decode("utf-8"))[0]
    # except:
    #   raise Exception(self.connection.stdout.readline().decode("utf-8"))
    hostname += ".jprq.live"
    jprqOpenDB[str(self.port)] = hostname
    accessSettingFile("jprqDB.json" , jprqOpenDB, v=False)
    return hostname

  def kill(self):
    self.connection.kill()

class PortForward:
  def __init__(self,connections,region=None,SERVICE="localhost",TOKEN=None,USE_FREE_TOKEN=None,config=None):
    c=dict()
    for con in connections:
      c[con[0]]=dict(port=con[1],proto=con[2])
    self.connections=c
    if config:config[1] = closePort(config[1])
    self.config = config
    if SERVICE=="ngrok":self.ngrok=ngrok(TOKEN,USE_FREE_TOKEN,connections,region,self.config)
    self.SERVICE = SERVICE
    

  def start(self,name,btc='b',displayB=True,v=True):
    from IPython.display import clear_output

    if self.SERVICE == "localhost":
        con=self.connections[name]
        port=con["port"]
        proto=con["proto"]
        if(proto=="tcp"):
          return self.ngrok.start(name,btc,displayB,v)
        else:
          if v:
              clear_output()
              loadingAn(name="lds")
              textAn("Starting localhost ...", ty="twg")
          data = dict(url="https://"+LocalhostRun(port).keep_alive())
          if displayB:
              displayUrl(data, btc)
          return data
    elif self.SERVICE == "ngrok":
        return self.ngrok.start(name,btc,displayB,v)
    elif self.SERVICE == "argotunnel":
        con=self.connections[name]
        port=con["port"]
        proto=con["proto"]
        if v:
          clear_output()
          loadingAn(name="lds")
          textAn("Starting Argo Tunnel ...", ty="twg")
        data = dict(url="https://"+ArgoTunnel(port, proto, closePort(self.config[1])).keep_alive())
        if displayB:
          displayUrl(data, btc)
        return data
    elif self.SERVICE == "jprq":
        con=self.connections[name]
        port=con["port"]
        proto=con["proto"]
        if v:
          clear_output()
          loadingAn(name="lds")
          textAn("Starting jprq ...", ty="twg")
        data = dict(url="https://"+jprq(port, proto).keep_alive())
        if displayB:
          displayUrl(data, btc)
        return data
        


class PortForward_wrapper(PortForward):
  def __init__(self,SERVICE,TOKEN,USE_FREE_TOKEN,connections,region,config):
    super(self.__class__,self).__init__(connections,region,SERVICE,TOKEN,USE_FREE_TOKEN,config)


def findPackageR(id_repo, p_name, tag_name=False, all_=False):
  import requests

  for rawData in requests.get(f"https://api.github.com/repos/{id_repo}/releases").json():
    if tag_name:
      if rawData['tag_name'] != tag_name:
        continue

    for f in rawData['assets']:
      if p_name == f['browser_download_url'][-len(p_name):]:
        rawData['assets'] = f 
        return f['browser_download_url'] if not all_ else rawData
  raise Exception("not found or maybe api changed!\n Try again with Change packages name")

def closePort(port):
  import socket
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    for _ in range(100):
      if s.connect_ex(('localhost', port)) == 0:
        port += 1
      else:
        return port
  raise Exception("Close port not found!")
