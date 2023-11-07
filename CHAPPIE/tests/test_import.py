import pygris

def test_bg():
  g_geos = pygris.block_groups(state='12', county='033', year='2021')
  assert 'GEOID' in g_geos.columns, 'Missing expected column'
