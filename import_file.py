import streamlit as st
import numpy as np
import datetime as dt
import shutil
import os
import pandas as pd
import base64

st.title('Lag importfil til IFS fra filsti')

username = st.text_input(label='Steg 1: Skriv inn ditt kortnavn')

if username:
    st.success(f'Kortnavn lagret')

facility = st.text_input(label='Steg 2: Skriv inn navn og kortnavn på anlegg (eks. FAG Fagrafjell)')

if facility:
    st.success(f'Du har valgt {facility} stasjon')

folder_path = st.text_input("Enter the path of the folder: ")

def import_documents(df):
    IMPORT_FILE = pd.DataFrame(columns=['DOC_CLASS', 'DOC_NO', 'DOC_SHEET', 'DOC_REV', 'FORMAT_SIZE', 'REV_NO',
       'TITLE', 'DOC_TYPE', 'INFO', 'FILE_NAME', 'LOCATION_NAME', 'PATH',
       'FILE_TYPE', 'FILE_NAME2', 'FILE_TYPE2', 'DOC_TYPE2', 'FILE_NAME3',
       'FILE_TYPE3', 'DOC_TYPE3', 'DT_CRE', 'USER_CREATED', 'ROWSTATE',
       'MCH_CODE', 'CONTRACT', 'REFERANSE'])

    doc_class = ["ANLEGGSDOK", "TEGNINGER"]

    IMPORT_FILE.TITLE = list(df)
    IMPORT_FILE.TITLE = IMPORT_FILE.TITLE.apply(lambda x: x.rsplit('.', 1)[0])
    IMPORT_FILE.FILE_NAME = list(df)
    IMPORT_FILE.DOC_CLASS = ""
    IMPORT_FILE.DOC_NO = np.nan
    IMPORT_FILE.DOC_SHEET = 1
    IMPORT_FILE.DOC_REV = 1
    IMPORT_FILE.FORMAT_SIZE = ""
    IMPORT_FILE.REV_NO = 1
    IMPORT_FILE.DOC_TYPE = 'ORIGINAL'
    IMPORT_FILE.INFO = np.nan
    IMPORT_FILE.LOCATION_NAME = 'XXXX'
    IMPORT_FILE.PATH = 'YYYY'
    IMPORT_FILE.FILE_TYPE = IMPORT_FILE.FILE_NAME.apply(create_filetype)
    IMPORT_FILE.FILE_NAME2 = np.nan
    IMPORT_FILE.FILE_TYPE2 = np.nan
    IMPORT_FILE.DOC_TYPE2 = np.nan
    IMPORT_FILE.FILE_NAME3 = np.nan
    IMPORT_FILE.FILE_TYPE3 = np.nan
    IMPORT_FILE.DOC_TYPE3 = np.nan
    IMPORT_FILE.DT_CRE = dt.datetime.today().strftime("%d.%m.%y")
    IMPORT_FILE.USER_CREATED = username.upper()
    IMPORT_FILE.ROWSTATE = 'Frigitt'
    IMPORT_FILE.MCH_CODE = ""
    IMPORT_FILE.CONTRACT = 10
    #IMPORT_FILE.REFERANSE = np.nan
    IMPORT_FILE.dropna(subset=['DOC_CLASS', 'FORMAT_SIZE'], inplace=True)
    IMPORT_FILE.set_index('DOC_CLASS', inplace=True)

    return IMPORT_FILE

def create_filetype(filename):
    """Fyll ut felt FILE_TYPE basert på filekstensjon"""

    filename = str(filename)
    return [word for word in filename.split('.')][-1].upper()

def list_files(folder_path):
    
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            file_list.append(os.path.join(root, filename))
    df = pd.DataFrame({"FILENAME": file_list, "Path": file_list})
    df["File Name"] =  df["Path"].apply(lambda x: x.split("/")[-1])
    return list(df["File Name"])

custom_cat = ['aaa', 'bbb']

df = import_documents(list_files(folder_path))

edited_df = st.experimental_data_editor(df, use_container_width=True)

if st.button('Download CSV'):
    csv = edited_df.to_csv(index=False)
    date = pd.datetime.today().strftime("%d.%m.%y")
    number_of_files = edited_df.FILE_TYPE.count() + edited_df.FILE_TYPE2.count()
    b64 = base64.b64encode(csv.encode()).decode()  # Encode the CSV data
    href = f'<a href="data:file/csv;base64,{b64}" download="Importfil til IFS med {number_of_files} filer ({date}).csv">Last ned CSV for filimport til IFS med {number_of_files} filer</a>'
    st.markdown(href, unsafe_allow_html=True)

st.title("File Mover")

source_folder = st.text_input("Enter the path to the source folder:")
target_folder = st.text_input("Enter the path to the target folder:")

if st.button("Move files"):
    if not os.path.exists(source_folder):
        st.error("Source folder does not exist!")
    elif not os.path.exists(target_folder):
        st.error("Target folder does not exist!")
    else:
        for filename in os.listdir(source_folder):
            source_file = os.path.join(source_folder, filename)
            target_file = os.path.join(target_folder, filename)
            shutil.move(source_file, target_file)
        st.success("Files moved successfully!")
