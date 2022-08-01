from numpy import NaN
import streamlit as st
import yfinance as yf
import pandas as pd


header = st.container()
dataset = st.container()
ticker_az = st.container()
note = st.container()

@st.cache
def get_data():
    # Pe
    pe = pd.read_html('https://www.multpl.com/s-p-500-pe-ratio/table/by-year')
    df_pe = pd.DataFrame(pe[0])
    df_pe['Value Value'] = df_pe['Value Value'].str.replace('estimate', '')
    df_pe['Value Value'] = pd.to_numeric(df_pe['Value Value'])
    df_pe.rename(columns = {'Value Value':'Pe'}, inplace = True)

    # Earning Yield %
    ey = pd.read_html('https://www.multpl.com/s-p-500-earnings-yield/table/by-year')
    df_ey = pd.DataFrame(ey[0])
    df_ey['Value Value'] = df_ey['Value Value'].str.replace('%', '')
    df_ey['Value Value'] = df_ey['Value Value'].str.replace('estimate', '')
    df_ey['Value Value'] = pd.to_numeric(df_ey['Value Value']) / 100
    df_ey.rename(columns = {'Value Value':'Earning_y'}, inplace = True)

    # Price to book value
    pb = pd.read_html('https://www.multpl.com/s-p-500-price-to-book/table/by-year')
    df_pb = pd.DataFrame(pb[0])
    df_pb['Value Value'] = df_pb['Value Value'].str.replace('%', '')
    df_pb['Value Value'] = df_pb['Value Value'].str.replace('estimate', '')
    df_pb['Value Value'] = pd.to_numeric(df_pb['Value Value'])
    df_pb.rename(columns = {'Value Value':'Price_book'}, inplace = True)

    # US real GDP growth %
    gr = pd.read_html('https://www.multpl.com/us-real-gdp-growth-rate/table/by-year')
    df_gr = pd.DataFrame(gr[0])
    df_gr['Value Value'] = df_gr['Value Value'].str.replace('%', '')
    df_gr['Value Value'] = df_gr['Value Value'].str.replace('estimate', '')
    df_gr['Value Value'] = pd.to_numeric(df_gr['Value Value']) / 100
    df_gr.rename(columns = {'Value Value':'real_gdp'}, inplace = True)

    # US inflazione
    infl = pd.read_html('https://www.multpl.com/inflation/table/by-year')
    df_infl = pd.DataFrame(infl[0])
    df_infl['Value Value'] = df_infl['Value Value'].str.replace('%', '')
    df_infl['Value Value'] = df_infl['Value Value'].str.replace('estimate', '')
    df_infl['Value Value'] = pd.to_numeric(df_infl['Value Value']) / 100
    df_infl.rename(columns = {'Value Value':'inflazione'}, inplace = True)

    # 10 yr interest rate
    ir = pd.read_html('https://www.multpl.com/10-year-treasury-rate/table/by-year')
    df_ir = pd.DataFrame(ir[0])
    df_ir['Value Value'] = df_ir['Value Value'].str.replace('%', '')
    df_ir['Value Value'] = pd.to_numeric(df_ir['Value Value']) / 100
    df_ir.rename(columns = {'Value Value':'interest_rate'}, inplace = True)

    # 10 yr real interest rate TIPS
    tips = pd.read_html('https://www.multpl.com/10-year-real-interest-rate/table/by-year')
    df_tips = pd.DataFrame(tips[0])
    df_tips['Value Value'] = df_tips['Value Value'].str.replace('%', '')
    df_tips['Value Value'] = pd.to_numeric(df_tips['Value Value']) / 100
    df_tips.rename(columns = {'Value Value':'tips'}, inplace = True)

    # Ampliamento df Price earnings
    df_pe['price_book'] = df_pb['Price_book']
    df_pe['earning_y'] = df_ey['Earning_y']
    df_pe['real_gdp'] = df_gr['real_gdp']
    df_pe['inflazione'] = df_infl['inflazione']
    df_pe['Roe'] = df_pe['price_book'] / df_pe['Pe']
    df_pe['interest_rate'] = df_ir['interest_rate']
    df_pe['tips'] = df_tips['tips']

    # Df intermedio
    partenza = df_pe.head(24)
    # Df finale
    df_ke = pd.DataFrame(columns = ['Date', 'earning_yield', 'g', 'Roe', 'gr', 'expected_inflation', 'interest_rate', 'tips', 'tips_spread'])
    # Inserire valori nel Df finale
    df_ke['Date'] = partenza['Date']
    df_ke['earning_yield'] = partenza['earning_y']
    df_ke['tips'] = partenza['tips']
    df_ke['interest_rate'] = partenza['interest_rate']


    for x in df_ke['Roe']:
        df_ke['Roe'] = partenza['Roe'].mean()

    for x in df_ke['gr']:
        df_ke['gr'] = partenza['real_gdp'].mean()

    e_infl = []
    z = 0
    for x in partenza['inflazione']:
        inflazione = (partenza.iloc[(0+z):(5+z)]['inflazione'].mean())
        z = z + 1
        e_infl.append(inflazione)

    df_ke['expected_inflation'] = e_infl

    # Calcoli tra colonne
    df_ke['g'] = df_ke['gr'] + df_ke['expected_inflation']
    df_ke['tips_spread'] = df_ke['interest_rate'] - df_ke['tips']
    df_ke['Ker'] = df_ke['earning_yield'] * (1 - (df_ke['g'] / df_ke['Roe'])) + df_ke['gr']

    # Inflation adjusted erp
    df_ke['erp'] = df_ke['Ker'] - df_ke['tips']
    # Ke con expected inflation
    df_ke['Ke_exp_inflation'] = df_ke['Ker'] + df_ke['expected_inflation']
    # Ke con tips spread
    df_ke['Ke_tips_spread'] = df_ke['Ker'] + df_ke['tips_spread']
    # Inflation adjusted erp
    df_ke['erp'] = df_ke['Ker'] - df_ke['tips']

    # Conversione Date
    d = 0
    for x in df_ke['Date']:
        df_ke['Date'][d] = df_ke['Date'][d].replace(x, x[-4:])
        d = d + 1

    df_ke['Date'] = pd.to_numeric(df_ke['Date'])

    return df_ke


df_ke = get_data()

# Dati Ke
# Real Ke
ker_attuale = round(df_ke['Ker'][0] *100, 2)
ker_medio = round(df_ke['Ker'].mean() *100, 2)
Ker_delta = round((df_ke['Ker'][0] / df_ke['Ker'][1] -1)*100, 2)

# Ke TIPS
Ke_tips_spread_attuale = round(df_ke['Ke_tips_spread'][0] *100, 2)
Ke_tips_spread_medio = round(df_ke['Ke_tips_spread'].mean() *100, 2)
Ke_tips_spread_delta = round((df_ke['Ke_tips_spread'][0] / df_ke['Ke_tips_spread'][1] -1)*100, 2)

# Ke expected inflation 5 yr
Ke_exp_inflation_attuale = round(df_ke['Ke_exp_inflation'][0] *100, 2)
Ke_exp_inflation_medio = round(df_ke['Ke_exp_inflation'].mean() *100, 2)
Ke_exp_inflation_delta = round((df_ke['Ke_exp_inflation'][0] / df_ke['Ke_exp_inflation'][1] -1)*100, 2)



with header:
    st.title('Cost of equity')
    col_x, col_y, col_z = st.columns(3)
    col_d, col_e, col_f = st.columns(3)
    
    col_x.metric('Real Ke corrente', f'{ker_attuale}%', f'{Ker_delta}%')
    col_y.metric('Ke corrente (TIPS spread)', f'{Ke_tips_spread_attuale}%', f'{Ke_tips_spread_delta}%')
    col_z.metric('Ke corrente (Inflazione attesa)', f'{Ke_exp_inflation_attuale}%', f'{Ke_exp_inflation_delta}%')
    col_d.metric('Real Ke medio', f'{ker_medio}%')
    col_e.metric('Ke medio (TIPS spread)', f'{Ke_tips_spread_medio}%')
    col_f.metric('Ke medio (Inflazione attesa)', f'{Ke_exp_inflation_medio}%')

minimo = int(df_ke['Date'][20])
massimo = int(df_ke['Date'][1])


with dataset:
    st.header('Implied real cost of equity')
    st.latex(r'''Ker = \frac{1}{PE} (1 - \frac{g}{Roe}) + gr''')
    st.write('''Il seguente grafico mostra il \'Real Ke\' degli ultimi 20 anni, calcolato attraverso
    la metodologia descritta da Marc H. Goedhart, Timothy M. Koller e Zane D. Williams (McKinsey & Company).
    Per maggiori informazioni consultare la seguente [pagina](https://www.mckinsey.com/business-functions/strategy-and-corporate-finance/our-insights/the-real-cost-of-equity).''')
    st.write('ERP = Equity Risk Premium')
    st.write('TIPS = Treasury Inflation-Protected Security')
             
    
    
    col1, col2, col3 = st.columns(3)
    slides = col1.slider('', min_value=minimo, max_value=massimo, value=(minimo, massimo))

    # Ker decomposto
    stack_ker = df_ke[['Date', 'tips', 'erp']].loc[1:20]
    stack_ker.rename(columns={'tips': 'TIPS', 'erp': 'ERP'}, inplace=True)
    stack_ker.set_index('Date', inplace = True)
    st.bar_chart(stack_ker.loc[slides[1]:slides[0]])

    


with ticker_az:
    st.header('Calcolatore cost of equity per azienda scelta')
    parametro = st.text_input(label='Ticker', placeholder='Inserire ticker es. GOOGL')

    # Singola azienda
    if len(parametro) == 0:
        ticker = NaN
        stock_info = NaN
    else:
        ticker = yf.Ticker(parametro)
        stock_info = ticker.info

    # Ke singola azienda
    if len(parametro) == 0:
        beta = 0
    else:
        beta = stock_info['beta']
    
    ker_azienda = (df_ke['erp'][0] * beta) + df_ke['tips'][0] 
    ke_azienda_Tips_s = ker_azienda + df_ke['tips_spread'][0]
    ke_azienda_ex_inf = ker_azienda + df_ke['expected_inflation'][0]

    st.text(f'{parametro} Beta: {beta}')

    col_1, col_2, col_3 = st.columns(3)

    if beta == 0:
        col_1.metric('Real Cost of equity', 'N/A')    
    else:
        col_1.metric('Real Cost of equity', f'{round(ker_azienda*100, 2)}%')

    if beta == 0:
        col_2.metric('Cost of equity (TIPS spread)', 'N/A')    
    else:
        col_2.metric('Cost of equity (TIPS spread)', f'{round(ke_azienda_Tips_s*100, 2)}%')

    if beta == 0:
        col_3.metric('Cost of equity (Inflazione attesa)', 'N/A')    
    else:
        col_3.metric('Cost of equity (Inflazione attesa)', f'{round(ke_azienda_ex_inf*100, 2)}%')


with note:    
    st.markdown("""---""")
    st.write('**Precisazioni:**')
    st.markdown('* l\'inflazione attesa viene calcolata come la media degli ultimi 5 anni, per ogni anno, dell\'inflazione effettivamente registrata')
    st.markdown('* la variazione esposta sotto i vari risultati rappresenta il delta % tra il valore corrente e l\'ultimo valore registrato')
    st.markdown('* i dati utilizzati per il calcolo del cost of equity riguardano lo S&P 500 e l\'economia degli USA')
    st.markdown('* utilizzare tickers di Yahoo Finance')
