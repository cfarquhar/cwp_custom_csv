- [Intro](#intro)
- [Setup](#setup)
  - [Clone repo](#clone-repo)
  - [Set up environment](#set-up-environment)
  - [Collect & set configuration items](#collect--set-configuration-items)
    - [CWP console path](#cwp-console-path)
    - [CWP access key](#cwp-access-key)
- [Run script](#run-script)


# Intro

This script demonstrates generating custom CSV output from the `/api/v1/hosts`
and `/api/v1/containers` endpoints.  It is "throwaway" code and does not include
test cases, is not optimized or elegant, and is not intended to be reused for other purposes.

# Setup

## Clone repo

```
git clone https://github.com/cfarquhar/cwp_custom_csv
```

## Set up environment

Exact steps will vary depending on what you use to manage python versions and
virtual environments.  This works for `pyenv` and `poetry` :

```
cd cwp_custom_csv
pyenv install 3.10.0
pyenv local 3.10.0
poetry install
poetry shell
```

If you are not using `poetry` , install the dependencies as shown below after
activating your virtualenv:

```
cd cwp_custom_csv
pip install -r requirements.txt
```

## Collect & set configuration items

### CWP console path

1. Log in to SaaS console
2. Navigate to Compute > System > Utilities
3. In the "Path to Console" section, copy the value
4. Create `TWISTLOCK_ADDRESS` environment variable with this value:

```
# export TWISTLOCK_ADDRESS=<CONSOLE_PATH>
```

### CWP access key

If you already have access keys created, configure them in the environment
variables as shown below.

1. Log in to SaaS console
2. Navigate to Settings > Access Control > Access Keys
3. Click Add > Access Key in the top right
4. Enter a name and expiration time (if desired)
5. Click "Save"
6. Copy the "Access Key ID" and "Secret Key" values
7. Create `TWISTLOCK_USER` and `TWISTLOCK_PASSWORD` environment variables with these values:

```
# export TWISTLOCK_USER=<ACCESS_KEY_ID>
# export TWISTLOCK_PASSWORD=<SECRET_KEY>
```

# Run script

```
$ python ./generate.py

$ ls -1 *csv
containers.csv
hosts.csv
```
