import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, dash_table, Input, Output, State
import os
from datetime import datetime
import io

# Caminho do arquivo Excel e imagem
caminho_arquivo = r"C:\Users\gabriel.brito.DF\Desktop\Desenvolvimento Vs\DashBord Gestão de Problemas\Controle Ligero Gestao de Problemas.xlsx.xlsx"
caminho_logo = "assets/logo.png"  # Copie a imagem para a pasta 'assets/'

# Carrega dados padrão
if os.path.exists(caminho_arquivo):
    df = pd.read_excel(caminho_arquivo, sheet_name="Gestão de Problemas")
    df['Data Criação'] = pd.to_datetime(df['Data Criação'], dayfirst=True, errors='coerce')
else:
    df = pd.DataFrame()

# Inicializa o app
app = dash.Dash(__name__)
app.title = "Dashboard de Problemas"

# Layout
app.layout = html.Div([
    html.Div([
        html.Img(src=app.get_asset_url("logo.png"), style={"height": "80px", "marginRight": "20px"}),
        html.H1("Dashboard de Gestão de Problemas", style={"textAlign": "center", "color": "white", "textShadow": "2px 2px 4px #000"})
    ], style={"display": "flex", "alignItems": "center", "padding": "20px", "backgroundColor": "#2a003f"}),

    html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div(['📁 Arraste ou clique para importar CSV ou Excel']),
            style={
                'width': '100%', 'padding': '10px', 'backgroundColor': '#800040',
                'color': 'white', 'textAlign': 'center', 'cursor': 'pointer',
                'marginBottom': '20px', 'borderRadius': '8px'
            },
            multiple=False
        ),

        html.Div(id='indicadores', style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': '20px'}),

        html.Div([
            html.Div([
                html.Label("Status Card", style={'color': 'white'}),
                dcc.Dropdown(id='filtro-status', multi=True)
            ], style={"flex": "1", "marginRight": "10px"}),

            html.Div([
                html.Label("Prioridade", style={'color': 'white'}),
                dcc.Dropdown(id='filtro-prioridade', multi=True)
            ], style={"flex": "1", "marginRight": "10px"}),

            html.Div([
                html.Label("Módulo Impactado", style={'color': 'white'}),
                dcc.Dropdown(id='filtro-modulo', multi=True)
            ], style={"flex": "1", "marginRight": "10px"}),

            html.Div([
                html.Label("Período", style={'color': 'white'}),
                dcc.DatePickerRange(
                    id='filtro-data', style={"width": "100%"}
                )
            ], style={"flex": "1"})
        ], style={"display": "flex", "marginBottom": "20px"})
    ], style={'padding': '20px'}),

    dcc.Graph(id='grafico-barra', config={"displayModeBar": False}),
    dcc.Graph(id='grafico-pizza', config={"displayModeBar": False}),
    dcc.Graph(id='grafico-linha', config={"displayModeBar": False}),

    html.Div([
        html.Button("Exportar CSV", id="btn-csv", style={"backgroundColor": "#800040", "color": "white", "marginRight": "10px", "borderRadius": "8px", "padding": "10px 20px", "boxShadow": "2px 2px 6px #000"}),
        html.Button("Exportar Excel", id="btn-xlsx", style={"backgroundColor": "#800040", "color": "white", "borderRadius": "8px", "padding": "10px 20px", "boxShadow": "2px 2px 6px #000"})
    ], style={"textAlign": "center", "margin": "20px"}),

    html.H3("Tabela de Registros", style={"textAlign": "center", "color": "white"}),
    dash_table.DataTable(
        id='tabela',
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'color': 'white', 'backgroundColor': '#2a003f'},
        style_header={'backgroundColor': '#800040', 'color': 'white'},
        export_format="none"
    )
], style={"backgroundColor": "#2a003f", "fontFamily": "Segoe UI, sans-serif"})

# Função de filtro
def filtrar_dados(dataframe, status, prioridade, modulo, data_ini, data_fim):
    df_filtrado = dataframe.copy()
    if status:
        df_filtrado = df_filtrado[df_filtrado['Status Card'].isin(status)]
    if prioridade:
        df_filtrado = df_filtrado[df_filtrado['Prioridade'].isin(prioridade)]
    if modulo:
        df_filtrado = df_filtrado[df_filtrado['Módulo Impactado'].isin(modulo)]
    if data_ini and data_fim:
        df_filtrado = df_filtrado[(df_filtrado['Data Criação'] >= data_ini) & (df_filtrado['Data Criação'] <= data_fim)]
    return df_filtrado

@app.callback(
    Output('filtro-status', 'options'),
    Output('filtro-prioridade', 'options'),
    Output('filtro-modulo', 'options'),
    Output('filtro-data', 'start_date'),
    Output('filtro-data', 'end_date'),
    Output('tabela', 'columns'),
    Output('tabela', 'data'),
    Output('grafico-barra', 'figure'),
    Output('grafico-pizza', 'figure'),
    Output('grafico-linha', 'figure'),
    Output('indicadores', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def atualizar_conteudo(contents, filename):
    if contents is None:
        dataframe = df.copy()
    else:
        content_type, content_string = contents.split(',')
        decoded = io.BytesIO(base64.b64decode(content_string))
        if filename.endswith('.csv'):
            dataframe = pd.read_csv(decoded)
        else:
            dataframe = pd.read_excel(decoded)

    dataframe['Data Criação'] = pd.to_datetime(dataframe['Data Criação'], dayfirst=True, errors='coerce')

    status_options = [{'label': s, 'value': s} for s in dataframe['Status Card'].dropna().unique()]
    prioridade_options = [{'label': p, 'value': p} for p in dataframe['Prioridade'].dropna().unique()]
    modulo_options = [{'label': m, 'value': m} for m in dataframe['Módulo Impactado'].dropna().unique()]

    start_date = dataframe['Data Criação'].min()
    end_date = dataframe['Data Criação'].max()

    df_filtrado = filtrar_dados(dataframe, None, None, None, start_date, end_date)

    total = len(df_filtrado)
    resolvidos = len(df_filtrado[df_filtrado['Status Card'] == 'Resolvido'])
    em_aberto = total - resolvidos
    indicadores = [
        html.Div([html.H4("Total", style={"color": "white"}), html.P(f"{total}", style={"color": "white"})]),
        html.Div([html.H4("Resolvidos", style={"color": "white"}), html.P(f"{resolvidos}", style={"color": "white"})]),
        html.Div([html.H4("Em Aberto", style={"color": "white"}), html.P(f"{em_aberto}", style={"color": "white"})])
    ]

    contagem_status = df_filtrado['Status Card'].value_counts().reset_index()
    contagem_status.columns = ['Status', 'count']
    fig_barra = px.bar(contagem_status, x='Status', y='count', title="Quantidade por Status Card",
                       labels={"Status": "Status", "count": "Quantidade"}, color_discrete_sequence=['#800040'])
    fig_barra.update_layout(plot_bgcolor='#2a003f', paper_bgcolor='#2a003f', font_color='white')

    fig_pizza = px.pie(df_filtrado, names='Prioridade', title="Distribuição por Prioridade",
                       color_discrete_sequence=px.colors.sequential.Purples)
    fig_pizza.update_layout(plot_bgcolor='#2a003f', paper_bgcolor='#2a003f', font_color='white')

    df_linha = df_filtrado.groupby(df_filtrado['Data Criação'].dt.date).size().reset_index(name='Quantidade')
    fig_linha = px.line(df_linha, x='Data Criação', y='Quantidade', title="Evolução Diária", markers=True,
                        color_discrete_sequence=['#800040'])
    fig_linha.update_layout(plot_bgcolor='#2a003f', paper_bgcolor='#2a003f', font_color='white')

    return status_options, prioridade_options, modulo_options, start_date, end_date, [{"name": i, "id": i} for i in dataframe.columns], dataframe.to_dict('records'), fig_barra, fig_pizza, fig_linha, indicadores

if __name__ == '__main__':
    app.run(debug=True)
