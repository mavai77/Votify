from jproperties import Properties


# read config.properties
def getProperties():
    configs = Properties()
    with open('config.properties', 'rb') as config_file:
        configs.load(config_file)
        clientId = configs.get("clientId")[0]
        clientSecret = configs.get("clientSecret")[0]
        # tokenUrl = configs.get("tokenUrl")[0]
        # authorizeUrl = configs.get("authorizeUrl")[0]
        # responseType = configs.get("response_type")[0]
        # grantType = configs.get("grant_type")[0]
        # redirectUri = configs.get("redirect_uri")[0]
    return clientId, clientSecret,
