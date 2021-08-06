from flask import Flask, request, redirect, url_for, flash, jsonify,render_template
import numpy as np
import pandas as pd
import joblib as jbl
import json
import pyodbc,psycopg2



# CREATE FLASK APP INSTANCE
app = Flask(__name__,template_folder='D:/SAPIENZA/COMPANIES/ProceedIt/Flutter/vscode_projects/har_ml_component/app/templates/')

# ------------- ORIGINAL DATASET -------------------------------------------------------------

subset = pd.read_csv(r'D:\SAPIENZA\COMPANIES\ProceedIt\Flutter\vscode_projects\har_ml_component\datasets\subset_ch_copy.csv')

# CALCULATE MEAN & STANDARD DEVIATION OF ORIGINAL DATASET
def column_mean_std(dataset):
    
    means, std = list(),list()

    for col in dataset.loc[:,dataset.columns!='NUM']:

        means.append(round(dataset[col].mean(),3))
        std.append(round(dataset[col].std(),3))
        
    return means,std

# COLLECT MEAN & STANDARD DEVIATION OF ORIGINAL DATASET
means, std = column_mean_std(subset)

#--------------- PREPROCESSING USER INPUT -----------------------------------------------------
# STANDARDIZATION OF INPUT DATA

def standardize_data(input_data,means,std):
    
    scaled_data = []
    
    for i in range(len(input_data)):
        
        scaled_data.append((input_data[i] - means[i])/ std[i])
    
    return scaled_data

#------------- CONNECTION TO DATABASE ---------------------------------------------------------------

# MS SQL 
servername  = r'VICKEYS\SQLEXPRESS'
database    = 'proceedit_har'
myconnect   = pyodbc.connect('Driver= {SQL Server};Server='+servername+';Database = '+database+';Trusted_connection=yes')

# PostgreSQL LOCAL
servername_postgre = 'localhost'
database_postgre   = 'proceedit_har'
password_postgre   = '.'

# dyDATA Server
# servername_postgre = '18.184.42.152'
# database_postgre   = 'dyHEALTH_proceedit_har'
# password_postgre   = 'Proc017postgres'

username_postgre   = 'postgres'
port_postgre       = '5432'
myconnect_postgre  = psycopg2.connect(host=servername_postgre,dbname=database_postgre,user=username_postgre,password=password_postgre,port=port_postgre)

# UPDATE DATABASE MS SQL & POSTGRESQL

def update_database(collect_data,myconnect):

    try:
         # var_string = ','.join('?' * len(collect_data))
        var_string = ['?' for item in collect_data]
        query = 'INSERT INTO [proceedit_har].[dbo].[proceedit_webform_request](CHOL,CP,CIGS,YEARS,PAINEXER,RELREST,RESTECG,PROTO,OLDPEAK,CXMAIN,CA,THALDUR,THAL,THALTIME,LADDIST,RCAPROX,LADPROX,EXANG,THALACH,SLOPE,RLDV5E,OM1,NUM) VALUES (%s)' % ','.join(var_string)

        print('UPDATING MS-SQL DATABASE')
        cursor = myconnect.cursor()
        cursor.execute(query,tuple(collect_data))
        myconnect.commit()
        print('****')
        print('**********')
        print('****************')
        print('**********************')
        print('DATABASE UPDATED')
        # cursor.close()
        # myconnect.close()
        # print("MS SQL CONNECTION IS CLOSED ")

    except (Exception, pyodbc.Error) as Error :
        if(myconnect):
            print("INSERT OPERATION FAILED AT THE POSITION DUE TO THE ERROR", Error)
            

def update_database_postgre(collect_data,myconnect_postgre):

    try:
         # var_string = ','.join('?' * len(collect_data))
        var_string = ['%s' for item in collect_data]
        query = 'INSERT INTO proceedit_har.public.proceedit_webform_request(CHOL,CP,CIGS,YEARS,PAINEXER,RELREST,RESTECG,PROTO,OLDPEAK,CXMAIN,CA,THALDUR,THAL,THALTIME,LADDIST,RCAPROX,LADPROX,EXANG,THALACH,SLOPE,RLDV5E,OM1,NUM) VALUES (%s)' % ','.join(var_string)

        # query = 'INSERT INTO proceedit_webform_request(CHOL,CP,CIGS,YEARS,PAINEXER,RELREST,RESTECG,PROTO,OLDPEAK,CXMAIN,CA,THALDUR,THAL,THALTIME,LADDIST,RCAPROX,LADPROX,EXANG,THALACH,SLOPE,RLDV5E,OM1,NUM) VALUES (%s)' % ','.join(var_string)

        print('UPDATING POSTGRESQL DATABASE')
        cursor = myconnect_postgre.cursor()
        cursor.execute(query,tuple(collect_data))
        myconnect_postgre.commit()
        print('****')
        print('**********')
        print('****************')
        print('**********************')
        print('DATABASE UPDATED')
        # cursor.close()
        # myconnect_postgre.close()
        # print("POSTGRESQL CONNECTION IS CLOSED ")
       
    except (Exception, psycopg2.Error) as Error :
        if(myconnect_postgre):
            print("INSERT OPERATION FAILED AT THE POSITION DUE TO THE ERROR", Error)


#--------------- COLLECT & COMPARE THE MODEL OUTPUT ------------------------------------------------------------
# THRESHOLD SET TO 50 PERCENT 

def collect_output(value1,value2):
    if value1 > 0.50:
        return 0
    else:
        return 1

# COLLECTING EACH FEATURE & COMBINING WITH OUTPUT

def collect_data(input_data,prediction_output):

    collect_data = []

    for i in input_data:
        collect_data.append(i)

    collect_data.append(float(collect_output(prediction_output[0][0],prediction_output[0][1])))

    print('PRINTING FINAL COLLECTED DATA')
    print(collect_data)

    return collect_data


#--------------- FLASK APPLICATION ---------------------------------------------------------

@app.route('/')
@app.route('/home')

def home():
    return render_template('main.html')

@app.route('/request_webform',methods=['POST'])
def heart_risk_webform():

    # REQUEST RECEIVED FROM FLASK APP
    print('REQUEST RECEIVED FROM FLASK WEB APPLICATION')
    input_data = [float(x) for x in request.form.values()]

    # CONVERTING THE INPUT DATA INTO 2-D ARRAY
    scaling_input = np.array([input_data])

    # STANDARDIZATION OF INPUT DATA & RESCALING INTO 1 BY 22 DIMENSIONAL ARRAY
    scaled_input = standardize_data(scaling_input,means,std)
    scaled_input = np.array(scaled_input).reshape(-1,22)

    # PREDICTIONS
    prediction_output = model_output.predict_proba(scaled_input)

    # COLLECTING EACH FEATURE & COMBINING WITH OUTPUT
    combined_data = collect_data(input_data,prediction_output)

    # UPDATE COLLECTED DATA TO THE DATABASE
    try:
        update_database_postgre(combined_data,myconnect_postgre)
        print('......')
        print('..........')
        print('................')
        print('..........................')
        update_database(combined_data,myconnect)
    except:
        print('CONNECTION TO DATABASE FAILED')

    # Rendering the results to HTML WEB PAGE
    return render_template('main.html',
    prediction_text = """PROBABILITY OF NO DISEASE : {} % |
                         PROBABILITY OF DISEASE    : {} % """.format(round(prediction_output[0][0],2)*100,round(prediction_output[0][1],2)*100))  



@app.route('/request_api',methods=['POST'])
def heart_risk_api():

    # REQUEST RECEIVED FROM API
    api_input = request.get_json()
    scaling_input = [sublist for mainlist in api_input for sublist in mainlist]
    print('REQUEST FROM OTHER APIs')
    print(scaling_input)

    # STANDARDIZATION OF INPUT DATA & RESCALING INTO 1-BY-22 DIMENSIONAL ARRAY
    scaled_input = standardize_data(scaling_input,means,std)
    scaled_input = np.array(scaled_input).reshape(-1,22)
    print('SCALED API INPUT')
    print((scaled_input))

    # PREDICTIONS
    prediction_output = model_output.predict_proba(scaled_input)
    prediction_to_api_request = np.array2string(model_output.predict_proba(scaled_input))

    # COLLECTING EACH FEATURE & COMBINING WITH OUTPUT
    combined_data = collect_data(scaling_input,prediction_output)

    # UPDATE COLLECTED DATA TO THE DATABASE
    try:
        update_database_postgre(combined_data,myconnect_postgre)
        print('......')
        print('..........')
        print('................')
        print('..........................')
        update_database(combined_data,myconnect)
    except:
        print('CONNECTION TO DATABASE FAILED')
 
    # RETURNING THE PREDICTIONS TO API CALL

    return jsonify(prediction_to_api_request)

@app.route('/flutter_api',methods=['POST'])
def heart_risk_flutter_api():

    # REQUEST RECEIVED FROM FLUTTER API
    api_input = request.get_json()
    #scaling_input = [sublist for mainlist in api_input for sublist in mainlist]

    # CONVERTING THE FLUTTER API REQUEST INTO PYTHON LIST
    api_input = [float(i) for i in (list(api_input.values()))] 

    print('REQUEST COMING FROM FLUTTER APP')
    print(api_input)

    # STANDARDIZATION OF INPUT DATA & RESCALING INTO 1-BY-22 DIMENSIONAL ARRAY
    scaled_input = standardize_data(api_input,means,std)
    scaled_input = np.array(scaled_input).reshape(-1,22)

    print('SCALED API INPUT')
    print((scaled_input))

    # PREDICTIONS
    prediction_output = model_output.predict_proba(scaled_input)
    print('MODEL OUTPUT')
    print(prediction_output)
    # print('ACTUAL MODEL OUTPUT')
    # print(tensor_output.predict_proba(scaled_input))


    # SENDING JSON RESPONSE TO FLUTTER APPLICATION
    flask2flutter_data = {}
    flask2flutter_data['NoDiseaseProb'] = round(prediction_output[0][0],1)*100
    flask2flutter_data['DiseaseProb'] = round(prediction_output[0][1],1)*100

    # flask2flutter_data['NoDiseaseProb'] = round(prediction_output[0][0],1)*100
    # flask2flutter_data['DiseaseProb'] = 100 - round(prediction_output[0][0],1)*100

    flask2flutter_data = json.dumps(flask2flutter_data)
    # prediction_to_flutter_api_request = np.array2string(model_output.predict_proba(scaled_input))

    # COLLECTING EACH FEATURE & COMBINING WITH OUTPUT
    combined_data = collect_data(api_input,prediction_output)

    # UPDATE COLLECTED DATA TO THE DATABASE
    try:
        print('-----------------------------')
        update_database_postgre(combined_data,myconnect_postgre)
        print('-----------------------------')
        print('-----------------------------')
        update_database(combined_data,myconnect)
    except:
        print('CONNECTION TO DATABASE FAILED')
 
    # RETURNING THE PREDICTIONS TO API CALL

    return jsonify(flask2flutter_data)

if __name__ == '__main__':

    # LOAD MODEL
    load_model = 'D:/SAPIENZA/COMPANIES/ProceedIt/Flutter/vscode_projects/har_ml_component/joblib_files/proceedit_ml_heart_risk_pred.sav'
    model_output = jbl.load(load_model)

    # NEURAL NETWORK
    # tensor_model = 'D:/SAPIENZA/COMPANIES/ProceedIt/Flutter/vscode_projects/har_ml_component/joblib_files/harp_orig_model.h5'
    # tensor_output = tensorflow.keras.models.load_model(tensor_model)

    
    # RUN THE APP
    app.run(debug=True)




