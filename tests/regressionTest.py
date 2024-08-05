import numpy as np
from linear_regression_model import AgentTrainer
from data_collection_model import LocationData
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sklearn.metrics import root_mean_squared_error, mean_absolute_error, r2_score
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure 


"""def test_model_training():
  
    randomLoc = randomCoords()
    example_lat = randomLoc[0]
    example_long = randomLoc[1]

    agent_trainer = AgentTrainer(example_lat,example_long)

    preprocessed_data = agent_trainer.preprocessData(float(example_lat),float(example_long))
        
    model = agent_trainer.trainModel(preprocessed_data)

    # Check if the model parameters have been updated
    assert model.coef_ is not None, "Model coefficients should not be None after training."
    assert len(model.coef_) > 0, "Model should have non-empty coefficients." """



def test_average_model_performance():

    example_lat = '19.076'
    example_long = '72.8777'
    totalScores = pd.DataFrame({'rmse':[],'r2':[],'mae':[],
                            'day':[],'temp':[],'humid':[],'dew':[],
                            'precip':[],'cloud':[],'wind':[]})

    agent_trainer = AgentTrainer(example_lat,example_long)
    
    for i in range(20):
        preprocessed_data = agent_trainer.preprocessData(float(example_lat),float(example_long))
        result = test_model_performance(example_lat,example_long,preprocessed_data)
        totalScores = pd.concat([totalScores,result], ignore_index=True)
        

    rmse = totalScores.loc[:, 'rmse'].mean()
    r2_score = totalScores.loc[:, 'r2'].mean()
    mae = totalScores.loc[:, 'mae'].mean()

    day = totalScores.loc[:, 'day'].mean()
    temp = totalScores.loc[:, 'temp'].mean()
    humid = totalScores.loc[:, 'humid'].mean()
    dew = totalScores.loc[:, 'dew'].mean()
    precip = totalScores.loc[:, 'precip'].mean()
    cloud = totalScores.loc[:, 'cloud'].mean()
    wind = totalScores.loc[:, 'wind'].mean()

    print("-----------------RESULTS----------------")
    print(rmse)
    print(r2_score)
    print(mae)
    print(day)
    print(temp)
    print(humid)
    print(dew)
    print(precip)
    print(cloud)
    print(wind)




def test_model_performance(example_lat,example_long,preprocessed_data):
    
    """randomLoc = randomCoords(example_lat,example_long)
    example_lat = randomLoc[0]
    example_long = randomLoc[1]"""

    

    agent_trainer = AgentTrainer(example_lat,example_long)
    
    training_data = preprocessed_data.iloc[:135,:]
    trainSetX = training_data.drop(columns='shortwave_radiation_instant')
    trainSetY = training_data['shortwave_radiation_instant']
    pmccs = []

    for i in trainSetX.columns.tolist():
                r = np.corrcoef(trainSetX[i], trainSetY)[0, 1]
                pmccs.append(r)

    testSet = preprocessed_data.iloc[135:,:]
    testSetX = testSet.drop(columns='shortwave_radiation_instant')
    testSetY = testSet['shortwave_radiation_instant']

    model = agent_trainer.trainModel(training_data)
    predictions = agent_trainer.modelPredictions(model, testSetX)

    """
    x = range(len(testSetY))
   
    # Creating the plot
    plt.figure(figsize=(10, 5))
    plt.plot(x, testSetY, label='Actual Values', marker='o')
    plt.plot(x, predictions, label='Predicted Values', linestyle='--', marker='x')

    # Customizing the labels (edit these as needed)
    plt.xlabel('Index of Samples')  # Edit for x-axis label
    plt.ylabel('Values')  # Edit for y-axis label
    plt.title('Comparison of Actual and Predicted Values')

    # Adding a legend
    plt.legend()

    # Display the plot
    plt.show()
    """


    # Calculate RMSE
    rmse = root_mean_squared_error(testSetY, predictions)
    #print("rmse: "+str(rmse))

    # Calculate R^2 score
    r_squared = r2_score(testSetY,predictions)
    #print("R2: "+str(r_squared))

    # Calculate MAE
    mae = mean_absolute_error(testSetY,predictions)
    #print("mae:" + str(mae))

    results = pd.DataFrame({'rmse':[rmse],'r2':[r_squared],'mae':[mae],
                            'day':[pmccs[0]],'temp':[pmccs[1]],'humid':[pmccs[2]],'dew':[pmccs[3]],
                            'precip':[pmccs[4]],'cloud':[pmccs[5]],'wind':[pmccs[6]]})

    return results



def test_graph_results():
    # Data from the user's model and Sharma model
    data = {
        "Location": ["London", "Paris", "New York", "Tokyo", "Los Angeles", "Mumbai", "Beijing"],
        "My_RMSE": [17.9124, 15.5923, 21.2631, 32.5766, 39.4963, 12.0720, 23.2226],
        "Sharma_RMSE": [28.2675, 26.8223, 56.9473, 38.4288, 37.4501, 25.5449, 28.8570],
        "My_MAE": [12.4386, 11.9099, 16.1732, 25.4082, 28.0832, 9.1404, 16.7239],
        "Sharma_MAE": [21.7145, 20.7463, 48.6144, 31.8951, 30.8858, 20.2291, 23.7148],
        "My_R2": [0.7993, 0.8789, 0.8924, 0.6628, 0.6984, 0.8932, 0.8131],
        "Sharma_R2": [0.5513, 0.6540, 0.1761, 0.5564, 0.6741, 0.5467, 0.6887]
    }

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Set the position of the bars on the x-axis
    r = range(len(df))

    # Bar width
    barWidth = 0.3

    # Plotting RMSE
    plt.figure(figsize=(14, 6))

    # Plot bars for My Model RMSE
    plt.bar(r, df['My_RMSE'], color='blue', width=barWidth, edgecolor='grey', label='My RMSE')

    # Plot bars for Sharma Model RMSE
    plt.bar([x + barWidth for x in r], df['Sharma_RMSE'], color='red', width=barWidth, edgecolor='grey', label='Sharma RMSE')

    # Add xticks on the middle of the group bars
    plt.xlabel('Location', fontweight='bold', fontsize=15)
    plt.xticks([r + barWidth for r in range(len(df))], df['Location'], fontsize=12)
    plt.ylabel('RMSE', fontweight='bold', fontsize=15)

    # Create legend & title and show the plot
    plt.title('RMSE Comparison', fontweight='bold', fontsize=16)
    plt.legend()
    plt.show()


    # Plotting MAE
    plt.figure(figsize=(14, 6))

    # Plot bars for My Model MAE
    plt.bar(r, df['My_R2'], color='purple', width=barWidth, edgecolor='grey', label='My R2')

    # Plot bars for Sharma Model MAE
    plt.bar([x + barWidth for x in r], df['Sharma_R2'], color='yellow', width=barWidth, edgecolor='grey', label='Sharma R2')

    # Add xticks on the middle of the group bars
    plt.xlabel('Location', fontweight='bold', fontsize=15)
    plt.xticks([r + barWidth for r in range(len(df))], df['Location'], fontsize=12)
    plt.ylabel('R2', fontweight='bold', fontsize=15)

    # Create legend & title and show the plot
    plt.title('R2 Comparison', fontweight='bold', fontsize=16)
    plt.legend()
    plt.show()

    # Plotting MAE
    plt.figure(figsize=(14, 6))

    # Plot bars for My Model MAE
    plt.bar(r, df['My_MAE'], color='green', width=barWidth, edgecolor='grey', label='My MAE')

    # Plot bars for Sharma Model MAE
    plt.bar([x + barWidth for x in r], df['Sharma_MAE'], color='orange', width=barWidth, edgecolor='grey', label='Sharma MAE')

    # Add xticks on the middle of the group bars
    plt.xlabel('Location', fontweight='bold', fontsize=15)
    plt.xticks([r + barWidth for r in range(len(df))], df['Location'], fontsize=12)
    plt.ylabel('MAE', fontweight='bold', fontsize=15)

    # Create legend & title and show the plot
    plt.title('MAE Comparison', fontweight='bold', fontsize=16)
    plt.legend()
    plt.show()


    """
    # Check if R^2 score is within an expected range
    assert 0.9 <= r_squared <= 1.0, "R^2 score is outside the best expected range."
    assert 0.9 <= r_squared <= 1.0, "R^2 score is outside a good expected range."
    assert 0.7 <= r_squared <= 1.0, "R^2 score is outside a sufficient expected range."
    """

    # ADD GRAPH TO SHOW THESE PERFORMANCE METRICS

"""
def test_modelPredictions():
    
    randomLoc = randomCoords()
    example_lat = randomLoc[0]
    example_long = randomLoc[1]

    agent_trainer = AgentTrainer(example_lat,example_long)
    preprocessed_data = agent_trainer.preprocessData(float(example_lat),float(example_long))



    # Known dataset and expected predictions
    X_test = np.array([[6], [7], [8], [9]])
    expected_predictions = np.array([11, 13, 15, 17])  # Assuming a simple model for illustration


    # Initialize the model and manually set coefficients for testing
    
    model = LinearRegressionModel()
    model.coefficients = np.array([2, 1])  # For a model y = 2x + 1

    # Generate predictions
    predictions = model.predict(X_test)

    # Compare each predicted value to the expected value
    np.testing.assert_array_almost_equal(predictions, expected_predictions, decimal=2, err_msg="Predictions do not match expected values.")
"""


"""
def test_preprocessData():

    randomLoc = randomCoords()
    example_lat = randomLoc[0]
    example_long = randomLoc[1]

    # Connect to the local database
    engine = create_engine("mysql+mysqlconnector://root:password1@localhost/stations")
    connection = engine.connect()

    # Load the datas the table containing the data
    unprocessed_data = pd.read_sql_table("("+str(example_lat)+"),("+str(example_long)+")",connection)

    agent_trainer = AgentTrainer(example_lat,example_long)
    preprocessed_data = agent_trainer.preprocessData(float(example_lat),float(example_long))
    
    assert not unprocessed_data.equals(preprocessed_data), "The data has not been preprocessed"
"""



def randomCoords(example_lat,example_long):

    """
    example_lat = random.uniform(-90,90)
    example_long = random.uniform(-180,180)
    example_lat = round(example_lat,4)
    example_long = round(example_long,4)
    """
    
    # Calculates the first date of the traiing set 
    currentD = datetime.now()
    newCurrentD = currentD.strftime('%Y-%m-%d')
    startD = currentD - relativedelta(months=5)
    newStartD = startD.strftime('%Y-%m-%d')

    # Retrievs the data that is needed to train the model
    location_instance = LocationData(example_lat,example_long,str(newCurrentD),str(newStartD))
    
    forecastData = location_instance.getSunData(example_lat,example_long,str(newCurrentD),str(newStartD))
    
    return [example_lat,example_long]
    


