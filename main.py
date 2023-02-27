import os
import re
from os import listdir

# Object to hold possible formatted file names. Index of pattern in lss_names corresponds to matching number in numbers
class PossibleLSSFileNames:
    def __init__(self, original_file_name: str, lss_names: list, numbers: list):
        self.original_file_name = original_file_name
        self.lss_names = lss_names
        self.numbers = numbers

    # for testing
    def print(self):
        print(self.original_file_name)
        for index, name in enumerate(self.lss_names):
            print(f"{name} {self.numbers[index]}")

        print()

    # Iterates through possible formatted names looking for a match to target
    # Returns number that corresponds with pattern entry
    def check_single_match(self, target: str):
        for index, name in enumerate(self.lss_names):
            if name == target:
                return self.numbers[index]

        return None

    # Iterates through this object's formatted file names looking for a match in other object's possible names
    # Returns a new LSSGroup containing 2 entries
    def check_list(self, lss_file):
        for index1, pattern in enumerate(self.lss_names):
            if pattern in lss_file.lss_names:
                index2 = lss_file.lss_names.index(pattern)

                return LSSGroup(pattern=pattern, number1=self.numbers[index1], number2=lss_file.numbers[index2])

        return None


# Collection of entries matching the same formatted file name pattern
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

    def add(self, number) -> None:
        self.count += 1
        self.numbers.append(int(number))

    # Formats and outputs entry for final lss list
    def print(self) -> None:
        if len(self.numbers) == 0:
            print(f"1 {self.pattern}")
        else:
            print(f"{self.count} {self.pattern} {self.make_ranges()}")

    # Generates file number ranges from collection of numbers
    # Returns formatted string
    def make_ranges(self) -> str:
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
            elif number == range_end + 1:
                range_end += 1

            else:
                # break in range, wrap current range and start a new one
                if range_start == range_end:
                    range_str += f"{range_start} "
                else:
                    range_str += f"{range_start}-{range_end} "

                range_start = number
                range_end = number

        # append last range
        if range_start == range_end:
            range_str += f"{range_start} "
        else:
            range_str += f"{range_start}-{range_end} "

        return range_str


# Generate all possible C-style formatted file names with matching numbers
# e.g. file4.0001.txt could be file%d.0001.txt: 4 or file4.%04d.txt: 1
# Returns PossibleLSSFileNames object. No possible formatted file names results in empty lists for lss_names and numbers
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
            # zero pad
            pattern = f"{file_name[:match.start()]}%0{length}d{file_name[match.end():]}"
            lss_names.append(pattern)

    return PossibleLSSFileNames(original_file_name=file_name, lss_names=lss_names, numbers=numbers)


# Iterates through files and folders at file_path looking for file names that can be grouped together.
# Prints out list of format [# of files matching pattern] [pattern] [range of numbers for pattern]
def lss(file_path=os.path.abspath(os.getcwd())) -> None:
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
