# Kingdom-2-APIs-
Lets you monitor APIs functionality
alert is sent if endpoint status code returned is other than 200 or expected result of payload 
provided is different. 
all configuration is done in YAML file. and SLacker data is provided in seperate .ini file available in same directory.

Every payload must have a corresponding output eg: output1 for payload1. 
any number of payloads can be provided

each api config section must have endpoint,method,maintainer id . no need to add '@' in beginning of maintainer's id

Requirements:
  python 2.7
Libraries:
  ConfigParser
  slacker
  yaml
  json
  urllib
  requests
  time
