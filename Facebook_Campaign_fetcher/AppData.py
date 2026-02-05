from dataclasses import dataclass


@dataclass
class AppAuthData:
    APP_ID : str = ""
    AD_ACCOUNT_ID : str = ""
    APP_SECRET : str = ""
    ACCESS_TOKEN : str = ""


