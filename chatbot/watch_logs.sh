#!/bin/bash

# Script to monitor application logs in real-time
LOG_FILE="/home/ubuntu/environment/apcr-dva/chatbot/log/app.log"

echo "Monitoring logs from: $LOG_FILE"
echo "Press Ctrl+C to stop"
echo "----------------------------------------"

# Follow the log file in real-time
tail -f "$LOG_FILE"