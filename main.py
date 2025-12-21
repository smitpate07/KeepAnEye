from keepaneye.user_input import UserInput
from keepaneye.api_call import ApiCall

def main():
    user_input_obj = UserInput()
    ApiCall(user_input_obj.user_input)



if __name__=='__main__':
    main()