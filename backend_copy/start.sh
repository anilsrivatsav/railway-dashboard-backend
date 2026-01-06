cat <<EOF > start.sh
#!/bin/bash
uvicorn app.main:app --host 0.0.0.0 --port 10000
EOF
chmod +x start.sh
