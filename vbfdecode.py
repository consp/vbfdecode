import argparse
import re
from binascii import unhexlify, hexlify

class VBF:
    version = 0
    description = ""
    sw_part = ""
    sw_part_type = ""
    network = 0x00
    data_format_identifier = 0x00
    ecu_address = 0x00
    verification_block_start = 0x00
    frame_format = ""
    erase = []
    checksum = bytes()
    raw = bytes()
    data = []

    def __init__(self, data):
        if not isinstance(data, bytes):
            raise TypeError("Requires binary input")

        try:
            self.version = data[data.find(b"vbf_version"):data.find(b"\n")].split(b"=")[1].replace(b" ", b"").replace(b";", b"").decode()
        except:
            raise ValueError("Version not found")

        header = data[data.find(b"header"):data.find(b"\n}")+2]

        desc = header[header.find(b"description ="):header.find(b"};")].replace(b"//", b"") # remove comment lines if they exist
        self.description = ""
        for line in desc.split(b"\n"):
            self.description = self.description + line[line.find(b"\"")+1:line.find(b"\",")].decode() + "\n" if len(line[line.find(b"\"")+1:line.find(b"\",")]) > 0 else self.description
        header = header[header.find(b"sw_part_number"):]
        erase = False
        for line in header.split(b"\n"):
            line = line.replace(b"\t", b"").replace(b"\r", b"")
            if line.startswith(b"//"):
                continue
            try:
                if b"sw_part_number" in line:
                    self.sw_part = line[line.find(b" = ")+3:line.find(b"\";")].replace(b" ", b"").replace(b"\"", b"").decode()
                if b"sw_part_type" in line:
                    self.sw_part_type = line[line.find(b" = ")+3:line.find(b";")].replace(b" ", b"").replace(b"\"", b"").decode()
                if b"network" in line:
                    self.network = line[line.find(b" = ")+3:line.find(b";")].replace(b" ", b"").replace(b"\"", b"").decode()
                if b"data_format_identifier" in line:
                    self.data_format_identifier = int(line[line.find(b" = ")+3:line.find(b";")].replace(b" ", b"").replace(b"\"", b"").decode(), 16)
                if b"ecu_address" in line:
                    self.ecu_address = int(line[line.find(b" = 0x")+5:line.find(b";")].replace(b" ", b"").replace(b"\"", b"").decode(), 16)
                if b"verification_block_start" in line:
                    self.verification_block_start = int(line[line.find(b" = 0x")+5:line.find(b";")].replace(b" ", b"").replace(b"\"", b"").decode(), 16)
                if b"frame_format" in line:
                    self.frame_format = line[line.find(b" = ")+3:line.find(b";")].replace(b" ", b"").replace(b"\"", b"").decode()
                if b"file_checksum" in line:
                    self.file_checksum = unhexlify(line[line.find(b" = 0x")+5:line.find(b";")].replace(b" ", b"").replace(b"\"", b""))
                if b"erase = " in line or erase:
                    # dirty find
                    erase = True
                    r = re.compile(r'{\s*0x([0-9A-Fa-f]+),\s*0x([0-9A-Fa-f]+)\s*}')
                    m = r.search(line.decode())
                    if m is not None:
                        self.erase.append([m.group(1), m.group(2)])
                if erase:
                    if b"};" in line:
                        erase = False
            except Exception as e:
                print(line)
                raise
        binary_offset = data.find(b"\n}")+2
        binary = data[binary_offset:]
        self.data = list()
        while len(binary) > 0:
            location = int.from_bytes(binary[:4], 'big')
            size = int.from_bytes(binary[4:8], 'big')
            data = binary[8:8+size]
            checksum = binary[8+size:8+size+2]
            binary = binary[8+size+2:]
            print("Offset: 0x{:X}, Location: 0x{:X}, Size: 0x{:X}, Data Offset: 0x{:X}".format(binary_offset,  location, size, binary_offset + 8))
            binary_offset += 8+size+2
            if location != self.verification_block_start:
                self.data.append((location, data, checksum))


    def __str__(self):
        string = "VBF v{}\n".format(self.version)
        string = string + "Description: {}".format(self.description)
        string = string + "Software part: {} type: {}\n".format(self.sw_part, self.sw_part_type)
        string = string + "Network: 0x{:08X}\n".format(self.network)
        string = string + "Data Format Identifier: 0x{:08X}\n".format(self.data_format_identifier)
        string = string + "ECU address: 0x{:08X}\n".format(self.ecu_address)
        string = string + "Frame_format:{}\n".format(self.frame_format)
        string = string + "Erase frames:\n"
        for x in self.erase:
            string = string + "0x{} (0x{})\n".format(x[1], x[0])
        string = string + "Data blobs:\n"
        for i in self.data:
            string = string + "0x{:08X}\t0x{:08X}\t {}\n".format(i[0], len(i[1]), hexlify(i[2]).decode())
        return string

    def dump(self, dst):
        for x in self.data:
            print("{:08X}.bin ".format(x[0]))
            filename = "{:08X}.bin".format(x[0]).replace(" ", "")
            with open(dst + "/" + filename, "wb") as f:
                f.write(x[1])
            f.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="VBF somewhat decoder and blob extracter", usage="Try me with a filename.vbf")
    parser.add_argument("file", help="VBF file to show data about", type=str)
    parser.add_argument("-b", "--binary", help="Write binary blobs in vbf to [address].bin", action="store_true", default=False)
    args = parser.parse_args()
    filename = args.file

    with open(filename, "rb") as f:
        vbf = VBF(f.read())
        print(vbf)

        if args.binary:
            print("Saving: ")
            for x in vbf.data:
                print("%8X.bin " % (x[0]))
                with open(("%8X.bin" % (x[0])).replace(" ", ""), "wb") as f:
                    f.write(x[1])
