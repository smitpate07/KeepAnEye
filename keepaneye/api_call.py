from keepaneye.user_input import UserInput

class ApiCall(UserInput):
    def __init__(self,user_input):
        try:
            print('Hello I am in 2nd')
        except Exception as e:
            raise e