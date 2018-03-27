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


# AWS Deployment guide

```
NB!
Assumed that Amazon services (Amazon RDS, Amazon Lambda and Amazon SNS) will be configured in the same Amazon region
```

* AWS cli command-line tool should be installed
https://aws.amazon.com/cli/

* AWS cli should be configured

* IAM account for deployment should have AdministratorAccess policy OR read more about needed policies
https://github.com/Miserlou/Zappa/issues/849 and https://github.com/Miserlou/Zappa/issues/244

* Initialize zappa with
```
zappa init
```

* Use ```zappa deploy dev``` or ```zappa deploy production``` for deploy the code.
At this point Amazon Lambda function for the bot deployment will be created.

* Configure Amazon RDS.
Postgres guide: 

https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_GettingStarted.CreatingConnecting.PostgreSQL.html

When DB instance will be created, you will get actual credentials to configure 
`DATABASE_URL` for the django app.

```
NB! It is preferred to specify DATABASE_URL in the Lambda function's environment
variables instead of .env file or django settings - because you won't be able to
connect to Amazon RDS instance locally and locally-stored DATABASE_URL would be an obstacle.
```

For the next step you should to configure Amazon VPC to make possible  connections between 
`Bot <-> Database` and `Bot <-> Internet`.

Please, see the following docs:

https://docs.aws.amazon.com/lambda/latest/dg/vpc-rds.html


## Example zappa_settings.json

(do not use it as is!)

```
{
  "dev": {
    "app_function": "config.wsgi.application",
    "aws_region": "eu-central-1",
    "profile_name": "default",
    "project_name": "infty-telegram",
    "runtime": "python3.6",
    "s3_bucket": "zappa-89cmidgtq",
    "django_settings": "config.settings.dev",
    "events": [
      {
        "function": "lambda.notify_subscribers_about_new_topic",
        "event_source": {
          "arn": "<arn>",
          "events": [
            "sns:Publish"
          ]
        }
      }
    ]
  }
}
```


# Database initialize
```
Assumed that you've configured Amazon RDS and djano database
connection (in the `DATABASE_URL` environment variable, for example)
```

Use ```zappa manage <stage> migrate``` for apply migrations


# Environment variables
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


# Connect to Amazon SNS
Assumed that you've configured Amazon SNS and have actual ARN on the API side

To configure SNS arn add the next lines in the `zappa_settings.json`
(INTO `<stage_name>` object)

Please, fill `<arn>` of the Amazon SNS topic

```
"<stage_name>": {
    ...
    "events": [
      {
        "function": "lambda.notify_subscribers_about_new_topic",
        "event_source": {
          "arn": "<arn>",
          "events": [
            "sns:Publish"
          ]
        }
      }
    ]
    ...
}
```

# Set telegram webhook
```
./manage.py set_webhook htts://<lambda_url>/telegram/webhook
```

Note the ```telegram/webhook``` url part
