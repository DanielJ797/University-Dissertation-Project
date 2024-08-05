import pandas as pd
from sqlalchemy import create_engine
from sklearn import linear_model


class AgentTrainer:

    def __init__(self,latV,longV):
        self.latV = latV
        self.longV = longV


    def preprocess_data(self,latV,longV):

        # Connect to the local database
        engine = create_engine("mysql+mysqlconnector://root:password1@localhost/stations")
        connection = engine.connect()

        # Load the datas the table containing the data
        table = pd.read_sql_table("("+str(self.latV)+"),("+str(self.longV)+")",connection)
        table = table.sample(frac=1).reset_index(drop=True)

        return table
    
    
    def train_model(self,table):

        # Define which variables are parameters and which is the output
        X = table[["date","temperature_2m","relative_humidity_2m","dew_point_2m","precipitation_probability","cloud_cover","wind_speed_10m"]]
        Y = table["shortwave_radiation_instant"]

        # Create the linear regression model, fit it with the training data and then run it  
        reg = linear_model.LinearRegression()
        reg.fit(X,Y)                                    # Change to trainX and trainY for tesing
  
        return reg
    

    def model_predictions(self,reg,testSet):
        
        predY = reg.predict(testSet)
        return predY
    

    def trainerFunction(self,testSet):

        latV = self.latV
        longV = self.longV

        table = self.preprocess_data(latV,longV)
        model = self.train_model(table)
        predictions = self.model_predictions(model,testSet)

        return predictions


        #parameters = ["temperature_2m","relative_humidity_2m","dew_point_2m","precipitation_probability","cloud_cover","wind_speed_10m"]
 
 #----------------------------------------------------------------------------------------------------------------
 
        """  FOR TESTING PURPOSES    

        
        parameter_combinations = []

        for i in range(len(parameters)+1):
            for combo in combinations(parameters, i):
                parameter_combinations.append(combo)
        
        parameter_combinations = parameter_combinations[1:]
        """
#----------------------------------------------------------------------------------------------------------------

        
        """
        # Define which variables are parameters and which is the output
        X = table[["daylight_duration","temperature_2m","relative_humidity_2m","dew_point_2m","precipitation_probability","cloud_cover","wind_speed_10m"]]
        Y = table["shortwave_radiation_instant"]
        """
        
    #----------------------------------------------------------------------------------------------------------------

        """  FOR TESTING PURPOSES 

        crossValSplit = int(floor((len(X.index)) * 0.8))
        testX = X.iloc[crossValSplit:]
        testY = Y.iloc[crossValSplit:]
        trainX = X.iloc[:crossValSplit]
        trainY = Y.iloc[:crossValSplit]


        CORRELATION TESTING FOR EACH PARAMETER

        for i in testX.columns.tolist():
                r = numpy.corrcoef(testX[i], testY)[0, 1]
                print(i + ": "+str(r))
        """
        

#----------------------------------------------------------------------------------------------------------------


        """                            DATA PROCESSING STAGE                                               """
        """
                                                        # Create he linear regression model, fit it with the training data and then run it  
        reg = linear_model.LinearRegression()
        reg.fit(X,Y)                                    #Change to trainX and trainY for tesing
        linear_model.LinearRegression()
        """

#----------------------------------------------------------------------------------------------------------------

        """  FOR TESTING PURPOSES  

        testPredY = reg.predict(testSet)
        testPredY = pd.DataFrame(testPredY, columns=["predicted"])
        testY = testY.to_frame(name="actual")

        testPredY = testPredY.reset_index(drop=True)
        testY = testY.reset_index(drop=True)

        resultTab = pd.concat([testPredY,testY], axis=1)

        rmse = mean_squared_error(testY,testPredY, squared=False)
        print(rmse)
        """

        #resultTab.to_csv('DUR - ' + str(rmse) + ' - ' + str(param),index=True)

#----------------------------------------------------------------------------------------------------------------

        # Generate a set of predicted values using the test
        #predY = reg.predict(testSet) 

        #resultTab = pd.concat([predY,Y], ignore_index=True)
        #rint(resultTab)

#----------------------------------------------------------------------------------------------------------------
        

        """for i in range(testY.index.size):
            print("predicted: "+str(predY[i])+"   actual: "+str(testY.iloc[i]))"""

        """currentD = datetime.now()
        startD = currentD + relativedelta(days=7)
        newCurrentD = currentD.strftime('%Y-%m-%d')
        newStartD = startD.strftime('%Y-%m-%d')"""

        #return predY

        