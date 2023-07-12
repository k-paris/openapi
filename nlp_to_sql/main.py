"""
    Convert NLP to SQL via OpenAI API, and send SQL request to database.
    Pandas module is used to convert a tabular source of data into a SQL database in memory
"""
import os
import pandas as pd
import sqlalchemy as sa
import openai

openai.api_key = os.getenv('OPENAI_API_KEY')

# create temp db in RAM
temp_db = sa.create_engine('sqlite:///:memory:', echo=True)

df = pd.read_csv('data/sales_data_sample.csv')

# push pandas df as sql table to temp db
data = df.to_sql(name='Sales', con=temp_db)

def create_table_definition(df):
    """create prompt, provide a table structure (columns names)"""
    promtp = f""" ### sqlite SQL table with it properties:
    #
    # Sales({','.join(str(col) for col in df.columns)})
    #
    """
    return promtp

def prompt_input():
    """user nlp query"""
    nlp_text = input("Enter the info you want extract from DB: ")
    return nlp_text

def combine_prompt(df, query_prompt):
    """combining both parts of prompt"""
    definition = create_table_definition(df)
    query_init_str = f"### A query to answer: {query_prompt}\nSELECT"
    return definition + query_init_str

#hardcoded NLP query
HC_NLP_TEXT = 'return the sum of SALES per POSTALCODE'
nlp_text = HC_NLP_TEXT

# ********  UNCOMENT TO USE USER INPUT FOR NLP QUERY  ***********
# ********  getting NLP query from user  ********
#
# user_nlp_text = prompt_input()
# nlp_text = user_nlp_text
# ***************************************************************

prompt = combine_prompt(df, nlp_text)

print(prompt)

response = openai.Completion.create(
    model="text-davinci-003",
    prompt = prompt,
    temperature = 0,
    max_tokens = 150,
    top_p  = 1.0,
    frequency_penalty = 0,
    presence_penalty = 0,
    stop = ['#', ';']
)

def format_response(response):
    """adding SELECT in front of response"""
    sql_query = response['choices'][0]['text']
    if sql_query.startswith(" "):
        sql_query = "SELECT" + sql_query
    return sql_query

# quering the temp db with SQL query returned by openai
with temp_db.connect() as conn:
    result = conn.execute(sa.text(format_response(response)))
    for row in result:
        print(row)
