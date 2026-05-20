import pandas as pd


class AnalyticsService:

    @staticmethod
    def preprocess(df):

        df["transaction_date"] = pd.to_datetime(
            df["transaction_date"],
            format="%m-%d-%Y",
            errors="coerce"
        )

        df["transaction_time"] = pd.to_datetime(
            df["transaction_time"],
            format="%H:%M:%S",
            errors="coerce"
        )

        df = df.dropna()

        df["month"] = (
            df["transaction_date"]
            .dt.strftime("%Y-%m")
        )

        df["hour"] = (
            df["transaction_time"]
            .dt.hour
        )

        return df


    @staticmethod
    def daily_revenue(df):

        return (

            df.groupby(
                "transaction_date"
            )["Total_Bill"]

            .sum()

            .reset_index()

        )


    @staticmethod
    def monthly_revenue(df):

        return (

            df.groupby(
                "month"
            )["Total_Bill"]

            .sum()

            .reset_index()

        )


    @staticmethod
    def product_ratio(df):

        return (

            df.groupby(
                "product_category"
            )["transaction_qty"]

            .sum()

            .reset_index()

        )


    @staticmethod
    def peak_hour(df):

        return (

            df.groupby(
                "hour"
            )["Total_Bill"]

            .mean()

            .reset_index()

        )