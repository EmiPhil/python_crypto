import sched, time, click, requests, json, re, datetime, sys, os

from terminaltables import AsciiTable

from ascii_graph import Pyasciigraph
from ascii_graph.colors import *
from ascii_graph.colordata import vcolor

from dateutil.relativedelta import relativedelta

from colorama import init
# windows color support
init()

def resize_terminal(rows, cols):
  # linux
  sys.stdout.write('\x1b[8;{rows};{cols}t'.format(rows=rows, cols=cols))
  # windows
  os.system('mode con: cols={cols} lines={rows}'.format(rows=rows, cols=cols))

url = 'https://api.coinmarketcap.com/v1/ticker/?convert=CAD&limit=0'

def fetch_data(url):
  res = requests.get(url)
  if (res.ok):
    data = json.loads(res.content)
    return data

def read_portfolio():
  portfolio = json.load(open('portfolio.json'))
  return portfolio

def portfolio_rows(data, portfolio):
  portfolio_data = []
  for row in data:
    try:
      portfolio[row['id']]
      portfolio_data.append(row)
    except KeyError:
      pass
  return portfolio_data

def total_rows(data):
  static_rows = 8
  return static_rows + (len(data) * 2)

def add_commas(num):
  num = str(num)
  arr = num.split('.')
  x1 = arr[0]
  if (len(arr) > 1):
    x2 = '.' + arr[1]
  else:
    x2 = ''
  rgx = '^(\d+)(\d{3})'
  while (re.match(rgx, x1)):
    m = re.match(rgx, x1)
    x1 = x1.replace(m.group(1), m.group(1) + ',', 1)
      
  return x1 + x2

def style_percent(val):
  val = float(val)
  string = str(val) + '%'
  if val < 0:
    percent = click.style(string, fg='red')
  else:
    percent = click.style(string, fg='white')
  return percent

def time_since(date):
  attrs = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
  human_readable = lambda delta: ['%d %s' % (getattr(delta, attr), getattr(delta, attr) > 1 and attr or attr[:-1]) 
    for attr in attrs if getattr(delta, attr)]
  now = datetime.datetime.fromtimestamp(time.time())
  date = datetime.datetime.fromtimestamp(int(date))
  human = human_readable(relativedelta(now, date))
  string = ', '.join(human) + ' ago'
  return string

def make_table(data, portfolio):
  """Format data into table"""
  table_data = [
    [
      # Header
      click.style('Rank', fg='white'),
      click.style('Coin', fg='white'),
      click.style('CAD Price', fg='white'),
      click.style('Coins Owned', fg='white'),
      click.style('Net Worth', fg='white'),
      click.style('24 Hour Volume', fg='white'),
      click.style('Market Cap', fg='white'),
      click.style('1 Hour', fg='white'),
      click.style('24 Hours', fg='white'),
      click.style('7 Days', fg='white'),
      click.style('Last Updated', fg='white')
    ]
  ]

  for row in data:
    id = row['id']
    table_row = [
      click.style(row['rank'], fg='white'),
      click.style(id, fg='cyan'),
      click.style('$' + add_commas(row['price_cad']), fg='green'),
      click.style(add_commas(portfolio[id]), fg='green'),
      click.style('$' + add_commas(str(int(round(float(portfolio[id]) * float(row['price_cad']),)))), fg='green'),
      click.style('$' + add_commas(format(float(row['24h_volume_cad']), '.2f')), fg='green'),
      click.style('$' + add_commas(format(float(row['market_cap_cad']), '.2f')), fg='green'),
      style_percent(row['percent_change_1h']),
      style_percent(row['percent_change_24h']),
      style_percent(row['percent_change_7d']),
      click.style(time_since(row['last_updated']), fg='white')
    ]
    table_data.append(table_row)
  
  table_instance = AsciiTable(table_data, 'Crypto Stats')
  cols = len(table_instance.table.split('\n')[0])
  resize_terminal(total_rows(data), cols)

  return table_instance.table

def make_graph(data, portfolio):
  bar_data = []
  portfolio_total = 0
  longest = 0
  for row in data:
    id = row['id']
    if (len(id) > longest):
      longest = len(id)
    value = float(portfolio[id]) * float(row['price_cad'])
    bar_data.append((id, value))
    portfolio_total += value
  
  def get_rank(elem):
    id = elem[0]
    for row in data:
      if (row['id'] == id):
        rank = row['rank']
    return int(rank)
  
  bar_data.sort(key=get_rank)

  graph_data = []
  i = 0
  for elem in bar_data:
    i += 1
    id = elem[0]
    value = elem[1]
    label = '$  -  ' + id
    
    spaces = longest - len(id)
    for _ in range(0, spaces):
      label += ' '
    
    percent = '\t' + str(round((value / portfolio_total) * 100, 2)) + '%'
    label += percent

    if (i % 2 == 0):
      label = click.style(label, fg='white')
    else:
      label = click.style(label, fg='cyan')    

    graph_data.append((label, value))
  
  pattern = [Cya, Whi]
  graph_data = vcolor(graph_data, pattern)
  graph = Pyasciigraph(graphsymbol=None)
  bar_graph = graph.graph(label=None, data=graph_data)
  return [bar_graph, portfolio_total]

def pretty_total(total):
  label = click.style(
    'Portfolio CAD Total: ',
    fg='magenta'
  )
  dollars = click.style(
    '$' + str(round(total, 2)),
    fg='yellow', bg='black', bold=True, underline=True
  )
  return label + dollars

def main(cycles):
  cycles += 1
  repeater.enter(6, 1, main, ([cycles]))
  portfolio = read_portfolio()
  data = portfolio_rows(fetch_data(url), portfolio)
  table = make_table(data, portfolio)
  graph_data = make_graph(data, portfolio)
  portfolio_total = pretty_total(graph_data[1])

  click.clear()
  print click.style(
    'Cycles: ' + str(cycles) + ' | Process is ' + click.style('live.', blink=True, fg='green') + '\n',
    fg='white'
  )
  for line in graph_data[0]:
    print line
  print table
  print portfolio_total

repeater = sched.scheduler(time.time, time.sleep)
repeater.enter(0, 1, main, ([0]))
repeater.run()
