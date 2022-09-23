

class PointsService():
    _point_table = [(5,25),(25, 75), (75, 50), (150, 25)]

    def fetch_points(self, timestamp, server_id, play_dao, guess_dao):
        plays = play_dao.get_all_plays_after(timestamp, server_id)
        all_guesses = guess_dao.get_all_guesses_for_plays(x['play_id'] for x in plays)

        # Build a dictionary of each member and their total points
        totals_by_player = {}
        for guess in all_guesses:
            if guess['member_id'] in totals_by_player:
                totals_by_player[guess['member_id']]['points'] += self.__get_points_for_diff__(guess['difference'])
            else:
                totals_by_player[guess['member_id']] = {}
                totals_by_player[guess['member_id']]['points'] = self.__get_points_for_diff__(guess['difference'])
                totals_by_player[guess['member_id']]['member_name'] = guess['member_name']

        # And now pull those numbers out into a list and sort them
        sorted_players = []
        for player in totals_by_player:
            sorted_players.append([player,
                                   totals_by_player[player]['member_name'],
                                   totals_by_player[player]['points']])

        sorted_players.sort(key=lambda x: x[2], reverse=True)
        return sorted_players

    def fetch_sorted_guesses_by_play(self, guess_dao, play_id):
        all_guesses = guess_dao.get_all_guesses_for_plays([play_id])
        player_list = []
        for guess in all_guesses:
            player_list.append([guess['member_id'], guess['member_name'], int(guess['difference']), self.__get_points_for_diff__(guess['difference'])])

        player_list.sort(key=lambda x: x[2])
        return player_list

    # Iterates through the point table, which we assume is sorted, and gets the points
    def __get_points_for_diff__(self, diff):
        if diff == 'None':
            return 0

        for i in range(0, len(self._point_table)):
            if int(diff) < self._point_table[i][0]:
                return self._point_table[i][1]

        return 0
