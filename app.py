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
from dateutil.parser import parse
import dateutil.relativedelta
 #, relativedelta
from datetime import datetime, date

from bokeh.charts import TimeSeries, output_file, vplot
YOURAPIKEY="WQxVvsi1gEbN8yfbQxUH"
import pandas
import requests
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
    edate = date.today().strftime("%Y-%m-%d")
    sdate = date.today()-dateutil.relativedelta.relativedelta(months=1)
    return(graphstocks("AAPL",sdate,edate,"Black"))

    

def graphstocks(ssymbol, sdate, edate,color):
    stock = ssymbol
    if color not in colors:
        color="Black"
    api_url='https://www.quandl.com/api/v3/datasets/WIKI/%(symbol)s.json?api_key=%(key)s&start_date=%(sdate)s&end_date=%(edate)s' % {"symbol":stock, "key":YOURAPIKEY,"sdate":sdate, "edate":edate}
    session = requests.Session()
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
    raw_data=session.get(api_url)
    aapl_stock=raw_data.json()
    color="Black"
    cnames = aapl_stock['dataset']['column_names']
    df = pandas.DataFrame(aapl_stock['dataset']['data'],columns=cnames) # create dataframe and assign column names
    df['Date']=pandas.to_datetime(df['Date']) # convert Date column to DateTime in place
    tsline = TimeSeries(df,x='Date', y='Close', ylabel=ssymbol+' Stock Prices', legend=True, color=colors[color])
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
        _from=sdate,
        to=edate,
        symbol_lulu=ssymbol
    )
    return encode_utf8(html)

@app.route("/butpush", methods=['GET','POST'])
def butpush():
    if request.method =='GET':
        ssymbol="AAPL"
        edate = date.today().strftime("%Y-%m-%d")
        sdate = date.today()-dateutil.relativedelta.relativedelta(months=1)
        return(graphstocks(ssymbol,sdate,edate,"Black"))
    else:
        ssymbol=request.form['symbol_lulu']
        sdate = request.form['_from']
        edate = request.form['to']
        color = request.form['color']
        try: 
            sdate = parse(sdate).strftime("%Y-%m-%d")
            edate = parse(edate).strftime("%Y-%m-%d")
        except ValueError:
            edate = date.today().strftime("%Y-%m-%d")
            sdate = date.today()-dateutil.relativedelta.relativedelta(months=1)
        return(graphstocks(ssymbol,sdate,edate,color))




def main():
    #app.debug = True
    #app.run()
    app.run(port=33507)   #before putting on heroku, take away debug and use port 33507
    #print "HI""hi"

if __name__ == "__main__":
    main()