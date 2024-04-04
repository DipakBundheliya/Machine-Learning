# -*- coding: utf-8 -*-
"""Customer-churn-prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1k8EpJaC7vuBoV3vKRD2pjYUYd9eG47wz
"""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler , FunctionTransformer
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split , GridSearchCV

df = pd.read_csv('/content/Telco-Customer-Churn.csv')

df.shape

df.head()

df.columns

# We have to remove customer id column
df.info()

df.drop('customerID' , inplace=True , axis=1)

# Collect categorical column
cat_column = []
for col in df.columns:
  if df[col].dtype == 'O':
    cat_column.append(col)

cat_column

for col in cat_column:
  print(df[col].unique())

# Total charges should be float
type(df['TotalCharges'][0])

df.dtypes

# We simply remove blank total charges column
df[df['TotalCharges'] != ' '].shape , df.shape

df = df[df['TotalCharges'] != ' ']

# This step will be added in preprocessing function
df['TotalCharges'] = df['TotalCharges'].astype(float)

cat_column.remove('TotalCharges')
cat_column

for col in cat_column:
  print(col , df[col].unique())

# In multilines ,TechSupport ,  ....  we should replce No phone service to No , because it doesnot make sense
df = df.replace({'No internet service' : 'No' , 'No phone service':'No'})

for col in cat_column:
  print(col , df[col].unique())

# Here we apply EDA and do feature engineering
df.info()

# sns.f
for col in df.columns:
  if df[col].dtype == 'O':
    plt.figure(figsize=(8,6))
    sns.countplot(df , x=col)

for col in df.columns:
  if df[col].dtype != 'O':
    plt.figure(figsize=(8,6))
    sns.boxplot(df[col])

# first we try implenet xgboost without making 3 category to 2 category of yes , no

len(cat_column) , pd.get_dummies(df , columns=cat_column , drop_first=True).shape[1]

encode_df = pd.get_dummies(df , columns=cat_column , drop_first=True , dtype=int)

encode_df.corr()['Churn_Yes']

encode_df.duplicated().sum()

encode_df= encode_df.drop_duplicates()

encode_df.columns

X = encode_df.drop('Churn_Yes' , axis=1)
y = encode_df['Churn_Yes']

# 1 means customer is churn(YES), 0 means not churned(NO)
y.value_counts()

X_train , X_test , y_train , y_test = train_test_split(X , y , test_size=0.2 , random_state=1 , stratify=y )

from xgboost import XGBClassifier

xgc = XGBClassifier()
xgc.fit(X_train , y_train)

y_pred = xgc.predict(X_test)

from sklearn.metrics import accuracy_score
accuracy_score(y_test , y_pred)

param_grid= {
    'learning_rate' : [0.1 , 0.2 , 0.3 , 0.4 ] ,
    'max_depth' : [ 3 , 4 , 5 , 6 , 7] ,
    'gamma' : [0.001 , 0.1 , 0.5 , 1] ,
    'n_estimators' : [90,100,120 , 130 , 140]
}
gsc = GridSearchCV(estimator = XGBClassifier() , param_grid=param_grid , cv=5 , n_jobs=-1)
gsc.fit(X,y)
gsc.best_params_ , gsc.best_score_

# Our model suffer overfitting
y_pred = xgc.predict(X_train)
accuracy_score(y_train , y_pred)

from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier()
rfc.fit(X_train , y_train)
y_pred = rfc.predict(X_test)
accuracy_score(y_test , y_pred) ,

# Our model suffer overfitting
y_pred = rfc.predict(X_train)
accuracy_score(y_train , y_pred)

params_grid = {
    'n_estimators' : [ 8 , 9 , 10 , 12 ],
    'max_depth' : [7 ,8 , 9 , 10],
    'min_samples_split' : [2,3,4 , 5]
}
gsc = GridSearchCV(RandomForestClassifier() , params_grid , n_jobs=-1 , cv=5 , scoring='f1' )

gsc.fit(X,y)

gsc.best_score_ , gsc.best_params_

# from sklearn.preprocessing import class
from sklearn.metrics import f1_score , confusion_matrix , classification_report
# We get this values
# (0.8018544935805993,
#  {'max_depth': 9, 'min_samples_split': 2, 'n_estimators': 12})
rfc_tune = RandomForestClassifier(max_depth=10 , min_samples_split=5 , n_estimators=10)
rfc_tune.fit(X_train , y_train)
y_pred = rfc_tune.predict(X_train)
accuracy_score(y_train , y_pred) , f1_score(y_train , y_pred)

confusion_matrix(y_train , y_pred)

print(classification_report(y_train , y_pred))

"""# **Generalized preprocessing function and create pipeline for model**"""

from sklearn.pipeline import Pipeline

df = pd.read_csv('/content/Telco-Customer-Churn.csv')

# Here we create generalize preprocessing function
def preprocessing(df):
  df.drop('customerID' , inplace=True , axis=1)

  # Collect categorical column
  cat_column = []
  for col in df.columns:
    if df[col].dtype == 'O':
      cat_column.append(col)

  # We simply remove blank total charges column
  df = df[df['TotalCharges'] != ' ']

  # This step will be added in preprocessing function
  df['TotalCharges'] = df['TotalCharges'].astype(float)
  cat_column.remove('TotalCharges')

  # In multilines ,TechSupport ,  ....  we should replce No phone service to No , because it doesnot make sense
  df = df.replace({'No internet service' : 'No' , 'No phone service':'No'})

  # Drop duplicates
  df= df.drop_duplicates()

  # Pandas OHE
  df = pd.get_dummies(df , columns=cat_column , drop_first=True , dtype=int)
  return df

custom_transformer = FunctionTransformer(preprocessing , validate=False)

preprocessor = ColumnTransformer(transformers=[
    ('preprocess' , custom_transformer , ['customerID'] )
],remainder='passthrough')

pipeline = Pipeline([
    ('preprocessor' , preprocessor),
    ('model' , RandomForestClassifier(max_depth=10 , min_samples_split=5 , n_estimators=10))
])

y_pred = pipeline.predict(X_test)
accuracy_score(y_test , y_pred)





df = pd.read_csv('/content/Telco-Customer-Churn.csv')
# Assume df is your original DataFrame, X_train and X_test are your feature matrices
# and y_train, y_test are your target vectors
# Example:
# df = pd.read_csv("your_data.csv")

# Split data into features (X) and target (y)
# Here, we assume that the target column is named 'target'
# Adjust this according to your actual column names
X = df.drop('Churn', axis=1)
y = df['Churn']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Preprocessing function
def preprocessing(df):
    df = df.copy()  # Make a copy to avoid modifying the original DataFrame

    # Perform preprocessing steps
    df.drop('customerID', inplace=True, axis=1)
    df = df[df['TotalCharges'] != ' ']
    df['TotalCharges'] = df['TotalCharges'].astype(float)
    df = df.replace({'No internet service': 'No', 'No phone service': 'No'})
    df = df.drop_duplicates()
    df = pd.get_dummies(df, drop_first=True, dtype=int)

    return df

# Custom transformer for preprocessing
preprocessing_transformer = FunctionTransformer(preprocessing, validate=False)

# Define pipeline
pipeline = Pipeline([
    ('preprocessor', preprocessing_transformer),
    ('model', RandomForestClassifier(max_depth=10, min_samples_split=5, n_estimators=10))
])

# Now you can fit the pipeline using X_train and y_train
pipeline.fit(X_train, y_train)

# Make predictions on the test data
predictions = pipeline.predict(X_test)

# Evaluate the model
# (evaluation code depends on the specific problem and metrics of interest)

X_train.shape, X_test.shape, y_train.shape, y_test.shape
