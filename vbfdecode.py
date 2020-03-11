import argparse
from binascii import unhexlify, hexlify

class VBF:
    version = 0
    description = ""
    sw_part = ""
    sw_part_type = ""
    network = ""
    ecu_address = 0x00
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
            if b"sw_part_number" in line:
                self.sw_part = line[line.find(b" = ")+3:line.find(b"\";")].replace(b" ", b"").replace(b"\"", b"").decode()
            if b"sw_part_type" in line:
                self.sw_part_type = line[line.find(b" = ")+3:line.find(b";")].replace(b" ", b"").replace(b"\"", b"").decode()
            if b"network" in line:
                self.network = line[line.find(b" = ")+3:line.find(b";")].replace(b" ", b"").replace(b"\"", b"").decode()
            if b"ecu_address" in line:
                self.ecu_address = int(line[line.find(b" = 0x")+5:line.find(b";")].replace(b" ", b"").replace(b"\"", b"").decode(), 16)
            if b"frame_format" in line:
                self.frame_format = line[line.find(b" = ")+3:line.find(b";")].replace(b" ", b"").replace(b"\"", b"").decode()
            if b"file_checksum" in line:
                self.file_checksum = unhexlify(line[line.find(b" = 0x")+5:line.find(b";")].replace(b" ", b"").replace(b"\"", b""))
            if b"erase = " in line or erase:
                # dirty find
                erase = True
                locs = [i+2 for i in range(len(line)) if line.startswith(b'0x', i)]
                for x in locs:
                    self.erase.append(int(line[x:x+8], 16))
            if erase:
                if b"};" in line:
                    erase = False

        binary = data[data.find(b"\n}")+2:]
        self.data = list()
        while len(binary) > 0:
            location = int.from_bytes(binary[:4], 'big')
            size = int.from_bytes(binary[4:8], 'big')
            data = binary[8:size]
            checksum = binary[8+size:8+size+2]
            binary = binary[8+size+2:]
            self.data.append((location, data, checksum))
            #print("%s %d %s" % (hex(location), size, hexlify(checksum).decode()))


    def __str__(self):
        string = "VBF [v%s]:\n" % (self.version)
        string = string + "Description: %s" % (self.description)
        string = string + "Software part: %s type: %s\n" % (self.sw_part, self.sw_part_type)
        string = string + "Network: %s @ 0x%3X\n" % (self.network, self.ecu_address)
        string = string + "Frame_format:%s\n" % (self.frame_format)
        string = string + "Erase frames:\n"
        for x in self.erase:
            string = string + "0x%08X\n" % (x)
        string = string + "Data blobs:\n"
        for i in self.data:
            string = string + "0x%08X\t%d\t %s\n" % (i[0], len(i[1]), hexlify(i[2]).decode())
        return string


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


