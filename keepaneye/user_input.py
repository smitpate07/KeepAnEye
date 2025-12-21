class UserInput:
    def __init__(self):
        try:
            self.user_input = input('Enter Amazon Product ID for Tracking:')
        except Exception as e:
            raise e
        