from dotenv import load_dotenv

class Env:

    @staticmethod
    def initialize_venv():
        load_dotenv()