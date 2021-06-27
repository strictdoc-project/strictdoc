def get_lines_count(string):
    # TODO: Windows strings
    count = string.count("\n")
    if string[-1] != "\n":
        count += 1
    return count
