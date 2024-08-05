import pandas as pd
from sqlalchemy import create_engine
from sklearn import linear_model


class AgentTrainer:

    def __init__(self,latV,longV):
        self.latV = latV
        self.longV = longV


    def preprocessData(self,latV,longV):

        # Connects to the local database
        engine = create_engine("mysql+mysqlconnector://root@localhost/stations")
        connection = engine.connect()

        # Loads the table containing the data
        table = pd.read_sql_table("("+str(self.latV)+"),("+str(self.longV)+")",connection)
        table = table.sample(frac=1).reset_index(drop=True)

        return table
    
    
    def trainModel(self,table):

        # Defines which variables are parameters and which is the output
        X = table[["daylight_duration","temperature_2m","relative_humidity_2m","dew_point_2m","precipitation_probability","cloud_cover","wind_speed_10m"]]
        Y = table["shortwave_radiation_instant"]

        # Creates the linear regression model, fit it with the training data and then run it  
        reg = linear_model.LinearRegression()
        reg.fit(X,Y)                                    
  
        return reg
    

    def modelPredictions(self,reg,testSet):
        
        # Returns the set of predicted Y values for the test set passed into the function as a parameter
        predY = reg.predict(testSet)
        return predY
    

    def trainerFunction(self,testSet):

        latV = self.latV
        longV = self.longV

        # Calls the preprocessing method in order to retrieve the required data from the local database, shuffle it and then return it
        table = self.preprocessData(latV,longV)

        # Calls the training method to train the model, which is then returned
        model = self.trainModel(table)

        # Calls the predictions method to recieve predictions using the testSet being passed into it
        predictions = self.modelPredictions(model,testSet)

        return predictions

 