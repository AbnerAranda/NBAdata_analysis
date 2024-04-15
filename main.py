import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

pd.set_option('display.max_columns', None)
from openpyxl import Workbook

data = pd.read_excel('/Users/abner/Documents/NBAdata/nba_player_data.xlsx')
# print(data)

#### Cleaning data
# print(data.isna().sum())
# Eleminating columns
data.drop(columns=['RANK', 'EFF'], inplace=True)
data['season_start_year'] = data['Year'].str[:4].astype(int)
# Replacing team name
data['TEAM'].replace(to_replace=['NOP', 'NOH'], value='NO', inplace=True)
# print(data.TEAM.nunique())
# print(data.TEAM.unique())
# Regular season spell
data['Season_type'].replace(to_replace=['Regular%20Season'], value='Regular Season', inplace=True)
# Dividing regular season and playoffs
rs_df = data[data['Season_type'] == 'Regular Season']
ply_df = data[data['Season_type'] == 'Playoffs']
# print(rs_df)
# print(ply_df)
# Getting rid of percentage columns
#print(data.columns)
total_cols = ['MIN', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 'OREB',
              'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']

#### Which player stats are correlated to each other?
data_per_min = data.groupby(['PLAYER', 'PLAYER_ID', 'Year'])[total_cols].sum().reset_index()
for col in data_per_min.columns[4:]:
    data_per_min[col] = data_per_min[col] / data_per_min['MIN']

# adding our percentaje variables
data_per_min['FG%'] = data_per_min['FGM'] / data_per_min['FGA']  # field goal percentaje
data_per_min['3PT%'] = data_per_min['FG3M'] / data_per_min['FG3A']  # 3 ponts field goal percentaje
data_per_min['FT%'] = data_per_min['FTM'] / data_per_min['FTA']  # free throw percentaje
data_per_min['FG3A%'] = data_per_min['FG3A'] / data_per_min['FGA']  # 3 points attemp percentaje
data_per_min['PTS/FGA'] = data_per_min['PTS'] / data_per_min['FGA']  # points by fielf goals attempts
data_per_min['FG3M/FGM'] = data_per_min['FG3M'] / data_per_min['FGM']  # 3 points field goals made by field goals made
data_per_min['FTA/FGA'] = data_per_min['FTA'] / data_per_min['FGA']  # free throw attempts by field goals attempt
data_per_min['TRU%'] = 0.5 * data_per_min['PTS'] / (
            data_per_min['FGA'] + 0.475 * data_per_min['FTA'])  # true shooting percentaje
data_per_min['AST_TOV'] = data_per_min['AST'] / data_per_min['TOV']  # assist over tornovers

# Filtering data,dropping variables and obtaining correlation
data_per_min = data_per_min[data_per_min['MIN'] >= 50]
data_per_min.drop(columns=['PLAYER', 'PLAYER_ID', 'Year'], inplace=True)

fig = px.imshow(data_per_min.corr())
fig.show()

#print(data_per_min.corr())
# print((data_per_min['MIN']>50).mean())
# print(data_per_min)

#### How are minutes played distributed?
fig = px.histogram(x=rs_df['MIN'], histnorm='percent')
fig.show()
fig = px.histogram(x=ply_df['MIN'], histnorm='percent')
fig.show()
fig = go.Figure()


def hist_data(df=rs_df, min_MIN=0, min_GP=0):
    return df.loc[(df['MIN'] >= min_MIN) & (df['GP'] >= min_GP), 'PTS'] / \
        df.loc[(df['MIN'] >= min_MIN) & (df['GP'] >= min_GP), 'GP']


fig.add_trace(go.Histogram(x=hist_data(rs_df, 50, 5), histnorm='percent', name='RS',
                           xbins={'start': 0, 'end': 40, 'size': 1}))
fig.add_trace(go.Histogram(x=hist_data(ply_df, 5, 1), histnorm='percent', name='Playoffs',
                           xbins={'start': 0, 'end': 40, 'size': 1}))
fig.update_layout(barmode='overlay')
fig.update_traces(opacity=0.5)
fig.show()

print(((hist_data(rs_df, 50, 5) >= 12) & (hist_data(rs_df, 50, 5) <= 36)).mean())

####How has the game changed over the years?
change_df = data.groupby('season_start_year')[total_cols].sum().reset_index()
change_df['POSS_est'] = change_df['FGA']+change_df['OREB']+change_df['TOV']+0.44*change_df['FTA']
change_df = change_df[list(change_df.columns[0:2])+['POSS_est']+list(change_df.columns[2:-1])]

change_df['FG%'] = change_df['FGM'] / change_df['FGA']
change_df['3FG%'] = change_df['FG3M'] / change_df['FG3A']
change_df['FT%'] = change_df['FTM'] / change_df['FTA']
change_df['AST%'] = change_df['AST'] / change_df['FGM']
change_df['FG3A%'] = change_df['FG3A'] / change_df['FGA']
change_df['PTS/FGA'] = change_df['PTS'] / change_df['FGA']
change_df['FG3M/FGM'] = change_df['FG3M'] / change_df['FGM']
change_df['FTA/FGA'] = change_df['FTA'] / change_df['FGA']
change_df['TRU%'] = 0.5*change_df['PTS'] / (change_df['FGA']+0.475*change_df['FTA'])
change_df['AST_TOV'] = change_df['AST'] / change_df['TOV']

#Team stats per 48 minutes
change_per48_df = change_df.copy()
for col in change_per48_df.columns[2:18]:
    change_per48_df[col] = (change_per48_df[col]/change_per48_df['MIN'])*48*5

#print(change_per48_df)
change_per48_df.drop(columns='MIN', inplace=True)

fig = go.Figure()
for col in change_per48_df.columns[1:]:
    fig.add_trace(go.Scatter(x=change_per48_df['season_start_year'],
                             y=change_per48_df[col], name=col))
fig.show()

#Team stats per 100 possesions
change_per100_df = change_df.copy()
for col in change_per100_df.columns[3:18]:
    change_per100_df[col] = (change_per100_df[col]/change_per100_df['POSS_est'])*100

change_per100_df.drop(columns=['MIN', 'POSS_est'], inplace=True)
#print(change_per100_df)

fig = go.Figure()
for col in change_per100_df.columns[1:]:
    fig.add_trace(go.Scatter(x=change_per100_df['season_start_year'],
                             y=change_per100_df[col], name=col))
fig.show()

####Compare regular season to playoffs
rs_change_df = rs_df.groupby('season_start_year')[total_cols].sum().reset_index()
ply_change_df = ply_df.groupby('season_start_year')[total_cols].sum().reset_index()

for i in [rs_change_df, ply_change_df]:
    i['POSS_est'] = i['FGA'] + i['OREB'] + i['TOV'] + 0.44 * i['FTA']
    i['Poss_per_48'] = (i['POSS_est'] / i['MIN']) * 48 * 5

    i['FG%'] = i['FGM'] / i['FGA']
    i['3FG%'] = i['FG3M'] / i['FG3A']
    i['FT%'] = i['FTM'] / i['FTA']
    i['AST%'] = i['AST'] / i['FGM']
    i['FG3A%'] = i['FG3A'] / i['FGA']
    i['PTS/FGA'] = i['PTS'] / i['FGA']
    i['FG3M/FGM'] = i['FG3M'] / i['FGM']
    i['FTA/FGA'] = i['FTA'] / i['FGA']
    i['TRU%'] = 0.5 * i['PTS'] / (i['FGA'] + 0.475 * i['FTA'])
    i['AST_TOV'] = i['AST'] / i['TOV']

    for col in total_cols:
        i[col] = 100*i[col]/i['POSS_est']

    i.drop(columns=['MIN','POSS_est'], inplace=True)

comp_change_df = round(((ply_change_df - rs_change_df)/rs_change_df)*100, 3)
comp_change_df['season_start_year'] = list(range(2012,2023))
print(comp_change_df)

fig = go.Figure()
for col in comp_change_df.columns[1:]:
    fig.add_trace(go.Scatter(x=comp_change_df['season_start_year'],
                             y=comp_change_df[col], name=col))
fig.show()