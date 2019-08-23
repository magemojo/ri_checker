import pandas as pd


### FUNCTIONS
def clean_data(df):
    df.columns = [c.replace(' ', '_') for c in df.columns]

    #rename some shit because its annoying
    df.rename(columns={'Linux_On_Demand_cost': 'monthly_cost'}, inplace=True)
    #drop inane extra shit
    df = df[['API_Name', 'monthly_cost']]
    return df


def get_families(df):
    families = list(df.API_Name)
    families = [f.split('.')[0] for f in families]
    families = set(families)
    return families


def format_cost(df):
    def cost(x):
        if x.monthly_cost == "unavailable":
            #if no value like the junky U9s, set to 1
            return 1.0
        return x.monthly_cost.split()[0].replace("$", "")

    df["monthly_cost"] = df.apply(lambda x: cost(x), axis=1)
    df["monthly_cost"] = pd.to_numeric(df["monthly_cost"])
    return df


def get_min_costs(families, df):
    min_costs = {}
    for f in families:
        min_costs[f] = df.loc[df.API_Name.str.contains(f)].min().monthly_cost
    return min_costs


def set_ratios(min_costs, df):
    def ratio(x):
        return x.monthly_cost/min_costs[x.API_Name.split('.')[0]]

    df["ratio"] = df.apply(lambda x: ratio(x), axis=1)
    return df
### END FUNCTIONS


### MAIN
if __name__ == "__main__":

    df = pd.read_csv("ec2_data.csv")

    df = clean_data(df)
    df = format_cost(df)
    families = get_families(df)

    print(families)
    min_costs = get_min_costs(families, df)
    #Linux_On_Demand_cost use this cost
    df = set_ratios(min_costs, df)
    #save to csv
    df.to_csv('ratios.csv', index=True, header=True)
