# -*- coding: utf-8 -*-

import logging
import operator
import itertools
import json
from collections import namedtuple
from recordtype import recordtype

logging.basicConfig(level=logging.DEBUG)

#Team = namedtuple('Team', ['player_name', 'team_name', 'character_id'])
Match = namedtuple('Match', ['scored', 'conceded', 'message'])
Result = recordtype('Result', ['player_name', 'city', ('wins', 0), ('losses', 0), ('draws', 0), ('walkovers', 0), ('scored', 0), ('conceded', 0)])


with open("wc.db", 'r') as f:
	s = eval(f.read().decode('utf-8'))

rounds = s['rounds']
teams = { city: { player: Result(player, city) for player in s['teams'][city] } for city in s['teams'].keys() };


all_players = list(itertools.chain.from_iterable(teams.values()))

for day, matches in rounds.iteritems():
	if set(matches.keys()) - set(all_players):
		logging.warning("On day %s unteamed players: %s", day, set(matches.keys()) - set(all_players));

	for city, team in teams.iteritems():
		for player, result in team.iteritems():
			if player not in matches:
				logging.info("No match for player %s (%s) in round %s, walkover", player, city, day)
				matches[player] = None

			match = matches[player]

			if match is None:
				result.walkovers += 1
				continue

			result.wins     += (match.scored > match.conceded)
			result.losses   += (match.scored < match.conceded)
			result.draws    += (match.scored == match.conceded)
			result.scored   += match.scored
			result.conceded += match.conceded


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

def rank(x):
	return (
		x['pts'],
		x['wins'],
		x['gd'],
		x['scored']
	)
def add_ranks(xs):
	prev = None
	for idx, x in enumerate(xs):
		if prev is None:
			x['rank'] = '1'
		else:
			x['rank'] = '%d'%(idx+1) if not rank(prev) == rank(x) else prev['rank']
		prev = x;


team_results = sorted(map(conv, teams.iteritems()), key=lambda x: x['name'], reverse=True)
team_results = sorted(team_results, key=rank)
team_results.reverse();
add_ranks(team_results)

namecollen = max([len(team['name']) for team in team_results]) + 2

padchar = '.'

def num_col(num):
	return str(num).rjust(3, padchar).ljust(4, padchar)

print ".#|%s||%s||%s|%s|%s|%s||%s||%s|%s" % ("Team".ljust(namecollen, padchar), num_col("Pts"), num_col("W"), num_col("D"), num_col("L"), num_col("M"), num_col("GD"), num_col("Sc"), num_col("Cn"))
print "--+%s++----++----+----+----+----++----++----+----" % "-".ljust(namecollen, "-")
for result in team_results:
	print ("%s|%s||%s||%s|%s|%s|%s||%s||%s|%s" %
		(
			str(result['rank']).rjust(2, padchar),
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

players = sorted(map(res_to_dic, players.values()), key=lambda x: x['name'], reverse=True)
players = sorted(players, key=rank)
players.reverse();
add_ranks(players)
pnamecollen = max([len(player['name']) for player in players]) + 2
print ".#|%s|%s||%s||%s|%s|%s|%s||%s||%s|%s" % ("Player".ljust(pnamecollen, padchar), "City".ljust(namecollen, padchar), num_col("Pts"), num_col("W"), num_col("D"), num_col("L"), num_col("M"), num_col("GD"), num_col("Sc"), num_col("Cn"))
print "--+%s+%s++----++----+----+----+----++----++----+----" % ("-".ljust(pnamecollen, "-"), "-".ljust(namecollen, "-"))
for result in players:
	print ("%s|%s|%s||%s||%s|%s|%s|%s||%s||%s|%s" %
		(
			str(result['rank']).rjust(2, padchar),
			result['name'].ljust(pnamecollen, padchar),
			result['city'].ljust(namecollen, padchar),
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

open('db.json', 'wb').write(json.dumps({'teams': team_results, 'players': list(reversed(players))}, indent=4, separators=(',', ': '), ensure_ascii=False).encode('utf8'))
