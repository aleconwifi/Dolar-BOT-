

if __name__ == '__main__':
    n = 5244575454544656564545457588644454577875454245
    z = format(n, ",.2f").replace(",", "X").replace(".", ",").replace("X", ".")
    print(z)