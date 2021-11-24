import re
from xlsxwriter import Workbook


def add_desh(s):
    r = re.findall('[a-z]+[0-9]+', s)
    return s.replace(''.join(r), '-'.join(r))


def write_new_woorkbook(filename, column_title, tables):
    workbook = Workbook(filename)
    sheet = workbook.add_worksheet("sheet1")

    for col_index, col in enumerate(column_title):
        sheet.write(0, col_index, col)

    for row_index, row in enumerate(tables, 1):
        for col_index, col in enumerate(row):
            sheet.write(row_index, col_index, col)

    workbook.close()


def transform_pinyin_format(pinyin):
    return re.sub("([0-9]+)", r"_\1", pinyin)


if __name__ == "__main__":
    r = transform_pinyin_format("siok10")
    print(r)
