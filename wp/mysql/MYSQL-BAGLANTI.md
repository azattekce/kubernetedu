# MySQL Bağlantı Kılavuzu

## 📊 Mevcut Durum

- **Namespace**: wp
- **Service**: wordpress-mysql
- **Pod**: wordpress-mysql-c8f7cc86c-bzvjb
- **Port**: 3306
- **Database**: wp_db
- **Root Password**: wproot
- **User**: burak
- **User Password**: admin

## 🔌 Bağlantı Yöntemleri

### 1. Hızlı Bağlantı (Tek Komut)

```powershell
# Root ile bağlan
kubectl exec -it -n wp deployment/wordpress-mysql -- mysql -u root -pwproot

# Belirli veritabanına bağlan
kubectl exec -it -n wp deployment/wordpress-mysql -- mysql -u burak -padmin wp_db
```

### 2. SQL Sorguları Çalıştırma

```powershell
# Veritabanlarını listele
kubectl exec -it -n wp deployment/wordpress-mysql -- mysql -u root -pwproot -e "SHOW DATABASES;"

# Tabloları listele
kubectl exec -it -n wp deployment/wordpress-mysql -- mysql -u root -pwproot wp_db -e "SHOW TABLES;"

# Kullanıcıları görüntüle
kubectl exec -it -n wp deployment/wordpress-mysql -- mysql -u root -pwproot -e "SELECT User, Host FROM mysql.user;"

# Tablo yapısını görüntüle
kubectl exec -it -n wp deployment/wordpress-mysql -- mysql -u root -pwproot wp_db -e "DESCRIBE table_name;"

# Veri sorgula
kubectl exec -it -n wp deployment/wordpress-mysql -- mysql -u root -pwproot wp_db -e "SELECT * FROM table_name LIMIT 10;"
```

### 3. Port Forward ile GUI Tool Bağlantısı

```powershell
# Terminal'de port forward başlat
kubectl port-forward -n wp service/wordpress-mysql 3306:3306

# MySQL Workbench / DBeaver / HeidiSQL ile bağlan:
# Host: localhost veya 127.0.0.1
# Port: 3306
# Username: root
# Password: wproot
# Database: wp_db
```

### 4. Pod İçinde İnteraktif Çalışma

```powershell
# Pod'a giriş yap
kubectl exec -it -n wp deployment/wordpress-mysql -- bash

# MySQL'e bağlan
mysql -u root -pwproot

# MySQL komutları
SHOW DATABASES;
USE wp_db;
SHOW TABLES;
SELECT DATABASE();
SELECT VERSION();
EXIT;

# Pod'dan çık
exit
```

## 📚 Faydalı MySQL Komutları

### Veritabanı Yönetimi

```sql
-- Tüm veritabanlarını listele
SHOW DATABASES;

-- Veritabanı seç
USE wp_db;

-- Yeni veritabanı oluştur
CREATE DATABASE yeni_db;

-- Veritabanını sil
DROP DATABASE yeni_db;

-- Mevcut veritabanını göster
SELECT DATABASE();
```

### Tablo Yönetimi

```sql
-- Tabloları listele
SHOW TABLES;

-- Tablo yapısını göster
DESCRIBE table_name;
SHOW CREATE TABLE table_name;

-- Tablo oluştur
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tablo sil
DROP TABLE table_name;

-- Tablodaki tüm veriyi sil
TRUNCATE TABLE table_name;
```

### Veri Sorgulama

```sql
-- Tüm kayıtları getir
SELECT * FROM table_name;

-- Sınırlı sayıda kayıt getir
SELECT * FROM table_name LIMIT 10;

-- Belirli sütunları getir
SELECT column1, column2 FROM table_name;

-- Filtreleme ile getir
SELECT * FROM table_name WHERE id = 1;

-- Sıralama ile getir
SELECT * FROM table_name ORDER BY created_at DESC;

-- Kayıt sayısı
SELECT COUNT(*) FROM table_name;
```

### Veri Ekleme ve Güncelleme

```sql
-- Veri ekle
INSERT INTO users (username, email) VALUES ('test', 'test@example.com');

-- Veri güncelle
UPDATE users SET email = 'new@example.com' WHERE id = 1;

-- Veri sil
DELETE FROM users WHERE id = 1;
```

### Kullanıcı Yönetimi

```sql
-- Tüm kullanıcıları listele
SELECT User, Host FROM mysql.user;

-- Yeni kullanıcı oluştur
CREATE USER 'yeni_kullanici'@'%' IDENTIFIED BY 'parola123';

-- Kullanıcıya yetki ver
GRANT ALL PRIVILEGES ON wp_db.* TO 'yeni_kullanici'@'%';

-- Yetkileri uygula
FLUSH PRIVILEGES;

-- Kullanıcı yetkilerini göster
SHOW GRANTS FOR 'burak'@'%';
```

### Sistem Bilgileri

```sql
-- MySQL versiyon
SELECT VERSION();

-- Mevcut kullanıcı
SELECT USER();

-- Sunucu durumu
SHOW STATUS;

-- Değişkenleri göster
SHOW VARIABLES LIKE 'max_connections';

-- Aktif bağlantılar
SHOW PROCESSLIST;
```

## 🔍 Durum Kontrolü (Kubernetes)

```powershell
# Pod durumunu kontrol et
kubectl get pods -n wp -l tier=mysql

# Service'i kontrol et
kubectl get svc -n wp wordpress-mysql

# PVC durumu
kubectl get pvc -n wp mysql-pv-claim

# Pod loglarını görüntüle
kubectl logs -n wp -l tier=mysql

# Pod detayları
kubectl describe pod -n wp -l tier=mysql

# MySQL servisi ile bağlantı testi
kubectl run -it --rm --image=mysql:5.6 --restart=Never mysql-client -n wp -- mysql -h wordpress-mysql -u burak -padmin wp_db
```

## 🛠️ Bakım Komutları

### Backup (Yedekleme)

```powershell
# Tek veritabanı yedekle
kubectl exec -n wp deployment/wordpress-mysql -- mysqldump -u root -pwproot wp_db > wp_db_backup.sql

# Tüm veritabanlarını yedekle
kubectl exec -n wp deployment/wordpress-mysql -- mysqldump -u root -pwproot --all-databases > all_databases_backup.sql

# Sadece tablo yapısı (veri olmadan)
kubectl exec -n wp deployment/wordpress-mysql -- mysqldump -u root -pwproot --no-data wp_db > wp_db_structure.sql
```

### Restore (Geri Yükleme)

```powershell
# Backup'ı pod'a kopyala
kubectl cp wp_db_backup.sql wp/wordpress-mysql-c8f7cc86c-bzvjb:/tmp/

# Restore işlemi
kubectl exec -n wp deployment/wordpress-mysql -- mysql -u root -pwproot wp_db < /tmp/wp_db_backup.sql

# Veya tek komutla
cat wp_db_backup.sql | kubectl exec -i -n wp deployment/wordpress-mysql -- mysql -u root -pwproot wp_db
```

### Log İnceleme

```powershell
# Canlı log izleme
kubectl logs -f -n wp -l tier=mysql

# Son 100 log satırı
kubectl logs --tail=100 -n wp -l tier=mysql

# Hata logları
kubectl logs -n wp -l tier=mysql | Select-String -Pattern "error"
```

## 🐛 Sorun Giderme

### Bağlantı Sorunları

```powershell
# DNS çözümlemesini test et
kubectl run -it --rm --image=busybox --restart=Never dns-test -n wp -- nslookup wordpress-mysql

# Port erişimini test et
kubectl run -it --rm --image=busybox --restart=Never port-test -n wp -- telnet wordpress-mysql 3306

# MySQL client ile test
kubectl run -it --rm --image=mysql:5.6 --restart=Never mysql-test -n wp -- mysql -h wordpress-mysql -u root -pwproot -e "SELECT 1"
```

### Pod Sorunları

```powershell
# Pod durumu detaylı
kubectl describe pod -n wp -l tier=mysql

# Events görüntüle
kubectl get events -n wp --sort-by='.lastTimestamp' | Select-String "mysql"

# Resource kullanımı
kubectl top pod -n wp -l tier=mysql

# Pod'u yeniden başlat
kubectl rollout restart deployment/wordpress-mysql -n wp
```

### Veritabanı Sorunları

```sql
-- Tablo onarma
REPAIR TABLE table_name;

-- Tablo optimizasyonu
OPTIMIZE TABLE table_name;

-- Tablo kontrolü
CHECK TABLE table_name;

-- Bağlantıları göster
SHOW PROCESSLIST;

-- Bağlantıları sonlandır
KILL <process_id>;
```

## 📝 Notlar

- **Password Warning**: Komut satırında parola kullanmak güvenli değildir. Production'da Secret referansları kullanın.
- **Backup**: Düzenli olarak yedek alın (PVC ile otomatik yedeklenir ama SQL dump'ları da önemli).
- **Root Access**: Root kullanıcısını sadece admin işlemleri için kullanın.
- **User Permissions**: Uygulama için burak kullanıcısını kullanın (least privilege principle).

## 🔐 Güvenlik İpuçları

1. Production'da güçlü parolalar kullanın
2. Secret'ları Git'e commit etmeyin
3. Gereksiz kullanıcı yetkilerini kaldırın
4. Network Policy ile erişimi kısıtlayın
5. TLS/SSL ile bağlantıları şifreleyin
6. Düzenli olarak güvenlik güncellemeleri yapın

## 📚 Kaynaklar

- [MySQL 5.6 Documentation](https://dev.mysql.com/doc/refman/5.6/en/)
- [Kubernetes MySQL StatefulSet](https://kubernetes.io/docs/tasks/run-application/run-replicated-stateful-application/)
- [MySQL Docker Hub](https://hub.docker.com/_/mysql)
