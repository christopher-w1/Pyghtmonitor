from utils.wsconnector import WSConnector
from time import sleep
import json
import re

class Interfacer:
    def __init__(self, username: str, token: str, address: str = "wss://lighthouse.uni-kiel.de/websocket",
                 ignore_ssl_cert=False):
        self.username = username
        self.token = token
        self.address = address
        self.connector = WSConnector(username, token, address, on_msg=print(),
                                     ignore_ssl_cert=ignore_ssl_cert)
        self.ph_thread = None
        self.connector.start()
        
    def update(self):
        self.connector.send("GET", "")
        sleep(0.01)
        self.data = self.connector.data
        
    def streamloop(self):
        while True:
            #print(response)
            print(" ")
            #self.json_to_file(response)
            rooms=self.get_rooms()
            if rooms: print(rooms.keys())
            sleep(2)
            
    def get_rooms(self, only_responding=True, api_version=None):
        self.update()
        response = self.data
        if response:
            roomlist = response["PAYL"]["rooms"]
            roomdict = {}
            for entry in roomlist:
                if not api_version or int(entry["api_version"]) == api_version:
                    if ((not only_responding) 
                        or int(entry["api_version"]) == 1 and bool(entry["controller_metrics"]["is_responding"])
                        or int(entry["api_version"]) == 2 and bool(entry["controller_metrics"]["responding"])):
                        roomdict[entry["room"]] = entry
                        roomdict[entry["room"]].pop("room")
            return roomdict
        
    def stop(self):
        self.connector.stop()