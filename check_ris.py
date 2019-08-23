import pandas as pd 
import sys
import boto3
#CONFIG
region = sys.argv[1]
try:
    base_unit = sys.argv[2]
except:
    base_unit = ''
ec2_client = boto3.client('ec2',region_name=region)

### FUNCTIONS
def find_instances(client):
    print("Checking for matching instances...\n")
    instances_found=[]
    response = client.describe_instances()
    for r in response['Reservations']:
        for i in r['Instances']:
            instances_found.append(i)
    return instances_found

def find_reserved_instances(client):
    reserved=[]
    response = client.describe_reserved_instances()["ReservedInstances"]
    return response

def running_instances(instances):
    return [instance["InstanceType"] for instance in instances if instance["State"]["Name"] == "running"]

def active_reserve_instances(reserved):
    return [ri for ri in reserved if ri["State"] == "active"]

def get_score_list(df):
    scores = {}
    types = list(df.API_Name)
    score = list(df.ratio)
    for i in range(0,len(types)):
        scores[types[i]] = score[i]
    return scores 


def get_families(df):
    families = list(df.API_Name)
    families = [f.split('.')[0] + r"\." for f in families]
    families = set(families)
    return families

def return_score(instance_type,scores):
    try:
        return scores[instance_type]
    except KeyError:
        return 0

def get_min_base(family,base_unit,scores):
    #gets the score for the base unit for conversion at the end.
    family = family.replace("\\","")
    for key,value in scores.items():
        if family + base_unit in key:
                return value
### END FUNCTIONS

if __name__ == "__main__":

    #CONSTANTS
    scores = get_score_list(pd.read_csv("ratios.csv"))
    families = get_families(pd.read_csv("ratios.csv"))
    #END CONSTANTS
    running_instances=running_instances(find_instances(ec2_client))
    reserved=active_reserve_instances(find_reserved_instances(ec2_client))

    df_running=pd.DataFrame(running_instances)
    df_reserved=pd.DataFrame(reserved)
    running_counts=df_running[0].value_counts()
    if df_reserved.empty:
        reserved_counts=0
    else:
        reserved_counts=df_reserved.groupby(["InstanceType"]).InstanceCount.sum()

    
    #Comparison loop
    compare=pd.DataFrame(dict(running_counts = running_counts,  reserved_counts= reserved_counts)).reset_index()
    compare.columns = ["type","running_counts","reserved_counts"]

    compare["running_score"] = compare.apply(lambda x: x["running_counts"]*return_score(x["type"],scores), axis=1)
    compare["reserved_score"] = compare.apply(lambda x: x["reserved_counts"]*return_score(x["type"],scores), axis=1)
    compare=compare.fillna(0)


    for FAMILY in families:
        base_score = get_min_base(FAMILY,base_unit,scores)
        running_score=compare.loc[compare["type"].str.contains(FAMILY)].running_score.sum()
        reserved_score=compare.loc[compare["type"].str.contains(FAMILY)].reserved_score.sum()
        #print(compare.loc[compare["type"].str.contains(FAMILY)])
        if reserved_score < running_score:
            #print(FAMILY,base_score)
            print("{1} More RIs needed for type {0}.  Buy this amount of {0}{2}".format(FAMILY,(running_score-reserved_score)/base_score,base_unit))
        if running_score  < reserved_score:
            #print(FAMILY,base_score)
            print("{1} Extra RIs for type {0}, convert {0}{2} to other types.".format(FAMILY,(compare.loc[compare["type"].str.contains(FAMILY)].reserved_score.sum()-compare.loc[compare["type"].str.contains(FAMILY)].running_score.sum())/base_score,base_unit))

    print("\n### Full scoring data and instance counts ###\n")
    print(compare)