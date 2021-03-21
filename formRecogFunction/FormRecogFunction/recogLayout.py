
from azure.ai.formrecognizer import FormRecognizerClient
from azure.ai.formrecognizer import FormTrainingClient
from azure.core.credentials import AzureKeyCredential

from pandas import DataFrame 

from FormRecogFunction.endpoint import ENDPOINT,KEY

form_recognizer_client = FormRecognizerClient(ENDPOINT, AzureKeyCredential(KEY))
form_training_client = FormTrainingClient(ENDPOINT, AzureKeyCredential(KEY))

# form = 'Form_1.jpg'
pages_tables_info = '-1'
specificInformation = 'allInfo'

def process(form_path):
    # try:
    #     with open(form_path, "rb") as f:
    #         poller = form_recognizer_client.begin_recognize_content(form=f)
    #         page = poller.result()
    # except:
    #     return "File Not Found"
    with open(form_path, "rb") as f:
        print("here")
        poller = form_recognizer_client.begin_recognize_content(form=f)
        page = poller.result()
        print(page)

    if isinstance(CheckPagesTables(page), str): # to see whether the output is an error string
        return CheckPagesTables(page)
    tables = CheckPagesTables(page) # list of Tables
    extractedInfo = []
    for i in range(len(tables)):
        # extractedInfo.append(["Table found on page {}:\n".format(tables[i].page_number)])
        print("Table found on page {}:".format(tables[i].page_number))
        table_contents = []
        table_contents = GetAllValues(table_contents, tables[i])
        extractedInfo.append(DataFrame.to_json(ChooseSpecificInfo(table_contents, i+1)))
        print(ChooseSpecificInfo(table_contents, i+1))
    return extractedInfo

def CheckPagesTables(page):
    quantity_of_pages_tables = pages_tables_info.split(",")

    try:
        multipleTables = []
        if len(quantity_of_pages_tables)==1:
            for each_page in range(len(page)):
                for each_table in range(len(page[each_page-1].tables)):
                    table = page[each_page-1].tables[each_table-1]
                    multipleTables.append(table)
            if len(multipleTables)==0:
                return "No Table Found"
            return multipleTables
        return "Wrong number of Arguments"
    except:
        return "Wrong values are placed"

def GetAllValues(table_contents, table):
    row_values = []
    column = 0
    currentRow = 0

    for cell in table.cells:
        rowsCount = cell.row_index
        if(rowsCount > currentRow): #row has been changed
            currentRow = rowsCount
            column = 0
            table_contents.append(row_values)
            row_values = []

        row_values.append(cell.text)
        column += 1
    table_contents.append(row_values)

    return table_contents

def ChooseSpecificInfo(table_contents):
    specificValues = specificInformation.split(',')

    if(specificValues[0]=="allInfo"):
        dataBase = DataFrame(table_contents)
        # png = dataBase.dfi.export('tables {}.png'.format(tableCount))
        return dataBase
    return "Wrong Requirement"
