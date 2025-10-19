mkdir -p ~/.streamlit

# Streamlit configuration
echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml