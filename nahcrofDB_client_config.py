# you do not need to use this file if you are not using enterprise mode, 
# this would be included with your client file if you are using enterprise mode.

# expand this list as much as you need, each database will be written to and utilized in the event of another database failure, 
# the one used in the init function will be the default
databases = [
    {"url": "http://0.0.0.0:8080", "password": "super_duper_password"}, 
]
