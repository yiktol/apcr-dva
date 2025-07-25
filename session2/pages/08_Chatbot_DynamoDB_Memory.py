# ------------------------------------------------------------------------
# Streamlit Chat with DynamoDB Memory - Amazon Bedrock and LangChain
# ------------------------------------------------------------------------
import streamlit as st
import boto3
import botocore
import uuid
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
# from langchain_community.chat_models import BedrockChat
from langchain_aws import ChatBedrock
from langchain_community.chat_message_histories import DynamoDBChatMessageHistory
import utils.common as common
import utils.authenticate as authenticate

def main():
    """Main application function"""
    # Page title
    st.set_page_config(
        page_title='Chatbot with DynamoDB Memory',
        page_icon=":brain:",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    common.initialize_session_state()
        
    st.subheader("Chatbot with DynamoDB Memory")
    st.write("""Amazon DynamoDB can act as the persistent memory to your conversational AI application""")

    # ------------------------------------------------------------------------
    # Amazon Bedrock Settings
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1",
    )

    model_kwargs = {}

    # Sidebar configuration
    with st.sidebar:
        common.render_sidebar()
        
        with st.expander('Model Parameters',expanded=False):
            model = st.selectbox('model', [
                "anthropic.claude-3-sonnet-20240229-v1:0",
                "mistral.mistral-large-2402-v1:0",
                "amazon.titan-tg1-large",
                "meta.llama2-70b-chat-v1"
            ])
            temperature = st.slider('temperature', min_value=0.0, max_value=1.0, value=0.1, step=0.1)
            top_p = st.slider('top_p', min_value=0.0, max_value=1.0, value=0.9, step=0.1)
            max_tokens = st.slider('max_tokens', min_value=50, max_value=4096, value=1024, step=10) 

    # Configure model parameters based on provider
    provider = model.split(":")[0]
    match provider:
        case "anthropic":
            model_kwargs = {
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_k": 200,
                "top_p": top_p,
                "stop_sequences": ["\n\nHuman"],
            }
        case "mistral":
            model_kwargs = {
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_k": 200,
                "top_p": top_p,
            }
        case "amazon":
            model_kwargs = {
                "maxTokenCount": max_tokens,
                "temperature": temperature,
                "topP": top_p,
            }
        case "meta":
            model_kwargs = {
                "max_gen_len": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
            }

    model_id = model

    # ------------------------------------------------------------------------
    # DynamoDB Setup
    TableName = "SessionTable"
    boto3_session = boto3.Session(region_name="us-east-1")
    client = boto3_session.client('dynamodb')
    dynamodb = boto3_session.resource("dynamodb")
    table = dynamodb.Table(TableName)

    # ------------------------------------------------------------------------
    # LCEL: chain(prompt | model | output_parser) + RunnableWithMessageHistory

    template = [
        ("system", "You are a helpful assistant."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]

    prompt = ChatPromptTemplate.from_messages(template)

    bedrock_model = ChatBedrock(
        client=bedrock_runtime,
        model_id=model_id,
        model_kwargs=model_kwargs,
    )

    chain = prompt | bedrock_model | StrOutputParser()

    # Chain with History
    chain_with_history = RunnableWithMessageHistory(
        chain,
        lambda session_id: DynamoDBChatMessageHistory(
            table_name="SessionTable", 
            session_id=session_id, 
            boto3_session=boto3_session
        ),
        input_messages_key="question",
        history_messages_key="history",
    )

    # ------------------------------------------------------------------------
    # Chat Interface Functions
    
    def clear_screen():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]


    def create_dynamodb_table():
        try:
            table = dynamodb.create_table(
                TableName='SessionTable',
                KeySchema=[{'AttributeName': 'SessionId', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'SessionId', 'AttributeType': 'S'}],
                BillingMode='PAY_PER_REQUEST'
            )
            table.meta.client.get_waiter('table_exists').wait(TableName='SessionTable')
            st.sidebar.success('DynamoDB table created!')
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'ResourceInUseException':
                st.sidebar.info('Table already exists!')
            elif error.response['Error']['Code'] == 'AccessDeniedException':
                st.sidebar.warning('Access Denied')
            else:
                st.sidebar.error(f"Error creating table: {error}")

    def delete_dynamodb_table():
        try:
            response = client.delete_table(TableName='SessionTable')
            st.sidebar.success("DynamoDB table is deleted!")
        except client.exceptions.ResourceNotFoundException:
            st.sidebar.info("Table does not exist, nothing to delete")         
        except Exception as e:
            if "AccessDeniedException" in str(e):
                st.sidebar.warning("Access Denied")
            else:
                st.sidebar.error(f"Error deleting DynamoDB table: {e}")

    # ------------------------------------------------------------------------
    # Streamlit UI

    # Store LLM generated responses
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Sidebar controls
    with st.sidebar:
        with st.container(border=True):
            st.write(":orange[Manage DynamoDB Table]")
            if st.button('Create DynamoDB Table'):
                create_dynamodb_table()
            if st.button('Delete DynamoDB Table'):
                delete_dynamodb_table()
                
        with st.container(border=True):
            st.markdown(':orange[Enable/Disable Streaming]')
            streaming_on = st.toggle('Streaming', value=True)
            
        with st.container(border=True):
            st.markdown(':orange[Manage Session]')
            st.button('Clear Chat History', on_click=clear_screen,use_container_width=True)


    # Chat input and processing
    if user_prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.write(user_prompt)

        # Configure the session id
        config = {"configurable": {"session_id": st.session_state.session_id}}

        if streaming_on:
            # Chain - Stream
            with st.chat_message("assistant"):
                placeholder = st.empty()
                full_response = ''
                for chunk in chain_with_history.stream({"question": user_prompt}, config=config):
                    full_response += chunk
                    placeholder.markdown(full_response)
                placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
        else:
            # Chain - Invoke
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):        
                    response = chain_with_history.invoke({"question": user_prompt}, config=config)
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

# Main execution flow
if __name__ == "__main__":
    if 'localhost' in st.context.headers["host"]:
        main()
    else:
        # First check authentication
        is_authenticated = authenticate.login()
        
        # If authenticated, show the main app content
        if is_authenticated:
            main()
