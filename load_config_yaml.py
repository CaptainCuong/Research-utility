from argparse import Namespace
import yaml

with open('config.yml') as f:
    args = Namespace(**yaml.full_load(f))