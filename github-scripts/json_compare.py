import sys
import json

def get_report(filename):
    secret_list={}
    with open(filename) as file:
        for line in file:
            readline=line.rstrip()
            json_data=json.loads(readline)
            json_data["Raw"]=str(hash(json_data["Raw"]))
            try:
                secret_list[json_data["Raw"]]={"detector":json_data["DetectorName"],"source":json_data["SourceMetadata"]["Data"]["Git"]["file"]}
            except KeyError:
                logging.error('similar secret aleady exist')
    return secret_list

def main(default,branch):
    secret_list=[]
    archive_test=False
    sanitise_list=[]
    main_results=get_report(default)
    branch_results=get_report(branch)
    result={x:branch_results[x] for x in branch_results if x not in main_results}
    print(json.dumps(result))
    if(len(result)>0):
        sys.exit(1)


if __name__ == '__main__':
    if(not len(sys.argv)>2):
        sys.exit(1)
    main(sys.argv[1],sys.argv[2])