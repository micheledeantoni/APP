import sys
sys.path.append("/Users/michele/code/micheledeantoni/APP")
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from player_profiling.preprocessor import *

def player_radar_plot(raw_data, index1 , index2):
    raw_data['idx']=raw_data.index
    filtered_data= filter_data(raw_data)
    columns_to_keep = [
    'attacking_crossing', 'attacking_finishing', 'attacking_heading_accuracy',
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
    'goalkeeping_positioning', 'goalkeeping_reflexes', 'goalkeeping_speed'
    ]
    df_subset = filtered_data[columns_to_keep]

    # 2. Group by Initial Work and Average
    grouped_df = df_subset.groupby(lambda x: x.split('_')[0], axis=1).mean()
    categories = grouped_df.columns

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=grouped_df.iloc[index1].values,
        theta=categories,
        fill='toself',
        name=raw_data[raw_data['idx']==index1]['short_name'].values[0]
    ))
    fig.add_trace(go.Scatterpolar(
        r=grouped_df.iloc[index2].values,
        theta=categories,
        fill='toself',
        name=raw_data[raw_data['idx']==index2]['short_name'].values[0]
    ))

    fig.update_layout(
    polar=dict(
        radialaxis=dict(
        visible=True,
        range=[0, 4]
        )),
    showlegend=True
    )

    fig.show()
