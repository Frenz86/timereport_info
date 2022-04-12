
import streamlit as st
import pandas as pd
import re
import os

month_word = {
'January':1,
'February':2,
'March':3,
'April':4,
'May':5,
'June':6,
'July':7,
'August':8,
'September':9,
'October':10,
'November':11,
'December':12
}

def clean_time(text):
    """Remove special patterns - email, url, date etc."""
    _regex = re.compile(r"(\d+):(\d+)-(\d+):(\d+)")
    _regex2 = re.compile(r"(\d+):(\d+)")
    spaces = re.compile(r"\s{2,}")

    ## remove
    text = _regex.sub(" ", text)
    text = _regex2.sub("", text)
    text = spaces.sub("", text)
    return text

def clean_special_patterns(text):
    """Remove special patterns - email, url, date etc."""
    #email_regex = re.compile(r"^(.{0,22})")
    #url_regex = re.compile(r"(.{33}$)")#last 33
    regex_32 = re.compile(r"[\da-z]{32}")
    string_regex = re.compile(r"https://www.notion.so/")
    minus_regex = re.compile(r"[-]")
    spaces = re.compile(r"\s{2,}")
    remove_singlelett= re.compile(r"(^| ).( |$)")
    beg_last_spaces = re.compile(r"^\s+|\s$")

    ## remove
    #text = text.lower()
    #text = email_regex.sub(" ", text)
    text = string_regex.sub(" ", text)
    text = regex_32.sub("", text)
    text = minus_regex.sub(" ", text)
    text = spaces.sub("", text)
    #text = remove_singlelett.sub("", text)  
    text = beg_last_spaces.sub("", text)  
    return text

def main():
    st.title("Data Cleaning")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df.fillna('', inplace=True)
        df['Project Owner'] = df['Project Owner'].apply(clean_special_patterns)
        df['Prodotto'] = df['Prodotto'].apply(clean_special_patterns)
        df['Azienda'] = df['Azienda'].apply(clean_special_patterns)
        df['Opportunità'] = df['Opportunità'].apply(clean_special_patterns)
        df['Call/Meeting'] = df['Call/Meeting'].apply(clean_special_patterns)
        df['Project Owner'] = df['Project Owner'].str.split(',')
        df = df.explode('Project Owner')
        df = df.reset_index(drop=True)
        df['Ore dedicate'] = df['Minuti']/60
        df['Data'] = df['Data'].apply(clean_time)
        df["Azienda"] = df["Azienda"].str.replace('S P A','SPA')
        df["Azienda"] = df["Azienda"].str.replace('S R L','SRL')

        df['year'] = df['Data'].str[-5:]
        df['day'] = df['Data'].str[-8:-5]
        df['month'] = df['Data'].str[:-7]
        df['year'] = df['year'].str.replace('[\s]','')
        df["month"] = df["month"].str.replace('[\d\s]','')
        df["day"] = df["day"].str.replace('[^\d]','')
        df['monthn'] = df['month'].map(month_word)
        df.dropna(inplace=True)
        df['day'] = df['day'].astype('int')
        df['monthn'] = df['monthn'].astype('int')
        df['year'] = df['year'].astype('int')
        df = df[df.day != 0]
        df = df[df.monthn != 0]
        df = df[df.year != 0]
        df["Data"] = df['day'].astype(str) +"-"+df['monthn'].astype(str)+"-"+df['year'].astype(str)
        #df["Data"] = pd.to_datetime(df['Data'], format='%d-%m-%Y')

        with st.spinner("Training..."):
            st.balloons()
            import io
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                # Write each dataframe to a different worksheet.
                st.dataframe(df)
                df.to_excel(writer, index=False)
                # Close the Pandas Excel writer and output the Excel file to the buffer
                writer.save()
                st.download_button(
                    label="Download Excel Result",
                    data=buffer,
                    file_name="cleaned_time_report_info.xlsx",
                    mime="application/vnd.ms-excel")

    ###### transformation #####################################


if __name__ == "__main__":
    main()