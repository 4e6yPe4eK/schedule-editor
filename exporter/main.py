import os.path

import pdfkit
import sys


class SchToHtml:
    def __init__(self, data):

        self.data = data
        self.table_of_schedule = None
        self.widths_of_schedule_cols = None
        self.get_schedule()

    def get_schedule(self):
        schedule = self.data["schedule"]

        table_of_schedule = []
        widths_of_schedule_cols = []

        for tb in schedule["tables"]:

            widths_of_tables_cols = []

            # здесь храниться номер и время урока (или первые столбцы)
            rows = []

            widths_of_columns = []

            # здесь заголовки первых колонок
            name_row = []
            if tb["num"]:
                widths_of_columns.append(1)
                name_row.append("урок")
            if tb["time"]:
                widths_of_columns.append(50)
                name_row.append("время")

            widths_of_tables_cols.append(widths_of_columns)
            rows.append(name_row)

            for i in range(tb["lessonsNum"]):
                row = []
                if tb["num"]:
                    row.append(str(tb["nums"][i]))
                if tb["time"]:
                    row.append(tb["times"][i])
                rows.append(row)

            tables_of_groups = [rows]

            for group in tb["groups"]:
                table_of_group = []
                widths_of_columns = []

                name_row = []
                if "lesson" in group["rows"][0]:
                    widths_of_columns.append(90)
                    name_row.append(group["group"])
                if "classroom" in group["rows"][0]:
                    widths_of_columns.append(10)
                    name_row.append("каб.")
                if "teacher" in group["rows"][0]:
                    widths_of_columns.append(50)
                    name_row.append("учитель")

                table_of_group.append(name_row)

                for row in group["rows"]:
                    row_of_group = []
                    if "lesson" in row:
                        row_of_group.append(row["lesson"])
                    if "classroom" in row:
                        row_of_group.append(row["classroom"])
                    if "teacher" in row:
                        row_of_group.append(row["teacher"])
                    table_of_group.append(row_of_group)
                tables_of_groups.append((group["group"], table_of_group))
                widths_of_tables_cols.append(widths_of_columns)

            table_of_schedule.append(tables_of_groups)
            widths_of_schedule_cols.append(widths_of_tables_cols)

        self.table_of_schedule = table_of_schedule
        self.widths_of_schedule_cols = widths_of_schedule_cols

    def merge_tables(self, a, b):
        c = []
        for i, j in zip(a, b):
            i = i.copy()
            i.extend(j)
            c.append(i)
        return c

    def format_table(self, table):
        new_heights = []
        new_table = []
        space_row = [None for _ in range(len(table[0]))]
        for row in table:
            num_spaces = 1
            rows = [space_row.copy()]
            for i, el in enumerate(row):
                els = el.split("/")
                if len(els) > num_spaces:
                    for _ in range(abs(num_spaces - len(els))):
                        rows.append(space_row.copy())
                    num_spaces = len(els)
                for j, el in enumerate(els):
                    rows[j][i] = el
            new_heights.extend([24 / len(rows) for i in range(len(rows))])
            new_table.extend(rows)

        return new_heights, new_table

    def get_html_table(self, table, widths_of_table, heights):
        heights = heights[::-1]
        rowspan_box = [1 for _ in range(len(table[0]))]
        html_table = "<table>"
        html_rows = []
        for j, row in enumerate(table[:0:-1]):
            html_row = "<tr>"
            for i, el in enumerate(row):
                if el != None:
                    if i < 1:
                        html_row += f'<th align="center" width="{widths_of_table[i]}px" height="{heights[j]}px" rowspan="{rowspan_box[i]}">{el}</th>'
                    else:
                        html_row += f'<td align="center" width="{widths_of_table[i]}px" height="{heights[j]}px" rowspan="{rowspan_box[i]}">{el}</td>'
                    rowspan_box[i] = 1
                else:
                    rowspan_box[i] += 1
            html_row += "</tr>"
            html_rows.append(html_row)
        html_row = "<tr>"
        for i, name in enumerate(table[0]):
            html_row += f'<th align="center" width="{widths_of_table[i]}px">{name}</th>'
        html_row += "</tr>"
        html_rows.append(html_row)
        html_table += "".join(html_rows[::-1])
        html_table += "</table>"
        return html_table

    def get_for_school(self):
        css = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.css"), "r")
        css = [i.replace("\n", "") for i in css]
        css = "".join(css)

        html = '<!DOCTYPE html><html lang="en"><head><meta ' \
               f'charset="UTF-8"><title>Title</title></head><body><style>{css}</style>'
        for i, tbs in enumerate(self.table_of_schedule[:]):
            table_of_groups = tbs[0]
            widths_of_table_cols = self.widths_of_schedule_cols[i][0]
            for j, tb in enumerate(tbs[1:]):
                group = tb[0]
                tb = tb[1]

                table_of_groups = self.merge_tables(table_of_groups, tb)
                widths_of_table_cols.extend(self.widths_of_schedule_cols[i][j + 1])

            heights, table_of_groups = self.format_table(table_of_groups)
            html += self.get_html_table(table_of_groups, widths_of_table_cols, heights)

        html += "</body>"
        return html

    def get_for_classes(self):
        tables = []
        for i, tbs in enumerate(self.table_of_schedule[:1]):
            for j, tb in enumerate(tbs[1:2]):
                group = tb[0]
                tb = tb[1]

                table_of_group = self.merge_tables(tbs[0], tb)
                heights, table_of_group = self.format_table(table_of_group)

                widths_of_table = self.widths_of_schedule_cols[i][0]
                widths_of_table.extend(self.widths_of_schedule_cols[i][j + 1])

                css = open("style.css", "r")
                css = [i.replace("\n", "") for i in css]
                css = "".join(css)
                html_table = '<!DOCTYPE html><html lang="en"><head><meta ' \
                             f'charset="UTF-8"><title>Title</title></head><body><style>{css}</style>'

                html_table += self.get_html_table(table_of_group, widths_of_table, heights[1:]) + "</body>"
                tables.append((group, html_table))
        return tables

    def save_to_pdf(self, filename='schedule.pdf'):
        pdfkit.from_string(self.get_for_school(), filename, verbose=True)
