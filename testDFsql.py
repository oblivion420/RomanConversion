from sqlite3 import connect
conn = connect(':standard_dictionary:')
df = pd.DataFrame(data=[[0, '10/11/12'], [1, '12/11/10']],
                  columns=['int_column', 'date_column'])
df.to_sql('test_data', conn)