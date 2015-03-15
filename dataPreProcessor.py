import csv, xlwt, xlrd, os, datetime, time
from elasticsearch import Elasticsearch
from shutil import copy

#Check if there is a file. If yes copy the file and delete it
srcname = "source.csv"
dstname = "destination.csv"

errors = []
postProcessedFileName = "data.xls"
dataAlreadyProcessed = 0

try:
    copy(srcname, dstname)
except (IOError, os.error) as why:
    errors.append((srcname, dstname, str(why)))
    dataAlreadyProcessed = 1

if dataAlreadyProcessed == 0:
    currentTime = str(time.strftime("_%m_%d_%Y_%I_%M_%S_%p"))
    #currentTime = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
    files = [dstname]
    for i in files:
        f=open(i, 'rb')
        g = csv.reader ((f), delimiter=";")
        workbook=xlwt.Workbook()
        sheet = workbook.add_sheet("Sheet 1")

        k = 0;
        for rowi, row in enumerate(g):
            if k < 16:
                if k == 11:
                    for headercoli, value in enumerate(row):
                        header = value.split(",")
                        sheet.write(rowi-k, headercoli, "Timestamp")
                        sheet.write(rowi-k, headercoli+1, header[2])
                        sheet.write(rowi-k, headercoli+2, header[3])
                        sheet.write(rowi-k, headercoli+3, header[4])
                        sheet.write(rowi-k, headercoli+4, header[5])
                k = k+1
                continue
            for coli, value in enumerate(row):
                colsValues = value.split(",")
                date_object = time.strptime(colsValues[0], '%m/%d/%Y %I:%M:%S %p')
                sheet.write(rowi-k+1, coli, xlrd.xldate_from_datetime_tuple(date_object, workbook.datemode))
                sheet.write(rowi-k+1, coli+1, int(colsValues[2]))
                sheet.write(rowi-k+1, coli+2, int(colsValues[3]))
                sheet.write(rowi-k+1, coli+3, int(colsValues[4]))
                sheet.write(rowi-k+1, coli+4, int(colsValues[5]))
        postProcessedFileName = os.path.splitext(f.name)[0] + currentTime + ".xls";
        workbook.save(postProcessedFileName)
        f.close()

    # Remove the file 
    os.remove(srcname)
    os.remove(dstname)

# Map the fields of a new performance doc_type
mapping = {
    "performanceData": {
        "properties": {
            "readIOPS": {"type": "integer"},
            "writeIOPS": {"type": "integer"},
            "readBlocks": {"type": "integer"},
            "writeBlocks": {"type": "integer"}
        }
    }
}

newFileName = "../performance/" + postProcessedFileName

# open workbook
xl_workbook = xlrd.open_workbook(newFileName)

# # print sheet names
sheet_names = xl_workbook.sheet_names()
xl_sheet = xl_workbook.sheet_by_index(0)

# # Create a new "sample" index that includes performance data with the above mapping
es = Elasticsearch()

es.indices.create(index='sample', ignore=400)
es.indices.put_mapping(index="sample", doc_type="performanceData", body=mapping)

# Read all values, iterating through rows and columns
num_cols = xl_sheet.ncols   # Number of columns
row_results = []
for row_idx in range(1, xl_sheet.nrows):    # Iterate through rows
    for col_idx in range(0, num_cols):  # Iterate through columns
        if col_idx == 0:
            cell_obj = datetime.datetime(*xlrd.xldate_as_tuple(xl_sheet.cell_value(row_idx, col_idx), xl_workbook.datemode))
            timestamp = cell_obj
            #timestamp = xlrd.xldate_as_tuple(xl_sheet.cell_value(row_idx, col_idx), xl_workbook.datemode)
            #timestamp = time.mktime(time.strptime(xl_sheet.cell_value(row_idx, col_idx), "%m/%d/%Y %I:%M:%S %p"))
            #timestamp = datetime.datetime(time.strptime(xl_sheet.cell_value(row_idx, col_idx), xl_workbook.datemode))
        else:
            cell_obj = xl_sheet.cell(row_idx, col_idx)  # Get cell object by row, col
            row_results.append(cell_obj.value)
            #print ('Column: [%s] cell_obj: [%s]' % (col_idx, cell_obj))
    content = {
         "@timestamp": timestamp,
         "readIOPS": int(row_results[0]),
         "writeIOPS": int(row_results[1]),
         "readBlocks": int(row_results[2]),
         "writeBlocks": int(row_results[3]),
    }
    es.index(index="lrs", doc_type='performanceData', id=row_idx+1, body=content)
    row_results.remove(row_results[0])
    row_results.remove(row_results[0])
    row_results.remove(row_results[0])
    row_results.remove(row_results[0])