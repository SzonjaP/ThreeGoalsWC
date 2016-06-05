# -*- coding: utf-8 -*-

import operator
from collections import namedtuple
from recordtype import recordtype

#Team = namedtuple('Team', ['player_name', 'team_name', 'character_id'])
Match = namedtuple('Match', ['scored', 'conceded', 'message'])
Result = recordtype('Result', ['player_name', 'city', ('wins', 0), ('losses', 0), ('draws', 0), ('walkovers', 0), ('scored', 0), ('conceded', 0)])


with open("wc.db", 'r') as f:
	s = eval(f.read().decode('utf-8'))
	rounds = s['rounds']

teams = {};

for day, cities in rounds.iteritems():
	for city, city_results in cities.iteritems():
		if city not in teams:
			teams[city] = {}

		for player, match in city_results.iteritems():
			if player not in teams[city]:
				teams[city][player] = Result(player, city);

			if match is False:
				teams[city][player].walkovers += 1
				continue

			res = teams[city][player]
			res.wins     += (match.scored > match.conceded)
			res.losses   += (match.scored < match.conceded)
			res.draws    += (match.scored == match.conceded)
			res.scored   += match.scored
			res.conceded += match.conceded


def conv(team):
	name = team[0]
	players = team[1]
	res = {
		'name': name,
		'pts': 0,
		'wins': 0,
		'draws': 0,
		'losses': 0,
		'gd': 0,
		'walkovers': 0,
		'scored': 0,
		'conceded': 0,
	}

	for name, result in players.iteritems():
		res['wins'] += result.wins
		res['losses'] += result.losses
		res['draws'] += result.draws
		res['walkovers'] += result.walkovers
		res['scored'] += result.scored
		res['conceded'] += result.conceded

	res['gd'] = res['scored']-res['conceded']
	res['pts'] = 3*res['wins'] + 1*res['draws'] + (-1)*res['walkovers']

	return res;

def sort_result(x):
	return (
		x['pts'],
		x['wins'],
		x['gd'],
		x['scored'],
		x['name']
	)

team_results = sorted(map(conv, teams.iteritems()), key=sort_result)

namecollen = max([len(team['name']) for team in team_results]) + 2

padchar = '.'

def num_col(num):
	return str(num).rjust(3, padchar).ljust(4, padchar)

print ".#|%s||%s||%s|%s|%s|%s||%s||%s|%s" % ("Team".ljust(namecollen, padchar), num_col("Pts"), num_col("W"), num_col("D"), num_col("L"), num_col("M"), num_col("GD"), num_col("Sc"), num_col("Cn"))
print "--+%s++----++----+----+----+----++----++----+----" % "-".ljust(namecollen, "-")
for idx, result in enumerate(reversed(team_results)):
	print ("%s|%s||%s||%s|%s|%s|%s||%s||%s|%s" %
		(
			str(idx+1).rjust(2, padchar),
			result['name'].ljust(namecollen, padchar),
			num_col(result['pts']),
			num_col(result['wins']),
			num_col(result['draws']),
			num_col(result['losses']),
			num_col(result['walkovers']),
			num_col(result['gd']),
			num_col(result['scored']),
			num_col(result['conceded'])
		)
	)

print ""


players = {}
for city, city_players in teams.iteritems():
	for player_name, result in city_players.iteritems():
		if player_name not in players:
			players[player_name] = result
		else:
			players[player_name] += result

def res_to_dic(res):
	return {
		'name': res.player_name,
		'city': res.city,
		'pts': 3*res.wins + 1*res.draws + (-1)*res.walkovers,
		'wins': res.wins,
		'draws': res.draws,
		'losses': res.losses,
		'gd': res.scored - res.conceded,
		'walkovers': res.walkovers,
		'scored': res.scored,
		'conceded': res.conceded,
	}


players = sorted(map(res_to_dic, players.values()), key=sort_result)
namecollen = max([len(player['name']) for player in players]) + 2
print ".#|%s||%s||%s|%s|%s|%s||%s||%s|%s" % ("Team".ljust(namecollen, padchar), num_col("Pts"), num_col("W"), num_col("D"), num_col("L"), num_col("M"), num_col("GD"), num_col("Sc"), num_col("Cn"))
print "--+%s++----++----+----+----+----++----++----+----" % "-".ljust(namecollen, "-")
for idx, result in enumerate(reversed(players)):
	print ("%s|%s||%s||%s|%s|%s|%s||%s||%s|%s" %
		(
			str(idx+1).rjust(2, padchar),
			result['name'].ljust(namecollen, padchar),
			num_col(result['pts']),
			num_col(result['wins']),
			num_col(result['draws']),
			num_col(result['losses']),
			num_col(result['walkovers']),
			num_col(result['gd']),
			num_col(result['scored']),
			num_col(result['conceded'])
		)
	)
