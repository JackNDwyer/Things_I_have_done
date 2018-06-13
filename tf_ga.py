#!/usr/bin/env python

import pandas as pd
import tensorflow as tf
import googleapi
import numpy as np
import argparse
import pdb

def to_xy(df, target):
   result = []
   for x in df.columns:
       if x != target:
           result.append(x)
   # find out the type of the target column.  Is it really this hard? :(
   target_type = df[target].dtypes
   target_type = target_type[0] if hasattr(target_type, '__iter__') else target_type
   # Encode to int for classification, float otherwise. TensorFlow likes 32 bits.
   if target_type in (np.int64, np.int32):
       # Classification
       dummies = pd.get_dummies(df[target])
       return df.as_matrix(result).astype(np.float32), dummies.as_matrix().astype(np.float32)
   else:
       # Regression
       return df.as_matrix(result).astype(np.float32), df.as_matrix([target]).astype(np.float32)

# Encode text values to dummy variables(i.e. [1,0,0],[0,1,0],[0,0,1] for red,green,blue)
def encode_text_dummy(df, name):
   dummies = pd.get_dummies(df[name])
   for x in dummies.columns:
       dummy_name = "{}-{}".format(name, x)
       df[dummy_name] = dummies[x]
   df.drop(name, axis=1, inplace=True)

# Encode text values to indexes(i.e. [1],[2],[3] for red,green,blue).
def encode_text_index(df, name):
   le = preprocessing.LabelEncoder()
   df[name] = le.fit_transform(df[name])
   return le.classes_

def create_train_input_fn():
   return tf.estimator.inputs.pandas_input_fn(
       x=traindf,
       y=label_train,
       batch_size=32,
       num_epochs=None, # Repeat forever
       shuffle=True,
       target_column = label)

def create_test_input_fn():
   return tf.estimator.inputs.pandas_input_fn(
       x=testdf,
       y=label_test,
       num_epochs=1, # Just one epoch
       shuffle=False,
       target_column = label)

if __name__ == '__main__':
   #if you only have a client_secrets.json file, plug that in for the path_to_credentials, otherwise put in your service account key
   parser = argparse.ArgumentParser(description='Python Program that grabs your GA data for you and does a bunch of cool predictions on it')
   parser.add_argument('-i','--view_id', help='VIEW_ID', required=True, action = 'store', dest = 'VIEW_ID', type = str)
   parser.add_argument('-c','--creds', help='Path to either service account credentials or clients_secrets, should end in .JSON file', required=True, action = 'store', dest = 'path_to_credentials', type = str)
   parser.add_argument('-s','--session_tok', help='Sessions token path, optional. if not provided, one will be created in the same directory as your credentials', required=False, default = '', action = 'store', dest = 'session_token_path', type = str)
   parser.add_argument('-d','--dim', help='ga dimensions in form ga:date, ga:campaign, etc.', required=True, action = 'store', dest = 'dimensions', type = str)
   parser.add_argument('-m','--metric', help='ga metrics in form ga:metric1,ga;metric2', required=True, action = 'store', dest = 'metrics', type = str)
   parser.add_argument('-l','--label', help='label column, for example -l bounce_rate', required=True, action = 'store', dest = 'label', type = str)
   args = parser.parse_args()

   #sample -d "ga:date,ga:campaign"
   #sample -m "ga:sessions,ga:bounces"
   #sample -i 52357388
   # sample -c "scripts/GA_DS_pipe/client_secrets.json"
   #if you do not have a session_token, then write the path you would like to store it in.
   #session_token_path  = str(args['session_tok'])
   path_to_credentials = str(args.path_to_credentials)
   session_token_path = str(args.session_token_path)
   label = str(args.label)
   if len(session_token_path) < 2:
       session_token_path = path_to_credentials.replace('client_secrets.json','session_token.json')

   try: #if you have a service account with admin access, this will access your data
       results = googleapi.main(path_to_credentials, dimensions, args.metrics, start_date = '7daysAgo', end_date='today')

   except:#if you don't have a service token with access, there is a roundabout way by using the client_secrets.json file
       service = googleapi.connect(path_to_credentials, session_token_path)
       results = googleapi.google_analytics_data(service, args.dimensions, args.metrics, args.VIEW_ID, start_date = '1daysAgo', end_date = 'today')
   #for all our dimensions and metrics, we make a list of them, as they'll become our columns names
   headers = []

   headers.extend(str(args.dimensions).split(','))
   headers.extend(str(args.metrics).split(','))
   headers = [x.split(':')[1] for x in headers]

   df = pd.DataFrame(results['rows'], columns=headers)
   headers.remove(label)
   df = df.convert_objects(convert_numeric = True)
   column_types = df.dtypes
   columns = {}
   column_names_list = []
   for i, column_name in enumerate(headers):
       if str(column_types[i]) in ['int64', 'float64', 'numeric']:
           columns[column_name] = tf.feature_column.numeric_column(column_name)
       else:
           #encode_text_dummy(df, label)

           if len(df[column_name].unique()) <= 20:
               columns[column_name] = tf.feature_column.categorical_column_with_vocabulary_list(column_name, df[column_name].unique())
           elif len(df[column_name].unique()) > 20 and len(df[column_name].unique()) < 100:
               columns[column_name] = tf.feature_column.categorical_column_with_hash_bucket(column_name,len(df[column_name].unique()))
           else:
               columns[column_name] = tf.feature_column.categorical_column_with_hash_bucket(column_name,len(df[column_name].unique())/2)
       column_names_list.append(columns[column_name])

   msk = np.random.rand(len(df)) < 0.7
   traindf = df.iloc[msk,:]
   testdf = df.iloc[~msk,:]
   label_train = traindf.pop(label)
   label_test = testdf.pop(label)

   sess = tf.Session()
   train_input_fn = create_train_input_fn()
   test_input_fn = create_test_input_fn()

   estimator = tf.estimator.LinearRegressor(column_names_list, model_dir='~/')
   # params = tf.contrib.tensor_forest.ForestHParams(
   #   num_classes=100, num_features=2,
   #   num_trees=FLAGS.num_trees, max_nodes=10)
   # graph_builder_class = tf.contrib.tensor_forest.RandomForestGraphs
   #   # Use the SKCompat wrapper, which gives us a convenient way to split
   #   # in-memory data like MNIST into batches.
   # estimator = estimator.SKCompat(random_forest.TensorForestEstimator(
   #   params, graph_builder_class=graph_builder_class,
   #   model_dir=model_dir))
   #figure out how to wrap in indicator or embedding
   # estimator = tf.estimator.DNNRegressor(
   # feature_columns=column_names_list,
   # hidden_units=[1024, 512, 256])
   estimator.train(train_input_fn, steps=15)



   predictions = estimator.predict(test_input_fn)
   i = 0
   for prediction in predictions:
       print prediction
       # true_label = label_test[i]
       # predicted_label = prediction['class_ids'][0]
       # # Uncomment the following line to see probabilities for individual classes
       # # print(prediction)
       # print("Example %d. Actual: %d, Predicted: %d" % (i, true_label, predicted_label))
       # i += 1
       # if i == 5: break
