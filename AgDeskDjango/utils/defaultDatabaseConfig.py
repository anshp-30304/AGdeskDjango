"""
A local configuration file intended to be added to .gitignore shortly
"""

def databaseContext():
    try:
        databaseConfig = {
            'NAME': "AgDeskDjango",
            'USER': "postgres",
            'PASSWORD': "ap1234",
        }
        return databaseConfig
    except:
        return {"err": "Something went wrong there!"}