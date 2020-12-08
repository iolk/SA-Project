import base64

import tensorflow as tf
import numpy as np
from google.cloud import storage

def getFreq(id, data):
    val = sensor_confs[id][2] if data>=sensor_confs[id][0] else sensor_confs[id][1]
    return 60000/val

def getId(msg):
    sensor_id = ((int(msg)%10)-1)
    msg /= 10 
    sensor_id += ((int(msg)%10)-1)*2
    msg /= 10 
    sensor_id += ((int(msg)%10)-1)*6
    return sensor_id

def printPrice(freqs):
    f = sum(freqs)
    min_v = (tier_avg[0]*tier_price[0] + 0.0000004)*f
    best_tier = 0
    for i in range(1,6):
        if min_v > (tier_avg[i]*tier_price[i] + 0.0000004)*f:
            best_tier = i
            min_v = (tier_avg[i]*tier_price[i] + 0.0000004)*f
    print("Price per min: {}    |    Best tier: {}".format(min_v, best_tier))

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print('Blob {} downloaded to {}.'.format(
        source_blob_name,
        destination_file_name))

def makeModel():
    m = Sequential()
    m.add(LSTM(64, activation='relu', return_sequences=True, input_shape=(n_steps, n_features)))
    m.add(LSTM(64, return_sequences=True, activation='relu'))
    m.add(LSTM(64, activation='relu'))
    m.add(Dense(1))
    m.compile(optimizer='adam', loss='mse')
    return m

# Global variables so we don't have to reload it in case of warm invocations
model = None

sensors_data = [[] for i in range(10)]
tier_avg = [500, 300, 350, 320, 250, 220]
tier_price = [0.000000231, 0.000000463, 0.000000925, 0.000001650, 0.000002900, 0.000005800]
actual_freq = [0 for i in range(10)]
future_freq = [0 for i in range(10)]
sensor_confs = [
    [5,5000,20000],
    [20,5000,20000],
    [10,5000,20000],
    [10,5000,20000],
    [10,5000,20000],
    [5,5000,20000],
    [10,10000,60000],
    [10,10000,60000],
    [12,10000,60000],
    [5,10000,30000],
]





def predictor(event, context):
    global model
    if model is None:
        download_blob('ml_sap_bucket', 'sap_64_64_64.index', '/tmp/sap_64_64_64.index')
        download_blob('ml_sap_bucket', 'sap_64_64_64.data-00000-of-00001', '/tmp/sap_64_64_64.data-00000-of-00001')
        model = makeModel()
        model.load_weights('/tmp/sap_64_64_64')

    global sensors_data
    global tier_avg
    global tier_price
    global actual_freq
    global future_freq
    global sensor_confs
        
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    print(pubsub_message)
    
    sensor_id = getId(int(message.split("&")[0]))
    sensor_data =  float(message.split("&")[1])

    sensors_data[sensor_id].append(sensor_data)
    actual_freq[sensor_id] = getFreq(sensor_id, sensor_data)
    
    print("### ACTUAL ###")
    printPrice(actual_freq)
    print("")
    
    if(len(sensors_data[sensor_id])>=10):
        X_input = np.array(sensors_data[sensor_id][-10:])
        X_input = X_input.reshape((1, X_input.shape[0], 1))
        prediction = model.predict(X_input, verbose=0)[0][0]
        future_freq[sensor_id] = getFreq(sensor_id, prediction)
        # print(prediction)

        print("### FUTURE ###")
        printPrice(future_freq)
        print("")