# awfol

The AWS full organization lister (awfol) gives you insights into your federated AWS organization accounts.

The analysis happens in two steps

* Gather all infos you need from the federated accounts. You do this with the help of the modules which reside under `mods`. You can use the existing modules or write your own. Every module uses a temporary AWS session. You need a working assume_role set up in your AWS organization to get your temporary session.

* Analyse the information from the modules via the rules residing in `rules`.

Right now, all modules will insert their information into a tree representing the organization.
If the existing modules and rules do not fit your purpose feel free to change them.

The tree looks like this:

```
     | (root)
       \
        123456789012 (account id)
          \ 
           EC2 (module identifier)
           |    \
      Result1  Result2
```

## Getting Started

```
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ aws-switch organization-master (or one of the other ways to set up the environment)
$ ./venv/bin/python aws-inventory.py -h
usage: awfol.py [-h] [-e] [-r] [-x] [-t]

awfol - your AWS organization recon tool

optional arguments:
  -h, --help  show this help message and exit
  -e          Evaluates the rules. This reads the stored results.
  -r          Reads the stored results and prints the tree.
  -x          Execute live on an AWS organization. This stores the results.
  -t          Do a test run.

```

### Prerequisites

* Set up a config.ini file with your specific settings

```
[MAIN]
PROFILE = YOUR-AWS-MASTER-ACCOUNT-PROFILE
ROLE    = YOUR ROLENAME, SUCH AS role/AUDITROLE
SESS_ID = YOUR-SESSION-ID, SUCH AS API-AUDIT
MASTER  = THE-ACCOUNT-NUMBER-OF-YOUR-MASTER-ACCOUNT

```

* Make sure you have activated your AWS environment. [aws-switch](https://github.com/advincze/aws-switch) is pretty neat to do that. The entry PROFILE in the config is just for the code to assume the role. It does not substitute a proper environment setup.

## Contributing


## Authors

* **Florian Junge** ([ShantyCode](https://twitter.com/shantycode)) - *Initial work*

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone who's code was used

