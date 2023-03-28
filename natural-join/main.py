# Liczby naturalne.
# Uporządkowanie wg rosnącej sumy podzielników.
import math
import random
from math import sqrt

import copy


def find_sum_of_factors(number):
    if number == 1 or number == 0:
        return 1
    sum_factors = 0
    for div in range(1, int(sqrt(number)) + 1):
        if number % div == 0:
            sum_factors += div
            if number / div != div:
                sum_factors += (number / div)
    return int(sum_factors)


def generate_numbers(file, amount):
    # tab = [1, 13, 18, 15, 18, 0, 6, 14, 15, 8, 20, 5, 1, 16, 15, 10, 2, 7, 11, 1, 13, 4, 19, 11, 12]
    # for nr in tab:
    #     bytes = nr.to_bytes(4, 'big')
    #     file.write(bytes)
    #random.seed(10)
    list = []
    for _ in range(amount):
        number = random.randint(0, 1000)
        # print(number,',',end='')
        list.append(number.to_bytes(4, 'big'))
    bytes = b''.join(list)
        # bytes = number.to_bytes(4, 'big')

    file.write(bytes)



def write_to_file(destination_file, numbers):
    list = []
    for nr in numbers:
        list.append(nr.to_bytes(4, 'big'))
        # print(number,',',end='')
    bytes = b''.join(list)
    destination_file.write(bytes)


    # print("koniec pliku")

    # # converting int to bytes with length
    # # of the array as 2 and byter order as big
    # array1 = ''.join([str((random.randint(0, 20)).to_bytes(4,'big')) for _ in range(amount)])
    # print(array1)
    # array1 = array1.replace('b\'', '')
    # array1 = array1.replace('\'', '')
    # print(array1)


# #file.write(''.join(hex([str((random.randint(0, 20))).to_bytes(2, 'big')) for _ in range(amount)]))
#     file.write(''.join(str('\''+[hex((random.randint(0, 20))) for _ in range(amount)]))

def split_file(source, destination_1, destination_2, first, lsn2, lsn3,i,bs):
    # splits source block into two another

    # print(source)
    # last_value = 4294967296 #4 bytes int max value
    buffor1 = []
    buffor2 = []

    for number in source:
        # if number>last_value:
        #     #change destination

        if ((first and find_sum_of_factors(lsn2) > find_sum_of_factors(number)) or (
                (not first) and (find_sum_of_factors(lsn3) > find_sum_of_factors(number)))):
            first = not first

        bytes = number.to_bytes(4, 'big')
        if first:
            if len(buffor1)<bs:
                buffor1.append(destination_1.write(bytes))
            else:
                bytes = b''.join(buffor1)
                destination_1.write(bytes)
                write_numbers[i] += 1
                buffor1 = []

            lsn2 = number
        else:
            if len(buffor2) < bs:
                buffor2.append(destination_2.write(bytes))
            else:
                bytes = b''.join(buffor2)
                destination_2.write(bytes)
                write_numbers[i] += 1
                buffor2 = []
            lsn3 = number


    return first, lsn2, lsn3


def print_file(source):
    output = []
    output_inner = []
    while True:
        byte = source.read(4)
        if byte != b'':
            int_val = int.from_bytes(byte, 'big')
            output.append(int_val)
            output_inner.append(find_sum_of_factors(int_val))
        else:
            break
    print("liczby:", output)
    print("suma  :", output_inner)


def read_series(input, ptr, bs,i):
    output = []
    for _ in range(bs):
        ptr = input.tell()
        byte = input.read(4)
        if byte != b'':
            int_val = int.from_bytes(byte, 'big')
            if (len(output)):
                if (output[-1] <= int_val):
                    output.append(int_val)
                else:
                    # input.seek(ptr)
                    break
            else:
                output.append(int_val)
            # print(byte, int_val)
        else:
            break
    read_numbers[i]+=1
    return output, ptr


def connect_series_into_one(block, source1, source2, block_s):
    copy_source1 = copy.deepcopy(source1)
    copy_source2 = copy.deepcopy(source2)
    # print("connected:")
    # print(copy_source1)
    # print(copy_source2)print("connected:")
    # print(copy_source1)
    # print(copy_source2)

    if (len(copy_source1) > 0):
        source1_number = copy_source1.pop(0)
    else:
        source1_number = -1
    if (len(copy_source2) > 0):
        source2_number = copy_source2.pop(0)
    else:
        source2_number = -1

    while True:
        for _ in range(block_s):

            if (source1_number != -1):
                if (source2_number != -1):
                    if (find_sum_of_factors(source2_number) < find_sum_of_factors(source1_number)):
                        block.append(source2_number)
                        if (len(copy_source2) > 0 and source2_number != -1):
                            source2_number = copy_source2.pop(0)
                        else:
                            source2_number = -1
                    else:
                        block.append(source1_number)
                        if (len(copy_source1) > 0 and source1_number != -1):
                            source1_number = copy_source1.pop(0)
                        else:
                            source1_number = -1
                    # there two numbers to select
                else:
                    # add element from source 1
                    block.append(source1_number)
                    if (len(copy_source1) > 0 and source1_number != -1):
                        source1_number = copy_source1.pop(0)
                    else:
                        source1_number = -1
            elif (source2_number == -1):
                break
            else:
                # add element from source 2
                block.append(source2_number)
                if (len(copy_source2) > 0 and source2_number != -1):
                    source2_number = copy_source2.pop(0)
                else:
                    source2_number = -1

        if (len(copy_source2) == 0) and (len(copy_source1) == 0):
            break
    # print("to this: ", block)
    return block

    # output_file.write(bytes)


# print(find_sum_of_factors(1848))


size_numbers = [100,1000,2000,3000,10000]
size_buffor = [10,10,10,10,10]
write_numbers = [0,0,0,0,0]
read_numbers = [0,0,0,0,0]
iters = [0,0,0,0,0]


for i in range(len(size_numbers)):

    t1_n = 'file1.bin'
    t1 = open(t1_n, 'wb')
    generate_numbers(t1, size_numbers[i])
    #
    t1 = open(t1_n, 'rb')
    print("surowy stan poczatkowy-------------")
    print_file(t1)
    t1.close()

    # t1 = open(t1_n, 'r')
    # number = 0


    block_size = size_buffor[i]  # 10 number every 4 bytes =  40 bytes == 10 int

    # byte = b'\x00\x05'
    # pointer = 0
    # with open('file1.bin', 'wb') as f:
    #     f.write(byte)

    iterrations = 1

    while True:

        open('file2.bin', 'w').close()  # cleaning all file
        open('file3.bin', 'w').close()  # cleaning all file

        t2 = open('file2.bin', 'wb')
        t3 = open('file3.bin', 'wb')

        first_to_write = True
        last_saved_number2 = 0
        last_saved_number3 = 0
        # print("iteracja nr ", i, "rozpoczynam rozdzielanie t1 ->t2+t3")
        with open('file1.bin', 'rb') as f:
            while True:
                block = []  # max bufor size == 40 bytes / 10 int
                byte = f.read(block_size * 4)
                read_numbers[i]+=1
                j=0
                new_value = 0
                for x in byte:
                    if j==4:
                        block.append(new_value)
                        j=0
                        new_value = 0
                    else:
                        new_value *= 10
                        new_value += int(byte[j])
                        j += 1


                # odczytano cały możliwe blok
                # przypisanie wartosci do t2 i t3
                first_to_write, last_saved_number2, last_saved_number3 = split_file(block, t2, t3, first_to_write,
                                                                                    last_saved_number2, last_saved_number3,i,block_size)

                write_numbers[i] += 1
                # print(block)
                if byte == b'':
                    break

        t2.close()
        t3.close()


        t1 = open('file1.bin', 'w').close()  # cleaning t1 file
        # clearing t1

        # print_file(open('file1.bin', 'rb'))
        # scalanie

        #
        t1 = open('file1.bin', 'ab')

        t2 = open('file2.bin', 'rb')
        t3 = open('file3.bin', 'rb')

        block = []  # max bufor size == 40 bytes / 10 int
        series_from_t2 = []
        series_from_t3 = []
        # print("iteracja nr ", i, "rozpoczynam sklejanie t2+t3 -> t1")
        #              for f2 f3
        end_of_file = [False, False]
        # val_from_t2 = 0
        # val_from_t3 = 0
        end_of_series = [False, False]
        seria2 = []
        seria3 = []
        byte_from_t2 = t2.read(4)
        val_from_t2 = int.from_bytes(byte_from_t2, 'big')
        byte_from_t3 = t3.read(4)
        val_from_t3 = int.from_bytes(byte_from_t3, 'big')
        read_numbers[i] += 1
        while True:


            #print(val_from_t2, val_from_t3,i)
            if end_of_series[0] == False and end_of_file[0]==False:
                if end_of_series[1] == False and end_of_file[1]==False:
                    #neither one is done
                    if (find_sum_of_factors(val_from_t2) <= find_sum_of_factors(val_from_t3)):
                        #t2 is to be append
                        block.append(val_from_t2)
                        byte_from_t2 = t2.read(4)

                        if byte_from_t2 != b'':
                            if find_sum_of_factors(int.from_bytes(byte_from_t2, 'big')) < find_sum_of_factors(val_from_t2):
                                end_of_series[0] = True
                            val_from_t2 = int.from_bytes(byte_from_t2, 'big')
                            seria2.append(val_from_t2)
                        else:
                            end_of_file[0] = True
                            end_of_series[0] = True
                    elif (not end_of_file[1] and not end_of_series[1]):
                        #t3 is to be append

                        block.append(val_from_t3)
                        byte_from_t3 = t3.read(4)
                        if byte_from_t3 != b'':
                            if find_sum_of_factors(int.from_bytes(byte_from_t3, 'big')) <  find_sum_of_factors(val_from_t3):
                                end_of_series[1] = True
                            val_from_t3 = int.from_bytes(byte_from_t3, 'big')
                            seria3.append(val_from_t3)
                        else:
                            end_of_file[1] = True
                            end_of_series[1] = True

                elif (not end_of_file[0] and not end_of_series[0]):
                    #series t3 is done so we complete t2
                    while len(block) < block_size:
                        block.append(val_from_t2)
                        byte_from_t2 = t2.read(4)
                        if byte_from_t2 != b'':
                            if find_sum_of_factors(int.from_bytes(byte_from_t2, 'big')) < find_sum_of_factors(val_from_t2):
                                end_of_series[0] = True
                            val_from_t2 = int.from_bytes(byte_from_t2, 'big')
                            seria2.append(val_from_t2)
                            if end_of_series[0]:
                                break
                        else:
                            end_of_file[0] = True
                            end_of_series[0] = True
                            break
            elif end_of_series[1] == False and end_of_file[1]==False:
                #series t2 is done so we complete t3
                while len(block)<block_size:
                    block.append(val_from_t3)
                    byte_from_t3 = t3.read(4)
                    if byte_from_t3 != b'':
                        if find_sum_of_factors(int.from_bytes(byte_from_t3, 'big')) < find_sum_of_factors(val_from_t3):
                            end_of_series[1] = True
                        val_from_t3 = int.from_bytes(byte_from_t3, 'big')
                        seria3.append(val_from_t3)
                        if end_of_series[1]:
                            break
                    else:
                        end_of_file[1] = True
                        end_of_series[1] = True
                        break
            else:
                #both series are done
                if not end_of_file[1]:
                    end_of_series[1] = False
                if not end_of_file[0]:
                    end_of_series[0] = False


            if len(block)==block_size:
                #print("write block to t1",block)
                write_to_file(t1, block)
                write_numbers[i] += 2
                read_numbers[i] += 2
                block = []



            if end_of_file[0] == True and end_of_file[1] == True:
                #print("write block to t1", block)
                write_to_file(t1, block)
                write_numbers[i] += 2
                read_numbers[i] += 2
                break

        t1.close()
        t2.close()
        t3.close()


        #check if there is one series on each tape
        t1 = open('file1.bin', 'rb')

        val_from_t1 = 0
        ascendingt1 = True
        while True:
            byte_from_t1 = t1.read(4)
            if byte_from_t1 != b'':
                if find_sum_of_factors(int.from_bytes(byte_from_t1, 'big')) < find_sum_of_factors(val_from_t1):
                    ascendingt1 = False
                    break
            else:
                break
            val_from_t1 = int.from_bytes(byte_from_t1, 'big')

        iterrations+=1
        iters[i] = iterrations
        t1.close()
        if ascendingt1:
            break

    #print(seria2)
    #print(seria3)
    print(" stan koncowy-------------",iterrations)
    iterrations=0
    t1 = open('file1.bin', 'rb')
    t2 = open('file2.bin', 'rb')
    t3 = open('file3.bin', 'rb')
    print_file(t1)
    print_file(t2)
    print_file(t3)

    t1.close()
    t2.close()
    t3.close()


for i in range(len(size_numbers)):
    print(size_numbers[i],size_buffor[i],write_numbers[i]+read_numbers[i],iters[i])
    print("number of phases |log2r|: " ,math.ceil(math.log2(size_numbers[i])),end = '')
    print(" number of disk writes/reads 4N|log2r|/b: ", 4*size_numbers[i]*math.ceil(math.log2(size_numbers[i]))/size_buffor[i],end = '')
    print('')
