class Weibo(object):
    def __init__(self, owner: str, context: str, sent_time: float, comments: list = None):
        '''
        init of a Weibo dataType.
        :param owner: owner of a weibo
        :param context: str
        :param comments: list, Object Comments
        :param sent_time: float sent time
        '''
        self.owner = owner
        self.context = context
        self.comments = comments
        self.sent_time = sent_time

    def value(self) -> dict:
        return {
            'owner': self.owner,
            'context': self.context,
            'comments': self.comments,
            'sent_time': self.sent_time}