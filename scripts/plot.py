import json
import pandas as pd
import matplotlib.pyplot as plt
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str)
    parser.add_argument("output", type=str, default="plot.png")
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as file:
        data = json.load(file)
    df = pd.json_normalize(data, record_path=["benchmarks"])
    print(df)

    x = df["nodes"]
    y = df["real_time"]
    plt.scatter(x, y)

    plt.title("Relationship between node count and APSP compute time")
    plt.xlabel("Nodes")
    plt.ylabel("Elapsed (us)") # TODO: Pull from json
    plt.show()


if __name__ == "__main__":
    main()
