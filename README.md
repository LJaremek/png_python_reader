# PNG Python Reader
Complete implementation of reading png files in Python

---

## How does a PNG file looks like?

Below is [test_png/bit_depth_32.png](https://github.com/LJaremek/png_python_reader/blob/main/test_png/bit_depth_32.png) file. Every byte is converted to hex. </br>
**89, 50, 4e, 47, d, a, 1a, a, 0, 0, 0, d, 49, 48, 44, 52, 0, 0, 0, 3, 0, 0, 0, 3, 8, 6, 0, 0, 0, 56, 28, b5, bf, 0, 0, 0, 1, 73, 52, 47, 42, 0, ae, ce, 1c, e9, 0, 0, 0, 4, 67, 41, 4d, 41, 0, 0, b1, 8f, b, fc, 61, 5, 0, 0, 0, 9, 70, 48, 59, 73, 0, 0, e, c1, 0, 0, e, c1, 1, b8, 91, 6b, ed, 0, 0, 0, 1b, 49, 44, 41, 54, 18, 57, 63, 64, 60, f8, ff, 9f, 1, a, 98, c0, e4, 7f, 
a0, 18, 10, 20, c9, 30, 30, 0, 0, 6e, 34, 5, 1, 78, 6c, 90, 61, 0, 0, 0, 0, 49, 45, 4e, 44, ae, 42, 60, 82**

First 8 bytes is a header of PNG which looks like: <br>
**89, 50, 4e, 47, d, a, 1a, a**

When we checked if it is for sure PNG, we can read the file data. </br>
A PNG file consists of "chunks". Every chunks contain 4 informations:
- chunk size (first 4 bytes)
- chunk type (next 4 bytes)
- chunk data (as many bits as the chunk size is)
- chunk crc (next 4 bytes)

## The most important chunk types:

### IHDR - start chunk
Chunk size:
- 13 bytes

Chunk data:
- image width (first 4 bytes)
- image height (next 4 bytes)
- image bit depth (next 1 byte)
- colour type: 0, 2, 3, 4 or 6 (next 1 byte)
- compression method: 0 only; deflate algorithm (next 1 byte)
- filter method: 0 only; 5 filters contain (next 1 byte)
- interlace method: 0 is no interlance, 1 is adam7 interlance (last 1 byte)
### IDAT - data chunk
### IEND - end chunk
