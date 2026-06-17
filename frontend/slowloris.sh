while true; do
  echo -ne "GET / HTTP/1.1\r\nHost: 192.168.24.8\r\nAccept: */*\r\nConnection: keep-alive\r\n\r\n" | nc -q 1 192.168.24.8 80
done
