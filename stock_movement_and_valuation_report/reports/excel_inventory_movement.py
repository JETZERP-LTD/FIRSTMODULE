import base64

import io

import time
from odoo import api, models, _
from datetime import datetime
# from xlsxwriter import worksheet
from PIL import Image

# import xlwt

try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
    from xlsxwriter.utility import xl_rowcol_to_cell
except ImportError:
    ReportXlsx = object

class ReportInventoryMovement(models.AbstractModel):
    _name = 'report.inventory_movement_report.inventory_movement'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):

        print(data)
        # code changed by jagadishmagesh1999@gmail.com
        sheet = workbook.add_worksheet('Inventory Movement Report')
        background_color = workbook.add_format({
            'align': 'left',
            'valign': 'top',
            "bg_color": "white",
            'border': 1
        })
        bold = workbook.add_format({'align': 'center', "bold": 1})
        today_date = datetime.strftime(datetime.now(), "%d/%m/%Y")
        heading_1 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'fg_color': '00661a',
            'color': 'white',
        })

        sheet.set_column('B:B', 18)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 18)
        sheet.set_column('E:E', 8)
        sheet.set_column('F:F', 17)
        sheet.set_column('G:G', 7)
        sheet.set_column('H:H', 18)
        sheet.set_column('I:I', 18)
        sheet.set_column('N:N', 30)
        sheet.set_column('K:K', 20)
        sheet.set_column('L:L', 20)
        sheet.set_column('M:M', 30)
        image_data = io.BytesIO(base64.b64decode(self.env.user.company_id.logo))
        sheet.insert_image('A1:C1', "any_name.png", {'image_data': image_data, 'x_scale': 0.25, 'y_scale': 0.30})

        sheet.set_row(0, 30)
        heading = "Inventory Movement Report"
        sheet.merge_range('C1:G1', heading, bold)

        sheet.set_row(1, 60)
        heading_ ="From Date : " + data['date_from'] +"                                 "+ "To Date: " + data['date_to']+ "                                 "+"Report date: " + today_date + "          "+  "\n"
        heading_ += "Opening Balance : " + data['open_balance']+"                                "+ "Closing Balance : " + data['close_balance'] + "                         "+"Total Value: " + data["t_out"] +"\n\n"
        uid = self._context.get('uid')
        user = self.env['res.users'].browse(uid)
        print("current user name "+ user.name)
        heading_ += "                                                                                                                                                          "+\
                    " printed by : " + user.name
        sheet.merge_range('A2:I2', heading_, background_color)

        border = workbook.add_format({'border': 1,
                                      'align': 'center',"bg_color": "white",})
        border_1 = workbook.add_format({'border': 1,
                                      "bg_color": "white",})
        row = 4
        col = 0
        sheet.set_row(0, 30)
        heading = data["product_name"] + " - Stock Movement & Valuation"
        sheet.set_row(3, 27)
        sheet.merge_range('A3:I3', heading, heading_1)

        sheet.write('A%s' % (row), 'S.No', heading_1)
        sheet.write('B%s' % (row), 'Date & Time', heading_1)
        sheet.write('C%s' % (row), 'Voucher Number', heading_1)
        sheet.write('D%s' % (row), 'Partner Name', heading_1)
        sheet.write('E%s' % (row), 'Quantity', heading_1)
        sheet.write('H%s' % (row), 'Source Location', heading_1)
        sheet.write('I%s' % (row), 'Destination', heading_1)
        sheet.write('G%s' % (row), 'Value', heading_1)
        sheet.write('F%s' % (row), 'Action', heading_1)
        row += 1

        rev = row
        s_no = 1
        # code commented by jagadishmagesh1999@gmail.com
        for cost in data['cost_in_values']:
            sheet.write('A%s' % (rev), s_no, border)
            sheet.write('B%s' % (rev), cost['create_date'], border_1)
            sheet.write('C%s' % (rev), cost['origin'], border)
            if cost['location_id'] == "Inventory adjustment":
                sheet.write('C%s' % (rev), cost['inventory_move'], border)
            if cost['location_id'] == "Product Quantity Updated":
                sheet.write('C%s' % (rev), "Product Quantity Updated", border)
            sheet.write('G%s' % (rev), cost['value'], border)
            sheet.write('E%s' % (rev), cost['quantity'], border)
            sheet.write('H%s' % (rev), cost['location_id'], border)
            if cost['location_id'] == "Vendors":
                sheet.write('F%s' % (rev), "Purchased", border)
            if cost['location_id'] == "Production":
                sheet.write('F%s' % (rev), "Manufactured", border)
            if cost['location_id'] == "Inventory adjustment":
                sheet.write('F%s' % (rev), "Inventory addon", border)
            if cost['location_id'] == "Product Quantity Updated":
                sheet.write('F%s' % (rev), "Quantity Updated", border)
            sheet.write('I%s' % (rev), cost['location_dest_id'], border)
            sheet.write('D%s' % (rev), cost['partner_name'], border)
            rev += 1
            s_no += 1

        for var in data['out_values']:
                sheet.write('A%s' % (rev), s_no, border)
                sheet.write('B%s' % (rev), var['create_date'], border_1)
                sheet.write('C%s' % (rev), var['stock_move'], border)
                if var['location_dest_id'] == "Inventory adjustment":
                    sheet.write('C%s' % (rev), var['inventory_move'], border)
                sheet.write('E%s' % (rev), var['quantity'], border)
                sheet.write('H%s' % (rev), var['location_id'], border)
                sheet.write('I%s' % (rev), var['location_dest_id'], border)
                if var['location_dest_id'] == "Customers":
                    sheet.write('F%s' % (rev), "Sold", border)
                if var['location_dest_id'] == "Production":
                    sheet.write('F%s' % (rev), "Manufacturing", border)
                if var['location_dest_id'] == "Inventory adjustment":
                    sheet.write('F%s' % (rev), "Inventory takeaway", border)
                if var['location_dest_id'] == "Scrap":
                    sheet.write('F%s' % (rev), "Scrap", border)
                if var['location_dest_id'] == "Product Quantity Updated":
                    sheet.write('F%s' % (rev), "Inventory takeaway", border)
                if var['location_dest_id'] == "Vendors":
                    sheet.write('F%s' % (rev), "Quantity Transfer", border)
                sheet.write('G%s' % (rev), var['value'], border)
                sheet.write('D%s' % (rev), var['partner_name'], border)
                rev += 1
                s_no += 1


