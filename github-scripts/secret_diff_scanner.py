import logging,os,requests,sys,subprocess
from dateutil import parser
from datetime import datetime, timezone
import json
import argparse


LAST_ACTIVITY=360

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
today=datetime.now(timezone.utc)
try:
    access_token=os.environ['GITHUB_TOKEN']

except:
    logging.error('github token not found')
    sys.exit(1)


def get_report(filename):
    secret_list={}
    with open(filename) as file:
        for line in file:
            readline=line.rstrip()
            json_data=json.loads(readline)
            try:
                secret_list.append["secret":json_data["Raw"]]={"detector":json_data["DetectorName"],"source":json_data["SourceMetadata"]["Data"]["Github"]["link"]}
            except KeyError:
                logging.error('similar secret aleady exist')
    return secret_list

def main(repo,default,branch):
    secret_list=[]
    archive_test=False
    sanitise_list=[]
    if(not repo or not default or branch):
        logging.error("Mandatory arguments missing repo,default,branch")
    repo_url="https://github.com/"+repo
    p = subprocess.run("trufflehog git --no-update --json --concurrency 10 --repo "+repo_url+" --branch "+default+" > default.json",stdout=subprocess.PIPE, shell=True,check=True)
    p = subprocess.run("trufflehog github --no-update --json --concurrency 10 --repo "+repo_url+" --branch "+branch+" > branch.json",stdout=subprocess.PIPE, shell=True,check=True)
    main_results=get_report("default.json")
    branch_results=get_report("branch.json")
    result={x:branch_results[x] for x in branch_results if x not in main_results}
    # Serializing json
    json_object = json.dumps(result, indent=4)
    # Writing to output.json
    with open("output.json", "w") as outfile:
        outfile.write(json_object)
    stats={}
    for x in sanitise_list:
        if(not x["detector"] in stats):
          stats[x["detector"]]=1
        else:
          stats[x["detector"]]+=1
    print(stats)



if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    parser.add_argument('-r','--repo', type = str, required = True, help='repo name of the project')
    parser.add_argument('-d','--default', type = str, required = True, help='default branch of the project')
    parser.add_argument('-b','--branch', type = str, required = True, help='current branch of the project')
    args = argparser.parse_args()
    repos=None
    exclude_list=[]
    main(args.repo,args.default,args.branch)