# -*- coding: utf-8 -*-
"""Sales_prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1UqsBY8_NFld5peh9lu8XoY_htP--Ae_H
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn import set_config
from sklearn.preprocessing import FunctionTransformer
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error , mean_absolute_error , r2_score

"""# **Import walmart dataset**"""

df = pd.read_csv('/content/WALMART_SALES_DATA.csv')

df.head()

df.shape

df.isnull().sum()

df.info()

def do_preprocess(df):
  df['month'] = df['Date'].str.split('-' , expand=True)[1].astype('int')
  df['year'] = df['Date'].str.split('-' , expand=True)[2].astype('int')
  df.drop('Date' , axis=1 , inplace=True)
  return df
custom_transformer = FunctionTransformer(do_preprocess , validate=False)

preprocessor = ColumnTransformer(transformers=[
     ('preprocess' , custom_transformer , ['Date'])
 ] , remainder='passthrough')

"""# **We creates pipeline for our model**"""

pipeline = Pipeline([
    ('preprocessor' , preprocessor),
    ('model' , XGBRegressor())
])

set_config(display='diagram')
pipeline

import seaborn as sns
sns.set()
plt.figure(figsize=(6,6))
sns.countplot(x = 'year' , data = df)
plt.show()

plt.figure(figsize=(20,6))
sns.countplot(x = 'Store' , data = df)
plt.show()

plt.figure(figsize=(6,6))
sns.countplot(x = 'month' , data = df)
plt.show()

plt.figure(figsize=(6,6))
sns.countplot(x = 'Holiday_Flag' , data = df)
plt.show()

sns.distplot(df['Temperature'])

sns.distplot(df['Fuel_Price'])

sns.distplot(df['CPI'])

sns.distplot(df['Weekly_Sales'])

for col in df.columns:
  plt.figure()
  sns.boxplot(df[col])
# Outliers columns are ['WeeklySale' , 'Temperature' , 'Unemployment']

outliers_col = ['Weekly_Sales' , 'Temperature' , 'Unemployment']
for i in outliers_col:
  plt.figure()
  sns.distplot(df[i])

# we remove outliers or we can capping it with boundary value , we try both methods
# print(f'Initial we have {df.shape} size data') - (6435 , 9)
# First we try to remove outliers
new_df = df
for col in outliers_col:
  Q3 =  new_df[col].quantile(0.75)
  Q1 =  new_df[col].quantile(0.25)
  IQR = Q3 - Q1
  upper = Q3 + (1.5 * IQR)
  lower = Q1 - (1.5 * IQR)
  new_df = new_df.loc[(new_df[col] < upper) & (new_df[col] > lower) ]

new_df.shape , df.shape

new_df.corr()['Weekly_Sales']

X = new_df.drop('Weekly_Sales',axis=1)
y = new_df['Weekly_Sales']

X.info() , y.info()

X_train , X_test , y_train , y_test = train_test_split(X , y , test_size=0.2 , random_state=99)

X_train.shape , X_test.shape , y_train.shape , y_test.shape

pipeline.fit(X_train , y_train)

pipeline.score(X_test , y_test) , pipeline.predict(X_test)

y_pred = pipeline.predict(X_test)
error_rate = mean_absolute_error(y_test , y_pred)
error_rate

from sklearn.metrics import r2_score , make_scorer  , mean_squared_error , mean_absolute_error
# Without removing outliers our r2_score is 0.9625 , mae is 61193 , rmse is 104076
# After removing outliers our r2_score is 0.9710 , mae is 58205 , rmse is 91175
r2_score(y_test , y_pred)

# We have only 60k error rate
mean_absolute_error(y_test , y_pred)

np.sqrt(mean_squared_error(y_test , y_pred))

residuals = np.abs(np.array(y_test) - y_pred)

plt.figure(figsize=(20,6))
sns.histplot(residuals , bins=100)
plt.figure(figsize=(14,6))
sns.distplot(residuals)

# Here we try to scaling data
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

xgr2 = XGBRegressor()
# xgr2.fit(X_train_scaled , y_train , verbose=True)

# y_pred = xgr2.predict(X_test_scaled)
# r2_score(y_test , y_pred)

# mean_absolute_error(y_test , y_pred)

# We get no changes after scaling
# Now we do hyper parameter tunning
from sklearn.model_selection import GridSearchCV
param_grid= {
    'learning_rate' : [0.1 , 0.2 , 0.3 , 0.4 ] ,
    'max_depth' : [ 3 , 4 , 5 , 6 , 7] ,
    'gamma' : [0.001 , 0.1 , 0.5 , 1] ,
    'n_estimators' : [90,100,120 , 130 , 140]
}
gsc = GridSearchCV(estimator = XGBRegressor() , param_grid=param_grid , cv=5 , n_jobs=-1)
# gsc.fit(X_train , y_train)

# gsc.best_params_ , gsc.best_score_

"""**Conclusion** :           
We get 97% R2 score at prediction side
Our loss is around 60k                                                          
Scaling parameters does not give improvement                                    
Hyperparameter tunning does not give improvement
"""

# pipeline.predict()
X_train.head(1)

y_testing = pd.DataFrame({
    'Store':17,
    'Date' :'22-01-2012',
    'Holiday_Flag' : 0,
    'Temperature' : 54,
    'Fuel_Price' : 3.5,
    'CPI' : 130,
    'Unemployment' : 5}, index=[0])

pipeline.predict(y_testing)

"""# **Save the model**"""

import pickle
with open('pipeline.pkl' , 'wb') as f:
  pickle.dump(pipeline , f)

with open('pipeline.pkl' , 'rb') as f:
  pipeline_saved = pickle.load(f)

pipeline_saved.predict(X_test)
