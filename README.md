# Teknofest İKA Parkuru — Gazebo Simülasyonu

2026 Teknofest parkurunun Gazebo Classic 11 için hazırlanmış, gerçek CAD
modelinden (SolidWorks STEP) üretilmiş 1:1 ölçekli simülasyon ortamı.

**İçerik:**

- **Renkli parkur:** kırmızı-beyaz bariyerler, turuncu trafik konileri,
  rampalar (dik/yan eğim), su geçişi, taşlı-çakıllı yol, kasisler
- **Görev tabelaları:** 2–11 arası sayılar (beyaz zemin, siyah rakam,
  kırmızı çerçeve), STOP ve görev-sonu tabelaları (kırmızı zemin, beyaz yazı).
  Rakamlar dokuyla değil geometriyle işlendiği için kamera hangi mesafeden
  bakarsa baksın nettir.
- **Hareketli kayar engel:** 7 m açıklıklı portal çerçevede, kiriş boyunca
  sabit hızla gidip gelen perde. Aracın geçişini zorlaştırır; hız ve hareket
  limitleri ayarlanabilir.

## Gereksinimler

- Ubuntu 20.04/22.04
- Gazebo Classic 11: `sudo apt install gazebo libgazebo-dev`
- Derleme araçları: `sudo apt install cmake g++`

## Çalıştırma

```bash
git clone https://github.com/talhadagci/Gazebo_Parkur.git
cd Gazebo_Parkur
./baslat.sh
```

Script ilk çalıştırmada kayar engel plugin'ini derler, ortam değişkenlerini
ayarlar ve Gazebo'yu açar.

## Kayar engel ayarları

`parkur/worlds/parkur_yeni.world` içinde `kayar_engel` modelinin plugin bölümü:

```xml
<hiz>0.2</hiz>   <!-- kayma hızı, m/s -->
<alt>-2.2</alt>  <!-- başlangıç konumuna göre alt limit, m -->
<ust>1.8</ust>   <!-- başlangıç konumuna göre üst limit, m -->
```

Değişiklikten sonra Gazebo'yu yeniden açmak yeterli, derleme gerekmez.

## Kendi aracını eklemek

World bağımsızdır; kendi rover/araç modelini bu world'e spawn etmen yeterli.
ROS 2 + `gazebo_ros` kullanıyorsan launch dosyanda world olarak
`parkur/worlds/parkur_yeni.world` dosyasını gösterip `GAZEBO_MODEL_PATH`'e
bu repo kökünü, `GAZEBO_PLUGIN_PATH`'e
`parkur/plugins/kayar_engel/build` dizinini eklemen gerekir
(örnek: `baslat.sh`).

## Notlar

- Ölçek 1:1'dir: parkur alanı ~49×42 m, tabela çapı 60 cm (merkez ~2 m
  yükseklikte), portal 7.09×2.46 m, perde stroku 4 m.
- Tabela rakamları tek yüzdedir ve sürüş yönüne göre yerleştirilmiştir.
- "1" ve "12" tabelaları kaynak CAD modelinde bulunmadığından sahnede yoktur.
- Mesh'ler OBJ+MTL formatındadır (metre, Z-up); Gazebo Classic tarafından
  doğrudan yüklenir.
