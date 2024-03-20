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
            
    def get_rooms(self):
        self.update()
        response = self.data
        if response and "PAYL" in response and response["PAYL"] and "rooms" in response["PAYL"] and response["PAYL"]["rooms"]:
            roomlist = response["PAYL"]["rooms"]
            ordered_rooms = {}
            for room_dict in roomlist:
                """if not api_version or int(entry["api_version"]) == api_version:
                    if ((not only_responding) 
                        or int(entry["api_version"]) == 1 and bool(entry["controller_metrics"]["is_responding"])
                        or int(entry["api_version"]) == 2 and bool(entry["controller_metrics"]["responding"])):
                        roomdict[entry["room"]] = entry
                        roomdict[entry["room"]].pop("room")
                        if int(entry["api_version"]) == 1 and bool(entry["controller_metrics"]["is_responding"]):
                            roomdict[entry["responding"]] = roomdict[entry["room"]].pop("is_responding")"""
                if not room_dict:
                    print(f"Error: Response {room_dict} is has None-Type!")
                else:
                    key = room_dict["room"]
                    ordered_rooms[key] = room_dict
                    ordered_rooms[key].pop("room")
                    # Translate responding key from API v.1
                    if "controller_metrics" in ordered_rooms[key] and ordered_rooms[key]["controller_metrics"]:
                        if "is_responding" in ordered_rooms[key]["controller_metrics"]:
                            responding = 1 if ordered_rooms[key]["controller_metrics"]["is_responding"] else 0
                            ordered_rooms[key]["controller_metrics"].pop("is_responding")
                            ordered_rooms[key]["controller_metrics"]["responding"] = responding
                    #print(f'Room {key} is {"responding" if responding else "not responding"}')
                       
            return ordered_rooms
        
    def stop(self):
        self.connector.stop()