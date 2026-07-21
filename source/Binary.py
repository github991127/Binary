def btd(binary):
    """二进制字符串转十进制字符串，验证输入仅含 0/1。"""
    binary = binary.strip()
    if not binary:
        return '0'
    if not set(binary).issubset({'0', '1'}):
        raise ValueError('二进制数只能包含 0 和 1')
    return str(int(binary, 2))


def dtb(decimal):
    """十进制字符串转二进制字符串，验证输入为有效整数。"""
    decimal = decimal.strip()
    if not decimal:
        return '0'
    if not decimal.lstrip('-').isdigit():
        raise ValueError('十进制数只能包含数字')
    return bin(int(decimal))[2:]


def binary_to_decimal(binary):
    """支持 `.` 分隔的多段二进制转十进制。"""
    binary = binary.strip('.')
    if not binary:
        return ''
    parts = binary.split('.')
    return '.'.join(btd(part) for part in parts)


def decimal_to_binary(decimal):
    """支持 `.` 分隔的多段十进制转二进制。"""
    decimal = decimal.strip('.')
    if not decimal:
        return ''
    parts = decimal.split('.')
    return '.'.join(dtb(part) for part in parts)


def main():
    binary = '...11000000.10101000.01100100.00111011'
    decimal = '192.168.100.59'
    print(binary_to_decimal(binary))
    print(decimal_to_binary(decimal))


if __name__ == "__main__":
    main()
