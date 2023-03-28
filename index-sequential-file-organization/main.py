"""
Author: Miłosz Ilecki 184577
SBD 2
Typ rekordu: 13. Rekordy pliku: Liczby naturalne.
"""


import math  # for ceil function
import os
import sys  # deleting/creating files
import random  # generating random numbers

RECORD_SIZE = 9
INDEX_SIZE = 4
PAGE_SIZE = 4  # records per page
ALPHA = 0.5
MAX_PRIMARY_PAGES = 5  # starting value
INDEX_FILE = "indexes.txt"
RECORD_FILE = "records.txt"
TMP_FILE = "tmp.txt"
EMPTY = "---"


def find_sum_of_factors(number):
    if number == 1 or number == 0:
        return 1
    sum_factors = 0
    for div in range(1, int(math.sqrt(number)) + 1):
        if number % div == 0:
            sum_factors += div
            if number / div != div:
                sum_factors += number / div
    return int(sum_factors)


class Index:
    def __init__(self, Key, PageNo):
        self.Key = Key  # 2 bytes
        self.PageNo = PageNo  # 2 bytes

    def print(self):
        print(
            "| Key : {:5s} | PageNumber : {:5s}|".format(
                str(self.Key), str(self.PageNo)
            )
        )

    def create_list(self):
        tmp_list = [self.Key.to_bytes(2, "big"), self.PageNo.to_bytes(2, "big")]
        return tmp_list


class Record:
    def __init__(self, *args):

        if len(args) == 4:
            self.Key = args[0]  # max 2 bytes
            self.Data = args[1]  # max 4 bytes
            self.OverflowPointer = args[2]  # max 2 bytes
            self.Delete = args[3]
        else:
            self.Key = 0  # max 2 bytes
            self.Data = 0  # max 4 bytes
            self.OverflowPointer = 0  # max 2 bytes
            self.Delete = 0  # 0- False max 1 byte        4+2+2+1 = 9 bytes

    def update(self, Key, Data):
        self.Key = Key
        self.Data = Data  # Record Type Natural Numbers

    def print(self):
        if self.Key == 0:
            print(
                "| Key : {:5s} | Data : {:5s} | OverflowPointer : {:5s} | Delete : {:3s} |".format(
                    EMPTY, EMPTY, EMPTY, EMPTY
                )
            )
        else:
            print(
                "| Key : {:5s} | Data : {:5s} | OverflowPointer : {:5s} | Delete : {:3s} |".format(
                    str(self.Key),
                    str(self.Data),
                    str(self.OverflowPointer),
                    str(self.Delete),
                )
            )

    def set_OV(self, ptr):
        self.OverflowPointer = ptr

    def create_list(self):
        tmp_list = [
            self.Key.to_bytes(2, "big"),
            self.Data.to_bytes(4, "big"),
            self.OverflowPointer.to_bytes(2, "big"),
            self.Delete.to_bytes(1, "big"),
        ]
        return tmp_list


def create_record_from_bytes(bytes):
    key_ = int.from_bytes(bytes[0:2], "big")
    data_ = int.from_bytes(bytes[2:6], "big")
    ov_ = int.from_bytes(bytes[6:8], "big")
    delete_ = int.from_bytes(bytes[8:9], "big")
    tmp_rec = Record(key_, data_, ov_, delete_)
    return tmp_rec


def create_index_from_bytes(bytes):
    key_ = int.from_bytes(bytes[0:2], "big")
    page_ = int.from_bytes(bytes[2:4], "big")
    tmp_ind = Index(key_, page_)
    return tmp_ind


def binary_search(arr, low, high, x):
    if high >= low:

        mid = (high + low) // 2
        if arr[mid] == x:
            return mid
        elif arr[mid] > x:
            return binary_search(arr, low, mid - 1, x)

        else:
            return binary_search(arr, mid + 1, high, x)
    else:
        return -1


def get_records_from_bytes(bin_read):
    output = []
    for j in range(PAGE_SIZE):
        tmp = bin_read[j * RECORD_SIZE : (j + 1) * RECORD_SIZE]
        tmp_rec = create_record_from_bytes(tmp)
        output.append(tmp_rec)
    return output


def get_bytes_from_records(arr):
    page_bufor = []
    for element in arr:
        tmp = element.create_list()
        bytes = b"".join(tmp)
        page_bufor.append(bytes)
    page_bufor_bytes = b"".join(page_bufor)
    return page_bufor_bytes


def sort_records(arr):
    for i in range(len(arr)):
        if arr[i].Key == 0:
            break
        else:
            for j in range(len(arr)):
                if arr[j].Key == 0:
                    break
                if arr[j].Key > arr[i].Key:
                    arr[j], arr[i] = arr[i], arr[j]


class Indexed_sequential_files:
    def __init__(self):
        self.Reads = 0
        self.Writes = 0
        self.PageSize = PAGE_SIZE
        self.Alpha = 0.5
        self.PrimaryRecords = 0
        self.OverflowRecords = 0
        self.MaxPrimaryRecords = MAX_PRIMARY_PAGES * PAGE_SIZE
        self.MaxOverflowRecords = PAGE_SIZE

    def createIndex(self):
        with open(RECORD_FILE, "rb") as rec_file, open(INDEX_FILE, "wb") as ind_file:
            if self.PrimaryRecords == 0:
                # if no starting records from which we can create index file
                num_pages = int(math.ceil(self.MaxPrimaryRecords / self.PageSize))
                for i in range(num_pages):
                    tmp_indx = Index(i * 10 + 1, i + 1)
                    tmp_index_array = tmp_indx.create_list()
                    bytes = b"".join(tmp_index_array)
                    ind_file.write(bytes)
                    self.inc_writes()
            else:
                num_pages = int(math.ceil(self.MaxPrimaryRecords / self.PageSize))
                for i in range(num_pages):
                    rec_file.seek(RECORD_SIZE * i * PAGE_SIZE)
                    bytes_ = rec_file.read(RECORD_SIZE)
                    self.inc_reads()
                    tmp_rec = create_record_from_bytes(bytes_)
                    if tmp_rec.Key == 0:
                        tmp_index = Index(i * 10 + 1, i + 1)
                    else:
                        tmp_index = Index(tmp_rec.Key, i + 1)

                    tmp_index_array = tmp_index.create_list()
                    bytes = b"".join(tmp_index_array)
                    ind_file.write(bytes)
                    self.inc_writes()

    def searchIndex(self, key):
        # searching through Index file to get page
        with open(INDEX_FILE, "rb") as ind_file:
            max_indx_per_read = int(RECORD_SIZE * PAGE_SIZE / INDEX_SIZE)
            num_pages = int(math.ceil(self.MaxPrimaryRecords / (self.PageSize*INDEX_SIZE)))
            found = False
            page = -1
            for i in range(num_pages):
                bytes_ = ind_file.read(max_indx_per_read * INDEX_SIZE)
                self.inc_reads()
                for j in range(max_indx_per_read):
                    tmp = bytes_[j * INDEX_SIZE : (j + 1) * INDEX_SIZE]
                    if tmp == b"":
                        break
                    tmp_ind = create_index_from_bytes(tmp)
                    global backup
                    backup = tmp_ind
                    if tmp_ind.Key > key:
                        page = tmp_ind.PageNo - 1
                        found = True
                        break

                if found:
                    break

            if page == -1:
                page = backup.PageNo
            return page

    def Search_and_Change(self, key, type, new_data):
        # type = 0 means that we want to delete some record
        # type = 1 means that we want to update some record
        if type not in [0, 1]:
            print("invalid operation", type)
            return

        page_num = self.searchIndex(key)
        if page_num == -1:
            print("Cannot find record with this key.", key)
            return

        with open(RECORD_FILE, "rb+") as rec_file:
            rec_file.seek((page_num - 1) * RECORD_SIZE * PAGE_SIZE)
            records_b = rec_file.read(self.PageSize * RECORD_SIZE)
            self.inc_reads()
            records = get_records_from_bytes(records_b)

            found = False
            for record in records:
                if record.Key == key:
                    if type == 0:
                        print("Set delete on record with key: ", key)
                        record.Delete = 1
                    elif type == 1:
                        print(
                            "Updated record with the key: ",
                            key,
                            " ",
                            record.Data,
                            "->",
                            new_data,
                        )
                        record.Data = new_data
                    found = True
                    break

            if found:
                rec_file.seek((page_num - 1) * RECORD_SIZE * PAGE_SIZE)
                rec_file.write(get_bytes_from_records(records))
                self.inc_writes()
            else:
                pointer = records[-1].OverflowPointer
                while pointer != 0:
                    rec_file.seek(
                        int(math.ceil((self.MaxPrimaryRecords * RECORD_SIZE)))
                    )
                    record_b = rec_file.read(self.PageSize * RECORD_SIZE)
                    self.inc_reads()
                    records = get_records_from_bytes(record_b)
                    for record in records:
                        if type == 0:
                            print("Set delete on record with key: ", key)
                            record.Delete = 1
                        elif type == 1:
                            print(
                                "Updated record with the key: ",
                                key,
                                " ",
                                record.Data,
                                "->",
                                new_data,
                            )
                            record.Data = new_data
                            found = True
                            rec_file.seek(
                                int(math.ceil((self.MaxPrimaryRecords * RECORD_SIZE)))
                            )
                            rec_file.write(get_bytes_from_records(records))
                            self.inc_writes()
                            break
                    pointer = record.OverflowPointer
                    if found:
                        break
                if not found:
                    print("Cannot find record with this key.", key)

    def DelRecord(self, key):
        self.Search_and_Change(key, 0, 0)

    def Reorganization(self):
        rec_file = open(RECORD_FILE, "rb")
        new_file = open(TMP_FILE, "wb")

        new_files = [Record()] * PAGE_SIZE

        # reading overflow area
        rec_file.seek(self.MaxPrimaryRecords * RECORD_SIZE)
        overflow_b = rec_file.read(self.MaxOverflowRecords * RECORD_SIZE)
        self.inc_reads()
        overflow = get_records_from_bytes(overflow_b)
        # setting on the begin
        rec_file.seek(0)
        print("--- REORGANISING FILE ----")
        counter = 0
        pointer = 0
        new_pages = 0
        overflow_record = 0
        max_pages = int(math.ceil(self.MaxPrimaryRecords / self.PageSize))
        for i in range(max_pages):
            primary_b = rec_file.read(self.PageSize * RECORD_SIZE)
            self.inc_reads()
            primary = get_records_from_bytes(primary_b)
            for record in primary:
                if record.Key != 0:
                    if record.Delete == 0:
                        if counter == int(PAGE_SIZE * self.Alpha):
                            # if buffor is full at Alpha level
                            for nf in range(counter):
                                new_files[nf].OverflowPointer = 0
                            save_buf = get_bytes_from_records(new_files)
                            new_file.write(save_buf)
                            self.inc_writes()
                            new_files = [Record()] * PAGE_SIZE
                            counter = 0
                            new_pages += 1
                        new_files[counter] = record
                        counter += 1
                        pointer = record.OverflowPointer
                        while (
                            pointer != 0 and overflow_record < self.MaxOverflowRecords
                        ):
                            if counter == int(PAGE_SIZE * self.Alpha):
                                # if buffor is full at Alpha level
                                for nf in range(counter):
                                    new_files[nf].OverflowPointer = 0
                                save_buf = get_bytes_from_records(new_files)
                                new_file.write(save_buf)
                                self.inc_writes()
                                new_files = [Record()] * PAGE_SIZE
                                counter = 0
                                new_pages += 1
                            if overflow[overflow_record].Delete == 0:
                                new_files[counter] = overflow[overflow_record]
                                counter += 1
                            pointer = overflow[overflow_record].OverflowPointer
                            overflow_record += 1
        if counter > 0:
            for nf in range(counter):
                new_files[nf].OverflowPointer = 0
            save_buf = get_bytes_from_records(new_files)
            new_file.write(save_buf)
            self.inc_writes()
            new_files = [Record()] * PAGE_SIZE
            counter = 0
            new_pages += 1
        new_file.close()
        rec_file.close()

        os.remove(RECORD_FILE)
        os.rename(TMP_FILE, RECORD_FILE)

        self.MaxPrimaryRecords = new_pages * self.PageSize
        self.MaxOverflowRecords = PAGE_SIZE
        self.PrimaryRecords += self.OverflowRecords
        self.OverflowRecords = 0

        self.createIndex()

    def AddRecord(self, key_, data_):

        global tmp_rec
        if key_ <= 0:
            print("Cannot add key with value: ",key_)


        if self.MaxOverflowRecords == self.OverflowRecords:
            self.Reorganization()

        key = key_
        page = self.searchIndex(key)

        rec_file = open(RECORD_FILE, "r+b")

        for _ in range(page - 1):
            buff = rec_file.read(RECORD_SIZE * PAGE_SIZE)
            self.inc_reads()

        save_ptr = rec_file.tell()
        buff = rec_file.read(RECORD_SIZE * PAGE_SIZE)
        self.inc_reads()

        tmp_records = get_records_from_bytes(buff)
        # check if free space in the page
        uploadIndex = False

        if tmp_records[PAGE_SIZE - 1].Key == 0:

            for rc in tmp_records:
                if rc.Key == key:
                    if rc.Delete == 1:
                        rec_file.close()
                        self.Reorganization()
                        self.AddRecord(key_,data_)
                    else:
                        print("Cannot add key already exists")
                    break

                elif rc.Key == 0:
                    if rc == tmp_records[0]:
                        # first record
                        uploadIndex = True
                    # can add here
                    rc.Key = key_
                    rc.Data = data_
                    self.PrimaryRecords += 1
                    sort_records(tmp_records)

                    buff = get_bytes_from_records(tmp_records)
                    rec_file.seek(save_ptr)
                    rec_file.write(buff)

                    self.inc_writes()
                    break
            if uploadIndex:
                self.createIndex()

        # add to overflow
        else:
            # find record to change pointer
            tmp_rec = tmp_records[0]
            for record in tmp_records:
                if record.Key == key:
                    print("Cannot add, key already exists", record.Key)
                    rec_file.close()
                    return
                elif record.Key > key:
                    break
                else:
                    tmp_rec = record
            # setting pointer
            pointer = tmp_rec.OverflowPointer
            if tmp_rec.OverflowPointer == 0 or tmp_rec.OverflowPointer > key:
                tmp_rec.OverflowPointer = key

            # saving page
            for record in tmp_records:
                if record.Key == tmp_rec.Key:
                    record = tmp_rec
                    break
            buff = get_bytes_from_records(tmp_records)
            rec_file.seek(save_ptr)
            rec_file.write(buff)

            self.inc_writes()

            rec_file.seek(int(math.ceil((self.MaxPrimaryRecords * RECORD_SIZE))))
            save_ptr = rec_file.tell()
            buff = rec_file.read(self.MaxOverflowRecords * RECORD_SIZE)
            self.inc_reads()
            tmp_records = get_records_from_bytes(buff)

            # add in overflow
            for j in range(self.MaxOverflowRecords):
                if tmp_records[j].Key == 0:
                    tmp_records[j].Key = key_
                    tmp_records[j].Data = data_
                    break
                elif tmp_records[j].Key == pointer:
                    if tmp_records[j].Key > key_:
                        pointer = tmp_records[j].Key
                    elif tmp_records[j].Key < key_:
                        if tmp_records[j].OverflowPointer == 0:
                            tmp_records[j].OverflowPointer = key_
                        elif tmp_records[j].OverflowPointer > key_:
                            pointer = tmp_records[j].Key
                            tmp_records[j].OverflowPointer = key_
                        else:
                            pointer = tmp_records[j].OverflowPointer
            self.OverflowRecords += 1
            buff = get_bytes_from_records(tmp_records)
            rec_file.seek(save_ptr)
            rec_file.write(buff)
            self.inc_reads()
            self.inc_writes()

            rec_file.close()

    def UpdateRecord(self, old_key_, new_key, data_):
        if old_key_ == new_key:
            # without changing the key costs the same as the delete record operation
            self.Search_and_Change(old_key_, 1, data_)

        else:
            # When the key changes, the update of the record consists of deleting the record and inserting a new record
            self.DelRecord(old_key_)
            self.AddRecord(new_key, data_)

    def startingValues(self):

        tmp_rec = Record()

        page_bufor = [tmp_rec for _ in range(self.PageSize)]

        page_bufor_bytes = get_bytes_from_records(page_bufor)

        tmp_file = open(RECORD_FILE, "wb")

        page_nr = int(
            math.ceil(
                (self.MaxPrimaryRecords + self.MaxOverflowRecords) / self.PageSize
            )
        )
        for i in range(page_nr):
            tmp_file.write(page_bufor_bytes)
            self.inc_writes()

        tmp_file.close()

        self.createIndex()

    def print_records(self):
        rec_file = open(RECORD_FILE, "rb")
        page_nr = int(
            math.ceil(
                (self.MaxPrimaryRecords + self.MaxOverflowRecords) / self.PageSize
            )
        )

        for i in range(page_nr):
            if i < (page_nr - 1):
                print(
                    "---PAGE NUMBER {:4s}---------------------------------------------------".format(
                        str(i + 1)
                    )
                )
            elif i == page_nr - 1:
                print("---OVERFLOW AREA----------------------------------")

            bytes_ = rec_file.read(RECORD_SIZE * PAGE_SIZE)
            self.inc_reads()
            for j in range(PAGE_SIZE):
                tmp = bytes_[j * RECORD_SIZE : (j + 1) * RECORD_SIZE]
                tmp_rec = create_record_from_bytes(tmp)
                tmp_rec.print()
            if i == page_nr - 1:
                print(
                    "----------------------------------------------------------------------"
                )

    def print_file(self):
        rec_file = open(RECORD_FILE, "rb")
        rec_file.seek(self.MaxPrimaryRecords * RECORD_SIZE)
        overflow_b = rec_file.read(self.MaxOverflowRecords * RECORD_SIZE)
        self.inc_reads()
        overflow = get_records_from_bytes(overflow_b)
        overflow_record = 0

        rec_file.seek(0)
        print("--- PRINTING FILE IN ORDER-------------------------------------------")
        max_pages = int(math.ceil(self.MaxPrimaryRecords / self.PageSize))
        for i in range(max_pages):
            primary_b = rec_file.read(self.PageSize * RECORD_SIZE)
            self.inc_reads()
            primary = get_records_from_bytes(primary_b)
            for record in primary:
                if record.Key != 0:
                    record.print()
                    pointer = record.OverflowPointer
                    if pointer != 0:
                        while (overflow_record < self.MaxOverflowRecords) and (
                            overflow[overflow_record].Key != 0
                        ):
                            if overflow[overflow_record].Key == pointer:
                                overflow[overflow_record].print()
                                pointer = overflow[overflow_record].OverflowPointer
                                if pointer == 0:
                                    break
                            overflow_record += 1
        rec_file.close()
        print(
            "----------------------------------------------------------------------"
        )

    def print_indexes(self):
        ind_file = open(INDEX_FILE, "rb")
        print("---INDEX---------------------------")
        max_indx_per_read = int(RECORD_SIZE * PAGE_SIZE / INDEX_SIZE)
        page_nr = int(math.ceil(self.MaxPrimaryRecords / self.PageSize))
        for i in range(page_nr):
            bytes_ = ind_file.read(max_indx_per_read * INDEX_SIZE)
            self.inc_reads()
            for j in range(max_indx_per_read):
                tmp = bytes_[j * INDEX_SIZE : (j + 1) * INDEX_SIZE]
                if tmp == b"":
                    break
                tmp_ind = create_index_from_bytes(tmp)
                tmp_ind.print()
        print("-----------------------------------")

    def inc_reads(self):
        self.Reads += 1

    def inc_writes(self):
        self.Writes += 1

    def reset_rw(self):
        self.Reads = 0
        self.Writes = 0

    def print_rw(self):
        print(
            "Previous operation used -> Reads: {:5s} Writes: {:5s}|".format(
                str(self.Reads), str(self.Writes)
            )
        )

    def random_values(self):
        for t in range(10):
            self.AddRecord((t+2)*2+2, random.randint(3, 9))


def main_program(isf):

    while True:
        # prompt the user for input
        command = int(
            input(
                "Enter a command: \n 1) add record \n 2) delete record \n 3) update record \n 4) print whole file \n 5) "
                "print records \n 6) print indexes \n 7) reorganize \n 8) exit \n 9) input random starting values \n"
            )
        )

        isf.reset_rw()
        # parse and execute the command
        if command == 1:
            arg1 = int(input("Enter the key: "))
            arg2 = int(input("Enter the data: "))
            isf.AddRecord(arg1, arg2)

        elif command == 2:
            arg1 = int(input("Enter the key: "))
            isf.DelRecord(arg1)

        elif command == 3:
            arg1 = int(input("Enter the old key: "))
            arg2 = int(input("Enter the new key: "))
            arg3 = int(input("Enter the data: "))
            isf.UpdateRecord(arg1, arg2, arg3)
        elif command == 4:
            isf.print_file()
        elif command == 5:
            isf.print_records()
        elif command == 6:
            isf.print_indexes()
        elif command == 7:
            isf.Reorganization()

        elif command == 8:
            sys.exit()
        elif command == 9:
            isf.random_values()
        else:
            print("Invalid command")
        isf.print_rw()



isf = Indexed_sequential_files()
isf.startingValues()
main_program(isf)


