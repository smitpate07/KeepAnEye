class UserInput:
    """
    Class to handle user input for Amazon product tracking
    """
    def __init__(self):
        try:
            self.user_input = input('Enter Amazon Product ASIN for Tracking: ')
            if not self.user_input.strip():
                raise ValueError("ASIN cannot be empty")
            print(f"✓ ASIN accepted: {self.user_input}")
        except Exception as e:
            raise e