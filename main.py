import os

# filename: written file by c function
# n: 2^n = length of matrix
# seeds: number of random seeds
# threads: number of threads
# threaded: 1 for threaded, 0 for not threaded
def getMatrixFromCFunction(n, seeds, threads, threaded = 1, filename = "cMultithread/output.txt"):
    commandLine = f"cd cMultithread && make && ./main.x {threaded} {n} {seeds} {threads} print && cd .."
    os.system(commandLine)
    matrix = []

    with open(filename, "r") as f:
        for line in f:
            matrix.append(list(map(int, line.split())))
    return matrix

def prettyPrintMatrix(matrix):
    for row in matrix:
        print(row)

if __name__ == '__main__':
    # print(getMatrixFromCFunction(6, 9, 3))
    matrix = getMatrixFromCFunction(5, 9, 3)
    prettyPrintMatrix(matrix)
