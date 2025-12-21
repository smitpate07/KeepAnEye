from keepaneye.user_input import UserInput
from keepaneye.api_call import ApiCall
from keepaneye.save_to_db import SaveToDB

def main():
    user_input_obj = UserInput()
    api_call_obj = ApiCall(user_input_obj.user_input)
    for_db= api_call_obj.call_load()
    save_to_db_obj = SaveToDB()
    save_to_db_obj.data_load(for_db)


    
if __name__ == '__main__':
    main()
