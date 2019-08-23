# ri_checker
For RIs


## Setup

pip install -r requirements.txt

## Usage

Open a command line, try:

```
python check_ris.py us-east-1 large
```

The first arg is the AWS region, the 2nd is the relative unit.  Since all families are scanned, not every family has every unit like nano, small etc. The only two in common to all instance types are *large* and *xlarge*

Otherwise, it will give results in the smallest base unit of a particular family.

Example output:

```
$ python check_ris.py us-east-1 large
Checking for matching instances...

4.0 More RIs needed for type c5d\..  Buy this amount of c5d\.large
2.1199999999999974 Extra RIs for type c4\., convert c4\.large to other types.
0.0021551724137931494 Extra RIs for type t2\., convert t2\.large to other types.
4.5 More RIs needed for type t3\..  Buy this amount of t3\.large
0.2514285714285714 More RIs needed for type m1\..  Buy this amount of m1\.large
26.0 Extra RIs for type i3en\., convert i3en\.large to other types.

### Full scoring data and instance counts ###

             type  running_counts  reserved_counts  running_score  reserved_score
0      c3.2xlarge             1.0              0.0       4.000000             0.0
1        c3.large             0.0              4.0       0.000000             4.0
2      c4.4xlarge             3.0              0.0      23.880000             0.0
3        c4.large             0.0             26.0       0.000000            26.0
4     c5d.2xlarge             1.0              0.0       4.000000             0.0
5   i3en.12xlarge            16.0             12.0     384.000000           288.0
6    i3en.3xlarge             7.0              0.0      42.000000             0.0
7      i3en.large             0.0            164.0       0.000000           164.0
8        m1.small             1.0              0.0       1.000000             0.0
9       m3.medium             2.0              2.0       2.000000             2.0
10      t2.medium             2.0              0.0      16.000000             0.0
11       t2.micro             2.0              0.0       4.000000             0.0
12        t2.nano             0.0             24.0       0.000000            24.0
13       t2.small             1.0              0.0       3.965517             0.0
14     t3.2xlarge             1.0              0.0      70.808511             0.0
15       t3.small             2.0              0.0       8.851064             0.0
16    z1d.3xlarge             8.0              0.0      48.000000             0.0
17    z1d.6xlarge             1.0              0.0      12.000000             0.0
18      z1d.large             3.0             39.0       3.000000            39.0
19      z1d.metal             0.0              1.0       0.000000            24.0
```

Note it gives a table of recommendation, and the scoring table so you can understand the data and what you have currently running. Scoring is generated via a separate csv called ratios.csv. Which in turn is generated via generate_ratios.py (python generate_ratios.py) and *that* depends on ec2_data.csv existing.

ec2_data.csv is pulled from ec2instances.info, the only columns needed are the instance name and the Linux on demand monthly cost.  Ratios between monthly costs are generally whole numbers, but with RIs etc they can be off by tiny decimal points, not enough to matter when it comes to calculating the RIs, so you may get results asking you to buy .9999 of an instance or similar.