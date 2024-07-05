class QuerierAdapter:
    def __init__(self, querier):
        self.querier = querier

    def get(self, cell_id):
        return self.querier.getState(cell_id)
