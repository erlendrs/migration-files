import streamlit as st
import numpy as np
import shutil
import os
import pandas as pd
import base64

st.title('Lag importfil til IFS fra filsti')

username = st.text_input(label='Steg 1: Skriv inn ditt kortnavn')

if username:
        st.success(f'Kortnavn lagret')

facility = st.text_input(label='Steg 2: Skriv inn navn og kortnavn på anlegg (f.eks. FAG Fagrafjell)')

if facility:
    st.success(f'Du har valgt {facility} stasjon')

folder_path = st.text_input("Enter the path of the folder: ")
folder_path = folder_path.strip()

def main():


    def import_files(df):
        IMPORT_FILE = pd.DataFrame(columns=['DOC_CLASS', 'DOC_NO', 'DOC_SHEET', 'DOC_REV', 'FORMAT_SIZE', 'REV_NO',
        "DOCUMENT_TYPE", 'TITLE', 'DOC_TYPE', 'INFO', 'FILE_NAME', 'LOCATION_NAME', 'PATH',
        'FILE_TYPE', 'FILE_NAME2', 'FILE_TYPE2', 'DOC_TYPE2', 'FILE_NAME3',
        'FILE_TYPE3', 'DOC_TYPE3', 'DT_CRE', 'USER_CREATED', 'ROWSTATE',
        'MCH_CODE', 'CONTRACT', 'REFERANSE'])
        
        IMPORT_FILE.TITLE = list(df)
        IMPORT_FILE.FILE_NAME = list(df)
        IMPORT_FILE.TITLE = IMPORT_FILE.TITLE.apply(lambda x: x.rsplit('.', 1)[0]) + ", " + facility
        IMPORT_FILE.DOCUMENT_TYPE = (doc_type_drop_down["DOCUMENT_TYPE"].astype("category").cat.add_categories(doc_type))
        IMPORT_FILE.FILE_TYPE = IMPORT_FILE.FILE_NAME.apply(create_filetype)
        IMPORT_FILE.DT_CRE = pd.datetime.today().strftime("%d.%m.%y")
        IMPORT_FILE.USER_CREATED = username.upper()
        IMPORT_FILE.DOC_NO = np.nan
        IMPORT_FILE.DOC_SHEET = 1
        IMPORT_FILE.DOC_REV = 1
        IMPORT_FILE.REV_NO = 1
        IMPORT_FILE.DOC_TYPE = 'ORIGINAL'
        IMPORT_FILE.INFO = np.nan
        IMPORT_FILE.LOCATION_NAME = 'XXXX'
        IMPORT_FILE.PATH = 'YYYY'
        IMPORT_FILE.FILE_NAME2 = np.nan
        IMPORT_FILE.FILE_TYPE2 = np.nan
        IMPORT_FILE.DOC_TYPE2 = np.nan
        IMPORT_FILE.FILE_NAME3 = np.nan
        IMPORT_FILE.FILE_TYPE3 = np.nan
        IMPORT_FILE.DOC_TYPE3 = np.nan
        IMPORT_FILE.ROWSTATE = 'Frigitt'
        IMPORT_FILE.MCH_CODE = ""
        IMPORT_FILE.CONTRACT = 10
        IMPORT_FILE.REFERANSE = np.nan
        return IMPORT_FILE

    def create_new_document_titles(df):
        """Lager ny dokumenttittel bsasert på dokumenttype, leverandørs tittel, dokumentnummer og anleggskode"""
        df.TITLE = df.DOCUMENT_TYPE.astype(str) + '_ ' + df.TITLE
        return df

    def import_documents(IMPORT_FILE):

        return IMPORT_FILE

    def check_for_comma_in_file_name(df):
        comma_check = df['FILE_NAME'].str.contains(',')
        df = df[comma_check]
        return df

    def rename_file(df, folder_path):

        remove_comma = lambda x: x.replace(",", "")

        # apply the lambda function to each filename in the Series
        #new_filenames = df["FILE_NAME"].apply(remove_comma)
        new_filenames = df["FILE_NAME"].tolist()

        for file in new_filenames:
            os.rename(folder_path + "/" + file, folder_path + "/" + remove_comma(file))

        return new_filenames

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

    def get_doc_attributes(doc_type, key=0):
        """Omega 365 dokumentkode (key value) henter dokumenttype fra IFS (default index=0), IFS klasse (index=1) og IFS format (index=2) fra liste i doc_dict"""

        if doc_type in doc_dict.keys():
            return doc_dict.get(doc_type)[key]
        else:
            return np.nan

    def create_doc_attributes(df):
        """Bruker get_doc_attributes til å fylle ut dokumenttype, klasse og format på df """

        df.DOC_CLASS = df.DOCUMENT_TYPE.apply(get_doc_attributes, key=0)
        df.FORMAT_SIZE = df.DOCUMENT_TYPE.apply(get_doc_attributes, key=1)

        return df

    doc_dict = {
                # DOKUMENTER
                'Drift-, Montasje- og Vedlikeholdsmanual': ['ANLEGGSDOK', 'TEKDOK'],
                'FAT-rapport': ['ANLEGGSDOK', 'PRPROT'],
                'Prøveprotokoll': ['ANLEGGSDOK', 'PRPROT'],
                "Sjekkliste montasje": ["ANLEGGSDOK", "TEKRAP"],
                
                # TEGNINGER
                'Målskisse': ['TEGNINGER', 'MONT'],
                'Fundamenttegning': ['TEGNINGER', 'FUNDT'],
                'Interne strømløpsskjema': ['TEGNINGER', 'SKJEMA'],
                'Stativtegning': ['TEGNINGER', 'MONT'],
                
                    }
    doc_type_drop_down = pd.DataFrame([{"DOCUMENT_TYPE": None},])
    doc_type = ["Målskisse", "Interne strømløpsskjema", 'Drift-, Montasje- og Vedlikeholdsmanual',  'Prøveprotokoll', 'Stativtegning',
                "Sjekkliste montasje", "FAT-rapport",
                ]
    doc_type = sorted(doc_type)
    
    if folder_path:
        df = import_files(list_files(folder_path))
        error = check_for_comma_in_file_name(df)
        if len(error) != 0:
            st.error("Følgende filer inneholder komma og må fikses")
            st.dataframe(error["FILE_NAME"])
            if st.button("Rename file"):
                renamed_files = rename_file(error, folder_path)
                st.dataframe(renamed_files)

        else:
            df2 = st.experimental_data_editor(df, use_container_width=True)
            if st.button('Lag lastefil'):
                edited_df = create_new_document_titles(df2)
                edited_df = create_doc_attributes(edited_df)
                edited_df = import_documents(edited_df.drop(columns=['DOCUMENT_TYPE']))
                st.dataframe(edited_df, use_container_width=True)
                csv = edited_df.to_csv(index=False)
                date = pd.datetime.today().strftime("%d.%m.%y")
                number_of_files = edited_df.FILE_TYPE.count() + edited_df.FILE_TYPE2.count()
                b64 = base64.b64encode(csv.encode()).decode()  # Encode the CSV data
                href = f'<a href="data:file/csv;base64,{b64}" download="Importfil til IFS med {number_of_files} filer ({date}).csv">Last ned CSV for filimport til IFS med {number_of_files} filer</a>'
                st.markdown(href, unsafe_allow_html=True)

    st.title("File Mover")

    source_folder = folder_path
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

if __name__ == "__main__":
    main()