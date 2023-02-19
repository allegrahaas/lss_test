import os, re
from os import listdir
from os.path import isfile, join


class PossibleLSSFileNames:
    def __init__(self, original_file_name, lss_names, numbers):
        self.original_file_name = original_file_name
        self.lss_names = lss_names
        self.numbers = numbers

    # for testing
    def print(self):
        print(self.original_file_name)
        for index, name in enumerate(self.lss_names):
            print(name + " " + self.numbers[index])

        print()

    def check_single_match(self, target):
        for index, name in enumerate(self.lss_names):
            if name == target:
                return self.numbers[index]

        return None

    def check_list(self, lss_file):
        for index1, pattern in enumerate(self.lss_names):
            if pattern in lss_file.lss_names:
                index2 = lss_file.lss_names.index(pattern)

                return LSSGroup(pattern=pattern, number1=self.numbers[index1], number2=lss_file.numbers[index2])

        return None

class LSSGroup:
    def __init__(self, pattern, number1=None, number2=None):
        self.pattern = pattern
        self.count = 1
        self.numbers = []

        if number1 is not None:
            self.numbers.append(int(number1))

        if number2 is not None:
            self.count += 1
            self.numbers.append(int(number2))

    def add(self, number):
        self.count += 1
        self.numbers.append(int(number))

    def print(self):
        if len(self.numbers) == 0:
            print(f"1 {self.pattern}")
        else:
            print(f"{self.count} {self.pattern} {self.make_ranges()}")

    def make_ranges(self):
        ranges = []
        range_str = ""
        self.numbers.sort()

        range_start = None
        range_end = None

        for number in self.numbers:
            # first iteration
            if range_start is None:
                range_start = number
                range_end = number

            # range continues
            elif int(number) == int(range_end) + 1:
                range_end += 1

            else:
                if range_start == range_end:
                    range_str += f"{range_start} "
                else:
                    range_str += f"{range_start}-{range_end} "

                range_start = number
                range_end = number

        #append last range
        if range_start == range_end:
            range_str += f"{range_start} "
        else:
            range_str += f"{range_start}-{range_end} "

        return range_str


def generate_variations(file_name) -> PossibleLSSFileNames:
    # find number sections and replace with %ds
    matches = re.finditer(r"\d+", file_name)

    lss_names = []
    numbers = []

    for match in matches:
        # reconstruct match with %d formatting

        length = match.end() - match.start()

        numbers.append(match.group().lstrip("0"))

        if length == 1:
            pattern = file_name[:match.start()] + "%d" + file_name[match.end():]
            lss_names.append(pattern)
        else:
            #zero pad
            pattern = file_name[:match.start()] + "%0" + str(length) + "d" + file_name[match.end():]
            lss_names.append(pattern)

    return PossibleLSSFileNames(original_file_name=file_name, lss_names=lss_names, numbers=numbers)


def lss(file_path=os.path.abspath(os.getcwd())):
    # get all file names
    # if isfile(join(file_path, file))
    files = [file for file in listdir(file_path)]

    unmatched_files = []
    lss_groups = []

    # iterate through files in directory
    for file_name in files:
        # generate possible formatted file names
        lss_file = generate_variations(file_name)

        # no possible potterns, skip search
        if len(lss_file.lss_names) == 0:
            lss_groups.append(LSSGroup(lss_file.original_file_name))

        else:
            # one or more possible patterns
            matched = False

            # check existing lss_groups and add if match
            for group in lss_groups:
                value = lss_file.check_single_match(group.pattern)

                if value is not None:
                    group.add(value)
                    matched = True
                    break

            if not matched:
                # check unmatched list
                for unmatched in unmatched_files:
                    new_lss_group = unmatched.check_list(lss_file)

                    if new_lss_group is not None:
                        lss_groups.append(new_lss_group)
                        unmatched_files.remove(unmatched)
                        matched = True
                        break

            # if still not matched, set aside to check for future matches
            if not matched:
                unmatched_files.append(lss_file)

    # add files that never matched
    for lss_file in unmatched_files:
        lss_groups.append(LSSGroup(pattern=lss_file.original_file_name))

    # print final list
    for group in lss_groups:
        group.print()