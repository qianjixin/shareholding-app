import pandas as pd
from shareholding_data_class import ShareholdingData
from dash import dcc, dash_table
import plotly.express as px
from config import *
from utils import *


logger = logging.getLogger(__name__)


class ShareholdingDisplay(ShareholdingData):

    def __init__(self, start_date: pd.Timestamp, end_date: pd.Timestamp, stock_code: int, threshold_percentage: float) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.stock_code = stock_code
        self.threshold_percentage = threshold_percentage

        # Pull and pre-process shareholding data
        data = self.pull_shareholding_data(start_date, end_date, stock_code)
        data = data.drop(columns='date_requested')
        data = data.sort_values(by=['date', 'participant_id'], ascending=True)
        data = data.drop_duplicates(
            subset=['date', 'stock_code', 'participant_id'])
        data['participant'] = data['participant_id'] + \
            ': ' + data['participant_name']
        self.data = data

    def generate_trend_tab_data(self) -> dict:
        # Identify top 10 participants as of the end_date
        data_end_date = self.data.loc[self.data['date'].eq(
            self.data['date'].max())].reset_index(drop=True).copy(deep=True)
        top_participants_ids = data_end_date.sort_values(
            'shareholding', ascending=False).loc[range(10), 'participant_id'].to_list()

        # Filter data to the top 10 participants
        data_top_participants = self.data.loc[self.data['participant_id'].isin(
            top_participants_ids)].reset_index(drop=True)

        # 1. Build trend plot of shareholding of top 10 participants
        trend_fig = px.line(
            data_frame=data_top_participants,
            x='date',
            y='shareholding',
            color='participant',
            title=f'Stock: {self.data["stock_name"].mode().iloc[0]} ({self.stock_code}), Shareholding of Top 10 Participants',
            markers=True,
            labels={
                'date': 'Date',
                'shareholding': 'Shareholding',
                'participant': 'Participants'
            }
        )
        #trend_fig.show()

        # 2. Build table for display
        trend_data = data_top_participants[['date', 'stock_code', 'participant_id',
                                            'participant_name', 'shareholding', 'pct_total_issued']].drop_duplicates()

        return {
            'trend_fig': trend_fig,
            'trend_data_dict': trend_data.to_dict()
        }

    def generate_finder_tab_data(self) -> dict:
        threshold_proportion = self.threshold_percentage / 100

        # Identify transactions as a shareholding_pct_change >= threshold_proportion
        finder_data = self.data.copy(deep=True)
        finder_data['shareholding_diff'] = finder_data.groupby('participant_id')['shareholding'].transform(lambda s: s.diff())
        finder_data['shareholding_pct_change'] = finder_data.groupby('participant_id')['shareholding'].transform(lambda s: s.pct_change())
        finder_data['transaction_detected'] = finder_data['shareholding_pct_change'].abs().ge(threshold_proportion)

        # Detect transaction parties
        # For each day, find parties with inverse changes
        potential_transactions_concat_list = []
        for _, date_df in finder_data.groupby('date'):
            # Loop through net buyers
            for _, buyer_row in date_df.loc[date_df['shareholding_diff'].gt(0)].iterrows():
                # Loop through net sellers with the opposite shareholding_diff
                for _, seller_row in date_df.loc[date_df['shareholding_diff'].eq(-1 * buyer_row['shareholding_diff'])].iterrows():
                    output = {
                        'date': buyer_row['date'],
                        'stock_code': buyer_row['stock_code'],
                        'buyer_id': buyer_row['participant_id'],
                        'buyer_name': buyer_row['participant_name'],
                        'seller_id' : seller_row['participant_id'],
                        'seller_name': seller_row['participant_name'],
                        'quantity': buyer_row['shareholding_diff'],
                        'buyer_pct_change': np.round(100 * buyer_row['shareholding_pct_change'], 5),
                        'seller_pct_change': np.round(100 * buyer_row['shareholding_pct_change'], 5),
                        'buyer_shareholding': buyer_row['shareholding'],
                        'seller_shareholding': seller_row['shareholding']
                    }
                    potential_transactions_concat_list.append(output)

        potential_transactions = pd.DataFrame(potential_transactions_concat_list)

        return {
            'potential_transactions_dict': potential_transactions.to_dict()
        }
