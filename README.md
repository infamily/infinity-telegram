# Configuration
All various (and sensitive) settings can be defined via .env file.

```example .env

TELEGRAM_BOT_TOKEN=123456789:ABCDEF_1234567890123456789012345678
SENTRY_DSN=https://token:token@sentry.io/12345678
SENTRY_LOGGING_LEVEL=40
```

# Deployment guide

1. AWS cli command-line tool should be installed
https://aws.amazon.com/cli/

2. AWS cli should be configured

3. IAM account for deployment should have AdministratorAccess policy OR read more about needed policies
https://github.com/Miserlou/Zappa/issues/849
https://github.com/Miserlou/Zappa/issues/244

4. Initialize zappa with
```
zappa init
```

Notice: Flask app can be resolved as "app.app"

5. Use ```zappa deploy dev``` or ```zappa deploy production``` for deploy the code

6. Use ```zappa update dev``` or ```zappa update production``` for update deployment

NB! AWS Lambda service has own way to define environment variables.
Variables defined this way have more priority, for example:

```.env
TEST=foo
```

```Lambda function variables
TEST=bar
```

```python
>>> os.getenv('TEST')
bar
```
