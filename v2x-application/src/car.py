#Collects GPS Data and publishes via mqtt
#from Client import Client
#from Modem import Modem
import settings
import time
import threading
import paho.mqtt.client as mqtt
import json
import pandas as pd
from io import StringIO
from datetime import datetime
class Car:
    carID = 0
    #client: Client
    data_NN: pd.DataFrame
    data_LR: pd.DataFrame
    data_Combi: pd.DataFrame
    

    def __init__(self):
        self.carID = Car.carID
        Car.carID += 1
        #self.client = Client(random_values = isDummy, carID=self.carID)
        #self.client.connect()
        self.mqttClient = mqtt.Client()
        self.data_LR = pd.DataFrame()
        self.data_NN = pd.DataFrame()
        self.connect()
        self.evaluateRoute("./routes/route1.csv")

        #thread1 = threading.Thread(target=self.subscribe)
        #thread1.start()
        
        #self.connect()
        
        #thread1 = threading.Thread(target=self.connect)
        #thread2 = threading.Thread(target=self.client.main_loop)
        #thread1.start()
        #thread2.start()
        #thread2.start()
        #self.client.main_loop()
        print(f"Car {self.carID} initialized")
        


    def evaluateRoute(self,path:str):
        with open(path,'r') as file:
            csv_data = file.read()
        self.mqttClient.publish(f"request/car/{self.carID}",csv_data)
        #print("I published:")
        print(csv_data)
        self.subscribe()
        

    def connect(self):
        def on_connect(client,userdata, flags, rc):
            print("Connected with result code " + str(rc))
        def on_message(client, userdata, msg):
            #print("HHIIIII")
            message = str(msg.payload.decode("utf-8"))
            data = pd.read_csv(StringIO(msg.payload.decode('utf-8')))
            print("I am receiving from "+msg.topic.split('/')[-1]+":")
            print(data)
            if msg.topic.split('/')[-1] == "NN":
                self.data_NN = data
            elif msg.topic.split('/')[-1] == "LR":
                self.data_LR = data

            if not self.data_LR.empty and not self.data_NN.empty:
                self.data_NN = self.data_NN.rename(columns={'uplink':'NN_uplink','downlink':'NN_downlink','latency':'NN_latency'})
                self.data_LR = self.data_LR.rename(columns={'predicted Uplink':'LR_uplink','predicted Downlink':'LR_downlink','predicted Latency':'LR_latency'})
                self.data_Combi = pd.merge(self.data_LR, self.data_NN, on=['lat', 'lon'])
                current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
                save_name = f"result_{current_time}"
                self.data_Combi.to_csv(f'./results/{save_name}.csv')

# rename the columns of both dataframes

            
        self.mqttClient.on_connect = on_connect
        self.mqttClient.on_message = on_message
        self.mqttClient.connect(settings.broker, settings.port, 60)
        #self.mqttClient.subscribe(topic=f'response/car/{self.carID}')
        #self.mqttClient.loop_forever()
    def subscribe(self):
        self.mqttClient.subscribe(topic=f'response/car/{self.carID}/NN')
        self.mqttClient.subscribe(topic=f'response/car/{self.carID}/LR')
        self.mqttClient.loop_forever()
    def measure_and_pubish(self):
        m = self.modem.measure()

    def getID(self):
        return self.carID
    


car1 = Car()
#car2 = Car(True)
#car2 = Car()
#car3 = Car()
#time.sleep(1)
#thread2 = threading.Thread(target=car2.client.main_loop)
#thread2.start()
#time.sleep(3)
#thread3 = threading.Thread(target=car3.client.main_loop)
#thread3.start()



