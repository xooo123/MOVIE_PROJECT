import pandas as pd 
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.preprocessing import MultiLabelBinarizer
from pathlib import Path 
from backend.src.preprocessor import get_clean_data
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix,classification_report
from sklearn.model_selection import train_test_split
import joblib


OUTPUT_DIR= Path(__file__).parent.parent / 'output'


def splitting_data(df):
    X= df[['runtimeMinutes', 'numVotes',
                'Action', 'Adult', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime',
                'Documentary', 'Drama', 'Family', 'Fantasy', 'Film-Noir', 'Game-Show',
                'History', 'Horror', 'Music', 'Musical', 'Mystery', 'News',
                'Reality-TV', 'Romance', 'Sci-Fi', 'Short', 'Sport', 'Talk-Show',
                'Thriller', 'War', 'Western', 'avg_actor_score',
                'writer_avg_score', 'director_avg_score']]


    df['Good_movie']= (df['averageRating'] >= 6.5).astype(int)
    Y= df['Good_movie']
    X= X.drop('runtimeMinutes', axis=1)
    X_train, X_test,Y_train, Y_test= train_test_split(X, Y, test_size= 0.4, random_state= 42)
    return X_train, X_test,Y_train, Y_test

def model():
    df= get_clean_data()
    X_train, X_test,Y_train, Y_test= splitting_data(df)
    rf_model= RandomForestClassifier(n_estimators=500, max_depth=40, max_features='sqrt', random_state=42, class_weight='balanced')
    rf_model.fit(X_train, Y_train)
    y_pred= rf_model.predict(X_test)
    return rf_model, y_pred

def eval_model(X_test, Y_test, model, y_pred):
    accuracy = accuracy_score(Y_test, y_pred)
    precision = precision_score(Y_test, y_pred)
    recall = recall_score(Y_test, y_pred)
    f1 = f1_score(Y_test, y_pred, average='weighted') 
    report_dict = classification_report(Y_test, y_pred, 
                                       target_names=['Bad Movie', 'Good Movie'], 
                                       output_dict=True)
    
    report_df = pd.DataFrame(report_dict).iloc[:-1, :].T  
    plt.figure(figsize=(10, 5))
    sns.heatmap(report_df, annot=True, cmap='RdYlGn', fmt='.2f')
    plt.title('Classification Report')
    plt.savefig(OUTPUT_DIR / 'classification_report.png')
    plt.close()
    conf_matrix = confusion_matrix(Y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Bad Movie', 'Good Movie'], 
                yticklabels=['Bad Movie', 'Good Movie'])
    plt.title('Confusion Matrix')
    plt.savefig(OUTPUT_DIR / 'confusion_matrix.png')
    plt.close()
    return accuracy, precision, recall, f1

if __name__ == "__main__":
    print("the pre-processing...")
    df= get_clean_data()
    print("the splitting...")
    X_train, X_test,Y_train, Y_test= splitting_data(df)
    print("the model training...")
    rf_model, y_pred= model()
    print("the evaluation...")
    accuracy, precision, recall, f1= eval_model(X_test, Y_test, rf_model, y_pred)
    model_path= Path(__file__).resolve().parent.parent / 'models' / 'model.pkl'
    joblib.dump(rf_model, model_path)
    print(f"Model saved to {model_path}")
