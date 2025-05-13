#!/bin/bash

# Increase Git buffer size
git config http.postBuffer 524288000  # 500MB

# Try pushing with verbose output
GIT_CURL_VERBOSE=1 GIT_TRACE=1 git push origin tanya1.0