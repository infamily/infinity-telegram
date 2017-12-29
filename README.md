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

5. zappa deploy <environment>