angular.module("three-goals-wc", ['tableSort'])
.factory("datasource", function($http) {
	var cache = null;

	var getResults = function() {
		return $http.get('db.json').then(function(res) {
			return res.data;
		});
	};

	return {
		getResults: getResults
	}
})
.controller("standings", function(datasource) {
	this.teams = [];
	this.players = [];

	self = this;
	datasource.getResults().then(function(data) {
		self.teams = data.teams;
		self.players = data.players;
	});
});
