# Streamlit Chatbot with Amazon Bedrock & ElastiCache Redis

A modern, production-ready chatbot application built with Streamlit that uses Amazon Bedrock's Claude 3.5 Sonnet model and ElastiCache Serverless for Redis as conversation memory.

## 🚀 Features

- 🤖 **Claude 3.5 Sonnet**: Latest Anthropic model via Amazon Bedrock
- 💾 **Redis Memory**: Persistent conversation history using ElastiCache Serverless
- 🎛️ **Dynamic Model Selection**: Switch between different Claude models
- 🔄 **Real-time Streaming**: Live response streaming from Bedrock
- 📊 **Advanced Monitoring**: Session management and connection status
- ⚙️ **Configurable Parameters**: Adjustable temperature, max tokens, top-p
- 🔒 **Enterprise Security**: Full AWS IAM integration
- 📱 **Responsive UI**: Modern Streamlit interface

## 🏗️ Architecture

```
User Interface (Streamlit)
         ↓
    Chat Manager
         ↓
Amazon Bedrock (Claude 3.5) ←→ ElastiCache Redis (Memory)
         ↓
    AWS IAM Security
```

## 📋 Prerequisites

- Python 3.8+
- AWS Account with:
  - Amazon Bedrock access (Claude models enabled)
  - ElastiCache Serverless for Redis
  - Appropriate IAM permissions
- AWS CLI configured (recommended)
