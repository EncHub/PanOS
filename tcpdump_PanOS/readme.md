Установка tcpdump в PanOS:

```bash
wget --no-check-certificate [https://github.com/EncHub/PanOS/raw/refs/heads/main/tcpdump -O /tmp/tcpdump
```

После загрузки:

1. Сделайте файл исполняемым:
   ```bash
   chmod +x /tmp/tcpdump
   ```

2. Переместите его в системную директорию, чтобы он был доступен:
   ```bash
   mv /tmp/tcpdump /usr/bin/tcpdump
   ```

3. Проверьте установку:
   ```bash
   tcpdump --version
   ```

Если `wget` недоступен, можно использовать `curl` с параметром `-k`, чтобы игнорировать проверки сертификатов:

```bash
curl -k -o /tmp/tcpdump https://github.com/EncHub/PanOS/raw/refs/heads/main/tcpdump
```
