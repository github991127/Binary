def btd(binary):
    return str(int(binary, 2))


def dtb(decimal):
    return bin(int(decimal))[2:]


def binary_to_decimal(binary):
    binary = binary.strip(".")
    binary = binary.split(".")
    decimal = []
    for b in binary:
        d = btd(b)
        decimal.append(d)
    decimal = ".".join(decimal)
    return decimal


def decimal_to_binary(decimal):
    decimal = decimal.strip('.')
    decimal = decimal.split(".")
    binary = []
    for d in decimal:
        b = dtb(d)
        binary.append(b)
    binary = ".".join(binary)
    return binary


def main():
    binary = '...11000000.10101000.01100100.00111011'
    decimal = '192.168.100.59...'
    # decimal = '192'
    print(binary_to_decimal(binary))
    print(decimal_to_binary(decimal))


if __name__ == "__main__":
    main()
