import os
import xlsxwriter
from . import app


def create_xlsx(date, salon, data, hairdressers, appointments_count, revenue):
    path = os.path.join(app.root_path, 'static/day_records', f'day_record_{date.date.strftime("%Y%m%d")}.xlsx')
    workbook = xlsxwriter.Workbook(path)
    worksheet = workbook.add_worksheet()
    worksheet.set_column(0, 0, 10)
    worksheet.set_column(1, 3, 20)
    worksheet.set_column(4, 4, 10)
    bold = workbook.add_format({'bold': 1})
    merge_format = workbook.add_format({
        'bold': 1,
        'align': 'center',
        'valign': 'vcenter'})
    merge_format_a = workbook.add_format({
        'bold': 1,
        'valign': 'vcenter'})
    worksheet.merge_range('A2:E2', f'Рабочий журнал парикмахерской "{salon.name}" за {date.date.strftime("%d.%m.%Y")}'.upper(), merge_format)
    worksheet.merge_range('A4:D4', 'Количество состоявшихся посещений:', merge_format_a)
    worksheet.write('E4', appointments_count)
    worksheet.merge_range('A5:D5', 'Общая дневная выручка:', merge_format_a)
    worksheet.write('E5', round(revenue, 2), bold)
    row = 6
    for hairdresser in hairdressers:
        worksheet.merge_range('A' + str(row) + ':D' + str(row), hairdresser[0].name, merge_format_a)
        worksheet.write('E' + str(row), round(hairdresser[1], 2) if hairdresser[1] else '-')
        row += 1
    row += 2
    worksheet.write('A' + str(row), 'Время', bold)
    worksheet.write('B' + str(row), 'Мастер', bold)
    worksheet.write('C' + str(row), 'Клиент', bold)
    worksheet.write('D' + str(row), 'Номер телефона', bold)
    worksheet.write('E' + str(row), 'Сумма', bold)

    col = 0
    for i in data:
        worksheet.write_string(row, col, i[0].time.strftime('%H:%M'))
        worksheet.write_string(row, col + 1, i[0].hairdresser_appointment.name)
        worksheet.write_string(row, col + 2, i[0].client_appointment.name)
        worksheet.write_string(row, col + 3, i[0].client_appointment.phone_number)
        worksheet.write_number(row, col + 4, i[1])
        row += 1
    workbook.close()
    return path
