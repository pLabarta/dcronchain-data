#Suite of pre-built charts for analysing Decred On-chain and price performance
from checkonchain.dcronchain.dcr_add_metrics import *
from checkonchain.btconchain.btc_add_metrics import *
from checkonchain.general.standard_charts import *
from checkonchain.general.regression_analysis import *
from checkonchain.general.general_helpers import *
from datetime import date, datetime, time, timedelta

repo_dir = os.environ["GITHUB_REPO"]

# Modules for generating small data insights
class ChartOverview:
    def __init__(self,df,column):
        self.values=df[column]
        self.name=column
        self.today=self.values[-1]
        self.yesterday=self.values[-2]
        self.past_week=self.values[-7]
        self.ma28=self.values.rolling(window=28).mean()
        self.period28=self.ma28[-1]

df = dcr_add_metrics().dcr_ticket_models()
df = dcr_add_metrics().metric_mvrv_relative_btc(df)
df = dcr_add_metrics().metric_mrkt_real_gradient_usd(df,28)
df = dcr_add_metrics().metric_unrealised_PnL(df)
df = dcr_add_metrics().metric_mayer_multiple(df)
df = df.set_index('date')
# Export full DataFrame to CSV and JSON
df.to_csv(f'{repo_dir}/data/full_decred_data.csv')
df.to_json(f'{repo_dir}/data/full_decred_data.json',orient='split')

# Generate Chart Overview Table v1
# Details:
#  - Market Gradient uses 28 days
# import csv
# columns='CapMVRVCur,Mayer_Multiple,Price_DCRBTC_Mid,MrktGradient,UnrealisedPnL_Net'.split(',')
# metrics = []
# for column in columns:
#     metrics.append(ChartOverview(df,column))

# with open('chart_overview_table.csv','w') as csvfile:
#     writer = csv.writer(csvfile)
#     writer.writerow(['name','value_current','pastvalue_1d','pastvalue_7d','ma28day'])
#     for metric in metrics:
#         writer.writerow([metric.name,metric.today,metric.yesterday,metric.past_week,metric.period28])

# Generate General Insights Table
# Key Components:
# - Primary Stat
# - Secondary Stat
# - Status Bar [-1:1]
# Metrics:
# - Treasury Growth
# - Decred Price (Power)
# - MarketCap

from collections import namedtuple
MetricInsight=namedtuple('MetricInsight',['name','primary','secondary','statusbar','description'])

insight_list = []

# Treasury Insight
# HACERLO EN USD usando el tipo de cambio a la fecha del dato
treasury_df = dcrdata_api().dcr_treasury()
treasury_desc = 'Primary: Today Balance, Secondary: Last Month Balance, Statusbar: IncomeSpent%'
treasury_primary = treasury_df['balance_dcr'].iloc[-1]
treasury_secondary = treasury_df['balance_dcr'].iloc[-30]
# Calculate growth
def calculate_growth_statusbar(treasury_df):
    last_month_income = treasury_df['received_dcr'].iloc[-30:].sum()
    last_month_spent = treasury_df['sent_dcr'].iloc[-30:].sum()
    net = last_month_income - last_month_spent
    status = net/last_month_income*100
    return status
treasury_statusbar = calculate_growth_statusbar(treasury_df)
treasury_insight = MetricInsight('Treasury Growth',treasury_primary,treasury_secondary,treasury_statusbar,treasury_desc)
insight_list.append(treasury_insight)

#Generate Decred Power Insight
power = df['PriceUSD']
power_desc = 'Primary: Today Price, Secondary: Last Month Price, Statusbar: MonthlyChange%'
power_primary=power[-1]
power_secondary=power[-30]
power_statusbar=(power_secondary-power_primary)/power_primary*100
power_insight = MetricInsight('Decred Power',power_primary,power_secondary,power_statusbar,power_desc)
insight_list.append(power_insight)

# Generate MarketCap Insight
realcap = df['CapRealUSD']
realcap_desc = 'Primary: Today RealisedCapUSD, Secondary: LastMonth RealisedCapUSD, Statusbar: MonthlyChange%'
realcap_primary = realcap[-1]
realcap_secondary = realcap[-30]
realcap_statusbar =(realcap_secondary-realcap_primary)/realcap_primary*100
realcap_insight = MetricInsight('Realised Cap',realcap_primary,realcap_secondary,realcap_statusbar,realcap_desc)
insight_list.append(realcap_insight)

insight_df = pd.DataFrame()
insight_df['name'] = [insight.name for insight in insight_list]
insight_df['primary'] = [insight.primary for insight in insight_list]
insight_df['secondary'] = [insight.secondary for insight in insight_list]
insight_df['statusbar'] = [insight.statusbar for insight in insight_list]
insight_df['description'] = [insight.description for insight in insight_list]

insight_df.to_json(f'{repo_dir}/data/homepage_insights.json',orient='split')