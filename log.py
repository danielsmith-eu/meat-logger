# Copyright (c) 2013, Daniel Alexander Smith
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import logging
import httplib
import sys
import cjson
import base64
import os
import uuid
import time
from ws4py.client.threadedclient import WebSocketClient

class MeatLoggerClient(WebSocketClient):

    def opened(self):
        pass

    def closed(self, code, reason=None):
        pass

    def received_message(self, m):
        msg = "{0}".format(m)
        if msg[0:3] == "2::":
            logging.error("Replying to heartbeat.")
            self.send("2::")
        elif msg[0:4] == "5:::":
            json = msg[4:]
            print json
            data = cjson.decode(json)
            #key = data['args'][0]['chat']['key']
            gif_dataurl = data['args'][0]['chat']['value']['media']
            preamble = "data:image/gif;base64,"
            if gif_dataurl.startswith(preamble):
                git_base64 = gif_dataurl[len(preamble):]
                gif_bytes = base64.b64decode(git_base64)
                fn = "{0}-{1}".format(int(time.time()), uuid.uuid1())
                f = open("gifs/{0}.gif".format(fn), "w")
                f.write(gif_bytes)
                f.close()
            else:
                logging.error("Couldn't decode GIF that preambled with: {0}".format(gif_dataurl[0:len(preamble)]))
            sys.stdout.flush()
        else:
            logging.error("Something weird happened: {0}".format(msg))

class MeatLogger:

    def __init__(self, hostname):
        self.hostname = hostname
        if not os.path.exists("gifs"):
            os.mkdir("gifs")

    def log(self) :
        conn  = httplib.HTTPSConnection(self.hostname)
        conn.request('GET','/socket.io/1/')
        resp  = conn.getresponse() 
        respline = resp.read()
        logging.error(respline)
        hskey = respline.split(':')[0]

        while True:
            ws = MeatLoggerClient('wss://{0}/socket.io/1/websocket/{1}'.format(self.hostname, hskey), protocols=['http-only', 'chat'])
            ws.connect()
            ws.run_forever()

hostname = "chat.meatspac.es"
ml = MeatLogger(hostname)
ml.log()

