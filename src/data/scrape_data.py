from datetime import datetime
import pandas as pd
import json
import logging
import os
import requests
import time

def get_regular_season_bookends(season):
    page = f'http://statsapi.web.nhl.com/api/v1/seasons/{season}'
    season_info = json.loads(requests.get(page).text)['seasons'][0]

    return (season_info['regularSeasonStartDate'], 
    	season_info['regularSeasonEndDate'])

def get_day_games_data(day_game_list):
    day_df = pd.DataFrame(day_game_list)
    away = (day_df['teams']
    	.apply(pd.Series)['away']
    	.apply(pd.Series)['team']
    	.apply(pd.Series)[['name','id']]
    	.rename(columns={'name':'away_name','id':'away_id'}))
    home = (day_df['teams']
    	.apply(pd.Series)['home']
    	.apply(pd.Series)['team']
    	.apply(pd.Series)[['name','id']]
    	.rename(columns={'name':'home_name','id':'home_id'}))
    ids = (day_df['teams']
    	.apply(pd.Series)['away']
    	.apply(pd.Series)['team']
    	.apply(pd.Series)[['name','id']]
    	.rename(columns={'name':'away_name','id':'away_id'}))

    return pd.concat([away,home,day_df['gamePk']],axis=1)


def get_date_range_game_data(start_date,end_date):
    page = 'http://statsapi.web.nhl.com/api/v1/schedule\
    ?startDate={}&endDate={}'.format(start_date,end_date)

    day_range_data = json.loads(requests.get(page).text)
    num_days = len(day_range_data['dates'])

    result_df = get_day_games_data(day_range_data['dates'][0]['games'])
    for i in range(1,num_days):
        result_df = pd.concat([result_df,
                   get_day_games_data(day_range_data['dates'][i]['games'])])
    
    return result_df


def create_game_team_players_df(team_data):
    data_df = pd.DataFrame(team_data['players']).transpose()
    players_df = data_df['person'].apply(pd.Series)
    positions_df = data_df['position'].apply(pd.Series)
    players_df = pd.concat([players_df,positions_df],axis=1)
    players_df['team_id'] = team_data['team']['id']
    players_df['team_name'] = team_data['team']['name']

    return players_df

def get_game_players(game_id):
    path = f'http://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live'
    game_data = json.loads(requests.get(path).text)
    
    team_data = game_data['liveData']['boxscore']['teams']
    away_players = create_game_team_players_df(team_data['away'])
    home_players = create_game_team_players_df(team_data['home'])
    
    players = pd.concat([away_players,home_players])
    players['game_id'] = game_id
    
    return players


def get_season_players(season):
    season_games = pd.read_csv(f'data/raw/game_lists/{season}_games.csv')
    season_games = season_games['gamePk'].tolist()
    season_games = [x for x in season_games if str(x)[5]=='2']    
    player_df = get_game_players(season_games[0])

    for game in season_games[1:]:
        try:
            player_df = pd.concat([
                player_df,
                get_game_players(game)
            ])
            
        except Exception as e:

            logging.warning(f'Error in game {game}. Will ignore and proceed.')
            
        finally:
            time.sleep(0.5)
            
        if season_games.index(game) % 20 == 0:
            time.sleep(2.5)
        if season_games.index(game) % 100 == 0:
            print(f'Scraped {game} at {datetime.now()}')
        
    return player_df

now = datetime.strftime(datetime.now(),"%Y%m%d%H%M%S")
logging.basicConfig(filename=f'log-{now}.log',
                    filemode='w',
                    format='%(levelname)s - %(message)s')

early_seasons = [f'19{i}19{i+1}' for i in range(17,99)]
naught_seasons = [f'200{i}200{i+1}' for i in range(9)]
decade_seasons = [f'20{i}20{i+1}' for i in range(10,19)]

# Add seasons that don't follow number pattern 
# and remove the lockout season
seasons = (early_seasons + ['19992000'] + 
	naught_seasons + ['20092010'] + decade_seasons)
seasons.remove('20042005')

if __name__ == '__main__':
	print('Scraping the entire NHL database of games and players')
	for season in seasons:
	    print(f'Scraping season {season} at', datetime.now())
		start_date, end_date = get_regular_season_bookends(season)
		result_df = get_date_range_game_data(start_date,end_date)
		result_df.to_csv(f'data/raw/game_lists/{season}_games.csv',index=False)
	    
	    player_season_df = get_season_players(season)
	    player_season_df.to_csv(f'data/raw/player_lists/players_{season}.csv',
	    	index=False)
		
		print(f'{season} games scraped...')
		time.sleep(15)

