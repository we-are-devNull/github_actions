# Appsec-utils
Utilities and scripts for application security team.



## Secret scanner
 The secret scanner reside in "github scripts" folder , The script uses "trufflehog" to scan for secrets.
 By default the scripts scans all repos in a given org , which are active since 'X' days (365 as default).

 ### Prerequisite
    
    Install [Trufflehog](https://github.com/trufflesecurity/trufflehog)
    Set GITHUB_TOKEN in environment
    Install Python3 
    run pip3 install -r requirements.txt

 ### Usage
  The secret scanner has two arguments that you may want to use:

    $ python3 secret_scanner.py --help

    Find credentials in github repositories.

    Flags:
       --repo                     list of repo names seperated by comma.
       --exclude                  list of secret scanners to be exluded from output.
       --version                  Prints code version.

    The output would be a json file created in the same working folder.

  And run the code as shown in example below.
        
        python3 secret_scanner.py --repo "web-offers" --exclude "Parseur,JDBC,SQLServer"

Exit Codes:
- 0: No errors and no results were found.
- 1: An error was encountered. Sources may not have completed scans.

## Dependabot_script
 The dependabot script would fetch the oss vulnerabilities available across all repositories in our org.

 ### Prerequisite
  ```
  Set GITHUB_TOKEN in environment
  Install Python3 
  run pip3 install -r requirements.txt
  ```

