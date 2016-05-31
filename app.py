# -*- coding: utf-8 -*-
"""
Created on Thu May 26 22:05:49 2016

@author: Adam
"""

'''
uses embed.html and flask to render an http call to yahoo for stock quotes
'''
from flask import Flask, render_template, request

from bokeh.embed import components
#from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.templates import JS_RESOURCES, CSS_RESOURCES
from bokeh.util.string import encode_utf8

import pandas as pd
from bokeh.charts import TimeSeries, output_file, vplot

app = Flask(__name__)

colors = {
    'Black': '#000000',
    'Red':   '#FF0000',
    'Green': '#00FF00',
    'Blue':  '#0000FF',
}


def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]


@app.route("/")
def nowbegin():
    return graphstocks("AAPL")
    

def graphstocks(ssymbol):
    """ Very simple embedding of a polynomial chart"""
    # Grab the inputs arguments from the URL
    # This is automated by the button
    args = ["ADAM"] 
    args = request.args

    # Get all the form arguments in the url with defaults
    color = colors[getitem(args, 'color', 'Black')]
    _from = int(getitem(args, '_from', 0))
    to = int(getitem(args, 'to', 10))

    # Create a polynomial line graph
    #x = list(range(_from, to + 1))
    #fig = figure(title="Polynomial")
    #fig.line(x, [i ** 2 for i in x], color=color, line_width=2)
    AAPL= pd.read_csv("https://ichart.yahoo.com/table.csv?s="+ssymbol+"&a=0&b=1&c=2000&d=0&e=1&f=2010",parse_dates=['Date'])   
    data = dict(AAPL=AAPL['Adj Close'], Date=AAPL['Date'])
    tsline = TimeSeries(data,x='Date', y='AAPL', ylabel='Stock Prices', legend=True)
    #tsline=TimeSeries(data,x='Date', y=['AAPL'], color=['AAPL'], dash=['AAPL'],
   #                   title="Timeseries", ylabel = 'Stock Prices', legend=True)
#    tspoint=TimeSeries(data,x='Date',y=[ssymbol], dash=[ssymbol],title="Timeseries",ylabel='Stock Prices', legend=True)
    output_file("timeseries.html")
    fig=vplot(tsline)
    
    # Configure resources to include BokehJS inline in the document.
    # For more details see:
    #   http://bokeh.pydata.org/en/latest/docs/reference/resources_embedding.html#bokeh-embed
    js_resources = JS_RESOURCES.render(
        js_raw=INLINE.js_raw,
        js_files=INLINE.js_files
    )

    css_resources = CSS_RESOURCES.render(
        css_raw=INLINE.css_raw,
        css_files=INLINE.css_files
    )
#from: http://bokeh.pydata.org/en/0.11.1/docs/releases/0.11.0.html  
# Before:

#html = file_html(layout, None, title=title, template=template, js_resources=js_resources, css_resources=css_resources)
#v0.11:
#
#html = file_html(layout, resources=(js_resources, css_resources), title=title, template=template)
 
   # For more details see:
    #   http://bokeh.pydata.org/en/latest/docs/user_guide/embedding.html#components
    script, div = components(fig, INLINE)
    html = render_template(
        'embed.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
        color=color,
        _from=_from,
        to=to
    )
    return encode_utf8(html)

@app.route("/butpush", methods=['GET','POST'])
def butpush():
    if request.method =='GET':
        ssymbol="AAPL"
        return(graphstocks(ssymbol))
    else:
        ssymbol=request.form['symbol_lulu']
        return(graphstocks(ssymbol))




def main():
    #app.debug = True
    app.run(port=33507)

if __name__ == "__main__":
    main()