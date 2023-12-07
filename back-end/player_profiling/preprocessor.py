import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler, OneHotEncoder
from sklearn.manifold import TSNE


def load_all_data():
    filename = '../raw_data/out.csv'
    chunksize = 100000

    chunks = pd.read_csv(filename, chunksize=chunksize, iterator=True, low_memory=False)
    df = pd.concat(chunks, ignore_index=True)

    return df

def load_data_fifa23():
    '''
    Function to return the unique players from Fifa 23
    The most updated version of each player
    '''

    data = load_all_data()
    data_fifa23 = data[data['fifa_version'] == 23]

    data_fifa23 = data_fifa23.drop_duplicates('long_name')

    return data_fifa23

def filter_data(df):
    '''
    Function to filter data to drop the useless columns of
    the dataframe
    '''
    #preferred_foot
    df['preferred_foot'].replace({'Right':1, 'Left':0}, inplace= True)

    #work_rate (offensive/defensive)
    df[['off_work_rate','def_work_rate']] = df['work_rate'].str.split('/', expand=True)
    priority_mapping = {'High': 3, 'Medium': 2, 'Low': 1}
    df['off_work_rate']=df['off_work_rate'].map(priority_mapping)
    df['def_work_rate']=df['def_work_rate'].map(priority_mapping)

    #scale all the characteristics to sum up to 100
    characteristics= df[['pace', 'shooting',
       'passing', 'dribbling', 'defending', 'physic', 'attacking_crossing',
       'attacking_finishing', 'attacking_heading_accuracy',
       'attacking_short_passing', 'attacking_volleys', 'skill_dribbling',
       'skill_curve', 'skill_fk_accuracy', 'skill_long_passing',
       'skill_ball_control', 'movement_acceleration', 'movement_sprint_speed',
       'movement_agility', 'movement_reactions', 'movement_balance',
       'power_shot_power', 'power_jumping', 'power_stamina', 'power_strength',
       'power_long_shots', 'mentality_aggression', 'mentality_interceptions',
       'mentality_positioning', 'mentality_vision', 'mentality_penalties',
       'mentality_composure', 'defending_marking_awareness',
       'defending_standing_tackle', 'defending_sliding_tackle',
       'goalkeeping_diving', 'goalkeeping_handling', 'goalkeeping_kicking',
       'goalkeeping_positioning', 'goalkeeping_reflexes', 'goalkeeping_speed']]

    characteristics['goalkeeping_speed'].fillna(0, inplace=True)

    def scale_row(row, target_sum=100):
        factor = target_sum / row.sum()
        return row * factor

    scaled_characteristics = characteristics.apply(scale_row, axis=1)

    merged_df = df.combine_first(scaled_characteristics)
    merged_df = merged_df[['off_work_rate', 'def_work_rate', 'preferred_foot', 'age', 'height_cm',
       'weight_kg', 'league_level', 'weak_foot', 'skill_moves', 'pace',
       'shooting', 'passing', 'dribbling', 'physic', 'attacking_crossing',
       'attacking_finishing', 'attacking_heading_accuracy',
       'attacking_short_passing', 'attacking_volleys', 'skill_dribbling',
       'skill_curve', 'skill_fk_accuracy', 'skill_long_passing',
       'skill_ball_control', 'movement_acceleration', 'movement_sprint_speed',
       'movement_agility', 'movement_reactions', 'movement_balance',
       'power_shot_power', 'power_jumping', 'power_stamina', 'power_strength',
       'power_long_shots', 'mentality_aggression', 'mentality_interceptions',
       'mentality_positioning', 'mentality_vision', 'mentality_penalties',
       'mentality_composure', 'defending', 'defending_marking_awareness',
       'defending_standing_tackle', 'defending_sliding_tackle',
       'goalkeeping_diving', 'goalkeeping_handling', 'goalkeeping_kicking',
       'goalkeeping_positioning', 'goalkeeping_reflexes', 'goalkeeping_speed']]

    return merged_df

def preprocess(df):

    # Instantiate a SimpleImputer object with your strategy of choice
    imputer = SimpleImputer(strategy="mean")

    for c in df.columns:
        # Call the "fit" method on the object
        imputer.fit(df[[c]])
        # Call the "transform" method on the object
        df[c] = imputer.transform(df[[c]])

    # Define the features based on categories
    binary_features = ['preferred_foot']
    one_hot_features = ['off_work_rate', 'def_work_rate']
    standard_scaling_features = ['pace', 'shooting', 'passing', 'dribbling', 'physic',
       'attacking_crossing', 'attacking_finishing',
       'attacking_heading_accuracy', 'attacking_short_passing',
       'attacking_volleys', 'skill_dribbling', 'skill_curve',
       'skill_fk_accuracy', 'skill_long_passing', 'skill_ball_control',
       'movement_acceleration', 'movement_sprint_speed', 'movement_agility',
       'movement_reactions', 'movement_balance', 'power_shot_power',
       'power_jumping', 'power_stamina', 'power_strength', 'power_long_shots',
       'mentality_aggression', 'mentality_interceptions',
       'mentality_positioning', 'mentality_vision', 'mentality_penalties',
       'mentality_composure', 'weight_kg', 'weak_foot', 'skill_moves',
       'height_cm', 'age']
    robust_scaling_features = ['defending', 'defending_marking_awareness',
        'defending_standing_tackle','defending_sliding_tackle', 'league_level']
    minmax_scaling_features = ['goalkeeping_diving', 'goalkeeping_handling',
        'goalkeeping_kicking','goalkeeping_positioning', 'goalkeeping_reflexes',
        'goalkeeping_speed']

    # Create a column transformer
    preprocessor_ = ColumnTransformer(
        transformers=[
            ('binary', OneHotEncoder(drop='if_binary'), binary_features),
            ('one_hot', OneHotEncoder(), one_hot_features),
            ('standard_scaling', StandardScaler(), standard_scaling_features),
            ('robust_scaling', RobustScaler(), robust_scaling_features),
            ('minmax_scaling', MinMaxScaler(), minmax_scaling_features),
        ], remainder= 'passthrough')
    preprocessor_.fit(df)

    df_preproc = preprocessor_.transform(df)

    return pd.DataFrame(df_preproc)

def preprocess_tfne(df, perplexity = 30, early_exaggeration = 12):

    tsne = TSNE(
        n_components=3,
        learning_rate='auto',
        perplexity=perplexity,
        early_exaggeration=early_exaggeration,
        init='pca'
    )
    return tsne.fit_transform(preprocess(df))
