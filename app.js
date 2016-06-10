angular.module("three-goals-wc", [])
.factory("datasource", function($http) {
	var cache = null;

	var getTeamResults = function() {
		return $http.get('db.json').then(function(res) {
			return res.data.teams;
		});
	};

	return {
		getTeamResults: getTeamResults
	}
})
.controller("team-standings", function(datasource) {
	this.teams = {};

	self = this;
	datasource.getTeamResults().then(function(teams) {
		self.teams = teams;
	});
});
