import pandas as pd
import matplotlib.pyplot as plt
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str)
    parser.add_argument("output", type=str, default="plot.png")
    args = parser.parse_args()

    df = pd.read_csv(args.input)

    x = df['Nodes']
    y = df['ElapsedNS']
    plt.scatter(x, y)

    plt.title("Perf")
    plt.xlabel("Nodes")
    plt.ylabel("Nanoseconds Elapsed")
    plt.show()

if __name__ == "__main__":
    main()
