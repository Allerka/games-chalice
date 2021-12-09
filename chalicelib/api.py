import requests
from datetime import datetime
import boto3
import pandas as pd

# Riot Games API key
headers = {'X-Riot-Token': ""}

class API():
	
	# server status
	def api_status():
		r = requests.get("https://na1.api.riotgames.com/lol/status/v4/platform-data", headers=headers)
		data = r.json()
		response = {'platforms': {}, 'timestamps': {}}
		response['server'] = {'region': data['name'], 'locale': data['locales'][0]}
		response['maint_list'] = data['maintenances'][0]['titles']
		for entry in ['maintenances', 'incidents']:
			response['platforms'][entry] = data[entry][0]['platforms']
			response['timestamps'][entry] = datetime.strptime(data[entry][0]['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime("%c") # cleans up datetime formatting into local format
		for i in range(len(response['maint_list'])):
			response['maint_list'][i]['message'] = data['maintenances'][0]['updates'][0]['translations'][i]['content'] # combines titles and messages into a single object
		response['inc_list'] = data['incidents'][0]['titles']
		for i in range(len(response['inc_list'])):
			response['inc_list'][i]['message'] = data['incidents'][0]['updates'][0]['translations'][i]['content']
		return response

	# ranked league info
	def api_rankings(category, queue):
		r = requests.get(f"https://na1.api.riotgames.com/lol/league/v4/{category}leagues/by-queue/{queue}", headers=headers)
		data = r.json()
		response = {'name': data['name'], 'category': category.capitalize(), 'queue': queue, 'stats': {}}
		response['player_list'] = data['entries']
		df = pd.DataFrame(response['player_list']) # Calculating stats for the rankings page
		response['stats']['avg_points'] = df['leaguePoints'].mean().astype(int)
		response['stats']['avg_wins'] = df['wins'].mean().astype(int)
		response['stats']['avg_losses'] = df['losses'].mean().astype(int)
		response['stats']['streak_count'] = len(df['hotStreak'][(df['hotStreak'] == True)])
		return response

	# featured games
	def api_featured():
		r = requests.get("https://na1.api.riotgames.com/lol/spectator/v4/featured-games", headers=headers)
		data = r.json()
		response = {}
		response['game_list'] = data['gameList']
		champions = get_db('champion-ids').scan().get('Items', None)
		spells = get_db('spell-ids').scan().get('Items', None)
		maps = get_db('map-ids').scan().get('Items', None)
		for x in response['game_list']: 
			for a in maps:
				if a['id'] == x['mapId']:
					x['mapId'] = a['name'] # replace map ID number with the actual name
					break
			x['gameStartTime'] = datetime.fromtimestamp(x['gameStartTime'] / 1000).strftime("%c") # converts timestamp from epoch, removing milliseconds
			x.update({'teams': []})
			team1 = []
			team2 = []
			for y in x['participants']: # sorts the players into each team
				for b in champions:
					if b['id'] == y['championId']:
						y['championId'] = b['name'] # replace champion ID number with the actual name
						break
				for c in spells:
					if c['id'] == y['spell1Id']:
						y['spell1Id'] = c['name'] # ditto spell choices
					elif c['id'] == y['spell2Id']:
						y['spell2Id'] = c['name']
				if y['teamId'] == 100:
					team1.append(y)
				else:
					team2.append(y)
			x['teams'] = zip(team1, team2)
		return response

def get_db(table_name):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    return table