#Suite of pre-built charts for analysing Decred On-chain and price performance
from checkonchain.dcronchain.dcr_add_metrics import *
from checkonchain.btconchain.btc_add_metrics import *
from checkonchain.general.standard_charts import *
from checkonchain.general.regression_analysis import *
from checkonchain.general.general_helpers import *
from datetime import date, datetime, time, timedelta
import os

class dcr_chart_suite():

    def __init__(self,theme):
        """
        Modules for producing standard check-onchain charts for Decred
        INPUT = theme (string)
            theme = 'light' = light theme chart
            theme = 'dark'  = dark theme chart (default)
        """
        self.theme = theme
        self.chart = check_standard_charts(self.theme)
        self.today = datetime.combine(date.today(), time())
        self.last = pd.to_datetime(self.today + pd.to_timedelta(90,unit='D'))
        self.start = '2016-01-01'

        #USD RANGE LEVELS (USD)
        self.cap_lb     = 5     #Market Cap Lower Bound (log)
        self.cap_ub     = 10    #Market Cap Upper Bound (log)
        self.price_lb   = -1    #Price Lower Bound (log)
        self.price_ub   = 3     #Price Lower Bound (log)

        #BTC RANGE LEVELS (BTC)
        self.cap_lb_btc     = 2     #Market Cap Lower Bound (log)
        self.cap_ub_btc     = 6     #Market Cap Upper Bound (log)
        self.price_lb_btc   = -4    #Price Lower Bound (log)
        self.price_ub_btc   = -1     #Price Lower Bound (log)
        
        self.df = dcr_add_metrics().dcr_ticket_models()
        #Create dataframe with key events like market tops, btms and halvings
        events = pd.DataFrame(
            data = [
                [np.datetime64('2016-02-08'),'genesis',0],
                [np.datetime64('2016-12-26'),'btm',0],
                [np.datetime64('2018-01-13'),'top',0],
                [np.datetime64('2020-05-16'),'btm',0],
            ],
            columns = ['date_event','event','epoch']
        )
        #Convert to UTC Timezone
        events['date_event'] = events['date_event'].dt.tz_localize('UTC')
        #Merge to add Price feed (keep date_event to calc deltas)
        events = pd.merge(
            events,
            self.df[['date','PriceUSD']],
            left_on='date_event',right_on='date'
        )
        #Rename price column
        events = events.rename(columns={'PriceUSD':'PriceUSD_event'})
        #Finalise into self and drop additional date column
        self.events = events.drop(columns='date')


    def add_slider(self,fig):
        """
        Adds x-axis slider to chart
        INPUT: fig = Plotly figure item to add slider
        """
        fig.update_layout(
            xaxis=dict(
                rangeslider=dict(
                    visible=True,
                    thickness=0.05
                )
            )
        )
        fig.update_yaxes(fixedrange=False)

    def write_html(self,fig,filename):
        pass # OVERWRITING
#         "Writes chart to checkmatey.github.io"
#         dirname = os.path.dirname(__file__).replace('/dcronchain/charts','')
#         html_path = dirname + '/hosted_charts/dcronchain' + filename  + filename + '_' + str(self.theme) + '.html'
#         pio.write_html(fig, file=html_path, auto_open=True)
#         json_path = dirname + '/hosted_charts/dcronchain' + filename  + filename + '_' + str(self.theme) + '.json'
#         pio.write_json(fig, file=json_path)

    def color_invert(self,color_data):
        """Inverts colors in a list
        INPUT
            color_data = list of 'rgb(rrr,ggg,bbb)' or 'rgba(rrr,ggg,bbb,a.aa)'
        """
        j = 0
        for i in color_data: #cycle through all colors
            if self.theme == 'light': #if light theme
                #split rbg and invert colors
                text = i.split('(')[1]
                text = text.split(')')[0]
                text = text.split(',')
                r = 255-int(text[0])
                g = 255-int(text[1])
                b = 255-int(text[2])
                if len(text) ==3:
                    text = 'rgb(' + str(r) + ',' + str(g) + ',' + str(b) + ')'
                if len(text) ==4:
                    a = float(text[3])
                    text = 'rgba(' + str(r) + ',' + str(g) + ',' + str(b) + ',' + str(a) + ')'
                color_data[j] = text
            j = j + 1
        return color_data

    def add_vol_bars(self,fig,df):
        """ =================================
            ADD VOLUME BAR CHARTS
        INPUTS:
            fig = figure to add volume bars to
            df  = DataFrame
        ================================="""
        x_data = [
            df['date'],
            df['date'],
            df['date']
        ]
        y_data = [
            df['dcr_tic_vol'],
            df['dcr_tfr_vol'],
            df['dcr_anon_mix_vol'],
        ]
        color_data = ['rgb(237,96,136)','rgb(37,187,217)','rgb(250, 38, 53)']
        loop_data = [0,1,2]
        name_data = ['Ticket Vol (DCR)','Transfer Vol (DCR)','Privacy Mix Vol (DCR)']
        for i in loop_data:
            fig.add_trace(
                go.Bar(x=x_data[i],y=y_data[i],name=name_data[i],opacity=0.5,marker_color=color_data[i],yaxis="y2"))
        fig.update_layout(barmode='stack',bargap=0.01,yaxis2=dict(side="right",position=0.15))

    def mvrv(self,model):
        """"Decred Realised Price and MVRV
            model = 0   = Network Valuation (Market Cap, Realised Cap etc)
            model = 1   = Pricing Model (Coin price, realised price etc)
        """
        df = self.df

        #STANDARD SETTINGS
        loop_data=[[0,1],[2,3,4,5,6]]
        width_data      = [2,2,2,1,1,2,1]
        opacity_data    = [1,1,1,1,1,1,1]
        dash_data = ['solid','solid','solid','dash','dash','dash','dash']
        color_data = [
            'rgb(255, 255, 255)',   #White
            'rgb(239, 125, 50)',    #Price Orange
            'rgb(46, 214, 161)',        #Turquoise
            'rgba(255, 80, 80, 0.0)',   #Gradient Red
            'rgba(255, 80, 80, 0.1)',   #Gradient Red
            'rgb(239, 125, 50)',        #Price Orange
            'rgba(36, 255, 136, 0.1)',  #Gradient Green
        ]
        #Invert Colors for Light Theme
        for i in [0,1,2,5]:
            color_data[i] = self.color_invert([color_data[i]])[0]
        #color_data = self.color_invert(color_data)

        legend_data = [True,True,True,False,True,False,True,]
        autorange_data = [False,False,False]
        type_data = ['date','log','log']
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            [self.start,self.last],    #N/A CEILING
            [self.start,self.last],    #SELL
            [self.start,self.last],    #UNITY
            [self.start,self.last],    #BUY
        ]
        fill_data = [
            'none','none','none',
            'none','tonexty','none','tozeroy'
        ]

        #MARKET CAP SETTINGS
        if model ==0:
            y_data = [
                df['CapMrktCurUSD'],
                df['CapRealUSD'],
                df['CapMVRVCur'],
                [5,5],      #NA Ceiling  
                [1.8,1.8],  #SELL
                [1.0,1.0],  #UNITY
                [0.7,0.7],  #BUY
            ]
            name_data = [
                'Market Cap',
                'Realised Cap',
                'MVRV Ratio',
                'N/A',
                'SELL ZONE (1.8)',
                'UNITY (1.0)',
                'BUY ZONE (0.7)',
            ]
            title_data = [
                '<b>Decred MVRV Ratio Valuation</b>',
                '<b>Date</b>',
                '<b>Network Valuation (USD)</b>',
                '<b>MVRV Ratio</b>']
            range_data = [[self.start,self.last],[self.cap_lb,self.cap_ub],[np.log10(0.3),4]]
        
        #MARKET CAP SETTINGS
        elif model ==1:
            y_data = [
                df['PriceUSD'],
                df['PriceRealUSD'],
                df['CapMVRVCur'],
                [5,5],      #NA Ceiling  
                [1.8,1.8],  #SELL
                [1.0,1.0],  #UNITY
                [0.7,0.7],  #BUY
            ]
            name_data = [
                'DCR Price',
                'Realised Price',
                'MVRV Ratio',
                'N/A',
                'SELL ZONE (1.8)',
                'UNITY (1.0)',
                'BUY ZONE (0.7)',
            ]
            title_data = [
                '<b>Decred MVRV Ratio Pricing</b>',
                '<b>Date</b>',
                '<b>Price (USD)</b>',
                '<b>MVRV Ratio</b>']
            range_data = [[self.start,self.last],[-1,3],[np.log10(0.3),4]]
        
        #BUILD CHART
        fig = self.chart.subplot_lines_doubleaxis_2nd_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        fig.update_yaxes(showgrid=False,secondary_y=True)
        self.add_slider(fig)
        
        #Write out html chart
        if model == 0:
            chart_name = '/mvrv_valuation_usd'
        elif model ==1:
            chart_name = '/mvrv_pricing_usd'
        # self.write_html(fig,chart_name)

        return fig

    def mvrv_relative_btc(self,model):
        """"Decred Relative Realised Price and MVRV after @permabullnino
            https://medium.com/@permabullnino/decred-on-chain-mini-pub-1-relative-mvrv-ratio-ea2564ca420f
            model = 0   = Network Valuation (Market Cap, Realised Cap etc)
            model = 1   = Pricing Model (Coin price, realised price etc)
        """
        df = self.df
        df = dcr_add_metrics().metric_mvrv_relative_btc(df)

        #STANDARD SETTINGS
        loop_data       = [[0,1,2,3,4],[5,6,7,   8,9,10,11]]
        width_data      = [2,2,2,2,2,    2,3,3,   1,1,1,1]
        opacity_data    = [1,1,1,1,1,    1,1,1,   1,1,1,1]
        dash_data = [
            'solid','dash','solid','solid','solid',
            'solid','solid','solid',
            'dash','dash','dash','dash']
        color_data = [
            'rgb(255, 255, 255)',       #White
            'rgb(41, 112, 255)',        #Key Blue
            'rgb(46, 214, 161)',        #Turquoise
            'rgb(237, 109, 71)',        #Decred Orange
            'rgb(209, 41, 94)',         #Turquoise (Inverted)
            #Secondary
            'rgb(46, 214, 161)',        #Turquoise
            'rgb(255, 192, 0)',         #Treasury Yellow
            'rgb(46, 214, 161)',        #Turquoise Blue

            'rgba(255, 80, 80, 0.0)',   #NA
            'rgba(255, 80, 80, 0.1)',   #Gradient Red
            'rgba(36, 255, 136, 0.0)',  #NA
            'rgba(36, 255, 136, 0.1)',  #Gradient Green
        ]
        #Invert Colors for Light Theme
        for i in [0,1,2,3,4,   5,6,]:
            color_data[i] = self.color_invert([color_data[i]])[0]
        #color_data = self.color_invert(color_data)

        legend_data = [
            True,True,True,True,True,
            True,True,True,
            False,True,False,True,]
        autorange_data = [False,False,False]
        type_data = ['date','log','log']
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            #Secondary
            df['date'],
            df['date'],
            df['date'],
            [self.start,self.last],    #N/A CEILING
            [self.start,self.last],    #UNITY
            [self.start,self.last],    #N/A CEILING
            [self.start,self.last],    #BUY

        ]
        fill_data = [
            'none','none','none','none','none',
            'none','none','none',
            'none','tonexty','none','tonexty'
        ]

        #MARKET CAP SETTINGS
        if model ==0:
            y_data = [
                df['CapMrktCurBTC'],
                df['CapRealBTC'],
                df['Price_DCRBTC_MVRV']*df['SplyCur'],    #Top
                df['Price_DCRBTC_Mid']*df['SplyCur'],     #Mid
                df['PriceBTC_onchain']*df['SplyCur'],     #Btm
                
                df['DCRBTC_MVRV'],
                df['DCRBTC_MVRV_28avg'],
                df['DCRBTC_MVRV_142avg'],

                [2,2],      #NA Ceiling  
                [1.0,1.0],  #UNITY
                [0.45,0.45],      #NA Ceiling  
                [0.01,0.01],  #BUY
            ]
            name_data = [
                'Market Cap (BTC)',
                'Realised Cap (BTC)',
                'Relative MVRV Cap (BTC)',
                'Mid Relative Realised Cap (BTC)',
                'Relative Onchain Cap (BTC)',

                'Relative MVRV Ratio',
                'Relative MVRV Ratio 28-DMA',
                'Relative MVRV Ratio 142-DMA',

                'N/A',
                'SELL ZONE (>1.0)',
                'N/A',
                'BUY ZONE (<0.4)',
            ]
            title_data = [
                '<b>Decred Relative BTC MVRV Ratio Valuation</b>',
                '<b>Date</b>',
                '<b>Network Valuation (BTC)</b>',
                '<b>Relative MVRV Ratio</b>']
            range_data = [[self.start,self.last],[self.cap_lb_btc,self.cap_ub_btc],[np.log10(0.2),3]]
        
        #MARKET CAP SETTINGS
        elif model ==1:
            y_data = [
                df['PriceBTC'],
                df['PriceRealBTC'],
                df['Price_DCRBTC_MVRV'],    #Top
                df['Price_DCRBTC_Mid'],     #Mid
                df['PriceBTC_onchain'],     #Btm
                
                df['DCRBTC_MVRV'],
                df['DCRBTC_MVRV_28avg'],
                df['DCRBTC_MVRV_142avg'],

                [2,2],      #NA Ceiling  
                [1.0,1.0],  #UNITY
                [0.45,0.45],      #NA Ceiling  
                [0.01,0.01],  #BUY
            ]
            name_data = [
                'Market Price (BTC)',
                'Realised Price (BTC)',
                'Relative MVRV Price (BTC)',
                'Mid Relative Realised Price (BTC)',
                'Relative Onchain Price (BTC)',

                'Relative MVRV Ratio',
                'Relative MVRV Ratio 28-DMA',
                'Relative MVRV Ratio 142-DMA',

                'N/A',
                'SELL ZONE (>1.0)',
                'N/A',
                'BUY ZONE (<0.4)',
            ]
            title_data = [
                '<b>Decred Relative BTC MVRV Ratio  Pricing</b>',
                '<b>Date</b>',
                '<b>Price (BTC)</b>',
                '<b>Relative MVRV Ratio</b>']
            range_data = [[self.start,self.last],[self.price_lb_btc,self.price_ub_btc],[np.log10(0.2),3]]
        
        #BUILD CHART
        fig = self.chart.subplot_lines_doubleaxis_2nd_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        fig.update_yaxes(showgrid=False,secondary_y=True)
        self.add_slider(fig)
        
        #Write out html chart
        if model == 0:
            chart_name = '/mvrv_valuation_btc'
        elif model ==1:
            chart_name = '/mvrv_pricing_btc'
        self.write_html(fig,chart_name)

        return fig

    def mrkt_real_gradient_usd(self,period):
        """"Presents an oscillator for the X-day gradient of the Market Cap and Realised Cap
            The metric helps to identify where off-chain sell/buy pressure front-runs on-chain signature
            INPUTS
                period = period of gradient (defaults to 28)
        """
        df = self.df
        df = dcr_add_metrics().metric_mrkt_real_gradient_usd(df,period)

        #STANDARD SETTINGS
        loop_data=[[0,1,6,7,8],[2,3,4,5]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
        ]
        y_data = [
            df['CapMrktCurUSD'],
            df['CapRealUSD'],
            df['MrktGradient'],
            df['RealGradient'],
            df['RealGradient'],
            df['DeltaGradient'],
            df['dcr_anon_mix_vol'],
            (df['dcr_anon_mix_vol'] + df['dcr_tic_vol']),
            df['TxTfrValNtv']
        ]
        name_data = [
            'Market Cap',
            'Realised Cap',
            'N/A',
            'Market Gradient',
            'Realised Gradient',
            'Delta Gradient',
            'CoinShuffle++ Mix Volume',
            'Ticket Purchase Volume',
            'Regular Tx Volume',
        ]
        color_data = [
            'rgb(255, 255, 255)',         #White
            'rgb(239, 125, 50)',          #Price Orange
            'rgba(255, 80, 80, 0.7)',     #Gradient Red
            'rgba(255, 80, 80, 0.3)',     #Gradient Red
            'rgba(36, 255, 136, 0.3)',    #Gradient Green
            'rgb(143, 207, 95)',          #Purple (Inverted)
            'rgba(250, 38, 53,0.3)',             #POW Red
            'rgba(46,  214, 161,0.3)',           #Turquoise
            'rgba(239, 125,  50,0.3)',           #Price Orange
        ]
        #Invert Colors for Light Theme
        for i in [0,1,2,3,4,5]:
            color_data[i] = self.color_invert([color_data[i]])[0]
        fill_data = [
            'none','none','none','tonexty','tozeroy','none','tozeroy','tonexty','tonexty'
        ]
        width_data      = [2,2,1,1,1,2,1,1,1]
        opacity_data    = [1,1,1,1,1,1,1,1,1]
        dash_data = ['solid','solid','solid','solid','solid','solid','solid','solid','solid',]
        legend_data = [True,True,False,True,True,True,True,True,True]
        autorange_data = [False,False,False]
        type_data = ['date','log','linear']
        range_data = [[self.start,self.last],[self.cap_lb,self.cap_ub],[-2,4]]
        title_data = [
            '<b>Decred Market-Realised Gradient Oscillator</b>',
            '<b>Date</b>',
            '<b>Network Valuation (USD)</b>',
            '<b>Market-Real Gradient</b>']
        #BUILD CHART
        fig = self.chart.subplot_lines_doubleaxis_both_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        fig.update_yaxes(showgrid=False,secondary_y=True)
        self.add_slider(fig)
        
        #Write out html chart
        chart_name = '/mrktrealgrad' + str(period) + 'day_oscillator_usd'

        self.write_html(fig,chart_name)
        return fig

    def mrkt_real_gradient_btc(self,period):
        """"Presents an oscillator for the X-day gradient of the Market Cap and Realised Cap in BTC
            The metric helps to identify where off-chain sell/buy pressure front-runs on-chain signature
            INPUTS
                period = period of gradient (defaults to 28)
        """
        df = self.df
        df = dcr_add_metrics().metric_mrkt_real_gradient_btc(df,period)

        #STANDARD SETTINGS
        loop_data=[[0,1,2,3,4],[5,6,7,8,9]] #,10,11,12 Volume
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
        ]
        y_data = [
            df['CapMrktCurBTC'],
            df['CapRealBTC'],
            df['Price_DCRBTC_MVRV']*df['SplyCur'],    #Top
            df['Price_DCRBTC_Mid']*df['SplyCur'],     #Mid
            df['PriceBTC_onchain']*df['SplyCur'],     #Btm

            df['MrktGradientBTC']*df['BTC_PriceUSD'],
            df['RealGradientBTC']*df['BTC_PriceUSD'],
            df['RealGradientBTC']*df['BTC_PriceUSD'],
            df['DeltaGradientBTC']*df['BTC_PriceUSD'],
            df['DeltaRelativeBTC'],

            df['dcr_anon_mix_vol']*df['PriceBTC'],
            (df['dcr_anon_mix_vol'] + df['dcr_tic_vol'])*df['PriceBTC'],
            df['TxTfrValNtv']*df['PriceBTC']
        ]
        name_data = [
            'Market Cap',
            'Realised Cap',
            'Relative MVRV Cap (BTC)',
            'Mid Relative Realised Cap (BTC)',
            'Relative Onchain Cap (BTC)',

            'N/A',
            'Market Gradient',
            'Realised Gradient',
            'Delta Gradient',
            'Delta Relative 28-142-day',

            'CoinShuffle++ Mix Volume',
            'Ticket Purchase Volume',
            'Regular Tx Volume',
        ]
        color_data = [
            'rgb(255, 255, 255)',         #White
            'rgb(41, 112, 255)',        #Key Blue
            'rgb(46, 214, 161)',        #Turquoise
            'rgb(237, 109, 71)',        #Decred Orange
            'rgb(209, 41, 94)',         #Turquoise (Inverted)

            'rgba(255, 80, 80, 0.7)',     #Gradient Red
            'rgba(255, 80, 80, 0.3)',     #Gradient Red
            'rgba(36, 255, 136, 0.3)',    #Gradient Green
            'rgb(143, 207, 95)',          #Purple (Inverted)
            'rgb(36, 255, 182)',          #Rich Red (Inverted)

            'rgba(250, 38, 53,0.3)',             #POW Red
            'rgba(46,  214, 161,0.3)',           #Turquoise
            'rgba(239, 125,  50,0.3)',           #Price Orange
        ]
        #Invert Colors for Light Theme
        for i in [0,1,2,3,4,5,6,7,8,9]:
            color_data[i] = self.color_invert([color_data[i]])[0]
        fill_data = [
            'none','none','none','none','none',
            'none','tonexty','tozeroy','none','none',
            'tozeroy','tonexty','tonexty'
        ]
        width_data      = [2,2,2,2,2,1,1,1,1,4,1,1,1]
        opacity_data    = [1,1,1,1,1,1,1,1,1,1,1,1,1]
        dash_data = [
            'solid','dash','solid','solid','solid',
            'solid','solid','solid','solid','solid',
            'solid','solid','solid',]
        legend_data = [True,True,True,True,True,False,True,True,True,True,True,True,True]
        autorange_data = [False,False,False]
        type_data = ['date','log','linear']
        range_data = [[self.start,self.last],[self.cap_lb_btc,self.cap_ub_btc],[-2,4]]
        title_data = [
            '<b>Decred Market-Realised Gradient Oscillator BTC</b>',
            '<b>Date</b>',
            '<b>Network Valuation (BTC)</b>',
            '<b>Market-Real Gradient (BTC)</b>']
        #BUILD CHART
        fig = self.chart.subplot_lines_doubleaxis_both_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        fig.update_yaxes(showgrid=False,secondary_y=True)
        self.add_slider(fig)
        
        #Write out html chart
        chart_name = '/mrktrealgrad' + str(period) + 'day_oscillator_btc'

        self.write_html(fig,chart_name)
        return fig

    def unrealised_PnL(self):
        """"Decred Unrealised PnL from Market and Realised"""
        df = self.df
        df = dcr_add_metrics().metric_unrealised_PnL(df)
            
        loop_data=[[0,1],[2,3,4,5,6]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
        ]
        y_data = [
            df['CapMrktCurUSD'],
            df['CapRealUSD'],
            df['UPnL_capitulation'],
            df['UPnL_fear'],
            df['UPnL_optimism'],
            df['UPnL_belief'],
            df['UPnL_euphoria'],
        ]
        name_data = [
            'Market Cap (USD)',
            'Realised Cap (USD)',
            'Capitulation',
            'Hope-Fear',
            'Optimism-Anxiety',
            'Belief-Denial',
            'Euphoria-Greed'
        ]
        width_data      = [2,2,1,1,1,1,1]
        opacity_data    = [1,1,1,1,1,1,1]
        dash_data = [
            'solid','solid','solid','solid','solid','solid','solid']
        color_data = [
            'rgb(255, 255, 255)',    #White
            'rgb(20, 169, 233)',    #Total Blue
            'rgba(233, 68,  68, 0.4)',     #Capitulation Red
            'rgba(247, 132, 16, 0.4)',    #Fear Orange
            'rgba(255, 192, 0 , 0.4)',     #Optimism Yellow
            'rgba(38, 200,  17, 0.4)',     #Belief Green
            'rgba(68, 103, 235, 0.4)',    #Greed Blue
        ]
        #Invert Colors for Light Theme
        color_data = self.color_invert(color_data)
        fill_data = [
            'none','none','tozeroy','tozeroy','tozeroy','tozeroy','tozeroy'
        ]
        legend_data = [
            True,True,True,True,True,True,True,
            ]
        title_data = [
            '<b>Decred Unrealised Profit and Loss</b>',
            '<b>Date</b>',
            '<b>Price (USD)</b>',
            '<b>Unrealised PnL</b>'
        ]

        range_data = [[self.start,self.last],[self.cap_lb,self.cap_ub],[-1.5,3.5]]
        
        autorange_data = [False,False,False]
        type_data = ['date','log','linear']
        fig = self.chart.subplot_lines_doubleaxis_2nd_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        fig.update_yaxes(showgrid=False,secondary_y=True,dtick=0.5)
        self.add_slider(fig)

        #Write out html chart
        chart_name = '/unrealisedpnl_oscillator_usd'
        self.write_html(fig,chart_name)
        return fig

    def difficulty_ribbon(self):
        """Decred Difficulty Ribbon and Block Subsidy Model

        Block Subsidy model paid after @permabullnino
        Realised cap after @Coinmetrics
        Difficulty Ribbon after @woonomic

        """
        df = self.df

        loop_data=[[0,2,3,4,5,],[6]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
        ]
        y_data = [
            df['CapMrktCurUSD'],
            df['CapRealUSD'],
            df['PoW_income_usd'].cumsum(),
            df['PoS_income_usd'].cumsum(),
            df['Fund_income_usd'].cumsum(),
            df['Total_income_usd'].cumsum(),
            df['DiffMean'],
        ]
        name_data = [
            'Market Cap',
            'Realised Cap',
            'POW-USD',
            'POS-USD',
            'Treasury-USD',
            'Total-USD',
            'Difficulty',
            ]
        color_data = [
            'rgb(255, 255, 255)',   #White
            'rgb(239, 125, 50)',    #Price Orange
            'rgb(250, 38, 53)',     #POW Red
            'rgb(114, 49, 163)',    #POS Purple
            'rgb(255, 192, 0)',     #Treasury Yellow
            'rgb(20, 169, 233)',    #Total Blue
            'rgb(46, 214, 161)',    #Turquoise
        ]
        #Invert Colors for Light Theme
        for i in [0,4,5,6]:
            color_data[i] = self.color_invert([color_data[i]])[0]
        dash_data = [
            'solid','dash','solid','solid','solid','solid','solid',
            ]
        width_data = [2,2,2,1,1,1,2]
        opacity_data = [1,1,1,0.7,0.7,0.7,1]
        legend_data = [True,True,True,True,True,True,True]#
        autorange_data = [False,False,True]
        type_data = ['date','log','log']#
        title_data = [
            '<b>Decred Difficulty Ribbon</b>',
            '<b>Date</b>',
            '<b>Network Valuation</b>',
            '<b>Difficulty</b>']
        range_data = [[self.start,self.last],[self.cap_lb,self.cap_ub],[0,0]]

        #BUILD FINAL CHART
        fig = self.chart.subplot_lines_doubleaxis(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data
            )
        fig.update_yaxes(showgrid=True,secondary_y=False)
        
        """ =================================
            ADD DIFFICULTY RIBBON
        ================================="""
        color_ribbon = str(color_data[6])
        for i in [9,14,25,40,60,90,128,200]:
            fig.add_trace(go.Scatter(
                mode='lines',
                x=df['date'], 
                y=df['DiffMean'].rolling(i).mean(),
                name='D_ '+str(i),
                opacity=0.5,
                showlegend=True,
                line=dict(
                    width=i/200*2,
                    color=color_ribbon,#Turquoise
                    dash='solid'
                    )),
                secondary_y=True)
        
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig = self.chart.add_annotation(fig,"@checkmatey<br />@permabullnino<br />after @woonomic")
        self.add_slider(fig)

        #Write out html chart
        chart_name = '/diffribbon_valuation_usd'
        self.write_html(fig,chart_name)

        return fig

    def difficulty_price(self):
        """
        Calculates Difficulty Multiple and Prices
        after @permabullnino
        https://medium.com/@permabullnino/decred-on-chain-mini-pub-3-difficulty-ribbon-price-d644e470b989
        Difficulty Ribbon after @woonomic

        """
        df = self.df
        df = dcr_add_metrics().metric_difficulty_price(df)
        df = dcr_add_metrics().metric_difficulty_model(df)[0]

        df['DiffPricePnL']      = (df['DiffPriceUSD']/df['Dif_Price_predict'])
        #df['DiffPricePnL']      = (df['DiffPriceUSD'] - df['Dif_Price_predict'])/df['Dif_Price_predict']
        df['DiffPriceRegPnL']   = (df['PriceUSD'] - df['Dif_Price_predict'])/df['PriceUSD']

        loop_data=[[0,2,1,5],[4,3]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
        ]
        y_data = [
            df['PriceUSD'],
            df['DiffPriceUSD'],
            df['Dif_Price_predict'],
            df['DiffMultiple'],
            df['DiffPriceRegPnL'],
            df['DiffPricePnL'],
        ]
        name_data = [
            'Price (USD)',
            'Difficulty Price',
            'Difficulty Regression',
            'Difficulty Multiple',
            'Difficulty Reg Multiple',
            'Difficulty Delta',
            ]
        color_data = [
            'rgb(255, 255, 255)',       #White
            'rgb(255, 80, 80)',         #Gradient Red
            'rgb(36, 255, 136)',        #Gradient Green
            'rgba(255, 80, 80, 0.3)',   #Gradient Red
            'rgba(36, 255, 136, 0.3)',  #Gradient Green
            'rgb(143, 207, 95)',          #Purple (Inverted)
        ]
        fill_data = [
            'none','none','none','tozeroy','tozeroy','none'
        ]
        #Invert Colors for Light Theme
        for i in [0,1,2,3,4,5]:
            color_data[i] = self.color_invert([color_data[i]])[0]
        dash_data = [
            'solid','solid','solid','solid','solid','solid'
            ]
        width_data = [2,2,2,2,2,2]
        opacity_data = [1,1,1,1,1,1]
        legend_data = [True,True,True,True,True,True]#
        autorange_data = [False,False,False]
        type_data = ['date','log','linear']#
        title_data = [
            '<b>Decred Difficulty Price Models</b>',
            '<b>Date</b>',
            '<b>PriceUSD</b>',
            '<b>Difficulty Multiple or PnL</b>']
        range_data = [[self.start,self.last],[self.price_lb,self.price_ub],[-10,30]]

        #BUILD FINAL CHART
        fig = self.chart.subplot_lines_doubleaxis_2nd_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_yaxes(showgrid=True,secondary_y=False)


        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig = self.chart.add_annotation(fig,"@checkmatey<br />@permabullnino")
        self.add_slider(fig)

        #Write out html chart
        chart_name = '/diffprice_pricing_usd'
        self.write_html(fig,chart_name)

        return fig


    def hashrate_income(self):
        """Decred Hashrate and PoW Income Chart
        """
        df = self.df
        df = df[1:]
        df = df[:-2]

        loop_data=[[1,0],[2]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
        ]
        y_data = [
            df['PoW_income_usd'],
            df['pow_hashrate_THs_avg'],
            df['PoW_income_dcr'].rolling(90).mean(),
        ]
        name_data = [
            'PoW Daily Income (USD, LHS)',
            'Hash-rate (TH/s, LHS)',
            'PoW Daily Income 90DMA (DCR, RHS)',
            ]
        color_data = [
            'rgb(255, 255, 255)',       #White
            'rgb(46, 214, 161)',        #Turquoise Blue
            'rgb(46, 214, 161)',        #Turquoise Blue
        ]
        #Invert Colors for Light Theme
        for i in [0,1]:
            color_data[i] = self.color_invert([color_data[i]])[0]
        dash_data = [
            'solid','solid','solid'
            ]
        width_data = [2,2,3]
        opacity_data = [1,1,0.75]
        legend_data = [True,True,True]#
        autorange_data = [False,False,False]
        type_data = ['date','linear','linear']#
        title_data = [
            '<b>Decred Hash-rate and Miner Income</b>',
            '<b>Date</b>',
            '<b>PoW Daily Income(USD)<br>Hash-rate (TH/s)</b>',
            '<b>PoW Daily Issuance (DCR)</b>'
        ]
        range_data = [[self.start,self.last],[0,6e5],[0,6000]]

        #BUILD FINAL CHART
        fig = self.chart.subplot_lines_doubleaxis(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data
            )
        fig.update_yaxes(showgrid=True,secondary_y=False)
        fig.update_xaxes(dtick='M3',tickformat='%d-%b-%y',showgrid=True)
        self.add_slider(fig)

        #Write out html chart
        chart_name = '/hashincome_performance_usd'
        self.write_html(fig,chart_name)

        return fig

    def block_subsidy_usd(self,model):
        """Decred Block Subsidy Models priced in USD with Difficulty Ribbon
        after @permabullnino
        INPUTS:
            model = 0   = Network Valuation (Market Cap, Realised Cap etc)
            model = 1   = Pricing Model (Coin price, realised price etc)
        """
        df = self.df
        df = dcr_add_metrics().metric_block_subsidy_usd(df)

        #STANDARD SETTINGS
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
        ]
        color_data = [
            'rgb(255, 255, 255)',    #White
            'rgb(250, 38, 53)',     #POW Red
            'rgb(114, 49, 163)',    #POS Purple
            'rgb(255, 192, 0)',     #Treasury Yellow
            'rgb(20, 169, 233)',    #Total Blue
        ]
        #Invert Colors for Light Theme
        for i in [0,3,4]:
            color_data[i] = self.color_invert([color_data[i]])[0]

        dash_data = ['solid','solid','solid','solid','solid','solid','dash']
        width_data = [2,2,2,2,2,2]
        opacity_data = [1,1,1,1,1,1]
        legend_data = [True,True,True,True,True,True]#
        autorange_data = [False,False,False]
        type_data = ['date','log','log']#
        
        #MARKET CAP SETTINGS
        if model ==0:
            loop_data = [[0,1,2,3,4],[]]
            y_data = [
                df['CapMrktCurUSD'],
                df['SubsidyPoWCapUSD'],
                df['SubsidyPoSCapUSD'],
                df['SubsidyFundCapUSD'],
                df['SubsidyCapUSD'],
            ]
            name_data = [
                'Market Cap',
                'POW-USD',
                'POS-USD',
                'Treasury-USD',
                'Total-USD', 
            ]
            title_data = [
                '<b>Decred Block Subsidy Valuation Models (USD)</b>',
                '<b>Date</b>',
                '<b>Network Valuation (USD)</b>',
                'N/A'
            ]
            range_data = [[self.start,self.last],[self.cap_lb,self.cap_ub],[5,11]]
        #MARKET CAP SETTINGS
        elif model == 1:
            loop_data = [[0,1,2,3,4],[]]
            y_data = [
                df['PriceUSD'],
                df['PoW_income_usd'].cumsum()/df['SplyCur'],
                df['PoS_income_usd'].cumsum()/df['SplyCur'],
                df['Fund_income_usd'].cumsum()/df['SplyCur'],
                df['Total_income_usd'].cumsum()/df['SplyCur'],
            ]
            name_data = [
                'DCR/USD Price', 
                'POW-USD',
                'POS-USD',
                'Treasury-USD',
                'Total-USD',
                ]
            title_data = [
                '<b>Decred Block Subsidy Pricing Models (USD)</b>',
                '<b>Date</b>',
                '<b>DCR Price (USD)</b>',
                '<b>Difficulty</b>'
            ]
            range_data = [[self.start,self.last],[self.price_lb,self.price_ub],[5,11]]
        
        #BUILD CHARTS
        fig = self.chart.subplot_lines_singleaxis(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data
            )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        
        #FINALISE CHART
        self.add_slider(fig)
        fig = self.chart.add_annotation(fig,"@checkmatey<br />@permabullnino")

        #Write out html chart
        if model == 0:
            chart_name = '/blocksubsidy_valuation_usd'
        elif model ==1:
            chart_name = '/blocksubsidy_pricing_usd'
        self.write_html(fig,chart_name)

        return fig

    def block_subsidy_btc(self,model):
        """Decred Block Subsidy Models priced in BTC with Difficulty Ribbon
        after @permabullnino
        INPUTS:
            model = 0   = Network Valuation (Market Cap, Realised Cap etc)
            model = 1   = Pricing Model (Coin price, realised price etc)
        """
        df = self.df
        df = dcr_add_metrics().metric_block_subsidy_btc(df)

        #STANDARD SETTINGS
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            ]
        color_data = [
            'rgb(250, 38, 53)' , #POW Red
            'rgb(114, 49, 163)', #POS Purple
            'rgb(255, 192, 0)',  #Treasury Yellow
            'rgb(20, 169, 233)', #Total Blue
            'rgb(255, 255, 255)', #White
            ]
        #Invert Colors for Light Theme
        for i in [2,3,4]:
            color_data[i] = self.color_invert([color_data[i]])[0]
            
        dash_data = ['solid','solid','solid','solid','solid','solid','dash']
        width_data = [2,2,2,2,2,2,2]
        opacity_data = [1,1,1,1,1,1,1]
        legend_data = [True,True,True,True,True,True,True,True]#
        autorange_data = [False,False,False]
        type_data = ['date','log','linear']#

        #NETWORK VALUATION SETTINGS
        if model == 0:
            loop_data = [[0,1,2,3,4],[]]
            y_data = [
                df['SubsidyPoWCapBTC'],
                df['SubsidyPoSCapBTC'],
                df['SubsidyFundCapBTC'],
                df['SubsidyCapBTC'],
                df['CapMrktCurBTC'],
                ]
            name_data = [
                'POW (BTC)',
                'POS (BTC)',
                'Treasury (BTC)',
                'Total (BTC)',
                'Market Cap (BTC)',
                ]
            title_data = [
                '<b>Decred Block Subsidy Valuation Models (BTC)</b>',
                '<b>Date</b>',
                '<b>Network Valuation (BTC)</b>',
                '<b>Total DCR in Tickets</b>'
                ]
            range_data = [[self.start,self.last],[self.cap_lb_btc,self.cap_ub_btc],[0,1]]

        #PRICING SETTINGS
        elif model == 1:
            loop_data = [[0,1,2,3,4],[]]
            y_data = [
                df['SubsidyPoWCapBTC']/df['SplyCur'],
                df['SubsidyPoSCapBTC']/df['SplyCur'],
                df['SubsidyFundCapBTC']/df['SplyCur'],
                df['SubsidyCapBTC']/df['SplyCur'],
                df['PriceBTC'],
                ]
            name_data = [
                'POW (BTC)',
                'POS (BTC)',
                'Treasury (BTC)',
                'Total (BTC)',
                'DCR Price (BTC)',
                ]
            title_data = [
                '<b>Decred Block Subsidy Pricing Models (BTC)</b>',
                '<b>Date</b>',
                '<b>DCR Price (BTC)</b>',
                '<b>Total DCR in Tickets</b>'
                ]
            range_data = [[self.start,self.last],[self.price_lb_btc,self.price_ub_btc],[0,1]]
        

        #BUILD CHARTS
        fig = self.chart.subplot_lines_doubleaxis(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,
            x_data,
            y_data,
            name_data,
            color_data,
            dash_data,
            width_data,
            opacity_data,
            legend_data
        )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        
        #FINALISE CHART
        fig = self.chart.add_annotation(fig,"@checkmatey<br />@permabullnino")
        self.add_slider(fig)

        #Write out html chart
        if model == 0:
            chart_name = '/blocksubsidy_pricing_btc'
        elif model ==1:
            chart_name = '/blocksubsidy_pricing_btc'
        self.write_html(fig,chart_name)

        return fig

    def commitment_usd(self,model):
        """Decred USD Stakeholder Commitment Models

        Block Subsidy model paid after @permabullnino
        Cumulative ticket value locked after @checkmatey
        Realised cap after @Coinmetrics

        INPUTS:
            model = 0   = Network Valuation (Market Cap, Realised Cap etc)
            model = 1   = Pricing Model (Coin price, realised price etc)
        """
        df = self.df
        df = dcr_add_metrics().metric_issued_cap(df)

        #STANDARD SETTINGS
        loop_data=[[0,1,2,3,4,5,6,7],[]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
        ]
        color_data = [
            'rgb(255, 255, 255)',   #White
            'rgb(239, 125, 50)',    #Price Orange
            'rgb(250, 38, 53)',     #POW Red
            'rgb(114, 49, 163)',    #POS Purple
            'rgb(255, 192, 0)',     #Treasury Yellow
            'rgb(20, 169, 233)',    #Total Blue
            'rgb(46, 214, 161)',    #Turquoise
            'rgb(156,225,143)',     #Turquoise Green
        ]
        #Invert Colors for Light Theme
        for i in [0,4,5,6,7]:
            a = [color_data[i]]
            color_data[i] = self.color_invert(a)[0]
        dash_data = ['solid','dash','solid','solid','solid','solid','solid','dash']
        width_data = [2,2,2,2,2,2,3,2]
        opacity_data = [1,1,1,1,1,1,1,1]
        legend_data = [True,True,True,True,True,True,True,True,]#
        autorange_data = [False,False,False]
        type_data = ['date','log','log']#

        #NETWORK VALUATION SETTINGS
        if model == 0:
            y_data = [
                df['CapMrktCurUSD'],
                df['CapRealUSD'],
                df['PoW_income_usd'].cumsum(),
                df['PoS_income_usd'].cumsum(),
                df['Fund_income_usd'].cumsum(),
                df['Total_income_usd'].cumsum(),
                df['tic_usd_cost'].cumsum(),
                df['IssuedCapUSD'],
            ]
            name_data = [
                'Market Cap',
                'Realised Cap',
                'POW-USD',
                'POS-USD',
                'Treasury-USD',
                'Total-USD',
                'Tickets Bound Cap',
                'Supply Issued Cap',
                ]
            title_data = [
                '<b>Decred Stakeholder Commitments Valuations (USD)</b>',
                '<b>Date</b>',
                '<b>Network Valuation</b>',
                '<b></b>']
            range_data = [[self.start,self.last],[self.cap_lb,self.cap_ub],[0,0]]

        #PRICING MODELS SETTINGS
        if model == 1:
            y_data = [
                df['PriceUSD'],
                df['PriceRealUSD'],
                df['PoW_income_usd'].cumsum()/df['SplyCur'],
                df['PoS_income_usd'].cumsum()/df['SplyCur'],
                df['Fund_income_usd'].cumsum()/df['SplyCur'],
                df['Total_income_usd'].cumsum()/df['SplyCur'],
                df['tic_usd_cost'].cumsum()/df['SplyCur'],
                df['IssuedPriceUSD'],
            ]
            name_data = [
                'DCR/USD Price',
                'Realised Price',
                'POW-USD',
                'POS-USD',
                'Treasury-USD',
                'Total-USD',
                'Tickets Bound Price',
                'Supply Issued Price'
                ]
            title_data = [
                '<b>Decred Stakeholder Commitments Pricing Models (USD)</b>',
                '<b>Date</b>',
                '<b>DCR/USD Pricing</b>',
                '<b></b>']
            range_data = [[self.start,self.last],[self.price_lb,self.price_ub],[0,0]]


        #BUILD FINAL CHART
        fig = self.chart.subplot_lines_singleaxis(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data
            )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)

        self.add_slider(fig)

        #Write out html chart
        if model == 0:
            chart_name = '/commitments_valuation_usd'
        elif model ==1:
            chart_name = '/commitments_pricing_usd'
        self.write_html(fig,chart_name)

        return fig

    def commitment_btc(self,model):
        """Decred BTC Stakeholder Commitment Models

        Block Subsidy model paid after @permabullnino
        Cumulative ticket value locked after @checkmatey
        Realised cap after @Coinmetrics
        
        INPUTS:
            model = 0   = Network Valuation (Market Cap, Realised Cap etc)
            model = 1   = Pricing Model (Coin price, realised price etc)
        """
        df = self.df
        df = dcr_add_metrics().metric_issued_cap(df)

        #STANDARD SETTINGS
        loop_data=[[0,1,2,3,4,5,6,7],[]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
        ]
        color_data = [
            'rgb(255, 255, 255)',   #White
            'rgb(239, 125, 50)',    #Price Orange
            'rgb(250, 38, 53)',     #POW Red
            'rgb(114, 49, 163)',    #POS Purple
            'rgb(255, 192, 0)',     #Treasury Yellow
            'rgb(20, 169, 233)',    #Total Blue
            'rgb(46, 214, 161)',    #Turquoise
            'rgb(156,225,143)',     #Turquoise Green
        ]
        #Invert Colors for Light Theme
        for i in [0,4,5,6,7]:
            a = [color_data[i]]
            color_data[i] = self.color_invert(a)[0]

        dash_data = ['solid','dash','solid','solid','solid','solid','solid','dash']
        width_data = [2,2,2,2,2,2,3,2]
        opacity_data = [1,1,1,1,1,1,1,1]
        legend_data = [True,True,True,True,True,True,True,True,]#
        autorange_data = [False,False,False]
        type_data = ['date','log','log']


        #NETWORK VALUATION SETTINGS
        if model == 0:
            y_data = [
                df['CapMrktCurBTC'],
                df['CapRealBTC'],
                df['PoW_income_btc'].cumsum(),
                df['PoS_income_btc'].cumsum(),
                df['Fund_income_btc'].cumsum(),
                df['Total_income_btc'].cumsum(),
                df['tic_btc_cost'].cumsum(),
                df['IssuedCapBTC'],
            ]
            name_data = [
                'Market Cap',
                'Realised Cap',
                'POW-BTC',
                'POS-BTC',
                'Treasury-BTC',
                'Total-BTC',
                'Tickets Bound Cap',
                'Supply Issued Cap'
                ]
            title_data = [
                '<b>Decred Stakeholder Commitments Valuations (BTC)</b>',
                '<b>Date</b>',
                '<b>Network Valuation</b>',
                '<b></b>']
            range_data = [[self.start,self.last],[self.cap_lb_btc,self.cap_ub_btc],[0,0]]
        #PRICING MODELS SETTINGS
        if model == 1:
            y_data = [
                df['PriceBTC'],
                df['PriceRealBTC'],
                df['PoW_income_btc'].cumsum()/df['SplyCur'],
                df['PoS_income_btc'].cumsum()/df['SplyCur'],
                df['Fund_income_btc'].cumsum()/df['SplyCur'],
                df['Total_income_btc'].cumsum()/df['SplyCur'],
                df['tic_btc_cost'].cumsum()/df['SplyCur'],
                df['IssuedPriceBTC']
            ]
            name_data = [
                'DCR/BTC Price',
                'Realised Price',
                'POW-BTC',
                'POS-BTC',
                'Treasury-BTC',
                'Total-BTC',
                'Tickets Bound Price',
                'Supply Issued Price',
                ]
            title_data = [
                '<b>Decred Stakeholder Commitments Pricing Models (BTC)</b>',
                '<b>Date</b>',
                '<b>DCR/BTC Pricing</b>',
                '<b></b>']
            range_data = [[self.start,self.last],[self.price_lb_btc,self.price_ub_btc],[0,0]]

        #BUILD FINAL CHART
        fig = self.chart.subplot_lines_singleaxis(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data
            )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)

        self.add_slider(fig)

        #Write out html chart
        if model == 0:
            chart_name = '/commitments_valuation_btc'
        elif model ==1:
            chart_name = '/commitments_pricing_btc'
        self.write_html(fig,chart_name)

        return fig

    def s2f_model(self,model):
        """Decred Stock to Flow Models

        Linear Regression for Price OR Market Cap after @checkmatey
        Stock to flow model by PlanB @100TrillionUSD for Bitcoin applied to DCR S2F for ref
        
        INPUTS:
            model = 0   = Network Valuation (Market Cap, Realised Cap etc)
            model = 1   = Pricing Model (Coin price, realised price etc)
        """
        df = self.df[['date','age_sply','S2F','PriceUSD','SplyCur','CapMrktCurUSD']]
        analysis   = dcr_add_metrics().metric_s2f_model(df)
        df      = analysis[0]
        const   = analysis[1].params['const']
        s2f     = analysis[1].params['S2F']

        #calculate projected supply curve
        df_sply = dcr_add_metrics().dcr_sply_curtailed(2000000)
        #   age_day assuming blocktime of 5mins
        #   calculate date from genesis
        df_sply['age_day'] = df_sply['blk']*5/(60*24)
        df_sply['date'] = (
            pd.to_datetime('2016-02-08 20:32:25+00:00',utc=True) 
            + df_sply['age_day'].apply(timedelta)
        )
        
        """Calculate projects S2F model from regression"""
        df_sply['S2F_Cap_ideal']       = (np.exp(
            const 
            + s2f 
            * np.log(df_sply['S2F_ideal'])
        ))
        df_sply['S2F_Price_ideal']     = (
            df_sply['S2F_Cap_ideal'] / df_sply['Sply_ideal']
        )

        """Calculate Plan B model projection"""
        df_sply['S2F_Price_ideal_PB']  = np.exp(-1.84)*df_sply['S2F_ideal']**3.36
        df_sply['S2F_Cap_ideal_PB']    = (
            df_sply['S2F_Price_ideal_PB'] 
            * df_sply['Sply_ideal']
        )

        last = pd.to_datetime(df_sply['date'].iloc[-1])

        #STANDARD SETTINGS
        loop_data=[[0,1,2],[5,7,8,9,10,11,12]]
        x_data = [
            df['date'], #Price
            df['date'], #CM S2F Model
            df_sply['date'],
            df['date'], #PB S2F Model
            df_sply['date'],
            #Secondary
            df['date'], #CM Multiple
            df['date'], #PB Multiple
            [self.start,last],    #N/A CEILING
            [self.start,last],    #STRONG SELL
            [self.start,last],    #SELL
            [self.start,last],    #NORMAL
            [self.start,last],    #BUY
            [self.start,last],    #BUY
        ]
        width_data      = [2,0.5,2,0.5,2,    1,0.5,   2,2,2,2,2,2]
        opacity_data    = [1,1,0.6,0.45,0.6,  1,0.45,  1,1,1,1,1,1]
        dash_data = ['solid','dot','dash','dot','dash','solid','solid','dash','dash','dash','dash','dash','dash']
        color_data = [
            'rgb(255,255,255)',     #White
            'rgb(46, 214, 161)',    #Turquoise
            'rgb(46, 214, 161)',    #Turquoise
            'rgb(239, 125, 50)',    #Price Orange
            'rgb(239, 125, 50)',    #Price Orange
            'rgb(46, 214, 161)',    #Turquoise
            'rgb(239, 125, 50)',    #Price Orange
            'rgba(255, 80, 80, 0.2)',     #Gradient Red
            'rgba(255, 80, 80, 0.2)',     #Gradient Red
            'rgba(255, 80, 80, 0.1)',     #Gradient Red
            'rgba(55 ,55, 55, 0)',        #NA
            'rgba(36, 255, 136, 0.1)',    #Gradient Green
            'rgba(36, 255, 136, 0.2)',    #Gradient Green
        ]
        #Invert Colors for Light Theme
        for i in [0,1,2,3,4,5,6]:
            color_data[i] = self.color_invert([color_data[i]])[0]
        fill_data = [
            'none','none','none','none','none','none','none',
            'none','tonexty','tonexty','none','tonexty','tozeroy',
        ]
        legend_data = [True,True,True,True,True,True,True,True,True,False,True,True,False,True,True]
        autorange_data = [False,False,False]
        type_data = ['date','log','log']

        #NETWORK VALUATION SETTINGS
        if model == 0:
            y_data = [
                df['CapMrktCurUSD'],
                df['S2F_CapMr_predict'],
                df_sply['S2F_Cap_ideal'],
                df['S2F_CapMr_predict_PB'],
                df_sply['S2F_Cap_ideal_PB'],
                #Secondary
                df['S2F_CapMr_multiple'],
                df['S2F_Price_multiple_PB'],
                [15,15],
                [8,8],
                [3,3],
                [0.3,0.3],
                [0.1,0.1],
                [0.1,0.1],
            ]
            name_data = [
                'Market Cap (USD)',
                'S2F Model (Checkmate)',
                'S2F Model Projected',
                'S2F Model (Plan B)',
                'S2F Model (Plan B, Projected)',
                'S2F Multiple (Checkmate)',
                'S2F Multiple (Plan B)',
                'na',
                'STRONG SELL (8.0)',
                'SELL (3.0)',
                'na',
                'BUY (0.4)',
                'STRONG BUY (0.1)',
            ]
            title_data = [
                '<b>Decred Stock-to-Flow Network Valuation (USD)</b>',
                '<b>Date</b>',
                '<b>Network Valuation (USD)</b>',
                '<b>S2F Multiple</b>']
            range_data = [[self.start,self.last],[self.cap_lb,self.cap_ub],[np.log10(0.05),7]]
        
        elif model == 1:
            y_data = [
                df['PriceUSD'],
                df['S2F_Price_predict'],
                df_sply['S2F_Price_ideal'],
                df['S2F_Price_predict_PB'],
                df_sply['S2F_Price_ideal_PB'],
                #Secondary
                df['S2F_CapMr_multiple'],
                df['S2F_Price_multiple_PB'],
                [15,15],
                [8,8],
                [3,3],
                [0.3,0.3],
                [0.1,0.1],
                [0.1,0.1],
            ]
            name_data = [
                'DCR Price (USD)',
                'S2F Model (Checkmate)',
                'S2F Model Projected',
                'S2F Model (Plan B)',
                'S2F Model (Plan B, Projected)',
                'S2F Multiple (Checkmate)',
                'S2F Multiple (Plan B)',
                'na',
                'STRONG SELL (8.0)',
                'SELL (3.0)',
                'na',
                'BUY (0.4)',
                'STRONG BUY (0.1)',
            ]
            title_data = [
                '<b>Decred Stock-to-Flow Price Model (USD)</b>',
                '<b>Date</b>',
                '<b>Price (USD)</b>',
                '<b>S2F Multiple</b>']
            range_data = [[self.start,self.last],[self.price_lb,self.price_ub],[np.log10(0.05),7]]
        
        
        fig = self.chart.subplot_lines_doubleaxis_2nd_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_xaxes(dtick='M12',tickformat='%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        fig.update_yaxes(showgrid=False,secondary_y=True)
        self.add_slider(fig)

        #Write out html chart
        if model == 0:
            chart_name = '/s2fmodel_valuation_usd'
        elif model ==1:
            chart_name = '/s2fmodel_pricing_usd'
        self.write_html(fig,chart_name)

        return fig

    def s2f_model_residuals(self):
        """Decred Stock to Flow Models - Residuals

        Shows the distance Price or Market Cap have moved away from the mean
        """
        #Run Decred Analysis
        df = self.df[['date','age_sply','S2F','PriceUSD','SplyCur','CapMrktCurUSD']]
        df = dcr_add_metrics().metric_s2f_model(df)[0]

        #Run OLS Linear Regression for Bitcoin dataset
        df2 = btc_add_metrics().btc_coin()
        df2 = df2[['date','age_sply','S2F','PriceUSD','SplyCur','CapMrktCurUSD']]
        df2['CapMrktCurUSD'] = df2['PriceUSD'] * df2['SplyCur']
        df2 = df2.dropna(axis=0)
        df2 = regression_analysis().ln_regression_OLS(df2,'S2F','CapMrktCurUSD',True)['df']
        
        #Add Bitcoin Halvings
        df3 = btc_add_metrics().btc_sply_halvings_step()
        df3 = df3[:10]
        df3['y_arb'].replace(to_replace=0,value=-10,inplace=True)
        df3['y_arb'].replace(to_replace=1e20,value=10,inplace=True)
        
        #STANDARD SETTINGS
        loop_data=[[3,4,5,6],[0,1,2]]
        x_data = [
            df['age_sply'],     #DCR Price
            df2['age_sply'],    #BTC Price
            df3['age_sply'],    #Halvings
            [0,1],    # Arbitrary Ceiling for Sell Fill
            [0,1],    # BUY
            [0,1],    # Arbitrary Ceiling for Sell Fill
            [0,1],    # SELL
        ]
        y_data = [
            df['S2F_CapMr_residual'].rolling(14).mean(),
            df2['S2F_CapMr_residual'].rolling(14).mean(),
            df3['y_arb'],
            [-10,-10],
            [-1.5,-1.5],
            [10,10],
            [1.5,1.5],
        ]
        name_data = [
            'Decred S2F Residuals',
            'Bitcoin S2F Residuals',
            'Bitcoin Halvings',
            'N/A',
            'BUY ZONE (-1.5 stdev)',
            'N/A',
            'SELL ZONE (+1.5 stdev)',
        ]
        title_data = [
            '<b>Decred Stock-to-Flow Model Residuals</b>',
            '<b>Coin Age (% of 21M Supply Mined)</b>',
            '<b>Standard Deviations from Mean</b>',
            '<b></b>'
        ]
        width_data      = [4,1.5,1,  2,2,2,2]
        opacity_data    = [1,0.75,1,  0.25,0.25,0.25,0.25]
        fill_data       = ['none','none','none','none','tonexty','none','tonexty',]
        dash_data = ['solid','solid','dash','dash','dash','dash','dash']
        color_data = [
            'rgb(46, 214, 161)',    #Turquoise
            'rgb(239, 125, 50)',    #Price Orange
            'rgb(255, 255, 255)',    #White
            'rgb(50, 50, 50)',    #Background
            'rgba(153, 255, 102,0.25)',   #Gradient Green
            'rgb(50, 50, 50)',    #Background
            'rgba(255, 80, 80,0.25)',     #Gradient Red
        ]
        #Invert Colors for Light Theme
        color_data = self.color_invert(color_data)
        legend_data = [True,True,True,False,True,False,True]
        autorange_data = [False,False,False]
        type_data = ['linear','linear','linear']
        range_data = [[0,1],[-4,4],[-4,4]]      
        fig = self.chart.subplot_lines_doubleaxis_1st_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_xaxes(dtick='0.1',tickformat='%d-%b-%y',showgrid=True)
        fig.update_yaxes(showgrid=True,secondary_y=False)
        fig.update_yaxes(showgrid=False,secondary_y=True)
        self.add_slider(fig)

        #Write out html chart
        chart_name = '/s2fresiduals_oscillator_usd'
        self.write_html(fig,chart_name)

        return fig

    def mayer_multiple(self):
        """"Mayer Multiple Bands"""
        df = self.df
        df = dcr_add_metrics().metric_mayer_multiple(df)

        df['Mayer_SBUY']    = df['200DMA'] * 0.4
        df['Mayer_BUY']     = df['200DMA'] * 0.6
        df['Mayer_SELL']    = df['200DMA'] * 2.0
        df['Mayer_SSELL']   = df['200DMA'] * 2.8

        loop_data=[[0,1,3,4,5,6],[7,8,9,10,11,12,13,14]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            #Secondary
            [self.start,self.last],    #N/A CEILING
            [self.start,self.last],    #STRONG SELL
            [self.start,self.last],    #SELL
            [self.start,self.last],    #NORMAL
            [self.start,self.last],    #BUY
            [self.start,self.last],    #BUY
            [self.start,self.last],    #UNITY
            df['date'],
        ]
        y_data = [
            df['PriceUSD'],
            df['200DMA'],
            df['128DMA'],
            df['Mayer_SBUY'],
            df['Mayer_BUY'] ,
            df['Mayer_SELL'], 
            df['Mayer_SSELL'],
            # SECONDARY
            [6,6],
            [2.8,2.8],
            [2.0,2.0],
            [0.6,0.6],
            [0.4,0.4],
            [0.4,0.4],
            [1.0,1.0],
            df['Mayer_Multiple'],
        ]
        name_data = [
            'DCR Price (USD)',
            '200DMA',
            '128DMA',
            'STRONG BUY (0.4)',
            'BUY (0.6)',
            'SELL (2.0)',
            'STRONG SELL (2.8)',
            #SECONDARY
            'N/A',
            'STRONG SELL (2.8)',
            'SELL (2.0)',
            'N/A',
            'BUY (0.6)',
            'STRONG BUY (0.4)',
            'Unity',
            'Mayer Multiple',
        ]
        width_data      = [
            2,2,2,   1,1,1,1,
            1,1,1,1,1,1,1,2
            ]
        opacity_data    = [
            1,1,1,   1,1,1,1,
            1,1,1,1,1,1,1,1
            ]
        dash_data = [
            'solid','solid','solid',
            'dash','dash','dash','dash',
            'dash','dash','dash','dash','dash','dash','dash','solid',
            ]
        color_data = [
            'rgb(255, 255, 255)',        #White
            'rgb(102, 255, 153)',        #Turquoise Green
            'rgb(237, 109, 71)',         #Decred Orange
            'rgb(153, 255, 102)',        #Gradient Green
            'rgb(255, 204, 102)',        #Gradient Yellow
            'rgb(255, 153, 102)',        #Gradient Orange
            'rgb(255, 80, 80)',          #Gradient Red
            # SECONDARY
            'rgba(255, 80, 80, 0.2)',    #Gradient Red
            'rgba(255, 80, 80, 0.2)',    #Gradient Red
            'rgba(255, 80, 80, 0.1)',    #Gradient Red
            'rgba(55 ,55, 55, 0)',       #NA
            'rgba(36, 255, 136, 0.1)',   #Gradient Green
            'rgba(36, 255, 136, 0.2)',   #Gradient Green
            'rgb(20, 169, 233)',         #Total Blue
            'rgb(102, 255, 153)',        #Turquoise Green
        ]
        #Invert Colors for Light Theme
        for i in [0,1,2,3,4,5,6,13,14]:
            color_data[i] = self.color_invert([color_data[i]])[0]
        fill_data = [
            'none','none','none','none','none','none','none',
            'none','tonexty','tonexty','none','tonexty','tozeroy','none','none',
        ]
        legend_data = [
            True,True,True,True,True,True,True,
            False,False,False,False,False,False,False,True,
            ]
        title_data = [
            '<b>Decred Mayer Multiple Bands</b>',
            '<b>Date</b>',
            '<b>Price (USD)</b>',
            '<b>Mayer Multiple</b>']
        range_data = [[self.start,self.last],[-2,3],[np.log10(0.2),5]]
        autorange_data = [False,False,False]
        type_data = ['date','log','log']
        fig = self.chart.subplot_lines_doubleaxis_2nd_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_xaxes(dtick='M3',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        self.add_slider(fig)

        #Write out html chart
        chart_name = '/mayermultiple_pricing_usd'
        # self.write_html(fig,chart_name)

        return fig

    def puell_multiple(self):
        """"Puell Multiple"""
        df = self.df
        df = dcr_add_metrics().metric_puell_multiple(df)

        loop_data=[[0,1,2,3,4],[5,6,7,8,9,10,11,12]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            #Secondary
            df['date'],
            [self.start,self.last],    #N/A CEILING
            [self.start,self.last],    #STRONG SELL
            [self.start,self.last],    #SELL
            [self.start,self.last],    #NORMAL
            [self.start,self.last],    #BUY
            [self.start,self.last],    #BUY
            [self.start,self.last],    #UNITY
        ]
        y_data = [
            df['Puell_income_pos'], #positive, black
            df['Puell_income'],     #NA fill from MA to pos (green)
            df['Puell_income_neg'], #negative, black
            df['Puell_income'],     #NA fill from MA to neg (red)
            df['Puell_income'],     #Blue Plot MA
            #Secondary
            df['Puell_Multiple'],
            [10,10],
            [5,5],
            [2.5,2.5],
            [0.6,0.6],            
            [0.4,0.4],
            [0.4,0.4],
            [1.0,1.0],
        ]
        name_data = [
            'Daily PoW Block Reward',
            'NA','NA','NA',
            '365-day MA',
            #Secondary
            'Puell Multiple',
            'N/A',
            'Extreme Miner Profit (2.8)',
            'Miner Profit (2.0)',
            'N/A',
            'Miner Stress (0.6)',
            'Extreme Miner Stress (0.4)',
            'Unity'
        ]
        width_data      = [
            2,0,2,0,2,
            1,1,2,1,1,1,1,1
            ]
        opacity_data    = [
            1,1,1,1,1,
            1,1,1,1,1,1,1,1
            ]
        dash_data = [
            'solid','solid','solid','solid','solid',
            'solid','dash','dash','dash','dash','dash','dash','dash'
            ]
        color_data = [
            'rgb(255, 255, 255)',         #White
            'rgba(36, 255, 136, 0.3)',    #Gradient Green
            'rgb(255, 255, 255)',         #White
            'rgba(255, 80, 80, 0.3)',     #Gradient Red
            'rgb(237, 109, 71)',          #Decred Orange
            #Secondary
            'rgb(46, 214, 161)',          #Turquoise
            'rgba(255, 80, 80, 0.2)',     #Gradient Red
            'rgba(255, 80, 80, 0.2)',     #Gradient Red
            'rgba(255, 80, 80, 0.1)',     #Gradient Red
            'rgba(55 ,55, 55, 0)',        #NA
            'rgba(36, 255, 136, 0.1)',    #Gradient Green
            'rgba(36, 255, 136, 0.2)',    #Gradient Green
            'rgb(20, 169, 233)',          #Total Blue
        ]
        #Invert Colors for Light Theme
        for i in [0,2,4,5]:
            color_data[i] = self.color_invert([color_data[i]])[0]
        fill_data = [
            'none','tonexty','none','tonexty','none',
            'none','none','tonexty','tonexty','none','tonexty','tozeroy','none'
        ]
        legend_data = [
            True,False,False,False,True,
            True,False,True,True,False,True,True,False
            ]
        title_data = [
            '<b>Decred Puell Multiple</b>',
            '<b>Date</b>',
            '<b>Daily PoW Block Reward (USD)</b>',
            '<b>Puell Multiple</b>']
        range_data = [[self.start,self.last],[2,6],[np.log10(0.2),6]]
        autorange_data = [False,False,False]
        type_data = ['date','log','log']
        fig = self.chart.subplot_lines_doubleaxis_both_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        self.add_slider(fig)

        #Write out html chart
        chart_name = '/puellmultiple_oscillator_usd'
        self.write_html(fig,chart_name)

        return fig

    def contractor_multiple(self):
        """"Contractor Multiple"""
        df = self.df
        df = dcr_add_metrics().metric_contractor_multiple(df)

        loop_data=[[0,1],[2,3,4,5]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            [self.start,self.last],    #NA
            [self.start,self.last],    #BUY
            [self.start,self.last],    #SELL
        ]
        y_data = [
            df['PriceUSD'],
            df['PriceUSD'].rolling(30).mean(),
            df['Contractor_Multiple'],
            [3.0,3.0],
            [1.7,1.7],
            [0.6,0.6],
        ]
        name_data = [
            'DCR Price (USD)',
            'DCR Price 30DMA (USD)',
            'Contractor_Multiple',
            'N/A',
            'BUY (0.6)',
            'SELL (1.7)'
        ]
        width_data      = [2,2,1,   1,2,2]
        opacity_data    = [1,1,1,   1,1,1]
        dash_data = ['solid','dot','solid','solid','dash','dash']
        color_data = [
            'rgb(255, 255, 255)',   #White
            'rgb(46, 214, 161)',    #Turquoise
            'rgb(46, 214, 161)',    #Turquoise
            'rgba(255,255,255,0)',   #NA
            'rgba(153, 255, 102,0.2)',   #Gradient Green
            'rgba(255, 80, 80,0.2)',     #Gradient Red
        ]
        fill_data = ['none','none','none',   'none','tonexty','tozeroy']
        #Invert Colors for Light Theme
        color_data = self.color_invert(color_data)
        legend_data = [True,True,True,False,True,True]
        title_data = [
            '<b>Decred Contractor Multiple</b>',
            '<b>Date</b>',
            '<b>Price (USD)</b>',
            '<b>Contractor Multiple</b>']
        range_data = [[self.start,self.last],[-1,3],[-0.6931471805599453,3]]
        autorange_data = [False,False,False]
        type_data = ['date','log','log']
        fig = self.chart.subplot_lines_doubleaxis_2nd_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        self.add_slider(fig)

        #Write out html chart
        chart_name = '/contractormultiple_oscillator_usd'
        self.write_html(fig,chart_name)

        return fig

    def beam_indicator(self):
        """"BEAM Indicator (Bitcoin Economics Adaptive Multiple) 
        after https://bitcoineconomics.io/beam.html"""
        df = self.df
        df = dcr_add_metrics().metric_beam_indicator(df)

        loop_data=[[0,1,2],[3,4,5,6,7,8,9]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            [self.start,self.last],    #N/A CEILING
            [self.start,self.last],    #STRONG SELL
            [self.start,self.last],    #SELL
            [self.start,self.last],    #NORMAL
            [self.start,self.last],    #BUY
            [self.start,self.last],    #BUY
        ]
        y_data = [
            df['PriceUSD'],
            df['BEAM_lower'],
            df['BEAM_upper'],
            df['BEAM'],
            [3.5,3.5],
            [2.5,2.5],
            [2.0,2.0],
            [0.5,0.5],
            [0.05,0.05],
            [-2,-2],
        ]
        name_data = [
            'BTC Price (USD)',
            'BEAM Lower Band',
            'BEAM Upper Band',
            'BEAM Indicator',
            'N/A',
            'STRONG SELL (2.6)',
            'SELL (1.0)',
            'N/A',
            'BUY (0.5)',
            'STRONG BUY (0.05)',
        ]
        width_data      = [2,2,2,1,1,1,1,1,1,1]
        opacity_data    = [1,1,1,1,1,1,1,1,1,1]
        dash_data = ['solid','solid','solid','solid','dash','dash','dash','dash','dash','dash']
        color_data = [
            'rgb(255, 255, 255)',   #White
            'rgb(153, 255, 102)',   #Gradient Green
            'rgb(255, 80, 80)',     #Gradient Red
            'rgb(46, 214, 161)',    #Turquoise
            'rgba(255, 80, 80, 0.2)',     #Gradient Red
            'rgba(255, 80, 80, 0.2)',     #Gradient Red
            'rgba(255, 80, 80, 0.1)',     #Gradient Red
            'rgba(55 ,55, 55, 0)',        #NA
            'rgba(36, 255, 136, 0.1)',    #Gradient Green
            'rgba(36, 255, 136, 0.2)',    #Gradient Green
        ]
        #Invert Colors for Light Theme
        color_data = self.color_invert(color_data)
        fill_data = [
            'none','none','none','none','none','tonexty','tonexty','none','tonexty','tonexty'
        ]
        legend_data = [True,True,True,True,False,True,True,False,True,True]
        title_data = [
            '<b>Decred BEAM Indicator<b>',
            '<b>Date</b>',
            '<b>Price (USD)</b>',
            '<b>BEAM Indicator</b>']
        range_data = [[self.start,self.last],[-1,3],[-1,10]]
        autorange_data = [False,False,False]
        type_data = ['date','log','linear']
        fig = self.chart.subplot_lines_doubleaxis_2nd_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        fig.update_yaxes(showgrid=False,secondary_y=True,dtick=0.5)
        self.add_slider(fig)

        #Write out html chart
        chart_name = '/beamindicator_pricing_usd'
        self.write_html(fig,chart_name)

        return fig

    def bottom_cycle(self):
        """"Price Growth over Days since capitulation for each cycle"""
        df = self.df
        #Filter events to market capitulation event
        df2 = self.events[self.events['event']=='btm']
        #Merge events onto df, fill backwards
        df = pd.merge(
            df,df2,
            how='left',
            left_on='date',
            right_on='date_event'
        )
        #Fill forwards for all event data
        #print(df.columns)
        df[['date_event','epoch','event','PriceUSD_event']] = (
            df[['date_event','epoch','event','PriceUSD_event']].fillna(method='ffill')
        )
        
        #Calculate days since event
        df['days_since_event'] = (df['date'] - df['date_event']) / np.timedelta64(1, 'D')
        #Calculate drawdown since event
        df['event_delta'] = df['PriceUSD']/df['PriceUSD_event']

        loop_data=[[0,1,2,3],[]]
        x_data = [
            df[df['epoch']==0]['days_since_event'],
            df[df['epoch']==1]['days_since_event'],
            df[df['epoch']==2]['days_since_event'],
            df[df['epoch']==3]['days_since_event'],
        ]
        y_data = [
            df[df['epoch']==0]['event_delta'],
            df[df['epoch']==1]['event_delta'],
            df[df['epoch']==2]['event_delta'],
            df[df['epoch']==3]['event_delta'],
        ]
        name_data = [
            'Epoch 1 (Genesis-2016)',
            'Epoch 2 (2016-2020)',
            'Epoch 3 (X)',
            'Epoch 4 (X)',
        ]
        width_data      = [2,2,2,2]
        opacity_data    = [1,1,1,1]
        dash_data = ['solid','solid','solid','solid',]
        color_data = [
            'rgb(46, 214, 161)',    #Turquoise
            'rgb(78,205,233)',      #Total Blue
            'rgb(255, 80, 80)',      #Gradient Red
            'rgb(153, 255, 102)',      #Gradient Green
        ]
        #Invert Colors for Light Theme
        color_data = self.color_invert(color_data)
        legend_data = [True,True,True,True,]
        title_data = [
            '<b>Decred Price Growth Since Cycle Low</b>',
            '<b>Days Since Capitulation</b>',
            '<b>Growth Multiple Since Low</b>',
            '<b></b>']
        range_data = [[0,1500],[0,3],[-1,2]]
        autorange_data = [False,False,False]
        type_data = ['linear','log','log']
        fig = self.chart.subplot_lines_singleaxis(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data
            )
        fig.update_xaxes(dtick=30)
        fig.update_yaxes(showgrid=True,secondary_y=False)
        #fig.update_yaxes(tickformat='.0%')
        self.add_slider(fig)

        #Write out html chart
        chart_name = '/cyclebtm_usd'
        self.write_html(fig,chart_name)

        return fig
    
    def top_cycle(self):
        """"Price Drawdown over since market top for each cycle"""
        df = self.df
        #Filter events to market top event
        df2 = self.events[self.events['event']=='top']
        #Merge events onto df, fill forwards
        df = pd.merge(
            df,df2,
            how='left',
            left_on='date',
            right_on='date_event'
        )
        #Fill forwards for all event data
        df[['date_event','epoch','event','PriceUSD_event']] = (
            df[['date_event','epoch','event','PriceUSD_event']].fillna(method='ffill')
        )
        #print(df.columns)
        #Calculate days since event
        df['days_since_event'] = (df['date'] - df['date_event']) / np.timedelta64(1, 'D')
        #Calculate drawdown since event
        df['event_delta'] = df['PriceUSD']/df['PriceUSD_event']

        loop_data=[[0,1,2,3],[]]
        x_data = [
            df[df['epoch']==0]['days_since_event'],
            df[df['epoch']==1]['days_since_event'],
            df[df['epoch']==2]['days_since_event'],
            df[df['epoch']==3]['days_since_event'],
        ]
        y_data = [
            df[df['epoch']==0]['event_delta'],
            df[df['epoch']==1]['event_delta'],
            df[df['epoch']==2]['event_delta'],
            df[df['epoch']==3]['event_delta'],
        ]
        name_data = [
            'Epoch 1 (2018-20)',
            'Epoch 2 (X)',
            'Epoch 3 (X)',
            'Epoch 4 (X)',
        ]
        width_data      = [2,2,2,2]
        opacity_data    = [1,1,1,1]
        dash_data = ['solid','solid','solid','solid',]
        color_data = [
            'rgb(46, 214, 161)',    #Turquoise
            'rgb(78,205,233)',      #Total Blue
            'rgb(255, 80, 80)',      #Gradient Red
            'rgb(153, 255, 102)',      #Gradient Green
        ]
        #Invert Colors for Light Theme
        color_data = self.color_invert(color_data)
        legend_data = [True,True,True,True,]
        title_data = [
            '<b>Decred Drawdown Since Market Top</b>',
            '<b>Days Since Market Top</b>',
            '<b>Drawdown Since Top</b>',
            '<b></b>']
        range_data = [[0,1500],[-1.301029996,0],[-1,2]]
        autorange_data = [False,False,False]
        type_data = ['linear','log','log']
        fig = self.chart.subplot_lines_singleaxis(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data
            )
        fig.update_xaxes(dtick=30)
        fig.update_yaxes(showgrid=True,secondary_y=False)
        #fig.update_yaxes(tickformat='.0%')
        self.add_slider(fig)

        #Write out html chart
        chart_name = '/cycletop_usd'
        self.write_html(fig,chart_name)

        return fig

    def nvt_rvt(self,mode):
        """"Bitcoin NVT and RVT Ratio
            mode: 0 = TxTfrValUSD
            mode: 1 = TxTfrValAdjUSD
        """
        df = pd.DataFrame()
        df = self.df
        df = dcr_add_metrics().metric_nvt_rvt(df,mode)

        loop_data=[[0,1],[2,3,4,5,6,7,   8,9,10,11,12]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            [self.start,self.last],    #N/A CEILING
            [self.start,self.last],    #SELL
            [self.start,self.last],    #NORMAL 1
            [self.start,self.last],    #NORMAL 2
            [self.start,self.last],    #BUY
        ]
        y_data = [
            df['CapMrktCurUSD'],
            df['CapRealUSD'],
            df['NVT_28'],
            df['NVT_90'],
            df['NVTS'],
            df['RVT_28'],
            df['RVT_90'],
            df['RVTS'],
            [250,250],
            [175,175],
            [100,100],
            [50,50],
            [50,50]
        ]
        if mode == 0:
            for i in [8,9,10,11,12]:
                y_data[i] = [x / 5 for x in y_data[i]]

        name_data = [
            'Market Cap (USD)',
            'Realised Cap (USD)',
            'NVT 28DMA',
            'NVT 90DMA',
            'NVTS',
            'RVT 28DMA',
            'RVT 90DMA',
            'RVTS',
            'N/A','N/A','N/A','N/A','N/A',
        ]
        width_data      = [2,2,1,1,1,1,1,1,1,1,1,1,1]
        opacity_data    = [1,1,1,1,1,1,1,1,0,0,0,0,0]
        dash_data = [
            'solid','solid','dot','dash','solid','dot','dash','solid',
            'solid','solid','solid','solid','solid'
            ]
        color_data = [
            'rgb(255, 255, 255)',    #White
            'rgb(239, 125, 50)',    #Price Orange
            'rgb(153, 255, 102)',
            'rgb(255, 255, 102)',
            'rgb(255, 204, 102)',
            'rgb(255, 153, 102)',
            'rgb(255, 102, 102)',
            'rgb(255, 80, 80)',
            'rgb(55,55,55)',              #N/A
            'rgba(255, 80, 80, 0.2)',     #Gradient Red
            'rgba(255, 153, 102, 0.0)',   #Gradient Orange
            'rgba(255, 204, 102, 0.0)',   #Gradient Yellow
            'rgba(36, 255, 136, 0.2)',    #Gradient Green
        ]
        #Invert Colors for Light Theme
        for i in [0,1,2,3,4,5,6,7,8]:
            color_data[i] = self.color_invert([color_data[i]])[0]
        legend_data = [
            True,True,True,True,True,True,True,True,
            False,False,False,False,False,
            ]
        fill_data = [
            'none','none','none','none','none','none','none','none',
            'none','tonexty','tonexty','tonexty','tozeroy',
            ]
        title_data = [
            '<b>Decred NVT and RVT Ratio</b>',
            '<b>Date</b>',
            '<b>Network Valuation (USD)</b>',
            '<b>NVT or RVT Ratio</b>']
        range_data = [[self.start,self.last],[5,10],[0,750]]
        autorange_data = [False,False,False]
        type_data = ['date','log','linear']
        fig = self.chart.subplot_lines_doubleaxis_2nd_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        fig.update_yaxes(showgrid=False,secondary_y=True,dtick=50)
        self.add_slider(fig)

        #Write out html chart
        chart_name = '/nvtrvt_oscillator_usd'
        self.write_html(fig,chart_name)

        return fig

    def TVWAP(self):
        """
        #############################################################################
                            REALISED CAP + 142DAY CAP
        #############################################################################
        """
        df = self.df
        df = dcr_add_metrics().metric_TVWAP(df)

        loop_data=[[0,1,2,3,4],[5,6,7,   8,9,10,11,12]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            #Ratios
            df['date'],
            df['date'],
            df['date'],

            [self.start,self.last],    #N/A CEILING
            [self.start,self.last],    #SELL
            [self.start,self.last],    #NORMAL 1
            [self.start,self.last],    #NORMAL 2
            [self.start,self.last],    #BUY
        ]
        y_data = [
            df['PriceUSD'],
            df['PriceRealUSD'],
            df['14day_TVWAP'],
            df['28day_TVWAP'],
            df['142day_TVWAP'],
            #Ratios
            df['14day_TVWAP_Ratio'],
            df['28day_TVWAP_Ratio'],
            df['142day_TVWAP_Ratio'],

            [2.00,2.00],    #NA Ceiling
            [1.20,1.20],    #SELL (above)
            [0.90,0.90],    #Normal 2 (above)
            [0.65,0.65],    #Normal 1 (above)
            [0.65,0.65],    #BUY (below)
        ]
        name_data = [
            'DCR/USD Price',
            'Realised Price',
            '14-Day TVWAP',
            '28-Day TVWAP',
            '142-Day TVWAP',
            #Ratios
            '14 Day Ratio',
            '28 Day Ratio',
            '142 Day Ratio',
            'N/A','N/A','N/A','N/A','N/A',
            ]
        color_data = [
            'rgb(255, 255, 255)',   #White
            'rgb(17, 255, 125)',    #Powerpoint Green
            'rgb(255, 192, 0)',     #Treasury Yellow
            'rgb(250, 38, 53)',     #POW Red
            'rgb(20, 169, 233)',    #Total Blue
            #Ratios
            'rgb(255, 192, 0)',     #Treasury Yellow
            'rgb(250, 38, 53)',     #POW Red
            'rgb(20, 169, 233)',    #Total Blue
            
            'rgba(255, 80, 80, 0.2)',     #Gradient Red
            'rgba(255, 80, 80, 0.2)',     #Gradient Red
            'rgba(255, 204, 102, 0.2)',   #Gradient Yellow
            'rgba(255, 204, 102, 0.2)',   #Gradient Yellow
            'rgba(36, 255, 136, 0.2)',    #Gradient Green
        ]
        #Invert Colors for Light Theme
        color_data = self.color_invert(color_data)
        dash_data = ['solid','solid','solid','solid','solid',   'solid','solid','solid'     ,'dash','dash','dash','dash','dash','dash']
        fill_data = ['none','none','none','none','none',         'none','none','none'       ,'none','tonexty','tonexty','tonexty','tozeroy']
        width_data = [2,2,1,1,2,  1,1,1,   2,2,2,2,2]
        opacity_data = [1,1,1,1,1,   1,1,1,   0,0.75,0.75,0.75,0.75]
        legend_data = [True,True,True,True,True,     True,True,True,     False,False,False,False,False,]#
        title_data = [
            '<b>Decred Ticket Volume Weighted Average Price (TVWAP)</b>',
            '<b>Date</b>',
            '<b>DCR/USD Price</b>',
            '<b>TVWAP Ratios</b>']
        range_data = [[self.start,self.last],[-2,3],[0,5]]
        autorange_data = [False,False,False]
        type_data = ['date','log','linear']#
        fig = self.chart.subplot_lines_doubleaxis_2nd_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        fig = self.chart.add_annotation(fig,"@checkmatey<br />@permabullnino")
        self.add_slider(fig)

        #Write out html chart
        chart_name = '/tvwap_valuation_usd'
        self.write_html(fig,chart_name)

        return fig

    def hodler_conversion(self):
        """"Decred Hodler Conversion Rates
            after @permabullnino"""
        df = self.df
        df = dcr_add_metrics().metric_hodler_conversion(df)

        #CHART
        loop_data=[[0,1,2],[3,4]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
        ]
        y_data = [
            df['PriceUSD'],
            df['PriceRealUSD'],
            df['142day_TVWAP'],
            df['hconv142d_pos'],
            df['hconv142d_neg'],
        ]
        name_data = [
            'DCR Price (USD)',
            'Realised Price (USD)',
            '142-Day TVWAP',
            'Hodler Conversion Rate +ve',
            'Hodler Conversion Rate -ve',
        ]
        fill_data = ['','','','tozeroy','tozeroy']
        width_data      = [2,2,2,2,2]
        opacity_data    = [1,1,1,1,1]
        dash_data = ['solid','solid','solid','solid','solid',]
        color_data = [
            'rgb(255,  255,  255)',        #White
            'rgb(17,   255,  125)',        #Powerpoint Green
            'rgb(20,   169,  233)',        #Total Blue
            'rgba(255, 80,   80, 0.7)',    #Gradient Red
            'rgba(153, 255,  102, 0.7)',   #Gradient Green
        ]
        #Invert Colors for Light Theme
        for i in [0,1,2,3,4]:
            color_data[i] = self.color_invert([color_data[i]])[0]

        legend_data = [True,True,True,True,True,]
        title_data = [
            '<b>Decred HODLer Converstion Rate</b>',
            '<b>Date</b>',
            '<b>Price (USD)</b>',
            '<b>HODLer Conversion Rate</b>']
        range_data = [[self.start,self.last],[-2,3],[-0.5,1.5]]
        autorange_data = [False,False,False]
        type_data = ['date','log','linear']
        fig = self.chart.subplot_lines_doubleaxis_2nd_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        fig.update_yaxes(showgrid=False,secondary_y=True,tickformat=',.0%',dtick=0.25)
        self.add_slider(fig)

        fig = self.chart.add_annotation(fig,"@checkmatey<br />@permabullnino")     
        
        #Write out html chart
        chart_name = '/hodlerconversion_oscillator_usd'
        self.write_html(fig,chart_name)

        return fig

    def strongest_hand(self,_28_142_toggle):
        """"
        Strongest Hand Metric after @permabullnino
        https://medium.com/@permabullnino/decred-on-chain-strongest-hand-market-cap-ratio-146d6854e1d6
        Maximum volume into tickets, on a rolling 28day or 142 day basis
            multiplied 28 (number of  days on avg to fill up the ticket pool) give Strong Hand Cap
            this is an implied ticket pool cap
        Ratio is calculated as Market Cap / Strongest Hand
        Top and Bottom boundaries calculated based on historical performance
        INPUTS:
            _28_142_toggle = 0 for 28 day (default)
                           = 1 for 142 day
        """
        df = self.df
        df = dcr_add_metrics().metric_strongest_hand(df)

        if _28_142_toggle == 1: #142 Day
            loop_data=[[0,3,4,5],[7,11,12,13]]
        else:                   #28-Day
            loop_data=[[0,1,2],[6,8,9,10]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            [self.start,self.last],    #N/A CEILING
            [self.start,self.last],    #STRONG SELL
            [self.start,self.last],    #BUY
            [self.start,self.last],    #N/A CEILING
            [self.start,self.last],    #STRONG SELL
            [self.start,self.last],    #BUY
        ]
        y_data = [
            df['CapMrktCurUSD'],
            #28-Day Caps
            df['stronghand_cap_28'],
            df['stronghand_top_28'],   
            #142-day Caps
            df['stronghand_cap_142'],  
            df['stronghand_btm_142'],
            df['stronghand_top_142'],
            #Secondary Axes
            df['stronghand_ratio_28'], 
            df['stronghand_ratio_142'],
            #28 Day
            [2,2],
            [1.618,1.618],
            [1.0,1.0],
            #142 Day
            [1.8,1.8],
            [1.45,1.45],
            [0.60,0.60]
        ]
        name_data = [
            'DCR Market Cap',
            'Strong Btm 28-day',
            'Strong Top 28-day',
            'Strongest Hand Cap 142-day',
            'Strong Btm 142-day',
            'Strong Top 142-day',
            'Strongest Hand Ratio 28-day',
            'Strongest Hand Ratio 142-day',
            'NA',
            'Weak Hands (1.618)',
            'Strong Hands (1.0)',
            'NA',
            'Weak Hands (1.45)',
            'Strong Hands (0.60)',
        ]
        width_data      = [
            2,2,2,2,2,2,
            2,2,
            1,1,1,
            1,1,1,]
        opacity_data    = [
            1,1,1,1,1,1,
            1,1,
            1,1,1,
            1,1,1,]
        dash_data = [
            'solid','solid','solid','dash','solid','solid',
            'solid','solid',
            'dash','dash','dash',
            'dash','dash','dash',]
        color_data = [
            'rgb(255, 255, 255)',       #White
            'rgb(237, 109, 71)',        #Decred Orange
            'rgb(46, 214, 161)',        #Turquoise
            'rgb(46, 214, 161)',        #Turquoise
            'rgb(255, 80, 80)',         #Gradient Red
            'rgb(36, 255, 136)',        #Gradient Green
            'rgb(237, 109, 71)',        #Decred Orange
            'rgb(46, 214, 161)',        #Turquoise
            'rgba(36, 255, 136,0.2)',        #Gradient Green
            'rgba(36, 255, 136,0.2)',        #Gradient Green
            'rgba(255, 80, 80,0.2)',         #Gradient Red
            'rgba(36, 255, 136,0.2)',        #Gradient Green
            'rgba(36, 255, 136,0.2)',        #Gradient Green
            'rgba(255, 80, 80,0.2)',         #Gradient Red
        ]        #Invert Colors for Light Theme
        color_data = self.color_invert(color_data)
        fill_data = [
            'none','none','none','none','none','none',
            'none','none',
            'none','tonexty','tozeroy',
            'none','tonexty','tozeroy',
        ]
        legend_data = [
            True,True,True,True,True,True,
            True,True,
            False,True,True,
            False,True,True,]
        title_data = [
            '<b>Decred Strongest Hand</b>',
            '<b>Date</b>',
            '<b>Network Valuation (USD)</b>',
            '<b>Strongest Hand Ratio</b>']
        range_data = [[self.start,self.last],[self.cap_lb,self.cap_ub],[0.1,5.0]]
        autorange_data = [False,False,False]
        type_data = ['date','log','linear']
        fig = self.chart.subplot_lines_doubleaxis_2nd_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        self.add_slider(fig)
        fig = self.chart.add_annotation(fig,"@checkmatey<br />@permabullnino")

        #Write out html chart
        if _28_142_toggle == 1:
            chart_name = '/stronghand142_oscillator_usd'
        else:
            chart_name = '/stronghand28_oscillator_usd'
        self.write_html(fig,chart_name)

        return fig

    def mining_pulse(self):
        """Decred Mining Pulse after @permabull Nino
        """
        df  = self.df
        df  = dcr_add_metrics().metric_puell_multiple(df)
        df2 = dcr_add_metrics().metric_mining_pulse()

        loop_data=[[0,1,2,3,4],[7,8,9,10,5,6,11,12]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            #Secondary
            df2['date'],
            df2['date'],
            [self.start,self.last], #NA Ceiling
            [self.start,self.last], #+2s
            [self.start,self.last], #NA Floor
            [self.start,self.last], #-2s
            df2['date'],
            df2['date'],
        ]
        y_data = [
            df['Puell_income_pos'], #positive, black
            df['Puell_income'],     #NA fill from MA to pos (green)
            df['Puell_income_neg'], #negative, black
            df['Puell_income'],     #NA fill from MA to neg (red)
            df['Puell_income'],     #Blue Plot MA
            #Secondary
            df2['miningpulse_pos'],
            df2['miningpulse_neg'],
            [6,6],
            [2,2],
            [-6,-6],
            [-2,-2],
            df2['miningpulse_pos'],
            df2['miningpulse_neg'],
        ]
        name_data = [
            'Daily PoW Block Reward',
            'NA','NA','NA',
            '365-day MA',
            #Secondary
            'Mining Pulse +ve',
            'Mining Pulse -ve',
            'na','na','na','na','na','na',
            ]
        color_data = [
            'rgb(255, 255, 255)',         #White
            'rgba(36, 255, 136, 0.3)',    #Gradient Green
            'rgb(255, 255, 255)',         #White
            'rgba(255, 80, 80, 0.3)',     #Gradient Red
            'rgb(237, 109, 71)',          #Decred Orange
            #Secondary
            #'rgba(112, 48, 160,0.7)',   #Purple
            'rgba(0, 255, 255, 0.7)',   #Retro Blue
            'rgba(255,0,255,0.7)',      #Retro Pink
            'rgba(0,0,0,0)',            #NA
            'rgba(153, 255, 102, 0.3)',  #Gradient Green
            'rgba(0,0,0,0)',            #NA
            'rgba(255, 80, 80, 0.3)',    #Gradient Red
            'rgb(255, 255, 255)',         #White
            'rgb(255, 255, 255)',         #White
        ]
        for i in [0,2,4,5,6,8,10,11,12]:
            color_data[i] = self.color_invert([color_data[i]])[0]
        fill_data = [
            'none','tonexty','none','tonexty','none',
            'tozeroy','tozeroy','none','tonexty','none','tonexty','none','none',
        ]
        #Invert Colors for Light Theme
        
        dash_data = [
            'solid','solid','solid','solid','solid',
            'solid','solid','solid','solid','solid','solid','solid','solid',
            ]
        width_data      = [2,0,2,0,2,     1,1,1,1,1,1,0.5,0.5]
        opacity_data    = [1,1,1,1,1,     1,1,1,1,1,1,1,1]
        legend_data     = [
            True,False,False,False,True,
            True,True,False,False,False,False,False,False
            ]
        autorange_data  = [False,False,False]
        type_data       = ['date','log','linear']
        title_data = [
            '<b>Decred Mining Pulse (seconds)</b>',
            '<b>Date</b>',
            '<b>DCR/USD Price</b>',
            '<b>Mining Pulse (seconds)</b>'
        ]
        range_data = [[self.start,self.last],[2,6],[-6,30]]

        #BUILD FINAL CHART
        fig = self.chart.subplot_lines_doubleaxis_both_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_yaxes(showgrid=True,secondary_y=False)
        fig.update_yaxes(dtick=2,secondary_y=True)
        
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        self.add_slider(fig)
        fig = self.chart.add_annotation(fig,"@checkmatey<br />@permabullnino")     

        #Write out html chart
        chart_name = '/miningpulse_oscillator_usd'
        self.write_html(fig,chart_name)

        return fig

    def ticket_funding_rate(self,period,sumperiod):
        """Decred Ticket Funding Rate after @permabull Nino
        https://medium.com/@permabullnino/decred-on-chain-ticket-funding-rates-4e7233c7b64f
        Funding Rate = Current Ticket ROI - 28-day Average ROI
        Positive Values = Low Relative demand for tickets, Mininmum willingness to hold DCR
        Negative Values = High Relative demand for tickets, Maximum willingness to hold DCR 
        """
        df  = self.df
        df  = dcr_add_metrics().metric_ticket_funding_rate(df,period,sumperiod)

        loop_data=[[0,1,],[2,3,4,5,6,7]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            [self.start,self.last], #NA Ceiling
            [self.start,self.last], #Sell
            [self.start,self.last], #NA CEILING
            [self.start,self.last], #BUY
        ]
        y_data = [
            df['PriceUSD'],
            df['PriceRealUSD'],
            df['tic_fund_zsum_pos'],
            df['tic_fund_zsum_neg'],
            [30.0,30.0],
            [15.0,15.0],
            [-15.0,-15.0],
            [-30.0,-30.0],
        ]
        name_data = [
            'Market Cap',
            'Realised Cap',
            'Ticket Funding Rate +ve',
            'Ticket Funding Rate -ve',
            'na','na','na','na',
            ]
        color_data = [
            'rgb(255, 255, 255)',       #White
            'rgb(239, 125, 50)',        #Price Orange
            'rgba(0, 255, 255, 0.7)',   #Retro Blue
            'rgba(255,0,255,0.7)',      #Retro Pink
            'rgba(0,0,0,0)',            #NA
            'rgba(153, 255, 102, 0.3)',  #Gradient Green
            'rgba(0,0,0,0)',            #NA
            'rgba(255, 80, 80, 0.3)',    #Gradient Red
        ]
        fill_data = [
            'none','none','tozeroy','tozeroy',
            'none','tonexty','none','tonexty'
        ]
        #Invert Colors for Light Theme
        color_data = self.color_invert(color_data)
        dash_data = [
            'solid','solid','solid','solid',
            'solid','solid','solid','solid',
            ]
        width_data      = [2,2,1,1,    1,1,1,1]
        opacity_data    = [1,1,1,1,    1,1,1,1]
        legend_data     = [True,True,True,True,False,False,False,False,]#
        autorange_data  = [False,False,False]
        type_data       = ['date','log','linear']#
        title_data = [
            '<b>Ticket Funding Rate ' + str(period) + '-day</b>',
            '<b>Date</b>',
            '<b>DCR/USD Price</b>',
            '<b>Ticket Funding Rate Z-Score Sum</b>'
        ]
        range_data = [[self.start,self.last],[self.price_lb,self.price_ub],[-30,150]]

        #BUILD FINAL CHART
        fig = self.chart.subplot_lines_doubleaxis_2nd_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_yaxes(showgrid=True,secondary_y=False)
        fig.update_yaxes(secondary_y=True)
        
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        self.add_slider(fig)
        fig = self.chart.add_annotation(fig,"@checkmatey<br />@permabullnino")     

        #Write out html chart
        chart_name = '/ticfundrate' + str(period) + 'day_oscillator_usd'
        self.write_html(fig,chart_name)

        return fig

    def ticket_overunder(self):
        """"Decred Ticket Over/Under Measure
            after @permabullnino"""
        df = self.df
        df = dcr_add_metrics().metric_ticket_overunder(df)

        #CHART
        loop_data=[[0,1],[2,3,4,5]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            [self.start,self.last],    #NA
            [self.start,self.last],    #BUY ZONE
            [self.start,self.last],    #SELL ZONE
        ]
        y_data = [
            df['PriceBTC'],
            df['PriceRealBTC'],
            df['tic_overunder'],
            [0.216,0.216],
            [0.210,0.210],
            [0.199,0.199],
        ]
        name_data = [
            'DCR Price (BTC)',
            'Realised Price (BTC)',
            'Ticket Over/Under Measure',
            'NA',
            'Buy Zone',
            'Sell Zone',
        ]
        width_data      = [2,2,2,1,1,1,]
        opacity_data    = [1,1,1,1,1,1,]
        dash_data = ['solid','solid','solid','solid','dash','dash',]
        color_data = [
            'rgb(255, 255, 255)',   #White
            'rgb(17, 255, 125)',    #Powerpoint Green
            'rgb(20, 169, 233)',    #Total Blue
            'rgba(255,255,255,0)',       #NA
            'rgba(153, 255, 102,0.2)',   #Gradient Green
            'rgba(255, 80,  80, 0.2)',     #Gradient Red
            'rgb(20, 169, 233)',    #Total Blue
        ]
        #Invert Colors for Light Theme
        color_data = self.color_invert(color_data)
        fill_data = ['none','none','none','none','tonexty','tozeroy',]
        legend_data = [True,True,True,False,True,True,True]
        title_data = [
            '<b>Decred Ticket Over/Under Measure</b>',
            '<b>Date</b>',
            '<b>Price (BTC)</b>',
            '<b>Ticket Over/Under Measure</b>']
        range_data = [['2018-01-01',self.last],[-3.698970004,-1.698970004],[0.190,0.300]]
        autorange_data = [False,False,False]
        type_data = ['date','log','linear']
        fig = self.chart.subplot_lines_doubleaxis_2nd_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        fig.update_yaxes(showgrid=False,secondary_y=True,dtick=0.005)
        self.add_slider(fig)

        fig = self.chart.add_annotation(fig,"@checkmatey<br />@permabullnino")     

        #Write out html chart
        chart_name = '/ticoverunder_oscillator_usd'
        self.write_html(fig,chart_name)

        return fig

    def tic_vol_sum_142day(self):
        """"Decred 142-day sum of tickets with Fibonacci multiple bands 
            after @permabullnino"""
        df = self.df
        df = dcr_add_metrics().metric_tic_vol_sum_142day(df)

        loop_data=[[0,1,2,3,4,5],[6,7,8,9,10,11,12]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            #secondary
            df['date'],
            [self.start,self.last], #NA Ceiling
            [self.start,self.last], #STRONG SELL
            [self.start,self.last], #SELL
            [self.start,self.last], #NA CEILING
            [self.start,self.last], #BUY
            [self.start,self.last], #STRONG BUY
        ]
        y_data = [
            df['PriceUSD'],
            df['tic_usd_cost_142sum'],
            df['tic_usd_cost_142sum']*0.236,
            df['tic_usd_cost_142sum']*0.382,
            df['tic_usd_cost_142sum']*0.500,
            df['tic_usd_cost_142sum']*0.618,
            #secondary
            df['tic_usd_cost_142sum_oscillator'],
            [5.000,5.000],
            [2.000,2.000],
            [1.236,1.236],
            [0.764,0.764],
            [0.472,0.472],
            [0.472,0.472],
        ]
        name_data = [
            'DCR/USD Price',
            '142d Ticket USD Sum',
            '142d Ticket USD Sum x23.6%',
            '142d Ticket USD Sum x38.2%',
            '142d Ticket USD Sum x50.0%',
            '142d Ticket USD Sum x61.8%',
            '142-day Ticket Multiple (50.0%)',
            'N/A',
            'STRONG SELL',
            'SELL',
            'N/A',
            'BUY',
            'STRONG BUY',
            ]
        color_data = [
            'rgb(255, 255, 255)',    #White
            'rgb(255, 80, 80)',     #Gradient Red
            'rgb(153, 255, 102)',   #Gradient Green
            'rgb(255, 204, 102)',   #Gradient Yellow
            'rgb(46, 214, 161)',    #Turquoise
            'rgb(255, 204, 102)',   #Gradient Yellow
            'rgb(46, 214, 161)',    #Turquoise
            'rgba(255, 80, 80, 0.0)',     #Gradient Red
            'rgba(255, 80, 80, 0.2)',     #Gradient Red
            'rgba(255, 80, 80, 0.1)',     #Gradient Red
            'rgb(55, 55, 55)',            #N/A
            'rgba(36, 255, 136, 0.1)',    #Gradient Green
            'rgba(36, 255, 136, 0.2)',    #Gradient Green
            ]
        #Invert Colors for Light Theme
        for i in [0,1,2,3,4,5,6]:
            color_data[i] = self.color_invert([color_data[i]])[0]
        fill_data = [ 
            'none','none','none','none','none','none','none',
            'none','tonexty','tonexty','none','tonexty','tozeroy',
            ]
        dash_data = [
            'solid','solid','solid','dash','dot','dash',
            'solid','dash','dash','dash','dash','dash','dash'
            ]
        width_data   = [2,2,2,1,1,1,   2,1,1,1,1,1,1]
        opacity_data = [1,1,1,1,1,1,   1,1,1,1,1,1,1]
        legend_data = [True,True,True,True,True,True,    True,False,True,True,False,True,True]#
        title_data = [
            '<b>Decred 142-Day Ticket USD Sum</b>',
            '<b>Date</b>',
            '<b>DCR/USD Pricing</b>',
            '<b>Price / (142-day Ticket Sum * 50%)</b>']
        range_data = [[self.start,self.last],[-2,3],[np.log10(0.2),5]]
        autorange_data = [False,False,False]
        type_data = ['date','log','log']#
        fig = self.chart.subplot_lines_doubleaxis_2nd_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)

        self.add_slider(fig)
        fig = self.chart.add_annotation(fig,"@checkmatey<br />@permabullnino")     

        #Write out html chart
        chart_name = '/142dayticsum_pricing_usd'
        self.write_html(fig,chart_name)

        return fig

    def tx_volatility_ratio(self):
        """"Decred Transactional Volatility Ratio
            after @permabullnino"""
        df = self.df
        df = dcr_add_metrics().metric_tx_volatility_ratio(df)

        #CHART
        loop_data=[[0,1],[2,3,4,5]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            [self.start,self.last,self.last,self.start],    #BUY ZONE
            [self.start,self.last,self.last,self.start],    #SELL ZONE
        ]
        y_data = [
            df['PriceBTC'],
            df['PriceRealBTC'],
            df['tx_volatility_ratio'],
            df['tx_volatility_ratio_Ntv'],
            [0.15,0.15,0.17,0.17],
            [0.26,0.26,0.28,0.28],
        ]
        name_data = [
            'DCR Price (BTC)',
            'Realised Price (BTC)',
            'Transaction Volatility (dcrdata)',
            'Transaction Volatility (CoinMetrics)',
            'Buy Zone',
            'Sell Zone',
        ]
        width_data      = [2,2,2,2,1,1]
        opacity_data    = [1,1,1,1,1,1]
        dash_data = ['solid','solid','dash','solid','dash','dash',]
        color_data = [
            'rgb(255, 255, 255)',   #White
            'rgb(17, 255, 125)',    #Powerpoint Green
            'rgb(20, 169, 233)',    #Total Blue
            'rgb(20, 169, 233)',    #Total Blue
            'rgb(153, 255, 102)',   #Gradient Green
            'rgb(255, 80, 80)',     #Gradient Red
        ]
        #Invert Colors for Light Theme
        color_data = self.color_invert(color_data)
        legend_data = [True,True,True,True,True,True]
        title_data = [
            '<b>Decred Transactional Volatility</b>',
            '<b>Date</b>',
            '<b>Price (BTC)</b>',
            '<b>Transaction Volatility Ratio</b>'
            ]
        range_data = [[self.start,self.last],[-4,-1.698970004],[0,1]]
        autorange_data = [False,False,False]
        type_data = ['date','log','linear']
        fig = self.chart.subplot_lines_doubleaxis(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data
            )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        fig.update_yaxes(showgrid=False,secondary_y=True,dtick=0.05)
        self.add_slider(fig)

        fig = self.chart.add_annotation(fig,"@checkmatey<br />@permabullnino")     

        #Write out html chart
        chart_name = '/txvolatilityratio_oscillator_btc'
        self.write_html(fig,chart_name)

        return fig

    def tx_sum_adjsply_28d_142d(self):
        """"Decred 28 and 142day Sum of coins moved, adjusted for supply
        after @permabullnino"""
        df = self.df
        df = dcr_add_metrics().metric_tx_sum_adjsply_28d_142d(df)

        loop_data=[[0],[3,4,5,1,2]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            [self.start,self.last],    #BUY ZONE Ceiling
            [self.start,self.last],    #BUY ZONE Floor
            [self.start,self.last],    #SELL ZONE Floor
        ]
        y_data = [
            df['PriceUSD'],
            df['tx_dcr_28sum_adj']*5,
            df['tx_dcr_142sum_adj'],
            [3.0,3.0],
            [1.7,1.7],
            [1.1,1.1],
        ]
        name_data = [
            'DCR Price (USD)',
            'tx_dcr_28sum_adj x5',
            'tx_dcr_142sum_adj',
            'N/A',
            'HIGH ACTIVITY',
            'LOW ACTIVITY',
        ]
        width_data      = [2,5,5,2,2,2]
        opacity_data    = [1,1,1,1,1,1]
        dash_data = ['solid','solid','solid','dash','dash','dash']
        color_data = [
            'rgb(255, 255, 255)',   #White
            'rgb(209, 41, 205)',    #Turquoise Inverted
            'rgb(46, 214, 161)',    #Turquoise
            'rgba(0,255,255,0.3)', #Retro Blue
            'rgba(0,255,255,0.3)', #Retro Blue
            'rgba(255,0,255,0.3)', #Retro Pink
            'rgba(255,0,255,0.3)', #Retro Pink
        ]
        #Invert Colors for Light Theme
        color_data = self.color_invert(color_data)

        color_data[3] = color_data[4] = 'rgba(0,255,255,0.3)' #Retro Blue
        color_data[5] = 'rgba(255,0,255,0.3)'                 #Retro Pink
        legend_data = [True,True,True,False,True,True,]
        fill_data       = ['none','none','none','none','tonexty','tozeroy',]
        title_data = [
            '<b>Decred 28 and 142-Day Moved Coins Adjusted for Supply</b>',
            '<b>Date</b>',
            '<b>Price USD</b>',
            '<b>Sum of DCR Moved over Period / Circ. Supply</b>']
        range_data = [[self.start,self.last],[-2,self.price_ub],[0,10]]
        autorange_data = [False,False,False]
        type_data = ['date','log','linear']
        fig = self.chart.subplot_lines_doubleaxis_2nd_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        fig.update_yaxes(showgrid=False,secondary_y=True)
        self.add_slider(fig)
        fig = self.chart.add_annotation(fig,"@checkmatey<br />@permabullnino")

        #Write out html chart
        chart_name = '/txsumadjsply_oscillator_usd'
        self.write_html(fig,chart_name)

        return fig

    def max_vol_ratio(self):
        """"Decred Maximum Volume Ratio
            after @permabullnino"""
        df = self.df
        df = dcr_add_metrics().metric_max_vol_ratio(df)

        #CHART
        loop_data=[[0,1],[2,3,4,5,6]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            [self.start,self.last],    #NA
            [self.start,self.last],    #BUY ZONE
            [self.start,self.last],    #SELL ZONE
        ]
        y_data = [
            df['PriceUSD'],
            df['PriceRealUSD'],
            df['max_vol_ratio_USD'],
            df['max_vol_ratio_BTC'],
            [3.5,3.5],
            [2.5,2.5],
            [1.5,1.5],
        ]
        name_data = [
            'DCR Price (USD)',
            'Realised Price (USD)',
            'max_vol_ratio_USD',
            'max_vol_ratio_BTC',
            'NA',
            'Sell Zone',
            'Buy Zone',
        ]
        width_data      = [2,2,2,2,1,1,1]
        opacity_data    = [1,1,1,1,1,1,1]
        dash_data = ['solid','solid','solid','dash','dash','dash','dash',]
        color_data = [
            'rgb(255, 255, 255)',   #White
            'rgb(17, 255, 125)',    #Powerpoint Green
            'rgb(20, 169, 233)',    #Total Blue
            'rgb(20, 169, 233)',    #Total Blue
            'rgba(255,255,255,0)',  #NA
            'rgb(153, 255, 102)',   #Gradient Green
            'rgb(255, 80, 80)',     #Gradient Red
        ]
        #Invert Colors for Light Theme
        color_data = self.color_invert(color_data)
        filldata = [
            'none','none','none','none',
            'none','tonexty','tozeroy'
        ]
        legend_data = [True,True,True,True,False,True,True]
        title_data = [
            '<b>Decred Max Vol Ratio</b>',
            '<b>Date</b>',
            '<b>Price (BTC)</b>',
            '<b>Transaction Volatility Ratio</b>'
            ]
        range_data = [[self.start,self.last],[self.price_lb,self.price_ub],[0,10]]
        autorange_data = [False,False,False]
        type_data = ['date','log','linear']
        fig = check_standard_charts(self.theme).subplot_lines_doubleaxis(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data
            )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        fig.update_yaxes(showgrid=False,secondary_y=True,dtick=0.5)
        self.add_slider(fig)

        fig = self.chart.add_annotation(fig,"@checkmatey<br />@permabullnino")     

        #Write out html chart
        chart_name = '/maxvolratio_oscillator_btc'
        self.write_html(fig,chart_name)

        return fig

    def dcr_vs_btc(self):
        """"Compare DCR and BTC by Coin Age"""

        dcr = self.df
        dcr['age_sply'] = dcr['age_sply']

        btc = btc_add_metrics().btc_real()
        doge = Coinmetrics_api('doge',"2013-01-01",today).convert_to_pd().set_index('date',drop=False)
        doge['age_sply'] = doge['SplyCur']/280666706295.71

        loop_data=[[0,1,4],[2,3,5]]
        x_data = [
            btc['age_sply'],
            dcr['age_sply'],
            btc['age_sply'],
            dcr['age_sply'],
            doge['age_sply'],
            doge['age_sply'],
        ]
        y_data = [
            btc['PriceUSD'],
            dcr['PriceUSD'],
            btc['CapMrktCurUSD'],
            dcr['CapMrktCurUSD'],
            doge['PriceUSD'],
            doge['CapMrktCurUSD'],
        ]
        name_data = [
            'BTC Price',
            'DCR Price',
            'BTC Market Cap',
            'DCR Market Cap',
            'Doge Price',
            'Doge Market Cap'
        ]
        width_data      = [2,2,2,2,2,2]
        opacity_data    = [1,1,1,1,1,1]
        dash_data = ['solid','solid','dash','dash','solid','dash']
        color_data = [
            'rgb(239, 125, 50)',    #Price Orange
            'rgb(46, 214, 161)',    #Turquoise
            'rgb(239, 125, 50)',    #Price Orange
            'rgb(46, 214, 161)',    #Turquoise
            'rgb(153, 255, 102)',   #Gradient Green
            'rgb(153, 255, 102)',   #Gradient Green
        ]
        #Invert Colors for Light Theme
        color_data = self.color_invert(color_data)
        legend_data = [True,True,True,True,True,True,]
        title_data = [
            'BTC vs DCR',
            '<b>Coin Age (Supply / 21M)</b>',
            '<b>Price (USD)</b>',
            '<b>Market Cap (USD)</b>']
        range_data = [[0,1],[-2,5],[5,12]]
        autorange_data = [False,False,False]
        type_data = ['linear','log','log']
        fig = self.chart.subplot_lines_doubleaxis(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data
            )
        fig.update_xaxes(dtick='0.1')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        fig.update_yaxes(showgrid=False,secondary_y=True)
        self.add_slider(fig)

        #Write out html chart
        chart_name = '/cyclebtcvsdcr_usd'
        self.write_html(fig,chart_name)

        return fig

    def MACD(self):
        """"Decred MACD Indicator
        """
        df = self.df
        df = dcr_add_metrics().metric_MACD(df)

        #CHART
        loop_data=[[0,1,2],[5,6]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
        ]
        y_data = [
            df['PriceUSD'],
            df['PriceUSD'].ewm(com=12).mean(),
            df['PriceUSD'].ewm(com=26).mean(),
            df['MACD'],
            df['Signal'],
            df['MACD_Hist_pos'],
            df['MACD_Hist_neg'],

        ]
        name_data = [
            'DCR Price (USD)',
            'EMA-12',
            'EMA-26',
            'MACD',
            'Signal',
            'MACD +ve',
            'MACD -ve',
        ]
        fill_data = [
            '','','',
            'none','none','tozeroy','tozeroy'
            ]
        width_data      = [2,1,1,1,1,1,1]
        opacity_data    = [1,1,1,1,1,1,1]
        dash_data = ['solid','solid','solid','solid','solid','solid','solid',]
        color_data = [
            'rgb(255, 255, 255)',   #White
            'rgb(239, 125, 50)',    #Price Orange
            'rgb(20, 169, 233)',    #Total Blue
            'rgb(239, 125, 50)',    #Price Orange
            'rgb(20, 169, 233)',    #Total Blue
            'rgba(255, 80,  80,  0.4)',   #Gradient Red
            'rgba(153, 255, 102, 0.4)',   #Gradient Green
        ]
        #Invert Colors for Light Theme
        color_data = self.color_invert(color_data)
        legend_data = [True,True,True,True,True,True,True,]
        title_data = [
            '<b>Decred MACD Indicator</b>',
            '<b>Date</b>',
            '<b>Price (USD)</b>',
            '<b>MACD</b>']
        range_data = [[self.start,self.last],[-2,3],[-8,20]]
        autorange_data = [False,False,False]
        type_data = ['date','log','linear']
        fig = self.chart.subplot_lines_doubleaxis_2nd_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        fig.update_yaxes(showgrid=False,secondary_y=True)
        self.add_slider(fig)

        
        #Write out html chart
        chart_name = '/macd_oscillator_usd'
        self.write_html(fig,chart_name)

        return fig

    def onchain_OBV(self):
        """"Decred Onchain Volume OBV Indicator
        """
        df = self.df
        df = dcr_add_metrics().metric_OBV(df)

        #CHART
        loop_data=[[0],[1,2,3,4,5,6]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
        ]
        y_data = [
            df['PriceUSD'],
            df['OBV_142_Indicator'],
            df['OBV_28_Indicator'],
            df['OBV_tic_142_Indicator'],
            df['OBV_tic_28_Indicator'],
            df[df['OBV_vol']>0],
            df[df['OBV_vol']>0],
        ]
        name_data = [
            'DCR Price (USD)',
            'OBV 142-day Total',
            'OBV 28-day Total',
            'OBV 142-day Ticket',
            'OBV 28-day Ticket',
            'Volume Bars +ve',
            'Volume Bars -ve',
        ]
        fill_data = [
            'none','tozeroy','tozeroy','tozeroy','tozeroy','tozeroy','tozeroy'
            ]
        width_data      = [2,1,1,1,1,1,1]
        opacity_data    = [1,1,1,1,1,1,1]
        dash_data = ['solid','solid','solid','solid','solid','solid','solid']
        color_data = [
            'rgb(255, 255, 255)',        #White
            'rgba(255, 80,  80,  0.4)',  #Gradient Red
            'rgba(153, 255, 102, 0.4)',  #Gradient Green
            'rgba(0, 175,  175,  0.6)',  #Gradient Red (inverted)
            'rgba(102, 0, 152, 0.6)',    #Gradient Green (inverted)
            'rgb(46, 214, 161)',         #Turquoise
            'rgb(209, 41, 94)',          #Turquoise (inverted)
        ]
        #Invert Colors for Light Theme
        for i in [0,1,2,3,4]:
            color_data[i] = self.color_invert([color_data[i]])[0]
        legend_data = [True,True,True,True,True,True,True]
        title_data = [
            '<b>Decred Onchain OBV Indicator</b>',
            '<b>Date</b>',
            '<b>Price (USD)</b>',
            '<b>Onchain On Balance Volume Indicator</b>']
        range_data = [[self.start,self.last],[-2,3],[-5e6,20e6]]
        autorange_data = [False,False,False]
        type_data = ['date','log','linear']
        fig = self.chart.subplot_lines_doubleaxis_2nd_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_xaxes(dtick='M6',tickformat='%d-%b-%y')
        fig.update_yaxes(showgrid=True,secondary_y=False)
        fig.update_yaxes(showgrid=False,secondary_y=True)
        self.add_slider(fig)

        
        #Write out html chart
        chart_name = '/onchainobv_oscillator_usd'
        self.write_html(fig,chart_name)

        return fig

    def privacy(self):
        """Decred Privacy Performance"""
        df = self.df

        #Regular Transactions
        df['dcr_tfr_reg'] = df['dcr_tfr_vol'] - df['dcr_anon_mix_vol']
        #Total Transactions
        df['total_tx'] = (
            df['dcr_tfr_reg']
            + df['dcr_tic_vol']
            + df['dcr_anon_mix_vol']
        )
        df['tx_mix'] = df['dcr_anon_mix_vol'].cumsum()
        df['tx_tic'] = df['dcr_tic_vol'].cumsum()
        df['tx_reg'] = df['dcr_tfr_reg'].cumsum()
        
        loop_data=[[0,1,2],[4,5]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
        ]
        y_data = [
            df['tx_reg'],
            (df['tx_reg']+df['tx_tic']),
            (df['tx_reg']+df['tx_tic']+df['tx_mix']),
            df['dcr_tfr_reg'].rolling(1).mean()/df['dcr_sply'],
            df['dcr_tic_sply_avg']/df['dcr_sply'],
            df['dcr_anon_part'],
        ]
        name_data = [
            'Regular Volume',
            'Ticket Volume',
            'Privacy Mix Volume',
            'Regular Transactions',
            'Stake Participation',
            'Unspent Anonymity Set',
            ]
        color_data = [
            'rgba(239, 125,  50, 0.5)',     #Price Orange
            'rgba(46,  214, 161, 0.5)',     #Turquoise
            'rgba(250, 38,   53, 0.5)',     #POW Red
            'rgb(239, 125,  50)',           #Price Orange
            'rgb(46,  214, 161)',           #Turquoise
            'rgb(250, 38, 53)',             #POW Red
            #'rgb(114, 49, 163)',    #POS Purple
            #'rgb(255, 192, 0)',     #Treasury Yellow
            #'rgb(20, 169, 233)',    #Total Blue
        ]
        #NO INVERSION
        fill_data = [
            'tozeroy','tonexty','tonexty','none','none','none'
        ]
        dash_data = [
            'solid','solid','solid','solid','solid','solid'
            ]
        width_data = [1,1,1,2,5,5]
        opacity_data = [1,1,1,1,1,1]
        legend_data = [True,True,True,True,True,True]#
        type_data = ['date','linear','linear']#
        title_data = [
            '<b>Decred Transaction Volumes</b>',
            '<b>Date</b>',
            '<b>Cumulative On-chain Volume (DCR)</b>',
            '<b>Proportion of Circ. Supply (DCR)</b>']
        range_data = [[self.start,self.last],[0,600e6],[0,0.6]]
        autorange_data = [False,False,False]
        #BUILD FINAL CHART
        fig = self.chart.subplot_lines_doubleaxis_1st_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        #Add Volume Bars for Regular Transactions
        #self.add_vol_bars(fig,x_data,y_data,color_data,name_data,[3])
        fig.update_yaxes(secondary_y=False,showgrid=True)
        fig.update_yaxes(secondary_y=True,dtick=0.1,tickformat=",.0%")
        self.add_slider(fig)

        #Write out html chart
        chart_name = '/privcum_performance'
        self.write_html(fig,chart_name)
        return fig

    def privacy_volume(self):
        """Decred Privacy Volumes"""
        df = self.df

        #Regular Transactions
        df['dcr_tfr_reg'] = df['dcr_tfr_vol'] - df['dcr_anon_mix_vol']
        #Total Transactions
        df['total_tx'] = (
            df['dcr_tfr_reg']
            + df['dcr_tic_vol']
            + df['dcr_anon_mix_vol']
        )
        df['tx_mix'] = df['dcr_anon_mix_vol'].cumsum()
        df['tx_tic'] = df['dcr_tic_vol'].cumsum()
        df['tx_reg'] = df['dcr_tfr_reg'].cumsum()
        
        loop_data=[[0,1,2],[3,4,5]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
        ]
        y_data = [
            df['tx_reg'],
            (df['tx_reg']+df['tx_tic']),
            (df['tx_reg']+df['tx_tic']+df['tx_mix']),
            df['dcr_tfr_reg'],
            df['dcr_tic_vol'],
            df['dcr_anon_mix_vol'],
        ]
        name_data = [
            'Regular Volume',
            'Ticket Volume',
            'Privacy Mix Volume',
            'Regular Transactions',
            'Stake Participation',
            'Unspent Anonymity Set',
            ]
        color_data = [
            'rgba(239, 125,  50, 0.5)',     #Price Orange
            'rgba(46,  214, 161, 0.5)',     #Turquoise
            'rgba(250, 38,   53, 0.5)',     #POW Red
            'rgb(239, 125,  50)',           #Price Orange
            'rgb(46,  214, 161)',           #Turquoise
            'rgb(250, 38, 53)',             #POW Red
            #'rgb(114, 49, 163)',    #POS Purple
            #'rgb(255, 192, 0)',     #Treasury Yellow
            #'rgb(20, 169, 233)',    #Total Blue
        ]
        #NO INVERSION
        fill_data = [
            'tozeroy','tonexty','tonexty','none','none','none'
        ]
        dash_data = [
            'solid','solid','solid','solid','solid','solid'
            ]
        width_data = [1,1,1,2,2,2]
        opacity_data = [1,1,1,1,1,1]
        legend_data = [True,True,True,True,True,True]#
        type_data = ['date','linear','linear']#
        title_data = [
            '<b>Decred Transaction Volumes</b>',
            '<b>Date</b>',
            '<b>Cumulative On-chain Volume (DCR)</b>',
            '<b>Daily Tx Volume (DCR)</b>']
        range_data = [[self.start,self.last],[0,600e6],[0,6e6]]
        autorange_data = [False,False,False]
        #BUILD FINAL CHART
        fig = self.chart.subplot_lines_doubleaxis_1st_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        #Add Volume Bars for Regular Transactions
        #self.add_vol_bars(fig,x_data,y_data,color_data,name_data,[3])
        fig.update_yaxes(secondary_y=False,showgrid=True)
        fig.update_yaxes(secondary_y=True,)
        self.add_slider(fig)

        #Write out html chart
        chart_name = '/privacyvol_performance'
        self.write_html(fig,chart_name)
        return fig

    def transaction_volume(self):
        """Decred Transaction Volumes"""
        df = self.df

        #Regular Transactions
        df['dcr_tfr_reg'] = df['dcr_tfr_vol'] - df['dcr_anon_mix_vol']
        #Total Transactions
        df['total_tx'] = (
            df['dcr_tfr_reg']
            + df['dcr_tic_vol']
            + df['dcr_anon_mix_vol']
        )
        
        loop_data=[[0,1],[2,3,4]]
        x_data = [
            df['date'],
            df['date'],
            df['date'],
            df['date'],
            df['date'],
        ]
        y_data = [
            df['CapMrktCurUSD'],
            df['CapRealUSD'],
            df['dcr_anon_mix_vol'],
            (df['dcr_anon_mix_vol'] + df['dcr_tic_vol']),
            df['TxTfrValNtv']
        ]
        name_data = [
            'Market Cap',
            'Realised Cap',
            'CoinShuffle++ Mix Volume',
            'Ticket Purchase Volume',
            'Regular Tx Volume',
            ]
        color_data = [
            'rgb(255, 255, 255)',   #White
            'rgb(239, 125, 50)',    #Price Orange
            'rgba(250, 38, 53,0.5)',             #POW Red
            'rgba(46,  214, 161,0.5)',           #Turquoise
            'rgba(239, 125,  50,0.5)',           #Price Orange
        ]
        #Invert Colors for Light Theme
        for i in [0,1]:
            color_data[i] = self.color_invert([color_data[i]])[0]
        fill_data = [
            'none','none','tozeroy','tonexty','tonexty'
        ]
        dash_data = [
            'solid','solid','solid','solid','solid'
            ]
        width_data = [2,2,2,2,2]
        opacity_data = [1,1,1,1,1]
        legend_data = [True,True,True,True,True]#
        type_data = ['date','log','linear']#
        title_data = [
            '<b>Network Daily Transaction Volume</b>',
            '<b>Date</b>',
            '<b>Network Valuation (USD)</b>',
            '<b>Daily Tx Volume (DCR)</b>']
        range_data = [[self.start,self.last],[self.cap_lb,self.cap_ub],[0,6e6]]
        autorange_data = [False,False,False]
        #BUILD FINAL CHART
        fig = self.chart.subplot_lines_doubleaxis_2nd_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        #Add Volume Bars for Regular Transactions
        #self.add_vol_bars(fig,x_data,y_data,color_data,name_data,[3])
        fig.update_yaxes(secondary_y=False,showgrid=False)
        fig.update_yaxes(secondary_y=True,showgrid=True)
        self.add_slider(fig)

        #Write out html chart
        chart_name = '/txvol_performance'
        self.write_html(fig,chart_name)
        return fig

    def fee_growth(self):
        """Decred Growth of Fees"""
        dcr = self.df
        btc = Coinmetrics_api('btc',"2009-01-03",today).convert_to_pd().set_index('date',drop=False)
        eth = Coinmetrics_api('eth',"2015-07-30",today).convert_to_pd().set_index('date',drop=False)

        dcr['Fee142Growth'] = dcr['FeeTotNtv'] / dcr['FeeTotNtv'].rolling(142).mean()
        btc['Fee142Growth'] = btc['FeeTotNtv'] / btc['FeeTotNtv'].rolling(142).mean()
        eth['Fee142Growth'] = eth['FeeTotNtv'] / eth['FeeTotNtv'].rolling(142).mean()


        
        loop_data=[[0,1,2],[3,4,5]]
        x_data = [
            dcr['date'],
            btc['date'],
            eth['date'],
            dcr['date'],
            btc['date'],
            eth['date'],
        ]
        y_data = [
            dcr['FeeTotNtv'],
            btc['FeeTotNtv'],
            eth['FeeTotNtv'],
            dcr['Fee142Growth'],
            btc['Fee142Growth'],
            eth['Fee142Growth'],
        ]
        name_data = [
            'Decred Total Fee (DCR)',
            'Bitcoin Total Fee (BTC)',
            'Ethereum Total Fee (ETH)',
            'Decred 142-day Fee Growth',
            'Bitcoin 142-day Fee Growth',
            'Ethereum 142-day Fee Growth',
            ]
        color_data = [
            'rgb(46, 214, 161)',    #Turquoise
            'rgb(239, 125, 50)',            #Price Orange
            'rgb(114, 49, 163)',            #POS Purple
            'rgb(46, 214, 161)',    #Turquoise
            'rgb(239, 125, 50)',            #Price Orange
            'rgb(114, 49, 163)',            #POS Purple
        ]
        #Invert Colors for Light Theme
        #for i in [0,1]:
        #    color_data[i] = self.color_invert([color_data[i]])[0]
        dash_data = [
            'solid','solid','solid','dash','dash','dash'
            ]
        width_data = [2,2,2,2,2,2,2]
        opacity_data = [1,1,1,1,1,1]
        legend_data = [True,True,True,True,True,True]#
        type_data = ['date','log','log']#
        title_data = [
            '<b>Fee Market Growth over 142-days</b>',
            '<b>Date</b>',
            '<b>Daily Fees (Native Unit)</b>',
            '<b>142-day Fee Growth</b>',]
        range_data = [[self.start,self.last],[self.cap_lb,self.cap_ub],[0,6e6]]
        autorange_data = [False,True,True]
        #BUILD FINAL CHART
        fig = self.chart.subplot_lines_doubleaxis(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data
            )
        #Add Volume Bars for Regular Transactions
        #self.add_vol_bars(fig,x_data,y_data,color_data,name_data,[3])
        fig.update_yaxes(secondary_y=False,showgrid=False)
        fig.update_yaxes(secondary_y=True,showgrid=True)
        self.add_slider(fig)

        #Write out html chart
        chart_name = '/feegrowth_performance'
        self.write_html(fig,chart_name)
        return fig

    def treasury_payments(self):
        """
        #############################################################################
                            TREASURY INFLOW OUTFLOW - DCR
        #############################################################################
        """
        df          = self.df
        df_pay      = dcr_add_metrics().metric_treasury_payments(df)
        treasury    = dcr_add_metrics().dcr_treasury()
        treasury    = treasury.merge(self.df[['date','PriceUSD']],on='date',copy=False)
        
        treasury['net_usd']      = treasury['net_dcr']      * treasury['PriceUSD']
        treasury['received_usd'] = treasury['received_dcr'] * treasury['PriceUSD']
        treasury['sent_usd']     = treasury['sent_dcr']     * treasury['PriceUSD']
        
        loop_data = [[0,1,2],[3,4]]
        x_data = [
            treasury['date'],
            treasury['date'],
            treasury['date'],
            df['date'],
            df['date'],
            ]
        y_data = [
            #Chart 1 - INFLOW/OUTFLOW DCR
            treasury['net_dcr'].cumsum(),
            treasury['received_dcr'].cumsum(),
            treasury['sent_dcr'].cumsum(),
            df['PriceUSD'],
            df['PriceUSD'].rolling(30).mean(),
            ]
        name_data = [
            #Chart 1
            'Treasury Balance DCR',
            'Treasury Inflows DCR',
            'Treasury Outflows DCR',
            'DCR Price (USD)',
            'DCR Price 30DMA (USD)',
            ]
        color_data = [
            #Chart 1
            'rgb(65, 191, 83)',     #Decred Green
            'rgb(46, 214, 161)' ,   #Turquoise
            'rgb(250, 38, 53)' ,    #PoW Red
            #Chart 2
            'rgb(255,255,255)',     #White
            'rgb(65, 191, 83)',     #Decred Green
            ]
        color_data = self.color_invert(color_data)

        dash_data = [
            'solid','solid','solid',
            'solid','dash'
            ]
        width_data = [
            2,2,2,
            1,2,
            ]
        opacity_data = [
            1,1,1,
            1,1,
            ]
        legend_data = [
            True,True,True,
            True,True,
            ]
        title_data = [
            '<b>Decred Treasury Flows - DCR</b>',
            '<b>Date</b>',
            '<b>Treasury Flows (DCR)</b>',
            '<b>DCR Price (USD)</b>']
        range_data = [['2016-01-01','2021-01-01'],[0,1e6],[-1,3]]
        autorange_data = [False,False,False]
        type_data = ['date','linear','log']
        fig = self.chart.subplot_lines_doubleaxis(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data
            )
        fig.update_yaxes(dtick=1e5,showgrid=True,secondary_y=False)
        #Increase tick spacing
        
        #Write out html chart
        chart_name = '/treasuryio_performance'
        self.write_html(fig,chart_name)

        return fig

    def dcr_staking(self,tic_num=5,blk_start=0):
        """"Present Ticket Staking Rewards as DCR reward and ROI
        INPUTS:
            tic_num   = int, ticket count to check up to and including (1x to tic_num_x)
            blk_start = start of staking for cumulative rewards
                            if <= zero, defaults to current block
        """

        df          = self.df
        blk_cur     = df['blk'].iloc[-2]
        if blk_start <= 0:
            blk_start = blk_cur
        sply        = dcr_add_metrics().metric_staking_return(df,tic_num,blk_start)

        #build chart dataset for DCR reward
        x_data = y_data = name_data = width_data = opacity_data = dash_data = legend_data =[]
        for i in range(1,tic_num+1): #
            _name        = 'tic_' + str(i)
            x_data      = x_data        + [sply['date']]
            y_data      = y_data        + [sply[_name]]
            name_data   = name_data     + [str(i) + 'x Tickets (LHS)']
            width_data  = width_data    + [2]
            opacity_data= opacity_data  + [1]
            dash_data   = dash_data     + ['solid']
            legend_data = legend_data   + [True]

        #Add in implied and actual ticket price
        x_data      = x_data        + [sply['date'],df['date'],sply['date'],sply['date']]
        y_data      = y_data        + [sply['tic_price_implied'],df['tic_price_avg'],sply['tic_roi'],sply['tic_roi_cum']]
        name_data   = name_data     + ['Estimated Ticket Price (LHS)','Ticket Price (LHS)','Annualised Ticket ROI (RHS)','Cumulative Ticket ROI (RHS)']
        width_data  = width_data    + [2,2,5,5]
        opacity_data= opacity_data  + [1,1,1,1]
        dash_data   = dash_data     + ['dash','solid','dash','solid']
        legend_data = legend_data   + [True,True,True,True]


        loop_data=[range(0,tic_num+2),[tic_num+2,tic_num+3]]
        color_data = [
            #'rgb(88, 42, 81)',
            'rgba(127, 44, 87, 0.7)',   
            #'rgb(164, 47, 82)',
            'rgba(194, 59, 67, 0.7)',
            #'rgb(215, 83, 42)',
            'rgba(223, 115, 0, 0.7)',
            #'rgb(216, 151, 0)',
            'rgba(193, 187, 0, 0.7)',
            #'rgb(149, 222, 0)',
            'rgba(29, 255, 0, 0.7)',
            'rgb(0,0,0)',
            'rgb(0,0,0)',
            'rgb(209,  41, 94)', #Turquoise (Inverted) 
            'rgb(209,  41, 94)', #Turquoise (Inverted) 
        ]
        fill_data = [
            'tozeroy','tonexty','tonexty','tonexty','tonexty',
            #'tonexty','tonexty','tonexty','tonexty','tonexty',
            'none','none','none'
        ]
        #Invert Colors for Light Theme
        #color_data = self.color_invert(color_data)
        title_data = [
            '<b>Decred Staking Reward Estimate<b>',
            '<b>Date</b>',
            '<b>Ticket Price (DCR)<br />Cumulative Staking Reward (DCR)</b>',
            '<b>Staking ROI in DCR (%)</b>',
            ]
        range_data = [[self.start,1],[0,250],[0,0.2]]
        autorange_data = [True,False,False]
        type_data = ['date','linear','linear']
        fig = self.chart.subplot_lines_doubleaxis_1st_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_xaxes(dtick='M12',tickformat='%d-%b-%y',showgrid=True)
        fig.update_yaxes(dtick=0.01,showgrid=True,secondary_y=True,tickformat='%',color='rgb(209,  41, 94)')
        fig.update_yaxes(dtick=25,showgrid=False,secondary_y=False)
        self.add_slider(fig)

        #Write out html chart
        chart_name = '/stakingroi_performance'
        self.write_html(fig,chart_name)

        return fig

    def dcr_stake_later(self,tic_num=5,blk_start=0):
        """"Present Difference in staking ROI for starting each window
        INPUTS:
            tic_num   = int, ticket count to check up to and including (1x to tic_num_x)
            blk_start = start of staking for cumulative rewards
                            if <= zero, defaults to current block
        """

        df          = self.df
        blk_cur     = df['blk'].iloc[-2]
        if blk_start <= 0:
            blk_start = blk_cur
        sply        = dcr_add_metrics().metric_staking_return(df,tic_num,blk_start)

        #build chart dataset for DCR reward
        x_data = y_data = name_data = width_data = opacity_data = dash_data = legend_data =[]
        for i in range(1,tic_num+1): #
            _name        = 'tic_' + str(i)
            x_data      = x_data        + [sply['date']]
            y_data      = y_data        + [sply[_name]]
            name_data   = name_data     + [str(i) + 'x Tickets']
            width_data  = width_data    + [2]
            opacity_data= opacity_data  + [1]
            dash_data   = dash_data     + ['solid']
            legend_data = legend_data   + [True]

        #Add in implied and actual ticket price
        x_data      = x_data        + [sply['date'],df['date'],sply['date']]
        y_data      = y_data        + [sply['tic_price_implied'],df['tic_price_avg'],sply['tic_roi']]
        name_data   = name_data     + ['Estimated Ticket Price','Actual Ticket Price','Ticket ROI (RHS)']
        width_data  = width_data    + [2,2,5]
        opacity_data= opacity_data  + [1,1,1]
        dash_data   = dash_data     + ['dash','solid','solid']
        legend_data = legend_data   + [True,True,True]


        loop_data=[range(0,tic_num+2),[tic_num+2]]
        color_data = [
            #'rgb(88, 42, 81)',
            'rgba(127, 44, 87, 0.7)',   
            #'rgb(164, 47, 82)',
            'rgba(194, 59, 67, 0.7)',
            #'rgb(215, 83, 42)',
            'rgba(223, 115, 0, 0.7)',
            #'rgb(216, 151, 0)',
            'rgba(193, 187, 0, 0.7)',
            #'rgb(149, 222, 0)',
            'rgba(29, 255, 0, 0.7)',
            'rgb(0,0,0)',
            'rgb(0,0,0)',
            'rgb(209,  41, 94)', #Turquoise (Inverted) 
        ]
        fill_data = [
            'tozeroy','tonexty','tonexty','tonexty','tonexty',
            #'tonexty','tonexty','tonexty','tonexty','tonexty',
            'none','none','none'
        ]
        #Invert Colors for Light Theme
        #color_data = self.color_invert(color_data)
        title_data = [
            '<b>Decred Staking Reward Estimate<b>',
            '<b>Date</b>',
            '<b>Ticket Price (DCR)<br />Cumulative Staking Reward (DCR)</b>',
            '<b>Staking ROI in DCR (%)</b>',
            ]
        range_data = [[self.start,1],[0,250],[0,0.2]]
        autorange_data = [True,False,False]
        type_data = ['date','linear','linear']
        fig = self.chart.subplot_lines_doubleaxis_1st_area(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            fill_data
            )
        fig.update_xaxes(dtick='M12',tickformat='%d-%b-%y',showgrid=True)
        fig.update_yaxes(dtick=0.01,showgrid=True,secondary_y=True,tickformat='%',color='rgb(209,  41, 94)')
        fig.update_yaxes(dtick=25,showgrid=False,secondary_y=False)
        self.add_slider(fig)

        #Write out html chart
        chart_name = '/stakelater_performance'
        self.write_html(fig,chart_name)

        return fig


    def miner_hardware_estimate(self,metric='_cnt',overhead=0.05,power_usdkWh=0.05,op_overhead=0.05):
        """
        Plots series of chart showing the number of ASIC devices to match current hashrate       
        INPUTS:
        metric          = metric to be plotted, default = device count
                        Options
                            _cnt            = device count (default)
                            _cost           = aggregate device cost
                            _power_kWh       = aggregate daily power consumption kW
                            _CAPEX          = aggregate CAPEX
                            _OPEX           = aggregate OPEX
                            _pow_prof       = PoW profitability (as proportion of CAPEX)
                            _pow_prof_cum   = cumulative protifitability
        overhead        = float, assumed ratio of hardware CAPEX applied for extra facility costs
                        = default of 5%
        power_usdkWh    = float, assumed power price in $/kWh
                        = default of $0.05/kWh
        """

        df = self.df
        df = df[df['pow_hashrate_THs_avg']>1]
        miners               = pd.read_csv(r'../resources/data/dcr_mining_hardware.csv')
        miners['TH_per_kWh'] = miners['hashrate_THs']/miners['power_kWh']
        miners[['max_cnt','avg_cnt']]    = 0


        #Cycles through each device in asic dataframe
        #Adds column to df for each 'device_cnt' = hashrate / unit hashpower
        #Adds column to df for each 'device_cost' = device_cnt * device_unitcost
        #Adds column to df for each 'device_power' = device_cnt * device_power_kWh
        print("...Calculating Performance for Mining Hardware")
        count = 0
        for i in miners['model']:
            #Device Count
            name_cnt        = i +'_cnt'
            df[name_cnt]    = df['pow_hashrate_THs_avg'] / miners.loc[count,'hashrate_THs']
            df[name_cnt]    = df[name_cnt].apply(np.ceil) #round to nearest integer
            #Device Purchase Cost
            name_cost       = i + '_cost'
            df[name_cost]   = df[name_cnt] * miners.loc[count,'device_price_usd']
            #Device Power Consumption per Day (kW)
            name_power      = i + '_power_kWh'
            df[name_power]  = df[name_cnt] * miners.loc[count,'power_kWh'] * 24
            #CAPEX and OPEX
            name_CAPEX      = i + '_CAPEX'
            name_OPEX       = i + '_OPEX'
            #CAPEX (aggregate) = ASIC cost * (1 + overhead factor)
            df[name_CAPEX]  = df[name_cost] * (1 + overhead)
            #OPEX (aggregate) = 
            #           ASIC count * 24hrs * ASIC_kWh consumption * Power Price
            #           + overhead/365 * device Capital Cost
            df[name_OPEX]  = df[name_power] * power_usdkWh + op_overhead/365 * df[name_cost]
            #Profitability per day per device (as proportion of device cost)
            #(Income - OPEX)_aggregate / CAPEX_aggregate
            name_prof       = i + '_pow_prof'
            df[name_prof]   = (df['PoW_income_usd'] - df[name_OPEX]) / df[name_CAPEX] #(Income - OPEX)/CAPEX
            #Record max and average device count
            _df             = df[df['blk']>=miners.loc[count,'blk_start']]   
            miners.loc[count,'max_cnt']         = int(_df[name_cnt].max())
            miners.loc[count,'avg_cnt']         = int(_df[name_cnt].mean())
            count += 1
        miners['max_CAPEX']     = miners['max_cnt'] * miners['device_price_usd'] * (1+overhead)
        miners['max_OPEX']      = miners['max_cnt'] * miners['power_kWh'] * 24 * power_usdkWh
        miners['max_OPEX_ratio']  = miners['max_OPEX'] / miners['max_CAPEX']
        print('...Calculating Miner Hardware Metrics')
        print(miners)
        self.miners = miners

        #Build Chart
        loop_data = [[count],range(0,count)]
        #Create Loop to produce the following charts:
        #   Chart 1 = Device Count
        #   Chart 2 = CAPEX Investment
        #   Chart 3 = OPEX Investment (power + )
        def build_xyname(miners_df,suffix):
            """
            builds x_data, y_data and name_data
            """
            miners = miners_df
            x_data = y_data = name_data = []
            for i in miners['model']:
                #Consider only data after device was launched
                blk_start = float(miners[miners['model']==i]['blk_start'])
                _df       = df[df['blk']>blk_start]
                #Add cumulative profitability
                name_prof            = i + '_pow_prof'
                name_prof_cum        = i + '_pow_prof_cum'
                _df[name_prof_cum]   = _df[name_prof].cumsum() #cumulative sum
                #Build chart datasets
                name_data = name_data + [i]
                x_data = x_data + [_df['date']]
                y_data = y_data + [_df[i+metric]]
            return x_data, y_data, name_data
            
        #Build X, Y and name datasets + add hashrate for 2nd axis
        x_data      = build_xyname(miners,metric)[0] + [df['date']]
        y_data      = build_xyname(miners,metric)[1] + [df['PriceUSD']]
        name_data   = build_xyname(miners,metric)[2] + ['DCR/USD Price']
        
        color_data = [
            'rgb(255, 0, 0)','rgb(255, 0, 99)','rgb(255, 46, 174)',
            'rgb(230, 107, 236)','rgb(168, 149, 255)','rgb(87, 179, 255)',
            'rgb(0, 200, 255)','rgb(0, 215, 255)','rgb(0, 255, 177)',
            'rgb(124, 238, 115)','rgb(176, 216, 56)','rgb(218, 190, 0)',
            'rgb(252, 158, 0)','rgb(255, 120, 48)','rgb(255, 73, 91)',
            'rgb(255, 4, 139)','rgb(255, 0, 189)',
            'rbg(255,255,255)',
            ]
        color_data[-2] = check_standard_charts(self.theme).color_invert(color_data)[-2]
        dash_data = [
            'dash','dash','dash',
            'solid','solid','solid',
            'solid','solid','solid',
            'solid','solid','solid',
            'solid','solid','solid',
            'solid','solid',
            'solid'
            ]
        width_data = [
            1,1,1,
            1,1,1,
            1,1,1,
            1,1,1,
            1,1,2,
            3,3,
            3,4,
            ]
        opacity_data = [
            1,1,1,
            1,1,1,
            1,1,1,
            1,1,1,
            1,1,1,
            1,1,
            1,1,
            ]
        legend_data = [
            True,True,True,
            True,True,True,
            True,True,True,
            True,True,True,
            True,True,True,
            True,True,
            True,True,
            ]       
        title_data = [
            '<b>Decred Mining Hardware Device Count</b>',
            '<b>Date</b>',
            '<b>DCR Price (USD)</b>',
            '<b>Mining Hardware Count</b>',]
        if metric == '_cost':
            title_data[0] = '<b>Decred Total PoW Mining Hardware Value</b>'
            title_data[3] = '<b>Mining Hardware Purchase Value (USD)</b>'
        elif metric == '_power_kWh':
            title_data[0] = '<b>Decred Total Daily PoW Power Consumption</b>'
            title_data[3] = '<b>Estimated Daily Power Consumption (kWh)</b>'
        elif metric == '_CAPEX':
            title_data[0] = '<b>Decred Total PoW Mining CAPEX Investment</b>'
            title_data[3] = '<b>Estimated Total CAPEX Investment (USD)</b>'
        elif metric == '_OPEX':
            title_data[0] = '<b>Decred Total PoW Mining OPEX Investment</b>'
            title_data[3] = '<b>Estimated Daily OPEX Expense (USD)</b>'
        elif metric == '_pow_prof':
            title_data[0] = '<b>Decred Daily Mining Profitability</b>'
            title_data[3] = '<b>Estimated Daily PoW Profitability (as Proportion of CAPEX)</b>'
        elif metric == '_pow_prof_cum':
            title_data[0] = '<b>Decred Cumulative Mining Profitability</b>'
            title_data[3] = '<b>Estimated Cumulative PoW Profitability (as Proportion of CAPEX)</b>'
        
        range_data = [[self.start,self.last],[0,120],[0,14]]
        autorange_data = [False,True,True]
        type_data = ['date','linear','log']
        if metric == '_pow_prof':
            type_data[2] = 'linear'
        elif metric == '_pow_prof_cum':
            loop_data[1] = [*loop_data[1]] + [count+1] #Add Breakeven
            x_data       = x_data    + [[self.start,self.last]]
            y_data       = y_data    + [[1,1]]
            name_data    = name_data + ['Break-even']
            color_data   = color_data+ ['rgb(255, 20, 60)'] #Red
            dash_data    = dash_data + ['dash']
        elif metric == '_OPEX':
            loop_data[1] = [*loop_data[1]] + [count+1] #Add Breakeven
            x_data       = x_data    + [df['date']]
            y_data       = y_data    + [df['PoW_income_usd']]
            name_data    = name_data + ['PoW Block Reward']
            color_data   = color_data+ ['rgb(255, 20, 60)'] #Red
            dash_data    = dash_data + ['solid']

        fig = check_standard_charts(self.theme).subplot_lines_doubleaxis(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data
            )
        #Increase tick spacing
        fig.update_xaxes(showgrid=True)
        fig.update_yaxes(secondary_y=False,showgrid=False)
        fig.update_yaxes(secondary_y=True,showgrid=True)

        #Write out html chart
        chart_name = '/minerhardware_performance' + metric
        self.write_html(fig,chart_name)
        
        return fig


    def add_volume_bars(self,fig,x_data,y_data,color_data,name_data,loop_data):

        """ =================================
            ADD VOLUME BAR CHARTS
            INPUTS:
                fig = Figure to add columns to
                x_data      = list of x data series for columns
                y_data      = list of y data series for columns
                color_data  = list of colors for columns
                name_data   = list of name strings for columns
                loop_data   = List of index for above lists
        ================================="""
        for i in loop_data:
            fig.add_trace(go.Bar(
                x=x_data[i],
                y=y_data[i],
                name=name_data[i],
                opacity=0.75,
                marker_color=color_data[i],
                secondary_y=True
            ))
        fig.update_layout(barmode='stack',bargap=0.01)#,yaxis2=dict(side="right",position=0.15))
        
    def hist_calc_multiples(self,metric):
        """
        Calculates the multiple values for use in histogram charts and returns
        DataFrame with metric bins, frequency count and cumulative distribution
        """
        df = self.df

        if metric == 'Mayer':
            #Mayer Multiple
            df['Mayer'] = df['PriceUSD']/df['PriceUSD'].rolling(200).mean()
            response = general_helpers().metric_histogram(df,'Mayer',0.1,3.0,0.1)
            response.columns = ['Mayer','Mayer_count','Mayer_cdf']
            
        elif metric == 'MVRV':
            response = general_helpers().metric_histogram(df,'CapMVRVCur',0.1,3.0,0.1)
            response.columns = ['MVRV','MVRV_count','MVRV_cdf']

        elif metric == 'S2F':
            #S2F Multiple
            df = df[['date','age_sply','S2F','PriceUSD','SplyCur','CapMrktCurUSD']]
            df = df.dropna(axis=0)
            x = 'S2F'
            y = 'CapMrktCurUSD'
            analysis    = regression_analysis().ln_regression_OLS(df,x,y,True)
            df          = analysis['df']
            reg_model   = analysis['model']
            df['S2F_Price_predict'] = df['S2F_CapMr_predict'] / df['SplyCur']
            response = general_helpers().metric_histogram(df,'S2F_CapMr_multiple',0.1,3.0,0.1)
            response.columns = ['S2F','S2F_count','S2F_cdf']

        elif metric == 'Puell':
            df['Puell'] = 0
            for i in df.index:
                _a = min(i,364)
                _b = df['DailyIssuedUSD'].rolling(_a).mean().loc[i]
                _c = df.loc[i,'DailyIssuedUSD']
                df.loc[i,'Puell'] = _c / _b
            response = general_helpers().metric_histogram(df,'Puell',0.1,3.0,0.1)
            response.columns = ['Puell','Puell_count','Puell_cdf']

        elif metric == 'Contractor':
            df['Contractor'] = df['PriceUSD'] / df['PriceUSD'].rolling(30).mean()
            response = general_helpers().metric_histogram(df,'Contractor',0.1,2.0,0.1)
            response.columns = ['Contractor','Contractor_count','Contractor_cdf']


        elif metric == '142d_tic':
            df['tic_usd_cost_142sum'] = df['tic_usd_cost'].rolling(142).sum()/df['dcr_sply']
            df['142d_tic'] = df['PriceUSD'] / (df['tic_usd_cost_142sum']*0.500)
            response = general_helpers().metric_histogram(df,'142d_tic',0.1,2.0,0.1)
            response.columns = ['142d_tic','142d_tic_count','142d_tic_cdf']

        return response

    def hist_metrics(self,metrics):
        """
        Produces a histogram and cumulative distribution plot for a set of metrics
        INPUTS:
            metric  = [str,str,...], Series of string metrics to be plotted.
                        Mayer       = mayer multiple
                        CapMVRVCur  = MVRV ratio
                        S2F         = S2F Multiple
                        Puell       = Puell Multiple
                        Contractor  = Contractor Multiple
                        142d_tic    = 142day Ticket Multiple (50%)
        """     

        hist = pd.DataFrame() #final histogram DataFrame
        count = 0
        x_data_temp = y_data_bar = y_data_cdf = name_data_bar = name_data_cdf = []
        for i in metrics:
            hist_temp = pd.DataFrame() #final histogram DataFrame
            hist_temp = self.hist_calc_multiples(i)
            if count == 0:
                j = i #store metric as 'previous' for merge
                hist = hist_temp
            else:
                hist = hist.merge(hist_temp,left_on=j,right_on=i,copy=False)
                j = i #store metric as 'previous' for merge
            count += 1
            #Use hist_temp to build up x_data and y_data
            #requires x_data to append itself, y_bar appends y_cdf
            x_data_temp     = x_data_temp   + [pd.DataFrame(hist_temp[i]).iloc[:,0]]
            y_data_bar      = y_data_bar    + [pd.DataFrame(hist[i + '_count']).iloc[:,0]]
            y_data_cdf      = y_data_cdf    + [pd.DataFrame(hist[i + '_cdf']).iloc[:,0]]
            name_data_bar   = name_data_bar + [i + ' Histogram']
            name_data_cdf   = name_data_cdf + [i + ' CDF']
            
        #print(count)
        loop_bar = range(0,count)
        loop_cdf = range(count,(count)*2)

        #Build Lists for chart inputs
        loop_data   =[loop_bar,loop_cdf]
        #x_data = Metric Bins on order
        #           metric_1, metric_2...metric_n (repeat for cdf)
        x_data      = x_data_temp + x_data_temp
        #x_data = frequency count THEN cdf in order 
        #           freq_1, freq_2...freq_n THEN cdf_1, cdf_2...
        y_data      = y_data_bar + y_data_cdf
        name_data   = name_data_bar + name_data_cdf

        a = len(metrics)
        width_data   = [2] * a + [6] * a
        opacity_data = [1] * a * 2
        dash_data    = ['solid'] * a * 2

        color_data = [
            'rgb(255, 102, 0)' ,            #Burnt Orange
            'rgb(41, 112, 255)',            #Key Blue
            'rgb(46, 214, 161)',            #Turquoise
            'rgb(255, 192, 0)',             #Treasury Yellow
            'rgb(114, 49, 163)',            #PoS_Purple
            'rgb(65, 191, 83)',             #Decred Green
        ]
        color_data = color_data[:count] + color_data[:count]
        #Invert Colors for Light Theme
        color_data = self.color_invert(color_data)
        legend_data = [True] * a * 2
        title_data = [
            '<b>Decred Probability Function</b>',
            '<b>Metric Value</b>',
            '<b>Daily Frequency</b>',
            '<b>Cumulative Distribution</b>']
        range_data = [[0,3],[-2,3],[0,1]]
        autorange_data = [False,True,False]
        type_data = ['linear','linear','linear']
        bar_type = 'group'
        fig = self.chart.subplot_hist_doubleaxis(
            title_data, range_data ,autorange_data ,type_data,
            loop_data,x_data,y_data,name_data,color_data,
            dash_data,width_data,opacity_data,legend_data,
            bar_type
            )
        fig.update_xaxes(showgrid=True,dtick=0.2)
        fig.update_yaxes(showgrid=False,secondary_y=False)
        fig.update_yaxes(showgrid=True,secondary_y=True,dtick=0.1,tickformat=",.0%")
        self.add_slider(fig)

        
        #Write out html chart
        chart_name = '/hist_metrics'
#         self.write_html(fig,chart_name)

        return fig


repo_dir = os.environ["GITHUB_REPO"]


#Start charting suite
dcr_charts = dcr_chart_suite('light')

#Export Mayer Multiple
fig_mayer_multiple = dcr_charts.mayer_multiple()
fig_mayer_multiple.write_json(f'{repo_dir}/data/mayermultiple_pricing_usd.json')

# Export both realised cap and MVRV (pricing and valuation)
fig_mvrv_valuation = dcr_charts.mvrv(0)
fig_mvrv_valuation.write_json(f'{repo_dir}/data/mvrv_valuation_usd.json')
fig_mvrv_pricing = dcr_charts.mvrv(1)
fig_mvrv_pricing.write_json(f'{repo_dir}/data/mvrv_pricing_usd.json')

# Export both Relative Realised Cap (valuation and pricing)
fig_relative_valuation = dcr_charts.mvrv_relative_btc(0)
fig_relative_valuation.write_json(f'{repo_dir}/data/mvrv_valuation_btc.json')
fig_relative_pricing = dcr_charts.mvrv_relative_btc(1)
fig_relative_pricing.write_json(f'{repo_dir}/data/mvrv_pricing_btc.json')
# fig_relative_pricing.show()
# fig_relative_valuation.show()

# Export Market Realised Gradient Oscilator both 28 and 142
market_oscillator_28 = dcr_charts.mrkt_real_gradient_usd(28)
market_oscillator_28.write_json(f'{repo_dir}/data/mrktrealgrad_28_day_oscillator_usd.json')
market_oscillator_142 = dcr_charts.mrkt_real_gradient_usd(142)
market_oscillator_142.write_json(f'{repo_dir}/data/mrktrealgrad_142_day_oscillator_usd.json')
# market_oscillator_142.show()
# market_oscillator_28.show()

# Export Unrealised Profit and Loss
unrealised_pnl = dcr_charts.unrealised_PnL()
unrealised_pnl.write_json(f'{repo_dir}/data/unrealisedpnl_oscillator_usd.json')