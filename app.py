import streamlit as st
import pandas as pd
import json


class DataFrameParser:
    DIMENSION = "Category"
    MEASURE = "Value"

    def __init__(self, df):
        self._df = df
        self._add_column_types()

    def _add_column_types(self):
        column_names = self._df.columns
        for column_name in column_names:
            if not self._is_column_convertable_to_float(column_name):
                continue
            index = (
                1 if pd.api.types.is_numeric_dtype(self._df[column_name].dtype) else 0
            )
            selected_type = st.selectbox(
                f"Set type for {column_name}",
                [DataFrameParser.DIMENSION, DataFrameParser.MEASURE],
                index=index,
            )
            self._convert_column(column_name, selected_type)

    def _is_column_convertable_to_float(self, column_name):
        try:
            self._df[column_name].astype(float)
            return True
        except ValueError:
            return False

    def _convert_column(self, column_name, selected_type):
        if selected_type == DataFrameParser.DIMENSION:
            self._df[column_name] = self._df[column_name].astype(str)
        else:
            self._df[column_name] = self._df[column_name].astype(float)


class CsvFileUploader:
    def __init__(self):
        self._csv_file = None
        self._df = None
        self._add_title()
        self._add_upload_button()
        self._parse_csv_file()
        self._init_data_frame_parser()

    @property
    def df(self):
        return self._df

    def _add_title(self):
        st.subheader("Create Data")

    def _add_upload_button(self):
        self._csv_file = st.file_uploader("Upload a CSV file", type=["csv"])

    def _parse_csv_file(self):
        if self._csv_file is not None:
            self._df = pd.read_csv(self._csv_file)

    def _init_data_frame_parser(self):
        if self._df is not None:
            DataFrameParser(self._df)
            st.write(self._df.head(5))


class ChartBuilder:
    KEYS = [
        "Cat1, Value1",
        "Cat1, Value1, Value2",
        "Cat1, Cat2, Value1",
        "Cat1, Cat2, Value1, Value2",
    ]

    def __init__(self, df):
        self._df = df
        self._categories1, self._categories2 = None, None
        self._values1, self._values2 = None, None
        self._key = None
        self._presets = self._parse_presets_file()
        if self._df is not None:
            self._categories, self._values = self._get_columns()
            self._add_title()
            self._add_select_buttons()
            self._set_key()
            self._add_show_button()

    def _add_title(self):
        st.subheader("Create Chart")

    def _get_columns(self):
        categories = []
        values = []
        for column_name in self._df.columns:
            if self._df[column_name].dtype == object:
                categories.append(column_name)
            else:
                values.append(column_name)
        return categories, values

    def _add_select_buttons(self):
        self._categories1, self._categories2 = self._add_select_buttons_by_type(
            DataFrameParser.DIMENSION
        )
        self._values1, self._values2 = self._add_select_buttons_by_type(
            DataFrameParser.MEASURE
        )

    def _add_select_buttons_by_type(self, type):
        items = self._categories
        if type == DataFrameParser.MEASURE:
            items = self._values
        button1 = st.selectbox(f"Select {type} 1 (mandatory)", items)
        items_for_button2 = [c for c in items if c != button1]
        items_for_button2.insert(0, None)
        button2 = st.selectbox(f"Select {type} 2 (optional)", items_for_button2)
        return button1, button2

    def _set_key(self):
        contains = {"Cat1": False, "Cat2": False, "Value1": False, "Value2": False}
        if self._categories1 is not None:
            contains["Cat1"] = True
        if self._categories2 is not None:
            contains["Cat2"] = True
        if self._values1 is not None:
            contains["Value1"] = True
        if self._values2 is not None:
            contains["Value2"] = True
        self._key = ", ".join(key for key, value in contains.items() if value)
        if self._key not in self.KEYS:
            st.warning("Please select both a category and a value for the chart!")

    def _parse_presets_file(self):
        with open("presets/presets.json", "r") as json_file:
            return json.load(json_file)

    def _add_show_button(self):
        if st.button("Show Charts"):
            if self._presets and self._key:
                if self._key in self._presets:
                    st.write(self._presets[self._key])


class App:
    def __init__(self):
        self._df = None
        self._add_title()
        self._init_csv_file_loader()
        self._init_chart_builder()

    def _add_title(self):
        st.title("Vizzu Chart Builder")

    def _init_csv_file_loader(self):
        csv_file_uploader = CsvFileUploader()
        self._df = csv_file_uploader.df

    def _init_chart_builder(self):
        ChartBuilder(self._df)


App()