import re
from zlib import decompress

from matplotlib import image  # , compress

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


def filter_value(filter_type: int,
                 row_index: int,
                 column_index: int,
                 value_to_filter: int,
                 bytes_per_row: int,
                 idat_data: list[int],
                 ready_data: int,
                 bytes_per_pixel: int) -> int:
    """
    Filter the given value using one of the 5 filter methods:
     0 - (None)  - No filter method
     1 - (Sub)   - Each byte is replaced with the difference between
                   it and the 'corresponding byte' to its left.
     2 - (Up)    - Each byte is replaced with the difference between
                   it and the byte above it (in the previous row,
                   as it was before filtering).  # For sure before filtering?)
     3 - (Avg)   - Each byte is replaced with the difference between
                   it and the average of the corresponding bytes to its
                   left and above it, truncating any fractional part.
     4 - (Paeth) - Each byte is replaced with the difference between
                   it and the Paeth 'predictor' of the corresponding bytes
                   to its left, above it, and to its upper left.
    """
    if (filter_type == 0 or (filter_type == 1 and column_index < bytes_per_pixel)):
        return value_to_filter
    elif filter_type == 1:
        return (ready_data[-bytes_per_pixel] - value_to_filter) % 256
    elif filter_type == 2:
        up_byte_index = (row_index-1)*bytes_per_row + column_index
        return (ready_data[up_byte_index] + value_to_filter) % 256
    elif filter_type == 3:
        left_byte = ready_data[-bytes_per_pixel]
        up_byte_index = (row_index-1)*bytes_per_row \
            + column_index - bytes_per_pixel
        up_byte = idat_data[up_byte_index]
        return abs(value_to_filter - (left_byte+up_byte)//2)
    elif filter_type == 4:
        left_byte = ready_data[-bytes_per_pixel]
        up_byte_index = (row_index-1)*bytes_per_row + column_index
        up_byte = idat_data[up_byte_index]
        up_left_byte_index = (row_index-1)*bytes_per_row \
            + column_index - 1 - bytes_per_pixel
        up_left_byte = idat_data[up_left_byte_index]
        base_value = left_byte + up_byte - up_left_byte
        sub_list = ((left_byte-base_value),
                    (up_byte-base_value),
                    (up_left_byte-base_value))
        index = sub_list.index(min(sub_list))
        the_value = (left_byte, up_byte, up_left_byte)[index]
        return abs(value_to_filter - the_value)
    else:
        raise Exception("Incorrect filter value")


def reshape(data: list[int],
            width: int,
            height: int,
            depth: int = 4) -> list[list[list[int]]]:

    numpy_data = [[[[] for d in range(depth)]
                  for w in range(width)]
                  for h in range(height)]

    index = 0
    for h in range(height):
        for w in range(width):
            for d in range(depth):
                element = data[index]
                numpy_data[h][w][d] = element
                index += 1

    return numpy_data


def main(file_path: str) -> None:
    all_bytes = open_file(file_path)

    header_bytes = tuple(pop_bytes(all_bytes, 8))
    if header_bytes != PNG_HEADER_HEX:
        print(header_bytes)
        print(PNG_HEADER_HEX)
        raise Exception("Header of file is not a PNG header.")

    chunks = get_chunks(all_bytes)

    chunk_ihdr = [chunk for chunk in chunks if chunk["type"] == "IHDR"][0]

    image_width = hex_to_dec(pop_bytes(chunk_ihdr["data"], 4))
    image_height = hex_to_dec(pop_bytes(chunk_ihdr["data"], 4))
    _ = hex_to_dec(pop_bytes(chunk_ihdr["data"], 1))  # image_depth
    image_color = hex_to_dec(pop_bytes(chunk_ihdr["data"], 1))
    # image_compression = hex_to_dec(pop_bytes(chunk_ihdr["data"], 1))
    # image_filter = hex_to_dec(pop_bytes(chunk_ihdr["data"], 1))
    # image_interlance = hex_to_dec(pop_bytes(chunk_ihdr["data"], 1))

    decompressed_data: list[int] = []
    chunk_idat_list = [chunk for chunk in chunks if chunk["type"] == "IDAT"]
    for chunk_idat in chunk_idat_list:
        compressed_data: list[int] = [int(number, 16)
                                      for number
                                      in chunk_idat["data"]]
        decompressed_data += [int_value
                              for int_value
                              in decompress(bytes(compressed_data))]

    if image_color == 6:  # TODO ładniej jakoś
        bytes_per_pixel = 4
    elif image_color == 2:
        bytes_per_pixel = 3
    else:
        raise Exception(f"""Unknown image color with value: {image_color}.
        Please implement it.""")

    bytes_per_row = bytes_per_pixel * image_width

    print("Decompressed data:\n", decompressed_data)

    ready_data: list[int] = []
    idat_index = 0
    for row_index in range(image_height):
        filter_type = decompressed_data[idat_index]
        idat_index += 1
        for column_index in range(bytes_per_row):
            value_to_filter = decompressed_data[idat_index]
            idat_index += 1

            ready_value = filter_value(filter_type,
                                       row_index, column_index,
                                       value_to_filter,
                                       bytes_per_row,
                                       decompressed_data, ready_data,
                                       bytes_per_pixel)
            ready_data.append(ready_value)

    print("Filtered data:\n", ready_data)

    reshaped_data = reshape(
        ready_data,
        image_width,
        image_height,
        bytes_per_pixel
        )

    print(reshaped_data)
    from matplotlib import pyplot as plt
    plt.imshow(reshaped_data)
    plt.show()


if __name__ == "__main__":
    main("test_png/bit_depth_32.png")

# bit -> depth, color
# 32 -> 8, 6
# 24 -> 8, 2
#  8 -> 8, 3
