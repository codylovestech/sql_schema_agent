import json
import os
from dotenv import load_dotenv

from groq_llm import get_chat

load_dotenv()

from langchain_core.prompts import ChatPromptTemplate


def convert_table_to_sql(node, technology):
    create_table_message = """

    here is a model definition of a database table. 

    Please convert this model to a """ + technology + """ CREATE SQL query with the following considerations (you can not ignore any of them): 

    1. Please us the "NOT EXISTS" clause to avoid creating the table if it already exists when it is supported by the technology.
    2. Escape the table name and the column names with double quotes to avoid reserved words and special characters.
    3. Use a logic where you only create the sql query when the table does not exist.
    4. Convert each column data type to the best corresponding """ + technology + """ data type.When it is a string, please use the most flexible data type of """ + technology + """.
    5. Ignore the comments in the model
    6. Set the Primary Key of the table to the most appropriate column. (mostly the "id" column)
    7. Ignore all constraints in the model

    Your Response: The result of your answer needs to be between a ---START--- and a ---END--- tag and needs to be a string with the CREATE TABLE statement.

    """
    human = "{text}"
    prompt = ChatPromptTemplate.from_messages([("system",
                                                "You are a SQL Developer specialist for " + technology + " and you are very detailed and can not miss any information. "),
                                               ("human", human)])

    chain = prompt | get_chat()

    message = create_table_message + "\n ----- \n" + json.dumps(node)

    data_result = chain.invoke({"text": message})

    return data_result


def create_foreign_keys(edges, technology):
    create_comments = """

        At first, check how to create foreign keys between two tables in """ + technology + """ database.
        
        For every given Edge definition, please create Foreign Key constraints between the tables.
        
        Please escape the table name and the column namesto avoid reserved words and special characters.

        Your Response: The resulting list of SQL commands of your answer needs to be between a ---START--- and a ---END--- tag and needs to be a list of string that only contains the SQL queries. Please dont give any other output than the SQL queries.

        Here is the model:
        
        """
    human = "{text}"
    prompt = ChatPromptTemplate.from_messages([("system",
                                                "You are a SQL Development machine specialised for " + technology + " and you are very detailed and can not miss any information. "),
                                               ("human", human)])

    chain = prompt | get_chat("llama3-70b-8192")

    message = create_comments + "\n ----- \n" + json.dumps(edges)

    data_result = chain.invoke({"text": message})

    return data_result


def convert_comments_to_sql(node, technology):
    create_comments = """
    
    At first, check how to add comments to columns in a table in """+technology+""".

    Next, here is a model definition of a database table.  The database already exists in a """+technology+""" database.

    Please create SQL syntax to update the comments of every column in the table. (You can not ignore any of them)
    
    You need to escape the table name and the column names with double quotes to avoid reserved words and special characters.
    
    Please escape the comments before adding them to the SQL query to avoid SQL injection.
    
    Your Response: The resulting list of SQL commands of your answer needs to be between a ---START--- and a ---END--- tag and needs to be a list of string that only contains the SQL queries. Please dont give any other output than the SQL queries.

    """
    human = "{text}"
    prompt = ChatPromptTemplate.from_messages([("system",
                                                "You are a SQL Development machine specialised for " + technology + " and you are very detailed and can not miss any information. "),
                                               ("human", human)])

    chain = prompt | get_chat("llama3-70b-8192")

    message = create_comments + "\n ----- \n" + json.dumps(node)

    data_result = chain.invoke({"text": message})

    return data_result