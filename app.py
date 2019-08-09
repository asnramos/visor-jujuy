# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import pathlib

from dash.dependencies import Input, Output, State

group_colors = {"control": "light blue", "reference": "red"}
categories = ['arq','bio','met','fis']
mapbox_access_token = 'pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w'

###########################################
# Default Settings
###########################################

map_layout = go.Layout(autosize= True,
                       height= 700,
                       hovermode='closest',
                       margin = dict(l=0,r=0,b=0,t=0),
                       showlegend = True,
                       legend = dict(x=0.8,y =0.95),
                       mapbox=dict(accesstoken = mapbox_access_token,
                                   bearing=0,
                                   center=dict(lat= -23.1877632, lon= -65.4493086),
                                   style='light',
                                   zoom=7))

map_data = []
map_data.append(go.Scattermapbox(
            lat=[], lon=[],
            mode='markers'))

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()
default_study_data = pd.read_csv(DATA_PATH.joinpath("study_default.csv"))

###############
# App Layout
###############
app.layout = html.Div(
    children=[
        # Error Message
        html.Div(id="error-message"),
        # Top Banner
        html.Div(
            className="study-browser-banner row",
            children=[
                html.H2(className="h2-title", children="Visor Ambiental Jujuy"),
                html.Div(
                    className="div-logo",
                    children=html.Img(
                        className="logo", src=app.get_asset_url("logo_jujuy.png")
                    ),
                ),
                html.H2(className="h2-title-mobile", children="Visor Ambiental Jujuy"),
            ],
        ),
        # Mapa y Filtros Principales
        html.Div(
            className="row app-body",
            children=[
                # User Controls
                html.Div(
                    className="three columns card-left",
                    children=[
                        html.Div(
                            className="bg-white user-control",
                            children=[
                                html.Div(
                                    className="padding-top-bot",
                                    style= {'font-size':'95%'},
                                    children=[
                                        html.H6("Estudios Arqueologicos"),
                                        dcc.Dropdown(id="arq-dropdown", multi= True, value=[]),
                                        html.H6("Estudios Biota"),
                                        dcc.Dropdown(id="bio-dropdown", multi= True, value=[]),
                                        html.H6("Clima y Metereologia"),
                                        dcc.Dropdown(id="met-dropdown", multi= True, value=[]),
                                        html.H6("Geografia Fisica"),
                                        dcc.Dropdown(id="fis-dropdown", multi= True, value=[])
                                    ]
                                ),
                                html.Div(
                                    className="padding-top-bot",
                                    children=[
                                        html.H6("Subir Estudio"),
                                        dcc.Upload(
                                            id="upload-data",
                                            className="upload",
                                            children=html.Div(
                                                children=[
                                                    html.P("Arrastrar o "),
                                                    html.A("Seleccionar Archivo"),
                                                ]
                                            ),
                                            accept=".csv",
                                        ),
                                    ]
                                ),
                            ],
                        )
                    ],
                ),
                # Graph
                html.Div(
                    className="nine columns card-left auto_height",
                    children=[
                        html.Div(
                            children=[
                                dcc.Graph(id="map", figure={'layout': map_layout, 'data': map_data}),
                            ],
                        )
                    ]
                ),
                dcc.Store(id="error", storage_type="memory"),
            ]
        ),
        # Detalles del estudio
        html.Div(
            className="row card",
            children=[
                html.Div(className='four columns',
                    children=[
                    html.H4('Detalles del estudio'),
                    html.Div(className= 'bg-white',
                             children=[
                                 dcc.Markdown(id='study-details-md'),
                                 html.B('Archivos:'),
                                 html.A(id='docs', children=[html.P()]),
                                 html.B('Imagenes:'),
                                 html.A(id='images', children=[html.P()])
                             ])
                    ]
                ),
                html.Div(className='eight columns',
                    children=[
                    html.H4('Visor de Documentos'),
                    dcc.Tabs(id='tabs',
                        value='doc-tab',
                        children=[
                            dcc.Tab(label='Report PDF',value='doc-tab'),
                            dcc.Tab(label='Imagen-1',value='img1-tab'),
                            dcc.Tab(label='Imagen-2',value='img2-tab')
                        ]),
                    html.Div(id='tabs-content')

                    ]
                )
            ]
        ),

    ]
)


###############
# App Callbacks
###############
# On Loading a CSV
@app.callback(
    [Output("map", "figure")],
    [Input("arq-dropdown", "value"),
     Input("bio-dropdown", "value"),
     Input("met-dropdown", "value"),
     Input("fis-dropdown", "value")])
def update_map(arq, bio, met, fis):
    study_Data = default_study_data
    map_data = []

    if (arq or bio or met or fis):
        # Plot and Group Arqueological Studies
        for c, st in enumerate(arq):
            color_i = len(arq)-1
            map_data.append(go.Scattermapbox(
                name= st,
                legendgroup= 'Arqueologicos',
                text= study_Data[study_Data.Titulo_estudio == st].Desc_punto,
                lat= study_Data[study_Data.Titulo_estudio == st].Lat,
                lon= study_Data[study_Data.Titulo_estudio == st].Lon,
                mode='markers',
                marker= dict(size= 12,
                             cmin= color_i - 3,
                             cmax= color_i + 1,
                             colorscale= 'Reds',
                             color= [color_i - c]*len(study_Data[study_Data.Titulo_estudio == st].Desc_punto)),
                hoverinfo= 'name+text',
                hoverlabel= dict(namelength = -1)
            ))

        # Plot and Group Biota Studies
        for c, st in enumerate(bio):
            color_i = len(bio)-1
            map_data.append(go.Scattermapbox(
                name= st,
                legendgroup='Biota',
                text= study_Data[study_Data.Titulo_estudio == st].Desc_punto,
                lat= study_Data[study_Data.Titulo_estudio == st].Lat,
                lon= study_Data[study_Data.Titulo_estudio == st].Lon,
                mode='markers',
                marker=dict(size=12,
                            cmin= color_i - 3,
                            cmax= color_i + 1,
                            colorscale='Greens',
                            color=[color_i - c] * len(study_Data[study_Data.Titulo_estudio == st].Desc_punto)),
                hoverinfo= 'name+text',
                hoverlabel= dict(namelength = -1)
            ))

        # Plot and Group Meteorological Studies
        for c,st in enumerate(met):
            color_i = len(met) - 1
            map_data.append(go.Scattermapbox(
                name= st,
                legendgroup='Meteorologicos',
                text= study_Data[study_Data.Titulo_estudio == st].Desc_punto,
                lat= study_Data[study_Data.Titulo_estudio == st].Lat,
                lon= study_Data[study_Data.Titulo_estudio == st].Lon,
                mode='markers',
                marker=dict(size=12,
                            cmin=color_i - 3,
                            cmax=color_i + 1,
                            colorscale='Blues',
                            color=[color_i - c] * len(study_Data[study_Data.Titulo_estudio == st].Desc_punto)),
                hoverinfo= 'name+text',
                hoverlabel= dict(namelength = -1)
            ))

        # Plot and Group Geografical Studies
        for c,st in enumerate(fis):
            color_i = len(met) - 1
            map_data.append(go.Scattermapbox(
                name= st,
                legendgroup='Geo Fisicos',
                text= study_Data[study_Data.Titulo_estudio == st].Desc_punto,
                lat= study_Data[study_Data.Titulo_estudio == st].Lat,
                lon= study_Data[study_Data.Titulo_estudio == st].Lon,
                mode='markers',
                marker=dict(size=12,
                            cmin=color_i - 3,
                            cmax=color_i + 1,
                            colorscale='Cividis',
                            color=[color_i - c] * len(study_Data[study_Data.Titulo_estudio == st].Desc_punto)),
                hoverinfo= 'name+text',
                hoverlabel= dict(namelength = -1)
            ))
    else:
        map_data.append(go.Scattermapbox(
            lat=[], lon=[],
            mode='markers'))

    return [{'layout': map_layout, 'data': map_data}]

# On Selection Study from Dropdowns
@app.callback(
    [Output("arq-dropdown", "options"),
     Output("bio-dropdown", "options"),
     Output("met-dropdown", "options"),
     Output("fis-dropdown", "options"),
     ],
    [Input("upload-data", "contents")])
def update_controls(contents):
    study_Data = default_study_data
    all_options = []

    for cat in categories:
        studies = study_Data[study_Data.Tipo_estudio == cat].Titulo_estudio.unique()
        options = []

        for st in studies:
            options.append({"label": st, "value": st})

        all_options.append(options)

    return all_options[0], all_options[1], all_options[2], all_options[3]

# On Selecting a Study from the map
@app.callback(
    [Output('study-details-md', 'children'),
     Output('docs', 'children'),
     Output('docs', 'href'),
     Output('images', 'children'),
     Output('images', 'href'),
     Output('tabs-content','children')],
    [Input('map', 'clickData'),
     Input('tabs','value')])
def display_click_data(clicked_study, tab_value):
    print(clicked_study)

    if clicked_study == None:
        details = '''
                    **Punto Seleccionado**:
                    
                    **Titulo:**
                    
                    **Descripcion:**
                    
                    **Autores**:
                    
                    **Institucion:**
                    
                    **Fuente:**
                    
                    **Pagina Web:**
                    
                    **Email Contacto:**
                    
                   '''

        docBody = html.P('')
        docHref = ''

        img1Body = html.P('')
        img1Href = ''
        img2Href = ''

        tabBody = html.P('')

    else:
        point_id = clicked_study['points'][0]['text']

        point_data = default_study_data[default_study_data.Desc_punto == point_id]

        details = f'''
                    **Punto Seleccionado:** {point_id}
                    
                    **Titulo:** {point_data.Titulo_estudio.iloc[0]}
                    
                    **Descripcion:** {point_data.Desc_estudio.iloc[0]}
                    
                    **Autores**: {point_data.Author.iloc[0]}
                    
                    **Institucion:**: {point_data.Institucion.iloc[0]}
                    
                    **Fuente:** 
                    
                    **Pagina Web:** [{point_data.Sitio.iloc[0]}]({point_data.Sitio.iloc[0]})
                    
                    **Email Contacto:** {point_data.Email.iloc[0]}
                    
                   '''

        docBody = html.P('Reporte no disponible')
        docHref = '/assets/no_data.html'

        img1Body = html.P('Imagen no disponible')
        img1Href = '/assets/no_data.html'
        img2Href = '/assets/no_data.html'

        tabBody = html.P('')
        tabSel = ''

        if point_data.Archivos.notnull().iloc[0]:
            print('Archivo OK')
            docBody = html.P(point_data.Archivos.iloc[0].rsplit('/',1)[-1])
            docHref = point_data.Archivos.iloc[0]

        if point_data.Imagen1.notnull().iloc[0]:
            print('Imagen1 OK')
            img1Body = html.P(point_data.Imagen1.iloc[0].rsplit('/', 1)[-1])
            img1Href = point_data.Imagen1.iloc[0]

            #tabBody = html.Iframe(src=img1Href, style={'width': '100%', 'height': 600})

        if point_data.Imagen2.notnull().iloc[0]:
            print('Imagen2 OK')
            img2Body = html.P(point_data.Imagen2.iloc[0].rsplit('/', 1)[-1])
            img2Href = point_data.Imagen2.iloc[0]



    if tab_value == 'doc-tab':
        tabBody = html.Iframe(src=docHref, style={'width': '100%', 'height': 600})
    elif tab_value == 'img1-tab':
        tabBody = html.Iframe(src=img1Href, style={'width': '100%', 'height': 600})
    elif tab_value == 'img2-tab':
        tabBody = html.Iframe(src=img2Href, style={'width': '100%', 'height': 600})



    return [details], docBody, docHref, img1Body, img1Href, [tabBody]


if __name__ == "__main__":
    app.run_server(debug=True)
