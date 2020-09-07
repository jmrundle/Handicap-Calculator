import os
import dotenv


class Config(object):
    URL = "https://ncrdb.usga.org"
    COURSE_ENDPOINT = "/courseTeeInfo.aspx"

    dotenv.load_dotenv()

    CHROME_DRIVER_PATH = os.environ["CHROME_DRIVER_PATH"]
    AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
    AWS_DEFAULT_REGION = os.environ["AWS_DEFAULT_REGION"]
    ENDPOINT_URL = "http://localhost:9696"
