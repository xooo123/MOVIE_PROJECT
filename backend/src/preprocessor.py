#This contains all the code to clean, transform, map, scale, and encode your raw data.
import pandas as pd 
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.preprocessing import MultiLabelBinarizer
from pathlib import Path 
 

def file_Path(file_name):
    current_file= Path(__file__).resolve()
    project_root= current_file.parent.parent
    return project_root / 'dataset' / file_name


def load_data():
    df1= pd.read_csv(file_Path('name.basics.tsv/name.basics.tsv'), sep="\t", na_values=['\\NA'])
    df2= pd.read_csv(file_Path('title.basics.tsv/title.basics.tsv'), sep= "\t", na_values= ['\\NA'])
    df2= df2.drop(index= df2[df2['titleType'] != 'movie'].index)
    df3= pd.read_csv(file_Path('title.crew.tsv/title.crew.tsv'), sep="\t", na_values= ['\\NA'])
    df3= df3.drop_duplicates(df3[['tconst']])
    df4= pd.read_csv(file_Path('title.principals.tsv/title.principals.tsv'), sep="\t", na_values= ['\\NA'])
    df5= pd.read_csv(file_Path('title.ratings.tsv/title.ratings.tsv'), sep= "\t", na_values=['\\NA'])
    df5= df5.drop_duplicates(df5[['tconst']])
    return df1, df2, df3, df4, df5

def merging_data(df1, df2, df3, df4, df5):
    df1_merged= df2.merge(df3, on='tconst', how='left')
    df2_merged= df1_merged.merge(df4, on= 'tconst', how='left')
    df3_merged= df2_merged.merge(df5, on='tconst', how='left')
    df4_merged= df3_merged.merge(df1, on='nconst', how='left')
    return df4_merged



def preprocessing(df):
    df= df.copy()
    df= df.drop(['isAdult', 'titleType', 'originalTitle', 'primaryTitle', 'endYear', 'characters', 'primaryName', 'birthYear', 'deathYear', 'ordering', 'job'], axis= 1)
    df= df.dropna(subset= ['knownForTitles', 'primaryProfession'])
    df['averageRating']= pd.to_numeric(df['averageRating'], downcast='float', errors= 'coerce')
    df['numVotes']= pd.to_numeric(df['numVotes'], downcast='float', errors= 'coerce')
    df['startYear']= pd.to_numeric(df['startYear'], downcast= 'float', errors= 'coerce')
    df['runtimeMinutes']= pd.to_numeric(df['runtimeMinutes'], downcast='float', errors='coerce')
    df['averageRating']= df['averageRating'].fillna(df['averageRating'].median())
    df['numVotes']= df['numVotes'].fillna(df['numVotes'].median())
    df['startYear']= df['startYear'].fillna(0)
    df['runtimMinutes']= df['runtimeMinutes'].fillna(df['runtimeMinutes'].median())
    df['category']= df['category'].fillna('')
    return df
      

def genre_transforming(df):
    df['genres']= df['genres'].fillna('')
    df['genres']= df['genres'].str.split(',')

    mlb= MultiLabelBinarizer()
    genre_encoded= mlb.fit_transform(df['genres'])
    genre_df= pd.DataFrame(genre_encoded, columns= mlb.classes_, index=df.index)
    columns_genre= ['Action', 'Adult', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime',
              'Documentary', 'Drama', 'Family', 'Fantasy', 'Film-Noir', 'Game-Show',
              'History', 'Horror', 'Music', 'Musical', 'Mystery', 'News',
              'Reality-TV', 'Romance', 'Sci-Fi', 'Short', 'Sport', 'Talk-Show',
              'Thriller', 'War', 'Western']
    genre_df[columns_genre]= genre_df[columns_genre].fillna(0)
    df= pd.concat([df, genre_df], axis=1)
    return df


def actor_featuring(df):
    df['actor_num_movie']= df.groupby('nconst')['tconst'].transform('nunique')
    df['actor_average_score']= df.groupby('nconst')['averageRating'].transform('mean')
    df['actor_score']= (df['actor_average_score'] * np.log1p(df['actor_num_movie']))
    actor_features= df.groupby('tconst').agg({
        'actor_score': ['mean']
    })
    actor_features.columns = ['avg_actor_score']
    actor_features= actor_features.reset_index()
    df= df.merge(actor_features, on='tconst', how='left')
    return df


def writer_featuring(df):
    writers_df= df[df['category']== 'writer'].copy()
    writers_df['writer_avg_scr']= writers_df.groupby('nconst')['averageRating'].transform('mean')
    writers_df['writer_num_movie']= writers_df.groupby('nconst')['tconst'].transform('nunique')
    writers_df['writer_score']= (writers_df['writer_avg_scr'] * np.log1p(writers_df['writer_num_movie']))
    writer_features= writers_df.groupby('tconst').agg({
        'writer_score': ['mean']
    })
    writer_features.columns=['writer_avg_score']
    writer_features= writer_features.reset_index()
    df= df.merge(writer_features,on= 'tconst', how='left')
    return df


def director_featuring(df):
    directors_df= df[df['category']== 'director'].copy()
    directors_df['director_avg_score']= directors_df.groupby('nconst')['averageRating'].transform('mean')
    directors_df['director_num_movies']= directors_df.groupby('nconst')['tconst'].transform('nunique')
    directors_df['director_score']= (directors_df['director_avg_score'] * np.log1p(directors_df['director_num_movies']))
    director_features= directors_df.groupby('tconst').agg({
        'director_score': ['mean']
    })
    director_features.columns=['director_avg_score']
    director_features= director_features.reset_index()
    df= df.merge(director_features, on='tconst', how='left')
    return df

def get_clean_data():
    df1, df2, df3, df4, df5 = load_data()
    df= merging_data(df1, df2, df3, df4, df5)
    df= preprocessing(df)
    df= genre_transforming(df)
    df['averageRating']= df['averageRating'].fillna(df['averageRating'].median())
    df['numVotes']= df['numVotes'].fillna(df['numVotes'].median())
    df['startYear']= df['startYear'].fillna(0)
    df['runtimMinutes']= df['runtimeMinutes'].fillna(df['runtimeMinutes'].median())
    df['category']= df['category'].fillna('')
    df= actor_featuring(df)
    df= writer_featuring(df)
    df= director_featuring(df)
    df[['writer_avg_score',  'director_avg_score', 'avg_actor_score', 'numVotes', 'averageRating', 'runtimeMinutes', 'startYear']]= df[['writer_avg_score',  'director_avg_score',  'avg_actor_score','numVotes', 'averageRating', 'runtimeMinutes', 'startYear']].fillna(df[['writer_avg_score', 'director_avg_score', 'avg_actor_score','numVotes', 'averageRating', 'runtimeMinutes', 'startYear']].median())
    df= df.drop_duplicates(df[['tconst']])
    return df
