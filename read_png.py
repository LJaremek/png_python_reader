PNG_HEADER_HEX = ("89", "50", "4e", "47", "d", "a", "1a", "a")
PNG_HEADER_INT = (137, 80, 78, 71, 13, 10, 26, 10)


def open_file(file_path: str) -> list[str]:
    """
    Read bytes from the file.

    Input:
     * file_path: str

    Output:
     * list[str] - bytes convert to hex values (string without '0x')
    """
    with open(file_path, "rb") as file:
        lines = file.readlines()

    byte_list = []
    for line in lines:
        byte_list += [hex(number)[2:] for number in list(line)]

    return byte_list


def pop_bytes(byte_list: list[str], n: int) -> list[str]:
    """
    Pop n bytes from the given list.

    Input:
     * byte_list: list[str] - original list with bytes in hex as list
     * n: int - number of bytes to pop

    Output:
     * list[str] - poped bytes
    """
    the_bytes: list[str] = [byte_list.pop(0) for _ in range(n)]
    return the_bytes


def hex_to_dec(hex_number: list[str]) -> int:
    """
    Convert hexal (16) number to decimal (10).

    Input:
     * list[str] - list of hex number for example ["1", "a4"]

    Output:
     * int - decimal number for example 420
    """
    return int("".join(hex_number), 16)


def hex_to_str(hex_number: list[str]) -> str:
    """
    Convert hexal (16) number to string.

    Input:
    * list[str] - list of hex number for example ["50", "4e", "47"]

    Output:
     * str - string for example "PNG"
    """
    return "".join([chr(int(number, 16)) for number in hex_number])


def get_chunk(all_bytes: list[str]) -> dict:
    """
    Read first encountered chunk in the given bytes.

    Input:
     * all_bytes: list[int]

    Output:
     * dict - chunk in the dict form:
        size: int,
        type: str,
        data: list[str] - list of bytes,
        crc: list[str] - list of bytes
    """
    chunk_size: int = hex_to_dec(pop_bytes(all_bytes, 4))
    chunk_type: str = hex_to_str(pop_bytes(all_bytes, 4))
    chunk_data: list[str] = pop_bytes(all_bytes, chunk_size)
    chunk_crc: list[str] = pop_bytes(all_bytes, 4)

    return {"size": chunk_size,
            "type": chunk_type,
            "data": chunk_data,
            "crc": chunk_crc}


def get_chunks(all_bytes: list[int]) -> list[dict]:
    """
    Read all chunks in the given bytes.

    Input:
     * all_bytes: list[int]

    Output:
     * list[dict] - chunks in the dict form:
        size: int,
        type: str,
        data: list[str] - list of bytes,
        crc: list[str] - list of bytes
    """
    chunks = []
    while len(all_bytes) != 0:
        chunks.append(get_chunk(all_bytes))
    return chunks


def main(file_path: str) -> None:
    all_bytes = open_file(file_path)

    header_bytes = tuple(pop_bytes(all_bytes, 8))
    if header_bytes != PNG_HEADER_HEX:
        print(header_bytes)
        print(PNG_HEADER_HEX)
        raise Exception("Header of file is not a PNG header.")

    chunks = get_chunks(all_bytes)

    print([chunk["type"] for chunk in chunks])


if __name__ == "__main__":
    main("test_png/cap.png")
