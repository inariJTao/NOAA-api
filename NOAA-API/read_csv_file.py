import math
import pandas as pd
import os
import json


class MakeDirectory:

    def make_directory(self):
        os.mkdir("output")

        os.chdir(r"output/")

        os.mkdir(r"NOAA-data-coverage")
        os.mkdir(r"NOAA-data-csv")
        os.mkdir(r"NOAA-data-JSON")
        os.mkdir(r"NOAA-data-missing-date")
        os.mkdir(r"NOAA-data-station-info")
        os.mkdir(r"NOAA-data-valid-station-report")

        os.chdir(r"../")


class ReadCsvFile:

    def __init__(self, arg_1):
        self.csv_file = arg_1

    def read_csv(self):
        path_csv = self.csv_file
        df = pd.read_csv(path_csv)

        return df


class CommandLine:

    def __init__(self, df, box_range, start, end):
        self.df = df
        self.box_range = box_range
        self.start = start
        self.end = end

    def create_command(self, station_id, latitude, longitude):
        filename = station_id + "_" + str(latitude) + "_" + str(longitude) + ".json"

        output_path_1 = "../../output/NOAA-data-station-info"
        output_path_2 = "../../output/NOAA-data-JSON/"

        command = "python search_api.py -d daily-summaries -sd " + self.start + " -ed " + self.end + " -la " + \
                  str(latitude) + " -lo " + str(longitude) + " -a TMIN TMAX PRCP -b " + str(self.box_range) + " -s " + \
                  output_path_1 + "/" + filename + " -dp " + output_path_2

        return command

    def operate_command(self):
        os.chdir(r"ncei-weather-api-evaluation/scripts")
        dataframe_list = self.df.values.tolist()

        for i in range(len(dataframe_list)):
            station_id = dataframe_list[i][0]
            latitude = dataframe_list[i][1]
            longitude = dataframe_list[i][2]

            command_script = self.create_command(station_id, latitude, longitude)
            os.system(command_script)

        os.chdir(r"../..")


class StationReport:

    def station_boolean(self, data, filename):
        list_whole = [filename]

        valid_file = 0

        for i in range(len(data["stations"])):
            count = 0
            for j in range(len(data["stations"][i]['dataTypes'])):

                if data["stations"][i]['dataTypes'][j]['id'] == 'TMIN':
                    count += 1

                if data["stations"][i]['dataTypes'][j]['id'] == 'TMAX':
                    count += 1

                if data["stations"][i]['dataTypes'][j]['id'] == 'PRCP':
                    count += 1

            station_id = data["stations"][i]['station']
            latitude = data["stations"][i]['latitude']
            longitude = data["stations"][i]['longitude']
            distance = data["stations"][i]['distance']

            if count == 3:
                valid_file += 1
                list_whole.append(station_id)
                list_whole.append(distance)
                list_whole.append(latitude)
                list_whole.append(longitude)

        list_whole.insert(1, valid_file)

        return list_whole

    def generate_report(self):
        os.chdir(r"output/NOAA-data-station-info")
        path = r"../../output/NOAA-data-station-info"

        list_whole = []

        max_length = 0

        count = 0
        for json_file in os.listdir(path):
            f = open(json_file)
            data = json.load(f)
            each_row = self.station_boolean(data, json_file)
            list_whole.append(each_row)
            count += 1

            list_length = each_row[1]

            if list_length >= max_length:
                max_length = list_length

        df = pd.DataFrame(list_whole)

        column_base = ["filename", "valid_station_num"]

        for i in range(1, max_length + 1):
            column_base.append("station_ID_" + str(i))
            column_base.append("distance(km)")
            column_base.append("latitude")
            column_base.append("longitude")

        df.columns = column_base

        os.chdir(r"../../output/NOAA-data-valid-station-report")

        df.to_csv("NOAA_valid_station_report.csv")

        os.chdir(r"../../")


class JsonToCsv:

    def temp_conversion(self, temp):
        return temp / 10 * (9 / 5) + 32

    def generate_NOAA_csv(self):
        os.chdir(r"output/NOAA-data-valid-station-report")

        df = pd.read_csv("NOAA_valid_station_report.csv")

        num_col = len(df.columns)
        number_of_ID = int((num_col - 3) / 4)

        NOAA_station_id = []

        for i in range(1, number_of_ID + 1):
            ID_string = "station_ID_" + str(i)

            station_id = df[ID_string].dropna().values.tolist()
            NOAA_station_id += station_id

        NOAA_station_id = set(NOAA_station_id)

        os.chdir(r"../../output/NOAA-data-JSON")
        path = r"../../output/NOAA-data-JSON"

        for json_file in os.listdir(path):
            file_name = json_file[:-5]
            if file_name in NOAA_station_id:
                f = open(json_file, )
                data = json.load(f)

                list_whole = []

                for i in range(len(data)):
                    list_row = [data[i]['DATE']]

                    if data[i].get('TMIN') is None:
                        list_row.append(None)
                    else:
                        list_row.append(self.temp_conversion(int(data[i]['TMIN'])))

                    if data[i].get('TMAX') is None:
                        list_row.append(None)
                    else:
                        list_row.append(self.temp_conversion(int(data[i]['TMAX'])))

                    if data[i].get('PRCP') is None:
                        list_row.append(None)
                    else:
                        list_row.append(int(data[i]['PRCP']))

                    list_whole.append(list_row)

                df = pd.DataFrame(list_whole)
                df.columns = ["date", "min", "max", "precipitation"]

                os.chdir(r"../../output/NOAA-data-csv")

                df.to_csv(file_name + ".csv")

                os.chdir(r"../../output/NOAA-data-JSON")

        os.chdir(r"../../")


class DataCoverage:

    def __init__(self, start_date, end_date):
        self.start = start_date
        self.end = end_date

    def convert_to_dictionary(self):
        os.chdir(r"output/NOAA-data-valid-station-report")
        df = pd.read_csv("NOAA_valid_station_report.csv")

        num_row = df.shape[0]
        df = df.values.tolist()

        list_key = []
        list_value = []

        for i in range(num_row):
            temp_list = df[i]
            new_list = [x for x in temp_list if pd.isnull(x) == False]

            filename = new_list[1]
            num_itr = new_list[2]  # number of iteration

            sub_list = []
            for j in range(1, num_itr + 1):
                item = new_list[(j * 4 - 1): (j * 4) + 3]
                sub_list.append(item)

            list_key.append(filename)
            list_value.append(sub_list)

        dictionary = dict(zip(list_key, list_value))

        os.chdir(r"../../")

        return dictionary

    # take in a list and convert it datafranem then
    def create_csv(self, list_whole):
        df = pd.DataFrame(list_whole, columns=["filename", "station_ID", "distance",
                                               "latitude", "longitude", "date_cov",
                                               "tmin_cov", "tmax_cov", "prcp_cov"])

        os.chdir(r"output/NOAA-data-coverage")

        df.to_csv("NOAA_data_coverage.csv")

        os.chdir(r"../../")

    def generate_date_list(self, start_date, end_date):
        df = pd.date_range(start=start_date, end=end_date)

        list_date = []

        for i in range(df.shape[0]):
            date = str(df[i])[:10]
            list_date.append(date)

        return list_date

    # function that returns the missing date of NOAA data
    def missing_date_value(self, date_original, list_date):
        date_original = set(date_original)
        list_date = set(list_date)

        missing = list(sorted(date_original - list_date))

        return len(missing), missing

    def tmin_missing_date(self, station_id):
        os.chdir(r"output/NOAA-data-csv")
        df = pd.read_csv(station_id + ".csv")
        df_date = df['date'].tolist()
        df_tmin = df['min'].tolist()

        tmin_missing_list = []

        for index, value in enumerate(df_tmin):
            if math.isnan(value):
                tmin_missing_list.append(df_date[index])

        os.chdir(r"../../")

        return tmin_missing_list

    def create_missing_data_csv(self, dictionary):
        list_whole = []
        for key in dictionary:
            for j in range(len(dictionary[key])):
                station_id = dictionary[key][j][0]
                tmin_missing = self.tmin_missing_date(station_id)

                list_sub = []
                list_sub.append(key)
                list_sub.append(station_id)
                list_sub.append(tmin_missing)
                list_whole.append(list_sub)

        os.chdir(r"output/NOAA-data-missing-date")
        df = pd.DataFrame(list_whole, columns=["filename", "station_id", "missing_date_tmin"])
        df.to_csv("NOAA_data_missing_date.csv")

        os.chdir(r"../../")

    def date_coverage(self, station_id, date_original):
        os.chdir(r"output/NOAA-data-csv")
        df = pd.read_csv(station_id + ".csv")
        df_date = df['date'].tolist()

        original_date_len = len(date_original)
        missing_date_num, missing_date_val = self.missing_date_value(date_original, df_date)

        date_coverage_pct = (original_date_len - missing_date_num) / original_date_len * 100

        os.chdir(r"../../")

        return date_coverage_pct

    def min_max_prcp_coverage(self, station_id, date_original_len):
        os.chdir(r"output/NOAA-data-csv")
        df = pd.read_csv(station_id + ".csv")

        min_nan_count = df['min'].isna().sum()
        min_count = df.shape[0] - min_nan_count

        max_nan_count = df['max'].isna().sum()
        max_count = df.shape[0] - max_nan_count

        prcp_nan_count = df['precipitation'].isna().sum()
        prcp_count = df.shape[0] - prcp_nan_count

        min_cov = min_count / date_original_len * 100
        max_cov = max_count / date_original_len * 100
        prcp_cov = prcp_count / date_original_len * 100

        os.chdir(r"../../")

        return min_cov, max_cov, prcp_cov

    def create_list_for_csv(self, dictionary):
        date_original = self.generate_date_list(self.start, self.end)

        list_whole = []
        for key in dictionary:
            for j in range(len(dictionary[key])):
                station_id = dictionary[key][j][0]

                date_cov = self.date_coverage(station_id, date_original)
                min_cov, max_cov, prcp_cov = self.min_max_prcp_coverage(station_id, len(date_original))

                list_each = dictionary[key][j]
                list_each.insert(0, key)
                list_each.append(date_cov)
                list_each.append(min_cov)
                list_each.append(max_cov)
                list_each.append(prcp_cov)

                list_whole.append(list_each)

        return list_whole


def main():
    # make folder to store output
    m = MakeDirectory()
    m.make_directory()

    ##########################################
    # input file and info
    input_file = r"input_csv/input_example.csv"
    box_range = 100
    start_date = "2020-01-01"
    end_date = "2021-07-01"
    ##########################################

    # read input csv file
    r = ReadCsvFile(input_file)
    df = r.read_csv()

    # generate command and run the command
    c = CommandLine(df, box_range, start_date, end_date)
    c.operate_command()

    # generate station report
    s = StationReport()
    s.generate_report()

    # convert JSON to csv
    j = JsonToCsv()
    j.generate_NOAA_csv()

    # data coverage and missing data report
    d = DataCoverage(start_date, end_date)
    dic = d.convert_to_dictionary()
    d.create_missing_data_csv(dic)
    list_csv = d.create_list_for_csv(dic)
    d.create_csv(list_csv)


if __name__ == "__main__":
    main()
