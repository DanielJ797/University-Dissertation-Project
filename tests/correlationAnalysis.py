from linear_regression_model import AgentTrainer
from data_collection_model import LocationData
from datetime import datetime
import random
from dateutil.relativedelta import relativedelta
import numpy as np


def test_feature_correlation():

    randomLoc = randomCoords()
    example_lat = randomLoc[0]
    example_long = randomLoc[1]

    agent_trainer = AgentTrainer(example_lat,example_long)
    preprocessed_data = agent_trainer.preprocess_data(float(example_lat),float(example_long))

    preprocessed_dataX = preprocessed_data.drop(columns='shortwave_radiation_instant')
    preprocessed_dataY = preprocessed_data['shortwave_radiation_instant']
    

    for i in preprocessed_dataX.columns.tolist():
                r = np.corrcoef(preprocessed_dataX[i], preprocessed_dataY)[0, 1]
                print(i + ": "+str(r))
        


def randomCoords():

    example_lat = random.uniform(-90,90)
    example_long = random.uniform(-180,180)
    example_lat = round(example_lat,4)
    example_long = round(example_long,4)

    # Calculates the first date of the traiing set 
    currentD = datetime.now()
    newCurrentD = currentD.strftime('%Y-%m-%d')
    startD = currentD - relativedelta(months=5)
    newStartD = startD.strftime('%Y-%m-%d')

    # Retrievs the data that is needed to train the model
    location_instance = LocationData(example_lat,example_long,str(newCurrentD),str(newStartD))
    
    forecastData = location_instance.getSunData(example_lat,example_long,str(newCurrentD),str(newStartD))
    
    return [example_lat,example_long]

        