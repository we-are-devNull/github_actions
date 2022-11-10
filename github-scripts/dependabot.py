import logging,os,requests,sys,subprocess
from dateutil import parser
from datetime import datetime, timezone
import json

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
today=datetime.now(timezone.utc)


try:
    access_token=os.environ['GITHUB_TOKEN']

except:
    logging.error('github token not found')
    sys.exit(1)

url="https://api.github.com/graphql"
headers = {'Authorization': 'token ' + access_token, 'Content-Type': 'application/json'}

dependabot_query="""query($repo:String!,$org:String!){
    repository(name: $repo, owner: $org) {
        vulnerabilityAlerts(first: 100) {
            nodes {
                createdAt
                dismissedAt
                vulnerableManifestPath
                vulnerableRequirements
                securityVulnerability {
                    package {
                        name
                    }
                    advisory {
                        description
                    }
                    severity
                    firstPatchedVersion{
                        identifier
                    }
                    vulnerableVersionRange
                }
            }
        }
    }
}
"""

variables= {"org":"<orgname>","repo":"web-offers"}
json={'query':dependabot_query,'variables':variables}
result_list=[]
vulnerabilities=[]
try:
    r = requests.post(url=url, json=json, headers=headers)
    result=r.json()
    print(result)
    result_list=result['data']['repository']['vulnerabilityAlerts']['nodes']
    for x in result_list:
        vulnerabilities.append({"createdAt":x["createdAt"],"dismissedAt":x["dismissedAt"],"file":x["vulnerableManifestPath"],
        "vulnerable_versions":x["vulnerableRequirements"],"name":x["securityVulnerability"]["package"]["name"],
        "severity":x["securityVulnerability"]["severity"],"fixedversion":x["securityVulnerability"]["firstPatchedVersion"]["identifier"]})
except TypeError:
    logging.error('error sending request to {repos}'.format(repos=repo))
for x in vulnerabilities:
    print(x)