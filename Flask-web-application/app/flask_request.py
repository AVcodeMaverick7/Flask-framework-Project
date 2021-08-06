import requests
import pandas as pd
import numpy as np
import json
from sklearn.preprocessing import StandardScaler, MinMaxScaler


url = 'http://127.0.0.1:5000/request_api'

dat = pd.read_csv(r'\har_ml_component\datasets\subset_ch_copy.csv')


X = dat.drop('NUM',axis=1)
X = X.values

# Just feeding a sample data
data = [(X[102]).tolist()] #23

print('PRINTING INPUT DATA')
print(data)

# Request object as JSON to the MODEL
j_data = json.dumps(data)

headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
r = requests.post(url, data=j_data, headers=headers)

print('---------------')
print(j_data)
print('RESPONSE CODE : {}'.format(r.status_code))
print('NO DISEASE PROBABILITY   : {} %'.format(round(float(r.json().strip('[]').split()[0]),2)*100))
print('DISEASE PROBABILITY      : {} %'.format(round(float(r.json().strip('[]').split()[1]),2)*100))