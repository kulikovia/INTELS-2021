import xml.etree.ElementTree as xml
import random
import numpy as np
from random import randrange
from datetime import datetime
from datetime import timedelta
import csv

def random_date(start, end):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)

d1 = datetime.strptime('4/29/21 00:00:00', '%m/%d/%y %H:%M:%S')
d2 = datetime.strptime('4/30/21 23:59:59', '%m/%d/%y %H:%M:%S')


Max_Devices = 7
Prediction_date = '2021-04-29'

SPARQL_path = "C:/Blazegraph/1"

class rule:

    def start(self, interval_id, parameter, mean, deviation):
        self.interval_id = interval_id
        self.parameter = parameter
        self.mean = mean
        self.deviation = deviation

class policy:

    def start(self, context_id, rule_id, action):
        self.context_id = context_id
        self.rule_id = rule_id
        self.action = action

class context_events:

    def start(self, context_id, traffic, devices):
        self.context_id = context_id
        self.traffic = traffic
        self.devices = devices

def createXML():
    """
    Создаем XML файл.
    """

#Read context events criteria
    i = 0
    context_criteria = []
    with open('Context_events.csv') as f_obj:
        reader = csv.DictReader(f_obj, delimiter=',')
        for line in reader:
            context_criteria.append(context_events())
            context_criteria[i].context_id = line["CONTEXT_ID"]
            context_criteria[i].traffic = line["TRAFFIC"]
            context_criteria[i].devices = line["DEVICES"]
            i = i + 1

# Read Policies
    i = 0
    policies = []
    with open('Policies.csv') as f_obj:
        reader = csv.DictReader(f_obj, delimiter=',')
        for line in reader:
            policies.append(policy())
            policies[i].context_id = line["CONTEXT_ID"]
            policies[i].rule_id = line["RULE_ID"]
            policies[i].action = line["ACTION"]
            i = i + 1

# Read Rules
    i = 0
    rules = []
    with open('Device_rules.csv') as f_obj:
        reader = csv.DictReader(f_obj, delimiter=',')
        for line in reader:
            rules.append(rule())
            rules[i].interval_id = line["INTERVAL_ID"]
            rules[i].parameter = line["PARAMETER"]
            rules[i].mean = float(line["MEAN"])
            rules[i].deviation = float(line["DEVIATION"])
            #print('rules[',i,  '].interval_id = ', rules[i].interval_id, 'rules[', i, '].parameter = ', rules[i].parameter, 'rules[', i, '].mean = ', rules[i].mean, 'rules[', i, '].deviation = ', rules[i].deviation)
            i = i + 1

#Open SPARQL file
    f = open("Predictions.nq", "wt")

# Add header
    header = str("<?xml version='1.0' encoding='UTF-8'?>\n<rdf:RDF\nxmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'\nxmlns:vCard='http://www.w3.org/2001/vcard-rdf/3.0#'\nxmlns:tnmo='http://127.0.0.1/tnmo#'\n>")
    f.write(header)


# Add Prediction nodes
    c = 0
    #j - indexes for the network devices net:Devive_4 ... net:Device_7
    devices_lower = [4,5,6,7]
    for j in devices_lower:
        i = 0
        while i <= len(rules) - 2:
            Additional_info = []
            timestamp = Prediction_date + 'T' + str(rules[i].interval_id) +':00:00'
            traffic = np.random.normal(rules[i].mean, rules[i].deviation)
            devices = int(np.random.normal(rules[i+1].mean, rules[i+1].deviation))

            #Define context event
            k = 0
            while k <= len(context_criteria) - 1:
                if traffic <= float(context_criteria[k].traffic) and devices <= int(context_criteria[k].devices):
                    context_event = context_criteria[k].context_id
                    k = len(context_criteria)
                k = k + 1
            #print('context_event = ', context_event)

            #Apply policy
            k = 0
            while k <= len(policies) - 1:
                #print('policies[', k, '].context_id = ', policies[k].context_id)
                if policies[k].context_id == context_event:
                    #Aggrigation action (nothing is changed)
                    if policies[k].action == 'aggregation':
                        traffic = traffic
                        devices = devices
                    #Collection action (collecting additional monitoring data)
                    elif policies[k].action == 'collection':
                        Additional_info = 'Collected monitoring data has been added'
                    # Overload action (limit incoming traffic and number of connected devices)
                    elif policies[k].action == 'overload':
                        if traffic > 1000: traffic = 1000
                        if devices > 800: devices = 800
                    # Failure action (reject incoming traffic and number of connected devices)
                    elif policies[k].action == 'failure':
                        if traffic > 1500: traffic = 0
                        if devices > 850: devices = 0
                k = k + 1

            #Create prediction node for the selected device and hour.
            body = '''\n<rdf:Description rdf:about = 'http://127.0.0.1/Prediction_''' + str(c) + '''/'>\n<tnmo:hasPrediction><rdf:Description rdf:about = 'http://127.0.0.1/User_device_''' + str(j) +'''/'></rdf:Description></tnmo:hasPrediction>\n<tnmo:prediction_timestamp rdf:datatype = 'http://www.w3.org/2001/XMLSchema#datetime'>''' + str(timestamp)+ '''</tnmo:prediction_timestamp>\n<tnmo:has_wired_traffic_value>''' + str(traffic) + '''</tnmo:has_wired_traffic_value>\n<tnmo:MobileDeviceConnected>''' + str(devices) + '''</tnmo:MobileDeviceConnected>\n<tnmo:hasContext>''' +str(context_event) + ''' / ''' + str (Additional_info) + '''</tnmo:hasContext>\n</rdf:Description>'''
            f.write(body)
            c = c + 1
            i = i + 2
    f.write("\n</rdf:RDF>\n")

    f.close()

if __name__ == "__main__":
    createXML()
