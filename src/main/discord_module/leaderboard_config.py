class LeaderboardConfig():
    closest = True
    def __init__(self, message_content):
        pieces = message_content.split(' ')
        if len(pieces) == 1:
            return

        if pieces[1] == 'average':
            self.closest = False

    def should_sort_by_pure_closest(self):
        return self.closest

    def should_sort_by_best_average(self):
        return not self.closest
