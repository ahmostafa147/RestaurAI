import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pull_dataset import PullDataset

# Handle env_config import with fallback
try:
    from ..env_config import token
except ImportError:
    from env_config import token
#make command run with snapshot_id as parameter and print the dataset 
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot_id", type=str)
    args = parser.parse_args()
    pull_dataset = PullDataset()
    dataset = pull_dataset.safe_pull_dataset(args.snapshot_id)
    print(dataset)