import base64

import tensorflow as tf
import numpy as np

# KAFKA CONSUMER
from kafka import KafkaConsumer
from json import loads


model = tf.keras.models.load_model('models/sap_64_64_64')
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


# def predictor(event, context):
    # pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    # print(pubsub_message)
def predictor(message):
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
    








def main():
    consumer = KafkaConsumer(
        'sensors_data',
        bootstrap_servers=['127.0.0.1:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='pyconsumer',
        value_deserializer=lambda x: x.decode('utf-8')
    )

    print("Start reading")
    for message in consumer:
        message = message.value
        # collection.insert_one(message)
        print('Consumed {}'.format(message))
        predictor(message)


if __name__ == "__main__":
    # execute only if run as a script
    main()