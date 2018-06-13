import argparse
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder,CategoricalEncoder
#from pre_sklearn import CategoricalEncoder
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import roc_curve, mean_squared_error, accuracy_score
from collections import defaultdict
from sklearn.ensemble import (ExtraTreesClassifier, RandomForestClassifier,
                              AdaBoostClassifier, GradientBoostingClassifier)
from sklearn.svm import SVC
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
import matplotlib.pyplot as plt

#takes a df, a popped column that has all the labels, and the name of the label column
def pred(df,label_col,pred_col_name):
    #if our label is categorical, we want to set up classifiers
    if label_col.dtype == 'object':
        #print('categorical column')
        flag = 'obj'
        models1 = {
            'ExtraTreesClassifier': ExtraTreesClassifier(),
            'RandomForestClassifier': RandomForestClassifier(),
            'AdaBoostClassifier': AdaBoostClassifier(),
            'GradientBoostingClassifier': GradientBoostingClassifier(),
            'SVC': SVC()
                }

        params1 = {
            'ExtraTreesClassifier': { 'n_estimators': [16, 32] },
            'RandomForestClassifier': { 'n_estimators': [16, 32] },
            'AdaBoostClassifier':  { 'n_estimators': [16, 32] },
            'GradientBoostingClassifier': { 'n_estimators': [16, 32], 'learning_rate': [0.8, 1.0] },
            'SVC': [
                {'kernel': ['linear'], 'C': [1, 10]},
                {'kernel': ['rbf'], 'C': [1, 10], 'gamma': [0.001, 0.0001]},
                    ]
                        }
        lab_encoder = CategoricalEncoder(encoding='ordinal')
        #label_col = label_col
        lab = lab_encoder.fit_transform(label_col.values.reshape(-1,1))
        encoder = CategoricalEncoder(encoding='onehot')
#else set up regressors
    else:
        #print('numeric label')
        lab = label_col.copy()
        flag = 'num'
        models1 = {
            'LinearRegression': LinearRegression(),
            'Ridge': Ridge(),
            'Lasso': Lasso()
                    }

        params1 = {
            'LinearRegression': { },
            'Ridge': { 'alpha': [0.1, 1.0] },
            'Lasso': { 'alpha': [0.1, 1.0] }
            }
        encoder = CategoricalEncoder(encoding='onehot')
#find our object columns so we can encode them
    object_cols = df.select_dtypes(include='object').columns

    converted_df = df.copy()
    #we encode using an encoder from a future sklearn release.
    converted_df = pd.concat([converted_df.drop(object_cols, axis = 1),\
    pd.DataFrame(encoder.fit_transform(converted_df[object_cols]).todense())], axis = 1, ignore_index = True)
    #converted_df[object_cols] = encoder.fit_transform(converted_df[object_cols])

    best_mod = ''
    score = 0
    #iterate through our models. I'm using a GridSearchCV to find best parameters for each
    for key,model in models1.iteritems():
        mod = model
        #split the data and do a grid search to find best parameters
        x_train, x_test, y_train, y_test = train_test_split(converted_df, lab, test_size = .3)
        mod_cv = GridSearchCV(mod, params1[key], cv = 3)
        mod_cv.fit(x_train, y_train)

        #print("Tuned predictor paramters: {}".format(mod_cv.best_params_))
        prediction = mod_cv.predict(x_test)
        if flag == 'obj':
            new_score = accuracy_score(y_test, prediction)

            #label_col = lab_encoder.inverse_transform(label_col)
        else:
            new_score = mean_squared_error(y_test,prediction)

        if new_score > score:
            score=new_score
            best_mod = mod_cv
    full_df_to_predict = df.copy()
    #once we have the best model (as scored by either MSE or Accuracy Score),
    #we predict on it
    full_df_to_predict = pd.concat([full_df_to_predict.drop(object_cols, axis = 1),\
    pd.DataFrame(encoder.fit_transform(full_df_to_predict[object_cols]).todense())], axis = 1, ignore_index = True)
    if flag == 'obj':
        df['predicted'] = lab_encoder.inverse_transform(best_mod.predict(full_df_to_predict).reshape(-1,1))
    else:
        df['predicted'] = best_mod.predict(full_df_to_predict)

    #df[object_cols]=encoder.inverse_transform(df[object_cols])
    #we want to graph our results, so we use a bar chart for our classifier output
    #and a scatter for our regressor output
    df[pred_col_name] = label_col
    if flag == 'obj':
        mega_df = df.copy()
        mega_df['key1'] = 'prediction'
        mega_df['key2'] = 'label'

        label_group = mega_df[[pred_col_name,'key2']]
        pred_group = mega_df[['predicted','key1']]
        pred_group = pred_group.rename(columns = {'key1':'key2','predicted':pred_col_name})
        mega_df = label_group.append(pred_group)
        mega_df['count'] = 1
        mega_df = mega_df.groupby([pred_col_name,'key2']).sum().unstack('key2')
        mega_df.columns = mega_df.columns.droplevel()
        mega_df[mega_df['label']>mega_df['label'].quantile(.5)].plot(kind = 'bar')
        #print mega_df.groupby([pred_col_name,'key2']).sum().unstack('key2')
        plt.show()
        # plt.bar(df.index,df.Price)
        # plt.show()
    else:
        plt.scatter(df['sq__ft'],df['predicted'])
        plt.scatter(df['sq__ft'],df[pred_col_name])
        plt.show()
    return best_mod,encoder,lab_encoder;





if __name__ == '__main__':
    #using argparser, we tell our program where to find relevant data, and what columns to use
    parser = argparse.ArgumentParser(description='Python Program that runs predictions and graphs them')
    parser.add_argument('-p','--path', help='path to our csv', required=True, action = 'store', dest = 'path', type = str)
    parser.add_argument('-i','--ind', help='independent variables we want to use in our regression, comma separated with no spaces e.g. var_1,var_2', required=True, action = 'store', dest = 'vars', type = str)
    parser.add_argument('-l','--label', help='label column, for example -l bounce_rate, this is the column we want to predict', required=True, action = 'store', dest = 'label', type = str)
    parser.add_argument('-t','--type', help='label column type', required=True, action = 'store', dest = 'type', type = str)
    parser.add_argument('-n','--new_data',help = 'New data frame you want to predict on', action = 'store',type = str, dest = 'new_df', required = False)
    args = parser.parse_args()
    vars = args.vars.split(',')
    df = pd.read_csv(args.path)
    df = df[df != 'nan']
    lab_col = df.pop(args.label)
    lab_col = lab_col.astype(args.type)
    lab_col.columns = [args.label]
    #because I wanted this to be hands-off, I thought it'd be best to blidnly drop na's in hope that
    #there is enough data. This is an ignorant approach, but this program is more of a
    #proof of concept
    df.dropna()
    df = df[vars]

    #run our function and get the best model)
    best_model,df_encoder,lab_encoder = pred(df,lab_col,args.label)

    if args.new_df:
        ndf = pd.read_csv(args.new_df)
        ndf = ndf[ndf!='nan']
        ndf = ndf[vars]
        object_cols = ndf.select_dtypes(include='object').columns

        converted_ndf = ndf.copy()

        converted_ndf = pd.concat([ndf.drop(object_cols, axis = 1),\
        pd.DataFrame(df_encoder.fit_transform(ndf[object_cols]).todense())], axis = 1, ignore_index = True)

        if args.type == 'object':
            print(1)
            ndf['predicted'] = lab_encoder.inverse_transform(best_model.predict(converted_ndf).reshape(-1,1))
        else:
            print(2)
            ndf['predicted'] = best_model.predict(converted_ndf)
        print ndf
