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

url="https://api.github.com/graphql"
headers = {'Authorization': 'token ' + access_token, 'Content-Type': 'application/json'}


get_commit = '''
query($owner:String!,$repo:String!){
  repository(owner: $owner, name: $repo) {
    defaultBranchRef {
      target {
        ... on Commit {
          history(first: 1) {
            nodes {
              message
              committedDate
            }
          }
        }
      }
    }
  }
}
'''


get_all_repos='''
query($org:String!)
{
  organization(login: $org) {
    repositories(first: 100 after:AFTER) {
      pageInfo {
        hasNextPage
        endCursor
      }
      edges {
        node {
          name
          url
          isPrivate
          isArchived
        }
        cursor
      }
    }
  }
}
'''

def get_github_repos():
  has_next=True
  after_cursor=None
  org_variables= {"org":"<org_name>"}
  repo_list=[]
  node_list=[]
  while(has_next):
    query=get_all_repos.replace(
          "AFTER", '"{}"'.format(after_cursor) if after_cursor else "null"
      )
    gql_data={'query':query,'variables':org_variables}
    r = requests.post(url=url, json=gql_data, headers=headers)
    result=r.json()
    node_list=result['data']['organization']['repositories']['edges']
    for x in node_list:
      repo=x['node']['name']
      is_archived=x['node']['isArchived']
      repo_list.append({'name':repo,'is_archived':is_archived})
    has_next=result['data']['organization']['repositories']['pageInfo']['hasNextPage']
    after_cursor=result['data']['organization']['repositories']['pageInfo']['endCursor']
  logging.info("total repositories collected "+str(len(repo_list)))
  return repo_list

def main(repo_list,exclude_list=[]):
  secret_list=[]
  archive_test=False
  sanitise_list=[]
  if(not repo_list):
    logging.warning("Running against list of repos in github")
    repo_list=get_github_repos()
    archive_test=True
  for x in repo_list:
    repo=x['name']
    logging.info(repo)
    if(archive_test and x['is_archived']==True):
      logging.info('Archived {repo} hence skipping'.format(repo=repo))
      continue
    variables= {"owner":"<org_name>","repo":repo}
    gql_data={'query':get_commit,'variables':variables}
    try:
      r = requests.post(url=url, json=gql_data, headers=headers)
      result=r.json()
      logging.debug(result)
      committedDate=result['data']['repository']['defaultBranchRef']['target']['history']['nodes'][0]['committedDate']
    except TypeError:
      logging.error('error sending request to {repos}'.format(repos=repo))
      continue
    committedDate=yourdate = parser.parse(committedDate)
    days=today-committedDate
    if(days.days<LAST_ACTIVITY):
      repo_url="https://github.com/<org_name>/"+repo
      p = subprocess.run("trufflehog github --no-update --json --concurrency 10 --repo "+repo_url+" > truffle.json",stdout=subprocess.PIPE, shell=True,check=True)
      with open("truffle.json") as file:
        for line in file:
          readline=line.rstrip()
          json_data=json.loads(readline)
          secret_list.append({"secret":json_data["Raw"],"detector":json_data["DetectorName"],"source":json_data["SourceMetadata"]["Data"]["Github"]["link"]})
      p = subprocess.run("rm truffle.json",stdout=subprocess.PIPE, shell=True,check=True)
  
  for x in secret_list:
    if(not x['detector'] in exclude_list):
      sanitise_list.append(x)
  # Serializing json
  json_object = json.dumps(sanitise_list, indent=4)
  
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
    argparser.add_argument('--repo', type=str, help='list of repos seperated by comma')
    argparser.add_argument('--exclude', type=str, help='list of secret scanners to exclude seperated by comma')
    args = argparser.parse_args()
    repos=None
    exclude_list=[]
    if(args.exclude):
      exclude_list=args.exclude.split(',')
    if(args.repo):
      repos=args.repo.split(',')
      temp=[]
      for x in repos:
        temp.append({"name":x})
      repos=temp
    main(repos,exclude_list)