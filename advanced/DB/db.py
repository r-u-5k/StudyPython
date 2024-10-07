import os

import pandas as pd
import psycopg2
from sqlalchemy import create_engine

import params as pa

conn_string = 'postgresql://' + pa.user + ":" + pa.password + "@" + pa.host + ":" + str(pa.port) + "/" + pa.dbname


def StatisticsDownloader():
    query = f"""SELECT * FROM input."DemandStatistics" """
    alchemyEngine = create_engine(conn_string)
    dbConnection = alchemyEngine.connect()
    Coordi = pd.read_sql(query, con=dbConnection)
    dbConnection.close()
    alchemyEngine.dispose()

    return Coordi


def DirectUpload(DBNAME, cur, FullPath, Data, Columns):
    Data.to_csv(FullPath, index=False, header=False)
    f = open(FullPath, 'r')
    cur.copy_from(f, DBNAME, sep=',', columns=Columns)
    f.close()

    # Remove
    os.remove(FullPath)

    return cur


# Always >= and <=
def Existing(DBNAME, Content, TargetA, TargetB):
    query = f"""select EXISTS(select * from "%s" where "%s" >= TIMESTAMP '%s' """ \
            f"""AND "%s" <= TIMESTAMP '%s')""" % (DBNAME, Content, TargetA, Content, TargetB)
    return query


# Always >= and <=
def Existing(DBNAME, Content, TargetA, TargetB):
    query = f"""select EXISTS(select * from "%s" where "%s" >= TIMESTAMP '%s' """ \
            f"""AND "%s" <= TIMESTAMP '%s')""" % (DBNAME, Content, TargetA, Content, TargetB)
    return query


def Counting(DBNAME, Content, TargetA, TargetB):
    query = f"""select count(*) from "%s" where "%s" >= TIMESTAMP '%s'""" \
            f"""AND "%s" <= TIMESTAMP '%s'""" % (DBNAME, Content, TargetA, Content, TargetB)

    return query


def NullTesting(DBNAME, Content, TargetA, TargetB):
    query = f"""select EXISTS(select * from "%s" where "%s" >= TIMESTAMP '%s' """ \
            f"""AND "%s" <= TIMESTAMP '%s' """ \
            f"""AND not ("%s" is not null))""" % (DBNAME, Content, TargetA, Content, TargetB, DBNAME)
    return query


def Deleting(DBNAME, Content, TargetA, TargetB):
    query = f"""delete from "%s" where "%s" >= TIMESTAMP '%s' AND "%s" <= TIMESTAMP '%s' """ \
            % (DBNAME, Content, TargetA, Content, TargetB)
    return query


def DeletingPRED(DBNAME, Content, TargetA, TargetB, Area):
    query = f"""delete from "%s"."%s" where "RunId"='%s' AND  "AreaId"='%s' AND "%s" >= TIMESTAMP '%s' AND "%s" <= TIMESTAMP '%s' """ \
            % ("output", DBNAME, pa.RunId, Area, Content, TargetA, Content, TargetB)
    return query


def PredDownloader(Variable, TargetDB, Area, Begin, End):
    # query = """ SELECT * FROM mkt."OcctoDemandActual" where "DateTime" = '2022-01-01 13:00:00' """

    query = """ SELECT "ModelId", "FcstDT", "AreaId","DeliveryDT", "%s" FROM fcst."%s" where "AreaId" = '%s' AND  "FcstDT" >=  '%s' AND "FcstDT" <= '%s' """ \
            % (Variable, TargetDB, Area, Begin, End)

    alchemyEngine = create_engine(conn_string)  # ,connect_args={'options':'-csearch_path={}'.format(pa.dbschema)}
    dbConnection = alchemyEngine.connect()
    Demand = pd.read_sql(query, con=dbConnection)
    dbConnection.close()
    alchemyEngine.dispose()

    return Demand


def UploadManager(Data, dday, dday2, Type, Content, NRows):
    Ideal = pa.Ideal[Type]
    DataRows = len(Data)

    # DB Info DB name, Data File, Data Column
    DBNAME = pa.DBNAME[Type]
    UploadFile = pa.UploadFile[Type]
    Col = pa.Columns[Type]

    conn = psycopg2.connect(host=pa.host, dbname=pa.dbname, user=pa.user, password=pa.password,
                            port=pa.port, options="-c search_path=weather,model,input,output")

    # Check with issue time
    cur = conn.cursor()
    cur.execute(Existing(DBNAME, Content, dday, dday2))
    Exists = cur.fetchone()[0]

    if Exists == True:
        cur = conn.cursor()
        cur.execute(Counting(DBNAME, Content, dday, dday2))
        NumberOfRows = cur.fetchone()[0]

        if NumberOfRows == Ideal:  # Perfect case
            cur = conn.cursor()
            cur.execute(NullTesting(DBNAME, Content, dday, dday2))
            NullCheck = cur.fetchone()[0]

            # There is null
            if NullCheck == True:
                ORDER = "DELETE"  # There are null values
                print(ORDER, Ideal, NumberOfRows, DataRows, NRows,
                      "There are null data, so please delete old data and insert new one.")

            else:
                ORDER = "PASS"
                print(ORDER, Ideal, NumberOfRows, DataRows, NRows,
                      "Ideal Case. The length of new and old data are equal and good.")

        elif NumberOfRows == NRows:  # This is our best, so it is not bad
            cur = conn.cursor()
            cur.execute(NullTesting(DBNAME, Content, dday, dday2))
            NullCheck = cur.fetchone()[0]

            # There is null
            if NullCheck is True:
                ORDER = "DELETE"  # There are null values
                print(ORDER, Ideal, NumberOfRows, DataRows, NRows,
                      "There are null data, so please delete old data and insert new one.")

            else:
                ORDER = "PASS"
                print(ORDER, Ideal, NumberOfRows, DataRows, NRows,
                      "Perfect Case. The length of new and old data are equal and good.")

        elif DataRows == Ideal:  # Input is perfect
            ORDER = "DELETE"
            print(ORDER, Ideal, NumberOfRows, DataRows, NRows,
                  "New data is ideal, so just delete old one and insert new one.")

        elif (NumberOfRows < DataRows) & (DataRows == NRows):
            ORDER = "DELETE"
            print(ORDER, Ideal, NumberOfRows, DataRows, NRows, "We got what we should've get. New one is better.")

        elif (NumberOfRows >= DataRows) & (DataRows == NRows):  # Self Satisfy
            ORDER = "DELETE"
            print(ORDER, Ideal, NumberOfRows, DataRows, NRows, "I am invinsible. Start from the beginning. Come on!")

        else:
            ORDER = "PASS"
            print(ORDER, Ideal, NumberOfRows, DataRows, NRows, "This is a rare case. Do nothing")

    elif Exists == False:
        ORDER = "DELETE"  # There is no data
        print(ORDER, Ideal, DataRows, NRows,
              "There is no data, so please insert the new data regardless of its length.")

    else:
        ORDER = "PASS"  # Please go safely

    # OverRide
    if Type == 'WFOR':
        ORDER = 'DELETE'
        print("Overide for WFOR. Receive the most recent")

    if ORDER == "INSERT":
        cur = DirectUpload(DBNAME, cur, UploadFile, Data, Col)  # Uploading

    elif ORDER == "DELETE":
        cur.execute(Deleting(DBNAME, Content, dday, dday2))
        cur = DirectUpload(DBNAME, cur, UploadFile, Data, Col)

    conn.commit()
    cur.close()
    conn.close()

    return []


def Deleting(DBNAME, Content, TargetA, TargetB):
    query = f"""delete from "%s" where "%s" >= TIMESTAMP '%s' AND "%s" <= TIMESTAMP '%s' """ \
            % (DBNAME, Content, TargetA, Content, TargetB)
    return query


def DeletingPRED(DBNAME, Content, TargetA, TargetB, Area):
    query = f"""delete from "%s"."%s" where "RunId"='%s' AND  "AreaId"='%s' AND "%s" >= TIMESTAMP '%s' AND "%s" <= TIMESTAMP '%s' """ \
            % ("output", DBNAME, pa.RunId, Area, Content, TargetA, Content, TargetB)
    return query


def ModelUpdating(PP):
    # Model Upload
    ModelName = PP['Machine'] + '_' + PP['Structure']
    SampleModel = [PP['Machine'], PP['Structure'], PP["Accuracy"]]

    PreviousModels = ModelDownloader()

    if len(PreviousModels) == 0:
        Action = "UPLOAD"
        ModelId = 0

    else:
        # Duplicate Test
        PreviousModels['Temp'] = PreviousModels['ModelGroup'] + '_' + PreviousModels['ModelName']
        ModelNameE = pa.Gen + '_' + ModelName
        SelectModel = PreviousModels[(PreviousModels['Temp'] == ModelNameE)]

        if len(SelectModel) == 0:
            MaximumNumber = max(PreviousModels['ModelId'])
            ModelId = MaximumNumber + 1
            Action = "UPLOAD"

        else:
            print("There is a model already, so just return the model id.")
            ModelId = SelectModel.ModelId.values[0]
            Action = "PASS"

    if Action == "UPLOAD":

        conn = psycopg2.connect(host=pa.host, dbname=pa.dbname, user=pa.user, password=pa.password,
                                port=pa.port, options="-c search_path=weather,model,input,output")

        cur = conn.cursor()
        query = f"""INSERT INTO "RefModel" ("ModelId","ModelGroup","ModelName","ModelDescription") 
                values ('%s','%s','%s','%s') """ % (ModelId, pa.Gen, ModelName, ' ')
        cur.execute(query)

        conn.commit()
        cur.close()
        conn.close()

        print("Upload: ", SampleModel, "for ", PP["FcstDT"])

    else:
        print("Do not upload the model.")

    return ModelId


def UploadManagerPRED(Data, dday, dday2, Type, Content, Area):
    # DB Info DB name, Data File, Data Column
    Ideal = pa.Ideal[Type]
    DataRows = len(Data)
    OutputDBNAME = pa.OutputDBNAME[Type]
    UploadFile = pa.UploadFile[Type]
    Col = pa.Columns[Type]

    if 1:  # DataRows == Ideal:
        conn = psycopg2.connect(host=pa.host, dbname=pa.dbname, user=pa.user, password=pa.password,
                                port=pa.port, options="-c search_path=weather,model,input,output")

        # Check with issue time
        cur = conn.cursor()
        cur.execute(DeletingPRED(OutputDBNAME, Content, dday, dday2, Area))
        cur = DirectUpload(OutputDBNAME, cur, UploadFile, Data, Col)

        conn.commit()
        cur.close()
        conn.close()

        print(dday, dday2, "Area", Area, "Uploading is compete")

    else:
        print("Pass, Something is wrong")
        sys.exit(1)

    return []
