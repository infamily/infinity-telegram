# Introduction
```pipenv``` (https://github.com/pypa/pipenv) is used instead of standard pip.

Setup development environment:
```pipenv install```

If you want to get native requirements.txt, use ```pipenv lock``` with ```-r``` key

```pipenv lock -r > requirements.txt```


# Configuration
All various (and sensitive) settings can be defined via .env file.

```example .env

TELEGRAM_BOT_TOKEN=123456789:ABCDEF_1234567890123456789012345678
SENTRY_DSN=https://token:token@sentry.io/12345678
SENTRY_LOGGING_LEVEL=40
```

# Set telegram webhook
```
FLASK_APP=app.py flask set_webhook https://example.com/telegram/webhook
```
Note the ```telegram/webhook``` url part

Also you can get current webhook info
```
FLASK_APP=app.py flask webhook_info
```


# Database initialize
To create DynamoDB tables use
```
FLASK_APP=app.py flask create_tables
```

To drop DynamoDB tables use:
```
FLASK_APP=app.py flask drop_tables
```

# AWS Deployment guide

1. AWS cli command-line tool should be installed
https://aws.amazon.com/cli/

2. AWS cli should be configured

3. IAM account for deployment should have AdministratorAccess policy OR read more about needed policies
https://github.com/Miserlou/Zappa/issues/849 and https://github.com/Miserlou/Zappa/issues/244

4. Initialize zappa with
```
zappa init
```

Notice: Flask app can be resolved as "app.app"

5. Use ```zappa deploy dev``` or ```zappa deploy production``` for deploy the code

6. Use ```zappa update dev``` or ```zappa update production``` for update deployment

NB! AWS Lambda service has own way to define environment variables.
Variables defined this way have more priority, for example:

```
(.env file)
TEST=foo
```

```
(Lambda function variables)
TEST=bar
```

```
(interpreter)
>>> os.getenv('TEST')
bar
```
