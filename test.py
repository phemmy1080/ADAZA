import openai
import streamlit as st


# Set up your OpenAI API key
openai.api_key = "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"

# Make the API call to check the usage
response = openai.Usage.retrieve()

# Print the permissions associated with the API key
print(response['data']['permissions'])
st.write(response['data']['permissions'])
